import { execSync } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function resolveDatabaseUrl() {
  const dbUrl = process.env.SUPABASE_DB_URL || process.env.DATABASE_URL;
  if (!dbUrl) {
    throw new Error("Set SUPABASE_DB_URL or DATABASE_URL before running this script.");
  }
  return dbUrl;
}

async function usePsqlDirect() {
  console.log("Trying direct psql approach...\n");

  try {
    const sqlPath = path.join(__dirname, "../missing_tables.sql");
    const sqlContent = fs.readFileSync(sqlPath, "utf8");
    const connStr = resolveDatabaseUrl();

    console.log("SQL file loaded");
    console.log("Running psql with configured DATABASE_URL...");

    const result = execSync(`psql "${connStr}" -c "${sqlContent}"`, {
      encoding: "utf8",
      stdio: ["pipe", "pipe", "pipe"],
      timeout: 30000,
    });

    console.log("psql execution successful");
    console.log("Output:", result);

    await verifyTables();
  } catch (error) {
    console.error("Direct psql approach failed:", error.message || error);
    process.exitCode = 1;
  }
}

async function verifyTables() {
  console.log("\nVerifying tables after psql execution...");

  try {
    const result = execSync("node scripts/quick_check.js", {
      encoding: "utf8",
      cwd: path.join(__dirname, ".."),
    });
    console.log(result);
  } catch (err) {
    console.log("Verification failed:", err.message);
  }
}

usePsqlDirect().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
