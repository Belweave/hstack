import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";

const base = process.env.SHOT_URL || "http://127.0.0.1:4173";
const outDir = process.env.SHOT_DIR || "/opt/cursor/artifacts";
mkdirSync(outDir, { recursive: true });

const chrome = spawn("google-chrome", [
  "--headless=new",
  "--no-sandbox",
  "--disable-gpu",
  "--hide-scrollbars",
  "--remote-debugging-port=9333",
  "--user-data-dir=/tmp/chrome-hstack-redesign",
  "about:blank",
], { stdio: "ignore" });

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function browserSocket() {
  for (let i = 0; i < 50; i += 1) {
    try {
      const version = await (await fetch("http://127.0.0.1:9333/json/version")).json();
      return version.webSocketDebuggerUrl;
    } catch {
      await sleep(150);
    }
  }
  throw new Error("chrome did not open a debugging port");
}

let seq = 0;
function cdp(ws) {
  const pending = new Map();
  ws.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const { resolve, reject } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) reject(new Error(JSON.stringify(message.error)));
      else resolve(message.result);
    }
  });
  return {
    call(method, params = {}) {
      return new Promise((resolve, reject) => {
        const id = ++seq;
        pending.set(id, { resolve, reject });
        ws.send(JSON.stringify({ id, method, params }));
      });
    },
  };
}

const browser = new WebSocket(await browserSocket());
await new Promise((resolve) => browser.addEventListener("open", resolve));
const send = cdp(browser);
const { targetId } = await send.call("Target.createTarget", { url: "about:blank" });
const { webSocketDebuggerUrl } = (await (await fetch("http://127.0.0.1:9333/json/list")).json())
  .find((target) => target.id === targetId);
const page = new WebSocket(webSocketDebuggerUrl);
await new Promise((resolve) => page.addEventListener("open", resolve));
const call = cdp(page);
await call.call("Page.enable");
await call.call("Runtime.enable");
try {
  await call.call("Browser.grantPermissions", {
    origin: base,
    permissions: ["clipboardReadWrite", "clipboardSanitizedWrite"],
  });
} catch {
  // Clipboard is best-effort in this headless session.
}

async function evaluate(expression) {
  const result = await call.call("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    const detail = result.exceptionDetails.exception?.description || result.exceptionDetails.text;
    throw new Error(detail || "page exception");
  }
  return result.result?.value;
}

async function open(urlPath, width, height, mobile) {
  await call.call("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile,
  });
  await call.call("Page.navigate", { url: `${base}${urlPath}` });
  await call.call("Page.loadEventFired").catch(() => {});
  for (let i = 0; i < 40; i += 1) {
    const ready = await evaluate("document.readyState");
    if (ready === "complete") break;
    await sleep(50);
  }
  await evaluate("document.fonts.ready");
  await sleep(40);
}

async function shot(name) {
  const { data } = await call.call("Page.captureScreenshot", { format: "png" });
  const file = path.join(outDir, `${name}.png`);
  writeFileSync(file, Buffer.from(data, "base64"));
  console.log(file);
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

try {
const pages = [
  ["/ ", "home"],
  ["/docs", "docs"],
  ["/skills/reframe", "skill"],
  ["/parity", "parity"],
];

for (const [urlPath, name] of pages) {
  const route = urlPath.trim();
  await open(route, 1440, 900, false);
  if (name === "parity") {
    await evaluate("(() => { const el = document.querySelector('.filters'); window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 80); })()");
  }
  await shot(`${name}-desktop`);
  await open(route, 390, 844, true);
  if (name === "parity") {
    await evaluate("(() => { const el = document.querySelector('.filters'); window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 64); })()");
  }
  await shot(`${name}-mobile`);
}

await open("/", 1440, 900, false);
const fontReady = await evaluate("document.fonts.check('16px \"Paper Mono\"')");
assert(fontReady === true, "Paper Mono did not load");
const windows = await evaluate(`
  document.querySelector("#tab-1-1").click();
  const selected = document.querySelector("#tab-1-1").getAttribute("aria-selected");
  const text = document.querySelector("#panel-1-1").innerText;
  selected === "true" && text.includes("install.ps1") && document.querySelector("#panel-1-0").hidden === true
`);
assert(windows === true, "install tabs did not switch to Windows");
const copied = await evaluate(`
  (async () => {
    const button = document.querySelector("#panel-1-1 [data-copy]");
    button.click();
    await new Promise((resolve) => setTimeout(resolve, 50));
    const wrote = await navigator.clipboard.readText();
    return button.textContent === "Copied" && wrote.includes("install.ps1");
  })()
`);
assert(copied === true, "copy button did not write the Windows command");

await open("/parity", 1440, 900, false);
const filtered = await evaluate(`(() => {
  const input = document.querySelector("#parity-q");
  input.value = "canary";
  input.dispatchEvent(new Event("input", { bubbles: true }));
  const text = document.querySelector("#parity-count").textContent;
  const shown = [...document.querySelectorAll("[data-parity-row]")].filter((row) => !row.hidden).length;
  return text.includes("of 520") && shown > 0 && shown < 520;
})()`);
assert(filtered === true, "parity search did not filter");
const source = await evaluate(`(() => {
  const input = document.querySelector("#parity-q");
  input.value = "";
  input.dispatchEvent(new Event("input", { bubbles: true }));
  document.querySelector('[data-filter="source"][data-value="tstack"]').click();
  const pressed = document.querySelector('[data-filter="source"][data-value="tstack"]').getAttribute("aria-pressed");
  const shown = [...document.querySelectorAll("[data-parity-row]")].filter((row) => !row.hidden).length;
  return pressed === "true" && shown > 0 && shown < 520;
})()`);
assert(source === true, "parity source filter did not apply");

await open("/docs", 390, 844, true);
const menu = await evaluate(`
  const button = document.querySelector(".menu");
  const before = getComputedStyle(document.querySelector(".top nav")).display;
  button.click();
  const after = getComputedStyle(document.querySelector(".top nav")).display;
  before === "none" && after !== "none" && button.getAttribute("aria-expanded") === "true"
`);
assert(menu === true, "mobile menu did not open");
await shot("docs-mobile-menu");

await open("/og.html", 1280, 640, false);
const { data } = await call.call("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: 1280, height: 640, scale: 1 } });
const og = Buffer.from(data, "base64");
writeFileSync(path.join(outDir, "social-preview.png"), og);
writeFileSync("/workspace/.github/social-preview.png", og);
writeFileSync("/workspace/site/dist/social-preview.png", og);
console.log("social-preview.png");

console.log("shots ok");
} finally {
  browser.close();
  page.close();
  chrome.kill();
}
