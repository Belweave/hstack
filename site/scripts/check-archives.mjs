import { buildReleaseArchive, CURRENT, PINS, sha256, vendorArchive } from "./archive.mjs";
import { readFileSync } from "node:fs";
import path from "node:path";

const site = path.resolve(import.meta.dirname, "..");
const root = path.resolve(site, "..");

function fail(message) {
  console.error(`check-archives: ${message}`);
  process.exit(1);
}

for (const [version, pin] of Object.entries(PINS)) {
  const file = vendorArchive(site, version);
  const digest = sha256(readFileSync(file));
  if (digest !== pin) fail(`vendored hstack-v${version}.tar.gz is ${digest}, pin is ${pin}`);
  console.log(`vendored ${version} ${digest}`);
}

const first = buildReleaseArchive(root, CURRENT);
const second = buildReleaseArchive(root, CURRENT);
const firstHash = sha256(first);
const secondHash = sha256(second);
console.log(`determinism: first  ${firstHash}`);
console.log(`determinism: second ${secondHash}`);
if (firstHash !== secondHash) fail("two archive builds differ");
if (!PINS[CURRENT]) fail(`missing pin for ${CURRENT}`);
if (firstHash !== PINS[CURRENT]) fail(`build ${firstHash} does not match vendored ${CURRENT} pin ${PINS[CURRENT]}`);
console.log(`determinism: match ${firstHash}`);
