import type { Entry, Transaction } from './Transaction'
import { UnbalancedTransactionError } from './Transaction'
import { accountBalance } from './Account'
import type { Account } from './Account'

export class InMemoryTransactionRepository {
  private readonly txs: Transaction[] = []

  add(tx: Transaction): void {
    this.txs.push(tx)
  }

  findById(id: string): Transaction | null {
    return this.txs.find((t) => t.id === id) ?? null
  }

  list(accountId?: string): Transaction[] {
    if (!accountId) return [...this.txs]
    return this.txs.filter((t) => t.entries.some((e) => e.accountId === accountId))
  }

  allEntries(): Entry[] {
    return this.txs.flatMap((t) => [...t.entries])
  }

  balanceOf(account: Account): bigint {
    return accountBalance(this.allEntries(), account)
  }

  assertLedgerBalanced(): void {
    const entries = this.allEntries()
    const dr = entries.filter((e) => e.direction === 'debit').reduce((a, e) => a + e.amountCents, 0n)
    const cr = entries.filter((e) => e.direction === 'credit').reduce((a, e) => a + e.amountCents, 0n)
    if (dr !== cr) throw new UnbalancedTransactionError(dr, cr)
  }
}
