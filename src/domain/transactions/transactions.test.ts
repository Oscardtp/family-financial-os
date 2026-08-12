import { describe, it, expect } from 'vitest'
import { TransactionFactory, UnbalancedTransactionError, isBalanced } from './Transaction'
import { InMemoryTransactionRepository } from './InMemoryTransactionRepository'
import { CASH, INCOME, EXPENSE, EQUITY, accountBalance } from './Account'

describe('Motor de doble entrada', () => {
  it('income genera 2 partidas cuadradas (debito Efectivo, credito Ingresos)', () => {
    const tx = TransactionFactory.income('Salario', 3000n)
    expect(tx.entries).toHaveLength(2)
    expect(isBalanced(tx)).toBe(true)
    const dr = tx.entries.find((e) => e.direction === 'debit')
    const cr = tx.entries.find((e) => e.direction === 'credit')
    expect(dr?.accountId).toBe(CASH.id)
    expect(cr?.accountId).toBe(INCOME.id)
    expect(dr?.amountCents).toBe(3000n)
    expect(cr?.amountCents).toBe(3000n)
  })

  it('expense genera 2 partidas (debito Gastos, credito Efectivo)', () => {
    const tx = TransactionFactory.expense('Comida', 1250n)
    expect(isBalanced(tx)).toBe(true)
    const dr = tx.entries.find((e) => e.direction === 'debit')
    const cr = tx.entries.find((e) => e.direction === 'credit')
    expect(dr?.accountId).toBe(EXPENSE.id)
    expect(cr?.accountId).toBe(CASH.id)
  })

  it('transaccion desequilibrada lanza UnbalancedTransactionError', () => {
    expect(() =>
      TransactionFactory.create({
        type: 'income',
        description: 'mala',
        entries: [
          { accountId: CASH.id, amountCents: 100n, direction: 'debit' },
          { accountId: INCOME.id, amountCents: 90n, direction: 'credit' },
        ],
      })
    ).toThrow(UnbalancedTransactionError)
  })

  it('repo: registrar income + gasto deja el libro cuadrado (debitos == creditos)', () => {
    const repo = new InMemoryTransactionRepository()
    repo.add(TransactionFactory.income('Salario', 3000n))
    repo.add(TransactionFactory.expense('Comida', 1250n))
    repo.assertLedgerBalanced()
    const dr = repo.allEntries().filter((e) => e.direction === 'debit').reduce((a, e) => a + e.amountCents, 0n)
    const cr = repo.allEntries().filter((e) => e.direction === 'credit').reduce((a, e) => a + e.amountCents, 0n)
    expect(dr).toBe(cr) // 4250 == 4250
  })

  it('repo: saldo de Efectivo = ingresos - gastos (3000 - 1250 = 1750 céntimos)', () => {
    const repo = new InMemoryTransactionRepository()
    repo.add(TransactionFactory.income('Salario', 3000n))
    repo.add(TransactionFactory.expense('Comida', 1250n))
    expect(accountBalance(repo.allEntries(), CASH)).toBe(1750n)
  })

  it('repo: Ingresos acumula ganado (3000) y Gastos lo gastado (1250)', () => {
    const repo = new InMemoryTransactionRepository()
    repo.add(TransactionFactory.income('Salario', 3000n))
    repo.add(TransactionFactory.expense('Comida', 1250n))
    expect(accountBalance(repo.allEntries(), INCOME)).toBe(3000n)
    expect(accountBalance(repo.allEntries(), EXPENSE)).toBe(1250n)
  })

  it('repo: list(accountId) devuelve solo los movimientos de esa cuenta', () => {
    const repo = new InMemoryTransactionRepository()
    repo.add(TransactionFactory.income('Salario', 3000n))
    repo.add(TransactionFactory.expense('Comida', 1250n))
    expect(repo.list(CASH.id)).toHaveLength(2)
    expect(repo.list(EXPENSE.id)).toHaveLength(1)
    expect(repo.list(EQUITY.id)).toHaveLength(0)
  })
})
