import { readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { createPreview } from "./preview.mjs";

const dist = path.resolve(import.meta.dirname, "..", "dist");
const server = createPreview();
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const { port } = server.address();
const base = `http://127.0.0.1:${port}`;

function fail(message) {
  console.error(`check-no-html: ${message}`);
  process.exitCode = 1;
}

function walk(dir) {
  const files = [];
  for (const name of readdirSync(dir)) {
    const file = path.join(dir, name);
    if (statSync(file).isDirectory()) files.push(...walk(file));
    else files.push(file);
  }
  return files;
}

const htmlFiles = walk(dist).filter((file) => file.endsWith(".html") && !file.endsWith(`${path.sep}og.html`));
const urls = new Set([
  "/favicon.svg",
  "/social-preview.png",
  "/install",
  "/install/",
  "/install.sh",
  "/install.ps1",
  "/fonts/LICENSE.txt",
  "/dl/hstack.tar.gz",
  "/dl/hstack.tar.gz.sha256",
  "/dl/hstack-v0.1.0.tar.gz",
  "/dl/hstack-v0.1.0.tar.gz.sha256",
  "/dl/hstack-v0.2.0.tar.gz",
  "/dl/hstack-v0.2.0.tar.gz.sha256",
]);
const external = new Set();

function addUrl(raw) {
  if (!raw || raw.startsWith("#") || raw.startsWith("mailto:")) return;
  let url;
  try {
    url = new URL(raw, "https://hstack.sh");
  } catch {
    fail(`bad url ${raw}`);
    return;
  }
  if (url.origin === "https://hstack.sh") urls.add(url.pathname);
  else external.add(url.href);
}

for (const file of htmlFiles) {
  const html = readFileSync(file, "utf8");
  if (!html.includes("<html")) fail(`${file} is not an html document`);
  if (!html.includes('href="/license"') || !html.includes('href="/notices"')) {
    fail(`${file} is missing the MIT or third-party notices link`);
  }
  if (!html.includes("not affiliated with, endorsed by, or an official product of Nous Research")) {
    fail(`${file} is missing the Nous disclaimer`);
  }
  for (const match of html.matchAll(/(?:src|href)="([^"]+)"/g)) addUrl(match[1]);
}

const css = readFileSync(path.join(dist, "assets", "site.css"), "utf8");
for (const match of css.matchAll(/url\(([^)]+)\)/g)) addUrl(match[1].replace(/['"]/g, ""));
if (css.includes("<style>") || !css.includes("PaperMono")) fail("stylesheet is missing the self-hosted font");

try {
  for (const url of urls) {
    const response = await fetch(base + url);
    if (response.status !== 200) fail(`${url} returned ${response.status}`);
    const body = Buffer.from(await response.arrayBuffer());
    if (body.length === 0) fail(`${url} was empty`);
    if (url === "/install" || url === "/install/" || url === "/install.sh" || url === "/install.ps1") {
      const type = response.headers.get("content-type") || "";
      const text = body.toString("utf8");
      if (!type.startsWith("text/plain")) fail(`${url} content-type ${type}`);
      if (url !== "/install.ps1" && !text.startsWith("#!/bin/sh")) fail(`${url} is not the installer`);
      if (url === "/install.ps1" && !text.includes("HSTACK_BASE_URL")) fail(`${url} is not the Windows installer`);
      if (/<!doctype|<html/i.test(text)) fail(`${url} contains HTML`);
    }
  }

  for (const url of external) {
    const response = await fetch(url, { redirect: "follow" });
    if (response.status >= 400) fail(`${url} returned ${response.status}`);
  }

  for (const url of ["/install/missing", "/install/foo/bar"]) {
    const response = await fetch(base + url);
    const type = response.headers.get("content-type") || "";
    const text = await response.text();
    if (response.status !== 404) fail(`${url} returned ${response.status}`);
    if (!type.startsWith("text/plain")) fail(`${url} content-type ${type}`);
    if (/<!doctype|<html/i.test(text)) fail(`${url} 404 is HTML`);
  }

  const sums = await (await fetch(`${base}/dl/hstack.tar.gz.sha256`)).text();
  const digest = sums.trim().split(/\s+/)[0];
  const archive = Buffer.from(await (await fetch(`${base}/dl/hstack.tar.gz`)).arrayBuffer());
  const { createHash } = await import("node:crypto");
  const actual = createHash("sha256").update(archive).digest("hex");
  if (actual !== digest) fail("hstack.tar.gz does not match its sha256");
  const current = Buffer.from(await (await fetch(`${base}/dl/hstack-v0.2.0.tar.gz`)).arrayBuffer());
  if (!current.equals(archive)) fail("latest alias is not hstack-v0.2.0.tar.gz");
  const frozen = Buffer.from(await (await fetch(`${base}/dl/hstack-v0.1.0.tar.gz`)).arrayBuffer());
  const frozenHash = createHash("sha256").update(frozen).digest("hex");
  if (frozenHash !== "0c8009ee04fb31126b76e4202c91eee14e8d5be7d1cd42ac0cee551012eeda6e") {
    fail("hstack-v0.1.0.tar.gz bytes changed");
  }
  if (frozen.equals(archive)) fail("latest alias is still the 0.1.0 archive");
  const frozenSum = await (await fetch(`${base}/dl/hstack-v0.1.0.tar.gz.sha256`)).text();
  if (!frozenSum.startsWith(`${frozenHash}  hstack-v0.1.0.tar.gz`)) fail("v0.1.0 checksum file drifted");

  const page = await (await fetch(`${base}/no-such-page`)).text();
  if (!page.includes("<html")) fail("site 404 should stay an HTML page");
  if (!page.includes('href="/notices"')) fail("site 404 is missing the notices link");
} finally {
  await new Promise((resolve) => server.close(resolve));
}

if (process.exitCode) process.exit(process.exitCode);
console.log(`check-no-html: ${htmlFiles.length} pages, ${urls.size} local urls, ${external.size} external urls`);
