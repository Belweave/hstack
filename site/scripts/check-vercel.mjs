import { createReadStream, existsSync, readFileSync, statSync } from "node:fs";
import http from "node:http";
import path from "node:path";

const site = path.resolve(import.meta.dirname, "..");
const dist = path.join(site, "dist");
const config = JSON.parse(readFileSync(path.join(site, "vercel.json"), "utf8"));

function fail(message) {
  console.error(`check-vercel: ${message}`);
  process.exitCode = 1;
}

if (config.framework !== null) fail("framework is not null");
if (config.buildCommand !== "npm run build") fail("buildCommand");
if (config.outputDirectory !== "dist") fail("outputDirectory");
if (config.cleanUrls !== true) fail("cleanUrls");

function headerValue(source, key) {
  const rule = config.headers.find((item) => item.source === source);
  const found = rule?.headers.find((item) => item.key.toLowerCase() === key.toLowerCase());
  return found?.value || "";
}

for (const source of ["/install", "/install/", "/install.sh"]) {
  if (headerValue(source, "content-type") !== "text/plain; charset=utf-8") fail(`${source} content-type`);
  if (!headerValue(source, "cache-control").includes("max-age=60")) fail(`${source} cache`);
}
if (headerValue("/(.*).tar.gz", "content-type") !== "application/gzip") fail("tar.gz content-type");
if (!headerValue("/(.*).sha256", "content-type").startsWith("text/plain")) fail("sha256 content-type");

const installRewrite = config.rewrites.find((item) => item.source === "/install");
const slashRewrite = config.rewrites.find((item) => item.source === "/install/");
const missRewrite = config.rewrites.find((item) => item.source === "/install/:path+");
if (installRewrite?.destination !== "/install.sh" || slashRewrite?.destination !== "/install.sh") {
  fail("install rewrites");
}
if (missRewrite?.destination !== "/install-404.txt" || missRewrite.statusCode !== 404) {
  fail("install 404 rewrite");
}

const www = config.redirects.find((item) => item.has?.some((cond) => cond.value?.eq === "www.hstack.sh"));
if (www?.destination !== "https://hstack.sh/:path*" || www.statusCode !== 308) fail("www redirect");
const httpRedirect = config.redirects.find((item) => item.has?.some((cond) => cond.value?.eq === "http"));
if (httpRedirect?.destination !== "https://hstack.sh/:path*" || httpRedirect.statusCode !== 308) {
  fail("http redirect");
}
if (readFileSync(path.join(dist, "install-404.txt"), "utf8") !== "not found\n") fail("404 body");

function compile(source) {
  const names = [];
  let re = "^";
  let index = 0;
  while (index < source.length) {
    if (source.startsWith(":path*", index)) {
      names.push("path");
      re += "(.*)";
      index += 6;
      continue;
    }
    if (source.startsWith(":path+", index)) {
      names.push("path");
      re += "(.+)";
      index += 6;
      continue;
    }
    if (source.startsWith("(.*)", index)) {
      names.push("splat");
      re += "(.*)";
      index += 4;
      continue;
    }
    const ch = source[index];
    re += /[.+?^${}()|[\]\\]/.test(ch) ? `\\${ch}` : ch;
    index += 1;
  }
  return { re: new RegExp(`${re}$`), names };
}

const compiled = new Map();
function matchSource(source, pathname) {
  if (!compiled.has(source)) compiled.set(source, compile(source));
  const { re, names } = compiled.get(source);
  const found = re.exec(pathname);
  if (!found) return null;
  const params = {};
  names.forEach((name, i) => {
    params[name] = found[i + 1] ?? "";
  });
  return params;
}

function conditionMatches(value, actual) {
  if (value && typeof value === "object") return value.eq === undefined || value.eq === actual;
  return value === undefined || value === actual;
}

function hasMatch(has, request) {
  if (!has) return true;
  return has.every((cond) => {
    if (cond.type === "host") return conditionMatches(cond.value, request.host);
    if (cond.type === "header") return conditionMatches(cond.value, request.headers[cond.key.toLowerCase()] || "");
    return false;
  });
}

function fill(template, params) {
  return template.replaceAll(":path*", params.path ?? "").replaceAll(":path+", params.path ?? "");
}

function headersFor(pathname) {
  const out = {};
  for (const rule of config.headers) {
    if (!matchSource(rule.source, pathname)) continue;
    for (const header of rule.headers) out[header.key.toLowerCase()] = header.value;
  }
  return out;
}

const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".sha256": "text/plain; charset=utf-8",
  ".gz": "application/gzip",
  ".sh": "text/plain; charset=utf-8",
  ".ps1": "text/plain; charset=utf-8",
};

