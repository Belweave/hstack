import { cpSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import esbuild from "esbuild";
import { Marked } from "marked";

const NAV = [
  ["/", "Home"],
  ["/docs", "Docs"],
  ["/skills", "Skills"],
  ["/integrations", "Integrations"],
  ["/parity", "Parity"],
  ["/changelog", "Changelog"],
];

const DOCS = [
  ["/docs", "Getting started"],
  ["/docs/install", "Install"],
  ["/docs/addons", "Add-ons"],
];

const REF_ORDER = [
  "routes", "frame", "feature", "fix", "check", "land", "refactor", "design", "qa", "perf",
  "trace", "retro", "docs", "security", "explain", "memory", "author", "prose", "experiment",
  "parallel", "overnight", "pickup", "worktree", "spec", "eval", "deploy", "browse", "safety",
  "decisions", "triage", "types", "verify", "diagram",
];

const DISCLAIMER = "HStack is a community project made for the Hermes Agent community. It is not affiliated with, endorsed by, or an official product of Nous Research. Hermes Agent and the Nous Research logo belong to Nous Research and appear here only to show compatibility.";

const KEYWORDS = {
  sh: new Set(["if", "then", "else", "elif", "fi", "for", "while", "do", "done", "in", "case", "esac", "function", "return", "export", "set", "unset", "shift", "exit"]),
  powershell: new Set(["if", "else", "elseif", "foreach", "while", "function", "return", "param", "switch", "try", "catch", "finally", "throw"]),
  yaml: new Set(["true", "false", "null", "yes", "no"]),
};

function esc(value) {
  return String(value).replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}

function fmt(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

function rewriteHref(href) {
  if (href === "RESEARCH.md") return "https://github.com/Belweave/hstack/blob/main/RESEARCH.md";
  return href;
}

function highlight(code, lang) {
  const kind = lang === "bash" ? "sh" : lang === "ps1" ? "powershell" : lang;
  const keys = KEYWORDS[kind];
  let out = "";
  let i = 0;
  while (i < code.length) {
    const ch = code[i];
    if ((kind === "sh" || kind === "yaml" || kind === "powershell") && ch === "#" && (i === 0 || code[i - 1] === "\n" || /\s/.test(code[i - 1]))) {
      const end = code.indexOf("\n", i);
      const slice = end === -1 ? code.slice(i) : code.slice(i, end);
      out += `<span class="cm">${esc(slice)}</span>`;
      i += slice.length;
      continue;
    }
    if (ch === '"' || ch === "'") {
      const quote = ch;
      let j = i + 1;
      while (j < code.length && code[j] !== quote && code[j] !== "\n") {
        if (code[j] === "\\" && quote === '"') j += 2;
        else j += 1;
      }
      if (j < code.length && code[j] === quote) j += 1;
      out += `<span class="st">${esc(code.slice(i, j))}</span>`;
      i = j;
      continue;
    }
    if (ch === "-" && code[i + 1] === "-") {
      let j = i + 2;
      while (j < code.length && /[A-Za-z0-9_-]/.test(code[j])) j += 1;
      out += `<span class="fl">${esc(code.slice(i, j))}</span>`;
      i = j;
      continue;
    }
    if (/[0-9]/.test(ch) && (i === 0 || !/[A-Za-z0-9_]/.test(code[i - 1]))) {
      let j = i;
      while (j < code.length && /[0-9.]/.test(code[j])) j += 1;
      out += `<span class="nu">${esc(code.slice(i, j))}</span>`;
      i = j;
      continue;
    }
    if (/[A-Za-z_]/.test(ch)) {
      let j = i;
      while (j < code.length && /[A-Za-z0-9_-]/.test(code[j])) j += 1;
      const word = code.slice(i, j);
      if (keys?.has(word)) out += `<span class="kw">${esc(word)}</span>`;
      else out += esc(word);
      i = j;
      continue;
    }
    out += esc(ch);
    i += 1;
  }
  return out;
}

function createMarkdown() {
  let headingOffset = 0;
  let tabSeq = 0;
  const slots = [];
  const marked = new Marked({ gfm: true });
  marked.use({
    renderer: {
      code({ text, lang }) {
        const info = (lang || "").trim().split(/\s+/);
        const language = info[0] || "text";
        const filename = info.slice(1).join(" ") || language;
        return `<figure class="code"><figcaption><span>${esc(filename)}</span><button type="button" data-copy>Copy</button></figcaption><pre><code class="language-${esc(language)}">${highlight(text.replace(/\n$/, ""), language)}</code></pre></figure>\n`;
      },
      link(token) {
        const href = rewriteHref(token.href);
        const inner = this.parser.parseInline(token.tokens);
        const title = token.title ? ` title="${esc(token.title)}"` : "";
        return `<a href="${esc(href)}"${title}>${inner}</a>`;
      },
      heading(token) {
        const level = Math.min(6, token.depth + headingOffset);
        const inner = this.parser.parseInline(token.tokens);
        return `<h${level}>${inner}</h${level}>\n`;
      },
    },
  });

  function hold(html) {
    const token = `SLOT${slots.length}HOLD`;
    slots.push(html);
    return `\n\n<!--${token}-->\n\n`;
  }

  function parse(md, offset = 0) {
    headingOffset = offset;
    const prepared = md
      .replace(/^:::tabs\n([\s\S]*?)\n:::[ \t]*$/gm, (_, body) => hold(renderTabs(body)))
      .replace(/^:::note\n([\s\S]*?)\n:::[ \t]*$/gm, (_, body) => hold(`<aside class="note"><p class="kicker">Note</p>${parse(body.trim())}</aside>`));
    const html = marked.parse(prepared);
    return String(html).replace(/<!--SLOT(\d+)HOLD-->/g, (_, n) => slots[Number(n)]);
  }

  function renderTabs(body) {
    const parts = body.split(/^:::tab[ \t]+(.+)$/m).slice(1);
    const panels = [];
    for (let i = 0; i < parts.length; i += 2) {
      panels.push({ title: parts[i].trim(), md: (parts[i + 1] || "").trim() });
    }
    const uid = ++tabSeq;
    const tabs = panels.map((panel, index) => ({
      id: `tab-${uid}-${index}`,
      panel: `panel-${uid}-${index}`,
      title: panel.title,
      selected: index === 0,
      html: parse(panel.md),
    }));
    return `<div class="tabs"><div role="tablist" aria-label="Options">${tabs.map((tab) => `<button type="button" role="tab" id="${tab.id}" aria-controls="${tab.panel}" aria-selected="${tab.selected}" tabindex="${tab.selected ? "0" : "-1"}">${esc(tab.title)}</button>`).join("")}</div>${tabs.map((tab) => `<div role="tabpanel" id="${tab.panel}" aria-labelledby="${tab.id}"${tab.selected ? "" : " hidden"}>${tab.html}</div>`).join("")}</div>`;
  }

  return { parse };
}

function frontmatter(md) {
  if (!md.startsWith("---\n")) return { meta: {}, body: md };
  const end = md.indexOf("\n---\n", 4);
  if (end === -1) return { meta: {}, body: md };
  const meta = {};
  for (const line of md.slice(4, end).split("\n")) {
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (match) meta[match[1]] = match[2].trim();
  }
  return { meta, body: md.slice(end + 5) };
}

function current(href, pathname) {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

const MARK = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="16" height="16" aria-hidden="true"><rect width="32" height="32" fill="#7DDCB2"/><g fill="#0C100E"><rect x="7" y="8" width="18" height="3.2"/><rect x="7" y="14.4" width="13" height="3.2"/><rect x="7" y="20.8" width="18" height="3.2"/></g></svg>`;

function layout({ pathname, title, description, main, wide = false }) {
  const fullTitle = pathname === "/" ? "HStack" : `${title} · HStack`;
  const nav = NAV.map(([href, label]) => {
    const on = current(href, pathname);
    return `<a href="${href}"${on ? ' aria-current="page"' : ""}>${label}</a>`;
  }).join("");
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(fullTitle)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="https://hstack.sh${pathname === "/" ? "/" : pathname}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#0C100E">
<meta property="og:title" content="${esc(fullTitle)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:image" content="https://hstack.sh/social-preview.png">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/fonts/PaperMono%5Bwght%5D.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
<a class="brand" href="/">${MARK}HStack</a>
<button class="menu" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
<nav id="nav" aria-label="Primary">${nav}</nav>
</header>
<main id="main"${wide ? ' class="wide"' : ""}>
${main}
</main>
<footer class="site-foot">
<nav class="foot-links" aria-label="Footer">
<a href="https://github.com/Belweave/hstack">GitHub</a>
<a href="/license">MIT</a>
<a href="/notices">Third-party notices</a>
</nav>
<p class="disclaimer">${esc(DISCLAIMER)}</p>
<p class="colophon">Set in <a href="/fonts/LICENSE.txt">Paper Mono</a>, SIL Open Font License.</p>
</footer>
<script type="module" src="/assets/site.js"></script>
</body>
</html>
`;
}

function side(links, pathname, kicker) {
  const items = links.map(([href, label]) => {
    const on = pathname === href;
    return `<a href="${href}"${on ? ' aria-current="page"' : ""}>${esc(label)}</a>`;
  }).join("");
  return `<aside class="side"><p class="kicker">${esc(kicker)}</p>${items}</aside>`;
}

function sheet(aside, article, wide = false) {
  return `<div class="sheet">${aside}<article class="page${wide ? " wide" : ""}">${article}</article></div>`;
}

function cells(line) {
  return line.replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function inlineCell(text) {
  const parts = text.split("`");
  return parts.map((part, index) => (index % 2 ? `<code>${esc(part)}</code>` : esc(part))).join("");
}

function parityTable(markdown) {
  const start = markdown.indexOf("\n| id | source |");
  const table = markdown.slice(start).trim().split("\n").filter((line) => line.startsWith("|"));
  const rows = table.slice(2).map(cells);
  const body = rows.map((row) => {
    const [id, source, item, kind, disposition, target, onDemand, reason] = row;
    const text = row.join(" ").toLowerCase();
    const tds = [id, source, item, kind, disposition, target, onDemand, reason]
      .map((cell) => `<td>${inlineCell(cell || "")}</td>`).join("");
    return `<tr data-parity-row data-source="${esc(source)}" data-disposition="${esc(disposition)}" data-text="${esc(text)}">${tds}</tr>`;
  }).join("");
  const sources = ["", "gstack", "tstack", "pstack"];
  const dispositions = ["", "skill", "routed-reference", "plugin-or-tool", "helper-script", "skip"];
  const group = (name, label, values) => `<div class="group" role="group" aria-label="${label}">${values.map((value) => {
    const pressed = value === "";
    const text = value === "" ? "All" : value;
    return `<button type="button" data-filter="${name}" data-value="${esc(value)}" aria-pressed="${pressed}">${esc(text)}</button>`;
  }).join("")}</div>`;
  return `<div class="filters">
<label for="parity-q">Search features</label>
<input id="parity-q" type="search" autocomplete="off">
<div class="groups">
${group("source", "Source", sources)}
${group("disposition", "Disposition", dispositions)}
</div>
<p id="parity-count" aria-live="polite">${rows.length} rows</p>
</div>
<div class="table-wrap"><table class="parity"><caption>Filter the ${rows.length}-row inventory. Search matches every column.</caption><thead><tr>
<th scope="col">Id</th><th scope="col">Source</th><th scope="col">Item</th><th scope="col">Kind</th><th scope="col">Disposition</th><th scope="col">Target</th><th scope="col">On demand</th><th scope="col">Reason</th>
</tr></thead><tbody>${body}</tbody></table></div>`;
}

function home({ skills, idle, planning, bodies, gstack }) {
  const md = createMarkdown();
  const install = md.parse(`:::tabs
:::tab macOS / Linux
\`\`\`sh install.sh
curl -fsSL https://hstack.sh/install | sh
\`\`\`
:::tab Windows
\`\`\`powershell install.ps1
irm https://hstack.sh/install.ps1 -OutFile install.ps1
powershell -ExecutionPolicy Bypass -File .\\install.ps1
\`\`\`
:::`);
  const roster = skills.map((skill, index) => `<li><a href="/skills/${skill.name}"><span class="num">${String(index + 1).padStart(2, "0")}</span><span class="name">${esc(skill.name)}</span><span class="desc">${esc(skill.description)}</span><span class="tok">${fmt(skill.body)}</span></a></li>`).join("");
  const main = `<section class="band"><div class="idx">01</div><div class="band-body"><p class="kicker">Hermes Agent skills</p><h1>Everything Hermes needs.<br>Nothing it doesn't.</h1><p class="lede">Twelve skills. One router. A playbook loads only when the task needs it.</p></div></section>
<section class="band"><div class="idx">02</div><div class="band-body"><h2>Install</h2><p>Version ${esc(skills[0].version)}. The archive is checked with sha256 and extracted into <code>~/.hermes/skills/hstack/</code>. The installer does not clone the repository.</p>${install}<p><a href="/docs/install">Install, dry-run, and uninstall</a></p></div></section>
<section class="band"><div class="idx">03</div><div class="band-body"><h2>Context</h2><p>Counts use Hermes's estimator, <code>ceil(bytes / 4)</code>. The planning path is <code>hstack</code>, <code>reframe</code>, and <code>shape</code>: ${fmt(planning)} tokens, under 2% of GStack. The idle index is about six times smaller.</p>
<div class="table-wrap"><table><caption>Measured from this repository. GStack figures are the Hermes host.</caption><thead><tr><th scope="col">Measure</th><th scope="col">GStack on Hermes</th><th scope="col">HStack</th></tr></thead><tbody>
<tr><th scope="row">Idle index</th><td>${fmt(gstack.idle)}</td><td class="fig">${fmt(idle)}</td></tr>
<tr><th scope="row">Planning load</th><td>${fmt(gstack.planning)}</td><td class="fig">${fmt(planning)}</td></tr>
<tr><th scope="row">All SKILL.md bodies</th><td>${fmt(gstack.bodies)}</td><td class="fig">${fmt(bodies)}</td></tr>
</tbody></table></div>
<p class="muted">GStack's planning column is SKILL.md bytes. That host also carries a preamble of about 5,600 tokens.</p></div></section>
<section class="band"><div class="idx">04</div><div class="band-body"><h2>Skills</h2><ol class="roster">${roster}</ol></div></section>`;
  return layout({
    pathname: "/",
    title: "HStack",
    description: `Twelve Hermes Agent skills. Idle index ${idle} tokens. Planning path ${planning}. All skill bodies ${fmt(bodies)}.`,
    main,
  });
}

function readContent(file) {
  return frontmatter(readFileSync(file, "utf8"));
}

function references(skillsRoot) {
  const dir = path.join(skillsRoot, "hstack", "references");
  const names = readdirSync(dir).filter((name) => name.endsWith(".md")).map((name) => name.slice(0, -3));
  names.sort((a, b) => {
    const ai = REF_ORDER.indexOf(a);
    const bi = REF_ORDER.indexOf(b);
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi) || a.localeCompare(b);
  });
  return names.map((name) => ({ name, md: readFileSync(path.join(dir, `${name}.md`), "utf8") }));
}

function ogDocument({ idle, planning, bodies }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<title>HStack</title>
<link rel="stylesheet" href="/assets/site.css">
<style>
html, body { width: 1280px; height: 640px; overflow: hidden; }
.poster { box-sizing: border-box; width: 1280px; height: 640px; padding: 72px 80px; display: flex; flex-direction: column; justify-content: space-between; }
.poster h1 { font-size: 64px; max-width: none; }
.stats { display: grid; grid-template-columns: 1fr 1fr 1fr; border-top: 1px solid var(--line); }
.stats div { padding: 22px 28px 0 0; }
.stats div + div { padding-left: 28px; box-shadow: inset 1px 0 0 var(--line); }
.stats span { display: block; color: var(--muted); font-size: 13px; letter-spacing: 0.12em; text-transform: uppercase; }
.stats strong { display: block; margin-top: 8px; color: var(--accent); font-size: 52px; font-weight: 400; letter-spacing: -0.04em; }
</style>
</head>
<body>
<div class="poster">
<div>
<p class="kicker">HStack</p>
<h1>Everything Hermes needs.<br>Nothing it doesn't.</h1>
</div>
<div class="stats">
<div><span>Idle</span><strong>${fmt(idle)}</strong></div>
<div><span>Planning</span><strong>${fmt(planning)}</strong></div>
<div><span>Bodies</span><strong>${fmt(bodies)}</strong></div>
</div>
</div>
</body>
</html>
`;
}

export async function emitSite({ site, root, dist, skills, idle, planning, bodies, gstack }) {
  const skillsRoot = path.join(root, "skills", "hstack");
  const md = createMarkdown();
  mkdirSync(path.join(dist, "assets"), { recursive: true });
  mkdirSync(path.join(dist, "dl"), { recursive: true });
  mkdirSync(path.join(dist, "fonts"), { recursive: true });
  cpSync(path.join(site, "public"), dist, { recursive: true });
  cpSync(path.join(site, "fonts"), path.join(dist, "fonts"), { recursive: true });
  cpSync(path.join(root, ".github", "social-preview.png"), path.join(dist, "social-preview.png"));
  cpSync(path.join(root, "install.sh"), path.join(dist, "install.sh"));
  cpSync(path.join(root, "install.ps1"), path.join(dist, "install.ps1"));
  cpSync(path.join(site, "_headers"), path.join(dist, "_headers"));
  cpSync(path.join(site, "_redirects"), path.join(dist, "_redirects"));

  const css = await esbuild.transform(readFileSync(path.join(site, "src", "site.css"), "utf8"), {
    loader: "css",
    minify: true,
  });
  writeFileSync(path.join(dist, "assets", "site.css"), css.code);
  await esbuild.build({
    entryPoints: [path.join(site, "src", "site.js")],
    bundle: true,
    minify: true,
    format: "esm",
    target: "es2020",
    outfile: path.join(dist, "assets", "site.js"),
  });
  const jsGzip = zlib.gzipSync(readFileSync(path.join(dist, "assets", "site.js"))).length;
  if (jsGzip > 250 * 1024) throw new Error(`site.js is ${jsGzip} bytes gzipped`);

  function write(pathname, html) {
    const rel = pathname === "/" ? "index.html" : `${pathname.slice(1)}/index.html`;
    const file = path.join(dist, rel);
    mkdirSync(path.dirname(file), { recursive: true });
    writeFileSync(file, html);
  }

  write("/", home({ skills, idle, planning, bodies, gstack }));

  const contentDir = path.join(site, "content");
  const pages = [
    ["/docs", path.join(contentDir, "docs", "index.md"), "Docs"],
    ["/docs/install", path.join(contentDir, "docs", "install.md"), "Docs"],
    ["/docs/addons", path.join(contentDir, "docs", "addons.md"), "Docs"],
    ["/integrations", path.join(contentDir, "integrations.md"), null],
    ["/changelog", path.join(contentDir, "changelog.md"), null],
  ];
  for (const [pathname, file, section] of pages) {
    const { meta, body } = readContent(file);
    const article = `<p class="kicker">${esc(section || meta.title)}</p><h1>${esc(meta.title)}</h1><div class="prose">${md.parse(body)}</div>`;
    const main = section ? sheet(side(DOCS, pathname, "Docs"), article) : `<article class="page">${article}</article>`;
    write(pathname, layout({
      pathname,
      title: meta.title,
      description: meta.description,
      main,
    }));
  }

  const skillLinks = skills.map((skill) => [`/skills/${skill.name}`, skill.name]);
  const indexItems = skills.map((skill, index) => `<li><a href="/skills/${skill.name}"><span class="num">${String(index + 1).padStart(2, "0")}</span><span class="name">${esc(skill.name)}</span><span class="desc">${esc(skill.description)}</span><span class="tok">${fmt(skill.body)} body</span></a></li>`).join("");
  write("/skills", layout({
    pathname: "/skills",
    title: "Skills",
    description: "Twelve HStack skills. The router is hstack. The others are reframe, shape, prove, council, ship, takeover, modernize, blast, swarm, arena, and principles.",
    main: sheet(side(skillLinks, "/skills", "Skills"), `<p class="kicker">Skills</p><h1>Skills</h1><div class="prose"><p>Idle cost is the index row. Body tokens are the full <code>SKILL.md</code>, loaded only when that skill is opened.</p></div><ol class="roster">${indexItems}</ol>`),
  }));

  const plays = references(skillsRoot);
  for (const skill of skills) {
    const file = path.join(skillsRoot, skill.name, "SKILL.md");
    const raw = readFileSync(file, "utf8");
    const { body } = frontmatter(raw);
    const stripped = body.replace(/^\s*#\s+.+\n+/, "");
    let extra = "";
    if (skill.name === "hstack") {
      extra = plays.map((play) => `<section class="playbook" id="ref-${play.name}">${md.parse(play.md, 1)}</section>`).join("");
    }
    const pathname = `/skills/${skill.name}`;
    write(pathname, layout({
      pathname,
      title: skill.name,
      description: skill.description,
      main: sheet(side(skillLinks, pathname, "Skills"), `<p class="kicker">Skill</p><h1>${esc(skill.name)}</h1><p class="muted">${skill.idle} idle · ${fmt(skill.body)} body · v${esc(skill.version)}</p><div class="prose">${md.parse(stripped)}${extra}</div>`),
    }));
  }

  const parityMd = readFileSync(path.join(root, "PARITY.md"), "utf8");
  const splitAt = parityMd.indexOf("\n## Feature table");
  const narrative = parityMd.slice(0, splitAt).replace(/^#\s+.+\n+/, "");
  write("/parity", layout({
    pathname: "/parity",
    title: "Parity",
    description: "520-row inventory of GStack, TStack, and PStack features, and where each one went in HStack.",
    wide: true,
    main: `<article class="page wide"><p class="kicker">Inventory</p><h1>Parity</h1><div class="prose">${md.parse(narrative)}${parityTable(parityMd.slice(splitAt))}</div></article>`,
  }));

  function legal(pathname, title, description, file) {
    const text = readFileSync(path.join(root, file), "utf8");
    write(pathname, layout({
      pathname,
      title,
      description,
      main: `<article class="page"><p class="kicker">License</p><h1>${esc(title)}</h1><pre class="legal">${esc(text.trim())}</pre></article>`,
    }));
  }
  legal("/license", "MIT License", "MIT license for HStack. Copyright (c) 2026 Preetham Kyanam / belweave.", "LICENSE");
  legal("/notices", "Third-party notices", "MIT notices for GStack and TStack material adapted by HStack.", "THIRD_PARTY_NOTICES");

  const missing = layout({
    pathname: "/404",
    title: "Page not found",
    description: "That page is not on hstack.sh.",
    main: `<article class="page"><p class="kicker">404</p><h1>Page not found</h1><div class="prose"><p>That URL is not on this site.</p><p><a href="/">Home</a> · <a href="/docs">Docs</a></p></div></article>`,
  });
  writeFileSync(path.join(dist, "404.html"), missing);
  writeFileSync(path.join(dist, "og.html"), ogDocument({ idle, planning, bodies }));
  return jsGzip;
}
