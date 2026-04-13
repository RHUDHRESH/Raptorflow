import { createHash } from "node:crypto";
import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";

const root = process.cwd();
const uploadsDir = join(root, "Uploads");
const digestDir = join(root, "docs", "source-digests");
const promptContractsDir = join(root, "docs", "prompt-contracts");
const manifestPath = join(root, "docs", "canonical", "source-manifest.json");
const decisionRegisterPath = join(root, "docs", "canonical", "decision-register.json");
const checklistPath = join(digestDir, "00-checklist.md");
const requiredManifestCheck = "scripts/check-docs.mjs";
const expectedDuplicateGroup = "vol3-office";
const expectedDuplicateCanonical = "Vol3_TheOffice_FULL.docx";
const expectedDuplicateCopy = "Vol3_TheOffice_FULL (1).docx";
const expectedPromptContracts = [
  "brief-evaluation.md",
  "content-generation.md",
  "council-position.md",
  "daily-wins.md",
  "eel-reflection.md",
  "event-harvester.md",
  "intern-dispatch.md",
  "intern-research.md",
  "muse-routing.md",
  "nudge.md",
  "private-reflection.md",
  "research-request.md",
  "replanning.md",
  "strategist-synthesis.md",
  "stream-coordinator.md",
  "tool-gateway.md",
  "voice-compliance.md"
];

function fail(message) {
  console.error(`docs check failed: ${message}`);
  process.exit(1);
}

function assert(condition, message) {
  if (!condition) {
    fail(message);
  }
}

function sha256(buffer) {
  return createHash("sha256").update(buffer).digest("hex");
}

const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
const decisionRegister = JSON.parse(await readFile(decisionRegisterPath, "utf8"));
const checklist = await readFile(checklistPath, "utf8");
const uploadEntries = await readdir(uploadsDir, { withFileTypes: true });
const actualUploads = uploadEntries.filter((entry) => entry.isFile()).map((entry) => entry.name).sort();
const manifestUploads = [...manifest.sources].map((source) => source.upload_name).sort();
const promptContractEntries = await readdir(promptContractsDir, { withFileTypes: true });
const actualPromptContracts = promptContractEntries
  .filter((entry) => entry.isFile() && entry.name !== "README.md")
  .map((entry) => entry.name);
const actualPromptContractSet = new Set(actualPromptContracts);
const missingPromptContracts = expectedPromptContracts.filter((name) => !actualPromptContractSet.has(name));
const extraPromptContracts = actualPromptContracts.filter((name) => !expectedPromptContracts.includes(name));

assert(decisionRegister.source_traceability?.manifest === "docs/canonical/source-manifest.json", "decision register must reference docs/canonical/source-manifest.json");
assert(decisionRegister.source_traceability?.source_count === 18, "decision register must record the 18-source corpus");
assert(manifest.version === "1.0.0", "source manifest version must be 1.0.0");
assert(manifest.source_count === 18, "source manifest must track 18 uploads");
assert(Array.isArray(manifest.sources), "source manifest sources must be an array");
assert(manifest.sources.length === manifest.source_count, "source_count must equal the number of manifest sources");
assert(manifest.checks?.includes(requiredManifestCheck), "source manifest must include scripts/check-docs.mjs as a root check");
assert(JSON.stringify(actualUploads) === JSON.stringify(manifestUploads), "Uploads directory must match the manifest exactly");

for (const source of manifest.sources) {
  assert(typeof source.upload_name === "string" && source.upload_name.length > 0, "each source needs an upload_name");
  assert(typeof source.upload_path === "string" && source.upload_path.startsWith("Uploads/"), `upload_path must live under Uploads/: ${source.upload_name}`);
  assert(typeof source.digest_file === "string" && source.digest_file.startsWith("docs/source-digests/"), `digest_file must live under docs/source-digests/: ${source.upload_name}`);
  assert(typeof source.checksum_sha256 === "string" && source.checksum_sha256.length === 64, `checksum_sha256 must be a sha256 hex digest for ${source.upload_name}`);
  assert(Array.isArray(source.checks) && source.checks.includes(requiredManifestCheck), `each source must be covered by ${requiredManifestCheck}: ${source.upload_name}`);

  const uploadPath = join(root, source.upload_path);
  const digestPath = join(root, source.digest_file);
  const uploadBytes = await readFile(uploadPath);
  const digestText = await readFile(digestPath, "utf8");

  assert(sha256(uploadBytes) === source.checksum_sha256, `sha256 mismatch for ${source.upload_name}`);
  assert(digestText.trim().length > 0, `digest file must not be empty: ${source.digest_file}`);
}

const vol3Sources = manifest.sources.filter((source) => source.duplicate_group === expectedDuplicateGroup);
assert(vol3Sources.length === 2, "vol3-office duplicate group must contain exactly two entries");

const canonicalVol3 = vol3Sources.find((source) => source.canonical === true);
const duplicateVol3 = vol3Sources.find((source) => source.duplicate_of === expectedDuplicateCanonical);

assert(canonicalVol3?.upload_name === expectedDuplicateCanonical, "vol3 canonical source must be Vol3_TheOffice_FULL.docx");
assert(duplicateVol3?.upload_name === expectedDuplicateCopy, "vol3 duplicate source must be Vol3_TheOffice_FULL (1).docx");
assert(canonicalVol3.checksum_sha256 === duplicateVol3.checksum_sha256, "vol3 duplicate uploads must have identical checksums");
assert(canonicalVol3.checks.includes(requiredManifestCheck) && duplicateVol3.checks.includes(requiredManifestCheck), "vol3 entries must be covered by the docs check");

for (const uploadName of manifestUploads) {
  assert(checklist.includes(uploadName), `checklist must include ${uploadName}`);
}

assert(checklist.includes("Traceability manifest"), "checklist must link to the source manifest");
assert(checklist.includes("Duplicate handling"), "checklist must document the duplicate Vol. 3 handling");
assert(missingPromptContracts.length === 0, `missing prompt-contract files: ${missingPromptContracts.join(", ")}`);
assert(extraPromptContracts.length === 0, `unexpected prompt-contract files: ${extraPromptContracts.join(", ")}`);

for (const fileName of expectedPromptContracts) {
  const contractPath = join(promptContractsDir, fileName);
  const contractText = await readFile(contractPath, "utf8");
  assert(contractText.trim().length > 0, `prompt-contract file must not be empty: ${fileName}`);
}

console.log(`docs check passed: ${manifest.sources.length} sources, checksum validation enabled, duplicate group ${expectedDuplicateGroup} verified`);
