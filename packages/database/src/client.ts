import { PrismaPg } from "@prisma/adapter-pg";
import { Pool } from "pg";
import { PrismaClient } from "./generated/prisma/client.js";
import type { PrismaClient as PrismaClientType } from "./generated/prisma/internal/class.js";

function createPrismaClient(): PrismaClientType {
  const connectionString =
    process.env.DATABASE_URL ?? process.env.DIRECT_DATABASE_URL;
  if (!connectionString) {
    throw new Error("DATABASE_URL is required for @raptorflow/database");
  }
  const pool = new Pool({ connectionString, max: 1, idleTimeoutMillis: 1, connectionTimeoutMillis: 1000 });
  const adapter = new PrismaPg(pool);
  return new PrismaClient({ adapter }) as PrismaClientType;
}

let _prisma: PrismaClientType | undefined;

export const prisma: PrismaClientType = new Proxy<PrismaClientType>(
  {} as PrismaClientType,
  {
    get(_target, prop, receiver) {
      if (!_prisma) {
        _prisma = createPrismaClient();
      }
      return Reflect.get(_prisma, prop, receiver);
    },
  },
);
