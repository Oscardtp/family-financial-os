import type { Direction, TransactionType } from './types'
import type { EntryView } from './Account'

export interface Entry {
  id: string
  transactionId: string
  accountId: string
  amountCents: bigint
  direction: Direction
}

export interface Transaction {
  id: string
  type: TransactionType
  description: string | null
  postedAt: Date
  entries: readonly Entry[]
}

export class UnbalancedTransactionError extends Error {
  constructor(public readonly debitTotal: bigint, public readonly creditTotal: bigint) {
    super(`Unbalanced transaction: debitTotal=${debitTotal} creditTotal=${creditTotal}`)
    this.name = 'UnbalancedTransactionError'
  }
}

const sum = (entries: ReadonlyArray<Entry>, dir: Direction): bigint =>
  entries.reduce((acc, e) => (e.direction === dir ? acc + e.amountCents : acc), 0n)

export const isBalanced = (tx: Transaction): boolean =>
  sum(tx.entries, 'debit') === sum(tx.entries, 'credit')

export interface NewTransaction {
  type: TransactionType
  description?: string | null
  id?: string
  postedAt?: Date
  entries: EntryView[]
}

const nextId = () => globalThis.crypto.randomUUID()

export class TransactionFactory {
  static create(input: NewTransaction): Transaction {
    const id = input.id ?? nextId()
    const postedAt = input.postedAt ?? new Date()
    const entries = Object.freeze(
      input.entries.map((e, i) => ({
        id: `${id}:e${i}`,
        transactionId: id,
        accountId: e.accountId,
        amountCents: e.amountCents,
        direction: e.direction,
      }))
    )
    const tx: Transaction = { id, type: input.type, description: input.description ?? null, postedAt, entries }
    if (sum(entries, 'debit') !== sum(entries, 'credit')) {
      throw new UnbalancedTransactionError(sum(entries, 'debit'), sum(entries, 'credit'))
    }
    return tx
  }

  static income(description: string, amountCents: bigint, opts?: { id?: string; postedAt?: Date }) {
    return TransactionFactory.create({
      type: 'income',
      description,
      id: opts?.id,
      postedAt: opts?.postedAt,
      entries: [
        { accountId: 'acct_cash', amountCents, direction: 'debit' },
        { accountId: 'acct_income', amountCents, direction: 'credit' },
      ],
    })
  }

  static expense(description: string, amountCents: bigint, opts?: { id?: string; postedAt?: Date }) {
    return TransactionFactory.create({
      type: 'expense',
      description,
      id: opts?.id,
      postedAt: opts?.postedAt,
      entries: [
        { accountId: 'acct_expense', amountCents, direction: 'debit' },
        { accountId: 'acct_cash', amountCents, direction: 'credit' },
      ],
    })
  }
}
