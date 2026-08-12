import { describe, it, expect, afterAll } from 'vitest'
import prisma from '@/infra/database/prisma'

describe('Prisma v7 + local Postgres wiring', () => {
  it('shares one PrismaClient instance (singleton)', () => {
    expect(prisma).toBeDefined()
    expect(typeof prisma.transaction.create).toBe('function')
  })

  it('auto-generates a UUID v7 id on Transaction.create (no id supplied)', async () => {
    const created = await prisma.transaction.create({
      data: {
        userId: '00000000-0000-0000-0000-000000000000',
        type: 'EXPENSE',
      },
    })

    expect(created.id).toBeTruthy()
    // UUID v7: version nibble = 7, variant 8/9/a/b
    expect(created.id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/
    )

    await prisma.$executeRawUnsafe('DELETE FROM "Transaction" WHERE id = $1', created.id)
    expect(await prisma.transaction.count()).toBe(0)
  })

  afterAll(async () => {
    await prisma.$disconnect().catch(() => {})
  })
})