function createServer() {
  return http.createServer((req, res) => {
    const requestUrl = new URL(req.url, "http://127.0.0.1");
    const pathname = decodeURIComponent(requestUrl.pathname);
    const host = String(req.headers.host || "").split(":")[0];
    const request = { host, headers: req.headers };
    for (const rule of config.redirects) {
      const params = matchSource(rule.source, pathname);
      if (!params || !hasMatch(rule.has, request)) continue;
      const status = rule.statusCode || (rule.permanent === false ? 307 : 308);
      res.writeHead(status, {
        Location: `${fill(rule.destination, params)}${requestUrl.search}`,
        "Content-Type": "text/plain; charset=utf-8",
      });
      res.end("");
      return;
    }
    let servePath = pathname;
    let status = 200;
    for (const rule of config.rewrites) {
      const params = matchSource(rule.source, pathname);
      if (!params || !hasMatch(rule.has, request)) continue;
      servePath = fill(rule.destination, params);
      if (rule.statusCode) status = rule.statusCode;
      break;
    }
    const file = path.normalize(path.join(dist, servePath === "/" ? "/index.html" : servePath));
    const matched = headersFor(pathname);
    if (!file.startsWith(`${dist}${path.sep}`) && file !== dist) {
      res.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("bad request\n");
      return;
    }
    if (!existsSync(file) || !statSync(file).isFile()) {
      res.writeHead(404, { "Content-Type": "text/html; charset=utf-8" });
      res.end(readFileSync(path.join(dist, "404.html")));
      return;
    }
    const type = matched["content-type"] || types[path.extname(file)] || "application/octet-stream";
    res.writeHead(status, {
      "Content-Type": type,
      ...(matched["cache-control"] ? { "Cache-Control": matched["cache-control"] } : {}),
      ...(matched["x-content-type-options"] ? { "X-Content-Type-Options": matched["x-content-type-options"] } : {}),
    });
    createReadStream(file).pipe(res);
  });
}

function request(urlPath, headers) {
  return new Promise((resolve, reject) => {
    const req = http.request({ hostname: "127.0.0.1", port, path: urlPath, headers }, (res) => {
      const chunks = [];
      res.on("data", (chunk) => chunks.push(chunk));
      res.on("end", () => resolve({
        status: res.statusCode,
        headers: res.headers,
        body: Buffer.concat(chunks).toString("utf8"),
      }));
    });
    req.on("error", reject);
    req.end();
  });
}

const server = createServer();
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const { port } = server.address();

try {
  for (const urlPath of ["/install", "/install/", "/install.sh"]) {
    const response = await request(urlPath, { Host: "hstack.sh", "X-Forwarded-Proto": "https" });
    const type = response.headers["content-type"] || "";
    if (response.status !== 200 || !type.startsWith("text/plain")) fail(`${urlPath} ${response.status} ${type}`);
    if (!response.body.startsWith("#!/bin/sh") || /<!doctype|<html/i.test(response.body)) fail(`${urlPath} body`);
    if (!String(response.headers["cache-control"] || "").includes("max-age=60")) fail(`${urlPath} cache header`);
  }
  for (const urlPath of ["/dl/hstack.tar.gz", "/dl/hstack-v0.1.0.tar.gz", "/dl/hstack-v0.2.0.tar.gz"]) {
    const response = await request(urlPath, { Host: "127.0.0.1" });
    if (response.status !== 200 || response.headers["content-type"] !== "application/gzip") {
      fail(`${urlPath} ${response.status} ${response.headers["content-type"]}`);
    }
  }
  const sum = await request("/dl/hstack.tar.gz.sha256", { Host: "127.0.0.1" });
  if (sum.status !== 200 || !String(sum.headers["content-type"]).startsWith("text/plain")) fail("sha256 response");
  for (const urlPath of ["/install/missing", "/install/foo/bar"]) {
    const response = await request(urlPath, { Host: "hstack.sh", "X-Forwarded-Proto": "https" });
    const type = response.headers["content-type"] || "";
    if (response.status !== 404 || !type.startsWith("text/plain") || response.body !== "not found\n") {
      fail(`${urlPath} ${response.status} ${type} ${JSON.stringify(response.body)}`);
    }
    if (/<!doctype|<html/i.test(response.body)) fail(`${urlPath} html`);
  }
  const wwwResponse = await request("/install?x=1", { Host: "www.hstack.sh" });
  if (wwwResponse.status !== 308 || wwwResponse.headers.location !== "https://hstack.sh/install?x=1") {
    fail(`www ${wwwResponse.status} ${wwwResponse.headers.location}`);
  }
  if (/<!doctype|<html/i.test(wwwResponse.body)) fail("www body is html");
  const httpResponse = await request("/install/", { Host: "hstack.sh", "X-Forwarded-Proto": "http" });
  if (httpResponse.status !== 308 || httpResponse.headers.location !== "https://hstack.sh/install/") {
    fail(`http ${httpResponse.status} ${httpResponse.headers.location}`);
  }
  const secure = await request("/install", { Host: "hstack.sh", "X-Forwarded-Proto": "https" });
  if (secure.status !== 200) fail("https apex redirected");
} finally {
  await new Promise((resolve) => server.close(resolve));
}

if (process.exitCode) process.exit(process.exitCode);
console.log("check-vercel: headers, plain-text 404, and 308 redirects ok");
