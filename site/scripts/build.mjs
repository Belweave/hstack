import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync, copyFileSync } from "node:fs";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import crypto from "node:crypto";
import zlib from "node:zlib";
import esbuild from "esbuild";

const site = path.resolve(import.meta.dirname, "..");
const root = path.resolve(site, "..");
const dist = path.join(site, "dist");
const skillsRoot = path.join(root, "skills", "hstack");

const ORDER = [
  "hstack",
  "reframe",
  "shape",
  "prove",
  "council",
  "ship",
  "takeover",
  "modernize",
  "blast",
  "swarm",
  "arena",
  "principles",
];

const GSTACK = { idle: 1182, planning: 62514, bodies: 420401 };

function tokens(text, label) {
  const bytes = Buffer.byteLength(text, "utf8");
  if (bytes !== text.length) throw new Error(`${label} is not ASCII`);
  return Math.ceil(bytes / 4);
}

function field(md, key, file) {
  const match = md.match(new RegExp(`^${key}:\\s*(.*)$`, "m"));
  if (!match || !match[1].trim()) throw new Error(`${file} is missing ${key}`);
  return match[1].trim();
}

function fmt(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

function esc(value) {
  return value.replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}

const skills = ORDER.map((name) => {
  const file = path.join(skillsRoot, name, "SKILL.md");
  const md = readFileSync(file, "utf8");
  const description = field(md, "description", file);
  const version = field(md, "version", file);
  const row = `    - ${name}: ${description}`;
  return {
    name,
    description,
    version,
    idle: tokens(row, row),
    body: tokens(md, file),
  };
});

const version = skills[0].version;
if (!skills.every((skill) => skill.version === version)) {
  throw new Error("skill versions differ");
}
if (version !== "0.1.0") {
  throw new Error(`version is ${version}; dist publishes hstack-v0.1.0.tar.gz`);
}

const idle = tokens("  hstack:", "category") + skills.reduce((sum, skill) => sum + skill.idle, 0);
const planning = ["hstack", "reframe", "shape"].reduce((sum, name) => {
  return sum + skills.find((skill) => skill.name === name).body;
}, 0);
const bodies = skills.reduce((sum, skill) => sum + skill.body, 0);

if (idle !== 204 || planning !== 965 || bodies !== 3820) {
  throw new Error(`measured idle ${idle}, planning ${planning}, bodies ${bodies}`);
}

const stack = skills.map((skill) => {
  const label = `${skill.name}. ${skill.description} ${skill.idle} idle tokens, ${fmt(skill.body)} body tokens.`;
  return `<div class="row"><button class="plate" type="button" aria-expanded="false" aria-label="${esc(label)}"><span class="pname">${esc(skill.name)}</span><span class="pmeta">${skill.idle} idle · ${fmt(skill.body)} body</span></button><p class="pdesc">${esc(skill.description)}</p></div>`;
}).join("");

const grid = skills.map((skill) => {
  return `<article class="skill"><h3>${esc(skill.name)}</h3><p>${esc(skill.description)}</p><p class="tokens">${skill.idle} idle · ${fmt(skill.body)} body</p></article>`;
}).join("");

function meter(title, hstack, gstack) {
  const share = (hstack / gstack).toFixed(6);
  return `<article><h3>${title}</h3><div class="meter"><div><span>HStack</span><div class="track"><span style="--share:${share}"></span></div><span class="num" data-count="${hstack}">${fmt(hstack)}</span></div><div><span>GStack</span><div class="track ghost"><span style="--share:1"></span></div><span class="num" data-count="${gstack}">${fmt(gstack)}</span></div></div></article>`;
}

const compare = `<div class="compare">${meter("Idle, every turn", idle, GSTACK.idle)}${meter("Planning load", planning, GSTACK.planning)}${meter("All skill bodies", bodies, GSTACK.bodies)}</div>`;

const css = await esbuild.transform(readFileSync(path.join(site, "src", "styles.css"), "utf8"), {
  loader: "css",
  minify: true,
});

let html = readFileSync(path.join(site, "index.html"), "utf8");
html = html.replace("/*__CSS__*/", () => css.code);
html = html.replace("<!--__STACK__-->", () => stack);
html = html.replace("<!--__GRID__-->", () => grid);
html = html.replace("<!--__COMPARE__-->", () => compare);
if (html.includes("__")) throw new Error("unreplaced template marker");

rmSync(dist, { recursive: true, force: true });
mkdirSync(path.join(dist, "assets"), { recursive: true });
mkdirSync(path.join(dist, "dl"), { recursive: true });
mkdirSync(path.join(dist, "fonts"), { recursive: true });
writeFileSync(path.join(dist, "index.html"), html);
cpSync(path.join(site, "public"), dist, { recursive: true });
cpSync(path.join(site, "fonts"), path.join(dist, "fonts"), { recursive: true });
copyFileSync(path.join(root, ".github", "social-preview.png"), path.join(dist, "social-preview.png"));
copyFileSync(path.join(root, "install.sh"), path.join(dist, "install.sh"));
copyFileSync(path.join(root, "install.ps1"), path.join(dist, "install.ps1"));
copyFileSync(path.join(site, "_headers"), path.join(dist, "_headers"));
copyFileSync(path.join(site, "_redirects"), path.join(dist, "_redirects"));

await esbuild.build({
  entryPoints: [path.join(site, "src", "main.js")],
  bundle: true,
  minify: true,
  format: "esm",
  target: "es2020",
  outfile: path.join(dist, "assets", "app.js"),
});

const jsGzip = zlib.gzipSync(readFileSync(path.join(dist, "assets", "app.js"))).length;
if (jsGzip > 250 * 1024) throw new Error(`app.js is ${jsGzip} bytes gzipped`);

const helpers = [
  "hstack-bench",
  "hstack-decisions",
  "hstack-pr",
  "hstack-scan",
  "hstack-test",
  "hstack-visdiff",
];
const stage = mkdtempSync(path.join(tmpdir(), "hstack-skills-"));
try {
  const top = path.join(stage, "hstack");
  mkdirSync(path.join(top, "skills"), { recursive: true });
  mkdirSync(path.join(top, "scripts"), { recursive: true });
  mkdirSync(path.join(top, "bin"), { recursive: true });
  cpSync(skillsRoot, path.join(top, "skills", "hstack"), { recursive: true });
  cpSync(path.join(root, "scripts", "apply_addons.py"), path.join(top, "scripts", "apply_addons.py"));
  for (const helper of helpers) {
    cpSync(path.join(root, "bin", helper), path.join(top, "bin", helper));
  }
  writeFileSync(path.join(top, "VERSION"), `${version}\n`);
  const versioned = path.join(dist, "dl", `hstack-v${version}.tar.gz`);
  execFileSync("tar", [
    "--format=ustar",
    "--owner=0",
    "--group=0",
    "--numeric-owner",
    "-czf",
    versioned,
    "-C",
    stage,
    "hstack",
  ], { stdio: "inherit" });
  const members = execFileSync("tar", ["-tzf", versioned], { encoding: "utf8" }).trim().split("\n");
  const tops = new Set(members.map((member) => member.replace(/^\.\//, "").split("/")[0]).filter(Boolean));
  if (tops.size !== 1 || !tops.has("hstack")) {
    throw new Error(`archive must have one top-level directory, saw ${[...tops].join(",")}`);
  }
  for (const member of members) {
    const norm = member.replace(/^\.\//, "");
    if (!norm || norm.startsWith("/") || norm.split("/").includes("..")) {
      throw new Error(`unsafe archive member ${member}`);
    }
  }
  const required = [
    "hstack/VERSION",
    "hstack/skills/hstack/hstack/SKILL.md",
    "hstack/scripts/apply_addons.py",
    ...helpers.map((helper) => `hstack/bin/${helper}`),
  ];
  for (const name of required) {
    if (!members.some((member) => member.replace(/^\.\//, "") === name)) {
      throw new Error(`archive is missing ${name}`);
    }
  }
  const listing = execFileSync("tar", ["-tvzf", versioned], { encoding: "utf8" });
  for (const line of listing.split("\n")) {
    if (line.startsWith("l") || line.startsWith("h")) {
      throw new Error(`archive contains a link: ${line}`);
    }
  }
  for (const helper of helpers) {
    const line = listing.split("\n").find((entry) => entry.endsWith(`hstack/bin/${helper}`));
    if (!line || !/^.r.x/.test(line)) {
      throw new Error(`archive helper is not executable: ${helper}`);
    }
  }
  const latest = path.join(dist, "dl", "hstack.tar.gz");
  copyFileSync(versioned, latest);
  const hash = crypto.createHash("sha256").update(readFileSync(versioned)).digest("hex");
  writeFileSync(`${versioned}.sha256`, `${hash}  hstack-v${version}.tar.gz\n`);
  writeFileSync(`${latest}.sha256`, `${hash}  hstack.tar.gz\n`);
  for (const published of ["install.sh", "install.ps1"]) {
    if (readFileSync(path.join(dist, published), "utf8").includes("github.com")) {
      throw new Error(`published ${published} still points at GitHub`);
    }
  }
  console.log(`idle ${idle}  planning ${planning}  bodies ${bodies}  js ${jsGzip} gzip  ${hash.slice(0, 12)}`);
} finally {
  rmSync(stage, { recursive: true, force: true });
}
