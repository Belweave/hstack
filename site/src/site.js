const menu = document.querySelector(".menu");
const top = document.querySelector(".top");

function setMenu(open) {
  if (!menu || !top) return;
  menu.setAttribute("aria-expanded", String(open));
  menu.textContent = open ? "Close" : "Menu";
  top.classList.toggle("is-open", open);
}

menu?.addEventListener("click", () => {
  setMenu(menu.getAttribute("aria-expanded") !== "true");
});

document.querySelector(".top nav")?.addEventListener("click", (event) => {
  if (event.target.closest("a")) setMenu(false);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && menu?.getAttribute("aria-expanded") === "true") {
    setMenu(false);
    menu.focus();
  }
  const tab = event.target.closest?.("[role=tab]");
  if (!tab) return;
  const tabs = [...tab.closest("[role=tablist]").querySelectorAll("[role=tab]")];
  const index = tabs.indexOf(tab);
  let next = null;
  if (event.key === "ArrowRight") next = tabs[(index + 1) % tabs.length];
  if (event.key === "ArrowLeft") next = tabs[(index - 1 + tabs.length) % tabs.length];
  if (event.key === "Home") next = tabs[0];
  if (event.key === "End") next = tabs[tabs.length - 1];
  if (!next) return;
  event.preventDefault();
  selectTab(next);
  next.focus();
});

function selectTab(tab) {
  const tabs = [...tab.closest("[role=tablist]").querySelectorAll("[role=tab]")];
  for (const item of tabs) {
    const on = item === tab;
    item.setAttribute("aria-selected", String(on));
    item.tabIndex = on ? 0 : -1;
    const panel = document.getElementById(item.getAttribute("aria-controls"));
    if (panel) panel.hidden = !on;
  }
}

document.addEventListener("click", (event) => {
  const tab = event.target.closest?.("[role=tab]");
  if (tab) selectTab(tab);
  const copy = event.target.closest?.("[data-copy]");
  if (copy) copyCode(copy);
  const filter = event.target.closest?.("[data-filter]");
  if (filter) applyFilter(filter);
});

async function copyCode(button) {
  const code = button.closest("figure")?.querySelector("code");
  if (!code || !navigator.clipboard) return;
  try {
    await navigator.clipboard.writeText(code.textContent);
  } catch {
    return;
  }
  const previous = button.textContent;
  button.textContent = "Copied";
  window.setTimeout(() => {
    button.textContent = previous;
  }, 1200);
}

const rows = [...document.querySelectorAll("[data-parity-row]")];
const query = document.querySelector("#parity-q");
const count = document.querySelector("#parity-count");
const parity = { source: "", disposition: "", text: "" };

function applyFilter(button) {
  const group = button.parentElement;
  for (const item of group.querySelectorAll("[data-filter]")) {
    item.setAttribute("aria-pressed", String(item === button));
  }
  parity[button.dataset.filter] = button.dataset.value;
  renderParity();
}

function renderParity() {
  if (!rows.length || !count) return;
  const needle = parity.text.trim().toLowerCase();
  let shown = 0;
  for (const row of rows) {
    const ok = (!parity.source || row.dataset.source === parity.source)
      && (!parity.disposition || row.dataset.disposition === parity.disposition)
      && (!needle || row.dataset.text.includes(needle));
    row.hidden = !ok;
    if (ok) shown += 1;
  }
  count.textContent = shown === rows.length
    ? `${rows.length} rows`
    : `${shown} of ${rows.length} rows`;
}

query?.addEventListener("input", () => {
  parity.text = query.value;
  renderParity();
});
