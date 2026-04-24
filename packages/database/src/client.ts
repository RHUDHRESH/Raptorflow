import { PrismaPg } from "@prisma/adapter-pg";
import { Pool } from "pg";
import { PrismaClient } from "./generated/prisma/client.js";
import type { PrismaClient as PrismaClientType } from "./generated/prisma/internal/class.js";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClientType | undefined;
};

const connectionString =
  process.env.DATABASE_URL ?? process.env.DIRECT_DATABASE_URL;

if (!connectionString) {
  throw new Error("DATABASE_URL is required for @raptorflow/database");
}

const adapter = new PrismaPg(new Pool({ connectionString }));

export const prisma: PrismaClientType =
  globalForPrisma.prisma ?? (new PrismaClient({ adapter }) as PrismaClientType);

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
