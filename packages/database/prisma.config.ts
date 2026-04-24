import dotenv from "dotenv";
import path from "node:path";
import { defineConfig } from "prisma/config";

dotenv.config({
  path: path.resolve(process.cwd(), "..", "..", ".env"),
});

const datasourceUrl =
  process.env.DATABASE_URL ??
  process.env.RAPTORFLOW_DATABASE_URL ??
  process.env.DIRECT_DATABASE_URL ??
  process.env.RAPTORFLOW_DIRECT_DATABASE_URL;

if (!datasourceUrl) {
  throw new Error("DATABASE_URL is required for Prisma");
}

export default defineConfig({
  schema: "prisma/schema.prisma",
  migrations: {
    path: "prisma/migrations",
  },
  datasource: {
    url: datasourceUrl,
  },
});
