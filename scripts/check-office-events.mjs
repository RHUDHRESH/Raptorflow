import { readFile } from "node:fs/promises";
import { join } from "node:path";

const schema = await readFile(join(process.cwd(), "schemas", "ws", "office-event.json"), "utf8");
const officeCrate = await readFile(join(process.cwd(), "crates", "office", "src", "lib.rs"), "utf8");

for (const eventType of [
  "file_delivery_start",
  "file_delivery_complete",
  "council_pager",
  "council_walk",
  "council_debate",
  "council_synthesis",
  "snark_refresh",
  "campaign_task_ready"
]) {
  if (!schema.includes(eventType) || !officeCrate.includes(eventType)) {
    console.error(`Missing office event type in schema or crate: ${eventType}`);
    process.exit(1);
  }
}

console.log("office event scaffold check passed");
