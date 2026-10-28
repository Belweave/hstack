import { readFileSync } from "node:fs";
import http from "node:http";
import path from "node:path";
import { createPreview } from "./preview.mjs";

const site = path.resolve(import.meta.dirname, "..");
const dist = path.join(site, "dist");

function fail(message) {
  console.error(`check-pages: ${message}`);
  process.exitCode = 1;
}

function parseHeaders(text) {
  const rules = [];
  let current = null;
  for (const line of text.split("\n")) {
    if (!line.trim() || line.trim().startsWith("#")) continue;
    if (!/^\s/.test(line)) {
      current = { path: line.trim(), headers: {} };
      rules.push(current);
      continue;
    }
    const match = line.match(/^\s+([^:]+):\s*(.*)$/);
    if (!match || !current) fail(`bad header line ${line}`);
    else current.headers[match[1].trim().toLowerCase()] = match[2].trim();
  }
  return rules;
}

function contentType(rules, rulePath) {
  const matches = rules.filter((rule) => {
    if (rule.path === rulePath) return true;
    if (rule.path.endsWith("/*")) return rulePath.startsWith(rule.path.slice(0, -1));
    return false;
  });
  return matches.length ? matches[matches.length - 1].headers["content-type"] : "";
}

const sourceHeaders = readFileSync(path.join(site, "_headers"), "utf8");
const builtHeaders = readFileSync(path.join(dist, "_headers"), "utf8");
const sourceRedirects = readFileSync(path.join(site, "_redirects"), "utf8");
const builtRedirects = readFileSync(path.join(dist, "_redirects"), "utf8");
if (sourceHeaders !== builtHeaders) fail("dist/_headers differs from site/_headers");
if (sourceRedirects !== builtRedirects) fail("dist/_redirects differs from site/_redirects");

const rules = parseHeaders(builtHeaders);
for (const rulePath of ["/install", "/install/", "/install.sh", "/install.ps1"]) {
  if (contentType(rules, rulePath) !== "text/plain; charset=utf-8") {
    fail(`${rulePath} content-type is not text/plain`);
  }
}

const redirectLines = builtRedirects.split("\n").map((line) => line.trim()).filter((line) => line && !line.startsWith("#"));
for (const from of ["/install", "/install/"]) {
  const line = redirectLines.find((entry) => entry.startsWith(`${from} `) || entry.startsWith(`${from}\t`));
  if (!line || !line.includes("/install.sh") || !/\s200$/.test(line)) {
    fail(`${from} is not a 200 rewrite to /install.sh`);
  }
}
if (redirectLines.some((line) => /\s404$/.test(line) || line.includes("http://"))) {
  fail("_redirects uses a 404 status or a protocol redirect Pages will ignore");
}

const installer = readFileSync(path.join(dist, "install.sh"), "utf8");
if (!installer.startsWith("#!/bin/sh")) fail("dist/install.sh is missing its shebang");
if (/<!doctype|<html/i.test(installer)) fail("dist/install.sh contains HTML");
if (installer.includes("github.com")) fail("dist/install.sh points at GitHub");
const windows = readFileSync(path.join(dist, "install.ps1"), "utf8");
if (windows.includes("github.com") || !windows.includes("HSTACK_BASE_URL")) {
  fail("dist/install.ps1 is not the site downloader");
}

const missing = readFileSync(path.join(site, "functions", "install", "[...path].js"), "utf8");
if (!missing.includes('new Response("not found\\n"') || !missing.includes("status: 404")) {
  fail("install 404 function does not return plain text");
}
if (/<!doctype|<html/i.test(missing)) fail("install 404 function contains HTML");

const server = createPreview();
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const { port } = server.address();

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

try {
  for (const urlPath of ["/install", "/install/"]) {
    const redirected = await request(urlPath, { Host: "hstack.sh" });
    if (redirected.status !== 301) fail(`${urlPath} over HTTP returned ${redirected.status}`);
    if (redirected.headers.location !== `https://hstack.sh${urlPath}`) {
      fail(`${urlPath} location ${redirected.headers.location}`);
    }
    if (/<!doctype|<html/i.test(redirected.body)) fail(`${urlPath} redirect body is HTML`);
    const followed = await request(urlPath, { Host: "hstack.sh", "X-Forwarded-Proto": "https" });
    const type = followed.headers["content-type"] || "";
    if (followed.status !== 200 || !type.startsWith("text/plain")) fail(`${urlPath} follow is ${followed.status} ${type}`);
    if (!followed.body.startsWith("#!/bin/sh") || /<!doctype|<html/i.test(followed.body)) {
      fail(`${urlPath} follow is not the installer`);
    }
  }
  for (const urlPath of ["/install/missing", "/install/foo/bar"]) {
    const redirected = await request(urlPath, { Host: "hstack.sh" });
    if (redirected.status !== 301 || redirected.headers.location !== `https://hstack.sh${urlPath}`) {
      fail(`${urlPath} did not redirect to HTTPS`);
    }
    if (/<!doctype|<html/i.test(redirected.body)) fail(`${urlPath} redirect body is HTML`);
    const missingPage = await request(urlPath, { Host: "hstack.sh", "X-Forwarded-Proto": "https" });
    const type = missingPage.headers["content-type"] || "";
    if (missingPage.status !== 404 || !type.startsWith("text/plain")) {
      fail(`${urlPath} returned ${missingPage.status} ${type}`);
    }
    if (missingPage.body !== "not found\n" || /<!doctype|<html/i.test(missingPage.body)) {
      fail(`${urlPath} 404 is not plain text`);
    }
  }
} finally {
  await new Promise((resolve) => server.close(resolve));
}

if (process.exitCode) process.exit(process.exitCode);
console.log("check-pages: install headers, https redirect, and plain-text 404 ok");
