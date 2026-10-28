import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { chmodSync, cpSync, lstatSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

// Commit time of 13678a1, the 0.2.0 release. SOURCE_DATE_EPOCH overrides it.
export const ARCHIVE_MTIME = process.env.SOURCE_DATE_EPOCH || "1793189427";

export const PINS = {
  "0.1.0": "0c8009ee04fb31126b76e4202c91eee14e8d5be7d1cd42ac0cee551012eeda6e",
  "0.2.0": "c16dfee4cd2841939a97a5cebf816c3fc3e8d71e28f2f1874639ea539ea20810",
  "0.2.1": "61108ad0d5f54ffa2f42ce91ee50758fc459eca7520ba6a1956353678c3c7816",
};

export const CURRENT = "0.2.1";

const HELPERS = [
  "hstack-bench",
  "hstack-decisions",
  "hstack-pr",
  "hstack-scan",
  "hstack-test",
  "hstack-visdiff",
];

export function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

export function vendorArchive(site, version) {
  return path.join(site, "vendor", "dl", `hstack-v${version}.tar.gz`);
}

function skipCache(src) {
  return !src.split(path.sep).includes("__pycache__");
}

function normalizeTree(top) {
  const stack = [top];
  while (stack.length) {
    const dir = stack.pop();
    chmodSync(dir, 0o755);
    for (const name of readdirSync(dir)) {
      const file = path.join(dir, name);
      const info = lstatSync(file);
      if (info.isSymbolicLink()) {
        throw new Error(`refusing symlink in archive tree: ${file}`);
      }
      if (info.isDirectory()) {
        stack.push(file);
        continue;
      }
      const rel = path.relative(top, file).split(path.sep).join("/");
      chmodSync(file, rel.startsWith("bin/") ? 0o755 : 0o644);
    }
  }
}

export function buildReleaseArchive(root, version) {
  const skillsRoot = path.join(root, "skills", "hstack");
  const stage = mkdtempSync(path.join(tmpdir(), "hstack-archive-"));
  try {
    const top = path.join(stage, "hstack");
    mkdirSync(path.join(top, "scripts"), { recursive: true });
    mkdirSync(path.join(top, "bin"), { recursive: true });
    cpSync(skillsRoot, path.join(top, "skills", "hstack"), { recursive: true, filter: skipCache });
    cpSync(path.join(root, "hooks"), path.join(top, "hooks"), { recursive: true, filter: skipCache });
    cpSync(path.join(root, "scripts", "apply_addons.py"), path.join(top, "scripts", "apply_addons.py"));
    cpSync(path.join(root, "scripts", "apply_hooks.py"), path.join(top, "scripts", "apply_hooks.py"));
    for (const helper of HELPERS) {
      cpSync(path.join(root, "bin", helper), path.join(top, "bin", helper));
    }
    writeFileSync(path.join(top, "VERSION"), `${version}\n`);
    normalizeTree(top);
    const tar = spawnSync("tar", [
      "--format=ustar",
      "--owner=0",
      "--group=0",
      "--numeric-owner",
      `--mtime=@${ARCHIVE_MTIME}`,
      "--sort=name",
      "-cf",
      "-",
      "-C",
      stage,
      "hstack",
    ], { maxBuffer: 20 * 1024 * 1024 });
    if (tar.status !== 0) {
      throw new Error(`tar failed: ${tar.stderr.toString()}`);
    }
    const gzip = spawnSync("gzip", ["-n", "-c"], { input: tar.stdout, maxBuffer: 20 * 1024 * 1024 });
    if (gzip.status !== 0) {
      throw new Error(`gzip failed: ${gzip.stderr.toString()}`);
    }
    return gzip.stdout;
  } finally {
    rmSync(stage, { recursive: true, force: true });
  }
}

export function assertVendoredPins(site) {
  for (const [version, pin] of Object.entries(PINS)) {
    const file = vendorArchive(site, version);
    const digest = sha256(readFileSync(file));
    if (digest !== pin) {
      throw new Error(`vendored hstack-v${version}.tar.gz is ${digest}, pin is ${pin}`);
    }
  }
}
