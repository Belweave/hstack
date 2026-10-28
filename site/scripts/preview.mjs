import { createReadStream, existsSync, readFileSync, statSync } from "node:fs";
import http from "node:http";
import path from "node:path";

const dist = path.resolve(import.meta.dirname, "..", "dist");

const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".woff2": "font/woff2",
  ".txt": "text/plain; charset=utf-8",
  ".sha256": "text/plain; charset=utf-8",
  ".gz": "application/gzip",
  ".sh": "text/plain; charset=utf-8",
  ".ps1": "text/plain; charset=utf-8",
};

function send(res, status, body, type, extra) {
  res.writeHead(status, {
    "Content-Type": type,
    "X-Content-Type-Options": "nosniff",
    "Cache-Control": "no-store",
    ...extra,
  });
  res.end(body);
}

function loadHeaders(file) {
  const rules = [];
  let current = null;
  for (const line of readFileSync(file, "utf8").split("\n")) {
    if (!line.trim() || line.trim().startsWith("#")) continue;
    if (!/^\s/.test(line)) {
      current = { path: line.trim(), headers: {} };
      rules.push(current);
      continue;
    }
    const match = line.match(/^\s+([^:]+):\s*(.*)$/);
    if (!match || !current) throw new Error(`bad _headers line: ${line}`);
    current.headers[match[1].trim().toLowerCase()] = match[2].trim();
  }
  return rules;
}

function loadRedirects(file) {
  const rules = [];
  for (const line of readFileSync(file, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const parts = trimmed.split(/\s+/);
    if (parts.length < 3) throw new Error(`bad _redirects line: ${line}`);
    rules.push({ from: parts[0], to: parts[1], status: Number(parts[2]) });
  }
  return rules;
}

function ruleMatches(pathname, rulePath) {
  if (rulePath === pathname) return true;
  if (rulePath.endsWith("/*")) return pathname.startsWith(rulePath.slice(0, -1));
  return false;
}

function headersFor(pathname, rules) {
  const found = {};
  for (const rule of rules) {
    if (ruleMatches(pathname, rule.path)) Object.assign(found, rule.headers);
  }
  return found;
}

export function createPreview() {
  const headerRules = loadHeaders(path.join(dist, "_headers"));
  const redirects = loadRedirects(path.join(dist, "_redirects"));
  return http.createServer((req, res) => {
    const requestUrl = new URL(req.url, "http://127.0.0.1");
    let pathname;
    try {
      pathname = decodeURIComponent(requestUrl.pathname);
    } catch {
      return send(res, 400, "bad request\n", "text/plain; charset=utf-8");
    }
    const host = String(req.headers.host || "").split(":")[0];
    const forwarded = String(req.headers["x-forwarded-proto"] || "");
    if ((host === "hstack.sh" || host === "www.hstack.sh") && forwarded !== "https") {
      const targetHost = host === "www.hstack.sh" ? "www.hstack.sh" : "hstack.sh";
      return send(res, 301, "\n", "text/plain; charset=utf-8", {
        Location: `https://${targetHost}${pathname}${requestUrl.search}`,
      });
    }
    const original = pathname;
    const redirect = redirects.find((rule) => rule.from === original);
    if (redirect && (redirect.status === 301 || redirect.status === 302)) {
      return send(res, redirect.status, "\n", "text/plain; charset=utf-8", {
        Location: redirect.to,
      });
    }
    if (redirect && redirect.status === 200 && redirect.to.startsWith("/")) {
      pathname = redirect.to;
    }
    if (original.startsWith("/install/") && original !== "/install/") {
      return send(res, 404, "not found\n", "text/plain; charset=utf-8");
    }
    const rel = pathname === "/" ? "/index.html" : pathname;
    const file = path.normalize(path.join(dist, rel));
    if (file !== dist && !file.startsWith(`${dist}${path.sep}`)) {
      return send(res, 400, "bad request\n", "text/plain; charset=utf-8");
    }
    const headerType = headersFor(original, headerRules)["content-type"];
    if (existsSync(file) && statSync(file).isFile()) {
      const type = headerType || types[path.extname(file)] || "application/octet-stream";
      res.writeHead(200, {
        "Content-Type": type,
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "no-store",
      });
      createReadStream(file).pipe(res);
      return;
    }
    if (original.startsWith("/install")) {
      return send(res, 404, "not found\n", "text/plain; charset=utf-8");
    }
    return send(res, 404, readFileSync(path.join(dist, "404.html")), "text/html; charset=utf-8");
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(import.meta.filename)) {
  const port = Number(process.env.PORT || 4173);
  createPreview().listen(port, "127.0.0.1", () => {
    console.log(`http://127.0.0.1:${port}`);
  });
}
