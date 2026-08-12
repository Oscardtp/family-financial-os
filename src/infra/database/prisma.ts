import { PrismaClient } from '@prisma/client'
import { PrismaPg } from '@prisma/adapter-pg'

declare global {
  // One PrismaClient instance across HMR reloads in dev to avoid
  // engine/adapter re-initialization and connection-pool leaks.
  var prisma: PrismaClient | undefined
}

function createClient(): PrismaClient {
  // Prisma ORM v7: direct Postgres connection requires the PrismaPg driver adapter
  // (rust-free engine). See ADR-003 and .ai/technology-stack.md.
  const adapter = new PrismaPg({
    connectionString: process.env.DATABASE_URL!,
  })
  return new PrismaClient({ adapter })
}

const client = global.prisma ?? createClient()

if (process.env.NODE_ENV !== 'production') {
  global.prisma = client
}

export default client
