import { PrismaPg } from "@prisma/adapter-pg";
import { Pool } from "pg";
import { PrismaClient } from "./generated/prisma/client.js";

const globalForPrisma = globalThis;

const connectionString = process.env.DATABASE_URL ?? process.env.DIRECT_DATABASE_URL;

if (!connectionString) {
  throw new Error("DATABASE_URL is required for @raptorflow/database");
}

const adapter = new PrismaPg(new Pool({ connectionString }));

export const prisma = globalForPrisma.prisma ?? new PrismaClient({ adapter });

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
