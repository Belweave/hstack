import { mountGlass } from "./glass.js";

const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const stage = document.querySelector(".stage");
const pin = document.querySelector(".pin");
const stack = document.querySelector(".stack");
const plates = [...document.querySelectorAll(".plate")];
const live = document.querySelector("#plate-live");
const glass = mountGlass(stage);

let pointerX = 0;
let pointerY = 0;
let hover = -1;
let spread = 0;
let running = false;

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function format(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

function applySpread(value) {
  spread = value;
  stack.style.setProperty("--spread", value.toFixed(4));
}

const forcedSpread = new URLSearchParams(window.location.search).get("spread");

function readSpread() {
  if (forcedSpread != null && forcedSpread !== "") {
    const value = Number(forcedSpread);
    if (Number.isFinite(value)) return clamp(value, 0, 1);
  }
  if (!pin) return 0;
  const rect = pin.getBoundingClientRect();
  const distance = pin.offsetHeight - window.innerHeight;
  if (distance <= 0) return 0;
  return clamp(-rect.top / distance, 0, 1);
}

function draw(now) {
  if (!glass) return;
  const t = reduced ? 0 : now / 1000;
  const driftX = reduced ? pointerX : pointerX + Math.sin(t * 0.35) * 0.12;
  const driftY = reduced ? pointerY : pointerY + Math.cos(t * 0.28) * 0.08;
  stack.style.setProperty("--px", driftX.toFixed(4));
  stack.style.setProperty("--py", driftY.toFixed(4));
  glass.draw(t, hover);
}

function frame(now) {
  applySpread(readSpread());
  draw(now);
  if (running) requestAnimationFrame(frame);
}

function start() {
  if (glass) stage.classList.add("is-live");
  if (reduced) {
    applySpread(readSpread());
    draw(0);
    return;
  }
  running = true;
  requestAnimationFrame(frame);
}

stage.addEventListener("pointermove", (event) => {
  if (reduced) return;
  const rect = stage.getBoundingClientRect();
  pointerX = clamp((event.clientX - rect.left) / rect.width - 0.5, -0.5, 0.5);
  pointerY = clamp((event.clientY - rect.top) / rect.height - 0.5, -0.5, 0.5);
});

stage.addEventListener("pointerleave", () => {
  pointerX = 0;
  pointerY = 0;
  hover = -1;
  if (reduced) draw(0);
});

plates.forEach((plate, index) => {
  plate.addEventListener("pointerenter", () => {
    hover = index;
    if (reduced) draw(0);
  });
  plate.addEventListener("focus", () => {
    hover = index;
    if (live) live.textContent = plate.getAttribute("aria-label") || "";
    if (reduced) draw(0);
  });
  plate.addEventListener("click", () => {
    const open = plate.classList.toggle("is-open");
    plate.setAttribute("aria-expanded", open ? "true" : "false");
    plates.forEach((other) => {
      if (other !== plate) {
        other.classList.remove("is-open");
        other.setAttribute("aria-expanded", "false");
      }
    });
    if (live) live.textContent = open ? plate.getAttribute("aria-label") || "" : "";
    hover = index;
    if (reduced) draw(0);
  });
});

document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const text = button.getAttribute("data-copy") || "";
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      return;
    }
    const previous = button.getAttribute("aria-label");
    button.classList.add("is-copied");
    button.setAttribute("aria-label", "Copied");
    window.setTimeout(() => {
      button.classList.remove("is-copied");
      if (previous) button.setAttribute("aria-label", previous);
    }, 1400);
  });
});

function countUp(el) {
  const target = Number(el.getAttribute("data-count"));
  if (!Number.isFinite(target)) return;
  if (reduced) {
    el.textContent = format(target);
    return;
  }
  const started = performance.now();
  const duration = 900;
  function tick(now) {
    const t = clamp((now - started) / duration, 0, 1);
    const eased = 1 - (1 - t) ** 3;
    el.textContent = format(Math.round(target * eased));
    if (t < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

const counts = [...document.querySelectorAll("[data-count]")];
if ("IntersectionObserver" in window) {
  const seen = new WeakSet();
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting || seen.has(entry.target)) return;
      seen.add(entry.target);
      countUp(entry.target);
    });
  }, { threshold: 0.6 });
  counts.forEach((el) => observer.observe(el));
} else {
  counts.forEach(countUp);
}

window.addEventListener("scroll", () => {
  if (!reduced) return;
  applySpread(readSpread());
  draw(0);
}, { passive: true });

window.addEventListener("resize", () => {
  if (reduced) {
    applySpread(readSpread());
    draw(0);
  }
});

if (document.fonts && document.fonts.ready) {
  document.fonts.ready.then(start);
} else {
  start();
}
