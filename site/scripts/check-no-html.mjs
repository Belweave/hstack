import { readFileSync } from "node:fs";
import path from "node:path";
import { createPreview } from "./preview.mjs";

const dist = path.resolve(import.meta.dirname, "..", "dist");
const html = readFileSync(path.join(dist, "index.html"), "utf8");
const server = createPreview();
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const { port } = server.address();
const base = `http://127.0.0.1:${port}`;

function fail(message) {
  console.error(`check-no-html: ${message}`);
  process.exitCode = 1;
}

const urls = new Set(["/favicon.svg", "/social-preview.png", "/install", "/install/", "/install.sh", "/install.ps1"]);
for (const match of html.matchAll(/(?:src|href)="(\/[^"]+)"/g)) urls.add(match[1]);
const style = html.match(/<style>([\s\S]*?)<\/style>/);
if (!style) fail("missing inlined css");
else {
  for (const match of style[1].matchAll(/url\(([^)]+)\)/g)) {
    urls.add(match[1].replace(/['"]/g, ""));
  }
}
for (const name of ["hstack.tar.gz", "hstack.tar.gz.sha256", "hstack-v0.1.0.tar.gz", "hstack-v0.1.0.tar.gz.sha256"]) {
  urls.add(`/dl/${name}`);
}

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
  const versioned = Buffer.from(await (await fetch(`${base}/dl/hstack-v0.1.0.tar.gz`)).arrayBuffer());
  if (!versioned.equals(archive)) fail("latest alias is not the versioned archive");

  const page = await (await fetch(`${base}/no-such-page`)).text();
  if (!page.includes("<html")) fail("site 404 should stay an HTML page");
} finally {
  await new Promise((resolve) => server.close(resolve));
}

if (process.exitCode) process.exit(process.exitCode);
console.log(`check-no-html: ${urls.size} assets ok`);
