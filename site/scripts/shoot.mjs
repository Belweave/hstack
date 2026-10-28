import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";

const base = process.env.SHOT_URL || "http://127.0.0.1:4173/";
const outDir = process.env.SHOT_DIR || "/tmp/hstack-shots";
mkdirSync(outDir, { recursive: true });

const chrome = spawn("google-chrome", [
  "--headless=new",
  "--no-sandbox",
  "--disable-gpu",
  "--remote-debugging-port=9222",
  "--user-data-dir=/tmp/chrome-hstack-shots",
  "about:blank",
], { stdio: "ignore" });

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function browserSocket() {
  for (let i = 0; i < 40; i += 1) {
    try {
      const version = await (await fetch("http://127.0.0.1:9222/json/version")).json();
      return version.webSocketDebuggerUrl;
    } catch {
      await sleep(150);
    }
  }
  throw new Error("chrome did not open a debugging port");
}

let id = 0;
function cdp(ws) {
  const pending = new Map();
  const events = new Map();
  ws.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const { resolve, reject } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) reject(new Error(JSON.stringify(message.error)));
      else resolve(message.result);
    } else if (message.method) {
      for (const fn of events.get(message.method) || []) fn(message.params);
    }
  });
  return {
    call(method, params = {}) {
      return new Promise((resolve, reject) => {
        const next = ++id;
        pending.set(next, { resolve, reject });
        ws.send(JSON.stringify({ id: next, method, params }));
      });
    },
    once(method) {
      return new Promise((resolve) => {
        const list = events.get(method) || [];
        list.push((params) => {
          events.set(method, (events.get(method) || []).filter((fn) => fn !== list[list.length - 1]));
          resolve(params);
        });
        events.set(method, list);
      });
    },
  };
}

const browser = new WebSocket(await browserSocket());
await new Promise((resolve) => browser.addEventListener("open", resolve));
const send = cdp(browser);
const { targetId } = await send.call("Target.createTarget", { url: "about:blank" });
const { webSocketDebuggerUrl } = (await (await fetch("http://127.0.0.1:9222/json/list")).json())
  .find((target) => target.id === targetId);
const page = new WebSocket(webSocketDebuggerUrl);
await new Promise((resolve) => page.addEventListener("open", resolve));
const call = cdp(page);
await call.call("Page.enable");
await call.call("Runtime.enable");

async function shot(name, width, height, fan) {
  await call.call("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width < 500,
  });
  const loaded = call.once("Page.loadEventFired");
  const url = fan ? `${base}?spread=1` : base;
  await call.call("Page.navigate", { url });
  await loaded;
  await call.call("Runtime.evaluate", {
    expression: `document.fonts.ready.then(() => new Promise((resolve) => {
      const started = performance.now();
      const tick = () => {
        const live = document.querySelector(".stage")?.classList.contains("is-live");
        if (live || performance.now() - started > 2500) resolve(live ? "live" : "poster");
        else requestAnimationFrame(tick);
      };
      tick();
    }))`,
    awaitPromise: true,
  });
  await sleep(fan ? 700 : 1200);
  const shot = await call.call("Page.captureScreenshot", { format: "png" });
  const file = `${outDir}/${name}.png`;
  writeFileSync(file, Buffer.from(shot.data, "base64"));
  console.log(file);
}

try {
  await shot("desktop-hero", 1440, 900, false);
  await shot("desktop-fan", 1440, 900, true);
  await shot("mobile-hero", 390, 844, false);
  await shot("mobile-fan", 390, 844, true);
} finally {
  browser.close();
  page.close();
  chrome.kill();
}
