'use strict';

class PrismaClient {}

const prisma = new PrismaClient();

exports.PrismaClient = PrismaClient;
exports.prisma = prisma;
exports.default = {
  PrismaClient,
  prisma,
};
