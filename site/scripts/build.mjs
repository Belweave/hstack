import { copyFileSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import crypto from "node:crypto";
import { emitSite } from "./render.mjs";
import { assertVendoredPins, CURRENT, PINS, vendorArchive } from "./archive.mjs";

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
if (version !== CURRENT) {
  throw new Error(`version is ${version}; dist publishes hstack-v${CURRENT}.tar.gz`);
}

const idle = tokens("  hstack:", "category") + skills.reduce((sum, skill) => sum + skill.idle, 0);
const planning = ["hstack", "reframe", "shape"].reduce((sum, name) => {
  return sum + skills.find((skill) => skill.name === name).body;
}, 0);
const bodies = skills.reduce((sum, skill) => sum + skill.body, 0);

if (idle !== 204 || planning !== 1052 || bodies !== 3907) {
  throw new Error(`measured idle ${idle}, planning ${planning}, bodies ${bodies}`);
}

rmSync(dist, { recursive: true, force: true });
const jsGzip = await emitSite({
  site,
  root,
  dist,
  skills,
  idle,
  planning,
  bodies,
  gstack: GSTACK,
});

const helpers = [
  "hstack-bench",
  "hstack-decisions",
  "hstack-pr",
  "hstack-scan",
  "hstack-test",
  "hstack-visdiff",
];
assertVendoredPins(site);
{
  for (const [frozenVersion, pin] of Object.entries(PINS)) {
    const bytes = readFileSync(vendorArchive(site, frozenVersion));
    const digest = crypto.createHash("sha256").update(bytes).digest("hex");
    if (digest !== pin) {
      throw new Error(`vendored hstack-v${frozenVersion}.tar.gz is ${digest}`);
    }
    const target = path.join(dist, "dl", `hstack-v${frozenVersion}.tar.gz`);
    writeFileSync(target, bytes);
    writeFileSync(`${target}.sha256`, `${digest}  hstack-v${frozenVersion}.tar.gz\n`);
  }
  const versioned = path.join(dist, "dl", `hstack-v${CURRENT}.tar.gz`);
  if (!PINS[CURRENT]) {
    throw new Error(`missing pin for hstack-v${CURRENT}.tar.gz`);
  }
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
    "hstack/skills/hstack/hstack/references/stacks.md",
    "hstack/skills/hstack/hstack/scripts/hstack_stack.py",
    "hstack/scripts/apply_addons.py",
    "hstack/scripts/apply_hooks.py",
    "hstack/hooks/guard.py",
    "hstack/hooks/save.py",
    "hstack/hooks/suggest.py",
    "hstack/hooks/hstack_hook.py",
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
  if (hash !== PINS[CURRENT]) {
    throw new Error(`latest alias is ${hash}, vendored ${CURRENT} pin is ${PINS[CURRENT]}`);
  }
  if (hash === PINS["0.1.0"] || hash === PINS["0.2.0"]) {
    throw new Error("latest alias still matches an older frozen archive");
  }
  writeFileSync(`${latest}.sha256`, `${hash}  hstack.tar.gz\n`);
  for (const published of ["install.sh", "install.ps1"]) {
    if (readFileSync(path.join(dist, published), "utf8").includes("github.com")) {
      throw new Error(`published ${published} still points at GitHub`);
    }
  }
  console.log(`idle ${idle}  planning ${planning}  bodies ${bodies}  js ${jsGzip} gzip  ${hash.slice(0, 12)}`);
}
