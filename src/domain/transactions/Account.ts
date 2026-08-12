import type { Direction, FinancialAccountType } from './types'

export const NORMAL_BALANCE: Record<FinancialAccountType, Direction> = {
  asset: 'debit',
  liability: 'credit',
  equity: 'credit',
  income: 'credit',
  expense: 'debit',
}

export interface Account {
  id: string
  name: string
  type: FinancialAccountType
}

export const CASH: Account = { id: 'acct_cash', name: 'Efectivo', type: 'asset' }
export const INCOME: Account = { id: 'acct_income', name: 'Ingresos', type: 'income' }
export const EXPENSE: Account = { id: 'acct_expense', name: 'Gastos', type: 'expense' }
export const EQUITY: Account = { id: 'acct_equity', name: 'Patrimonio', type: 'equity' }

export const DEFAULT_CHART: Record<string, Account> = {
  [CASH.id]: CASH,
  [INCOME.id]: INCOME,
  [EXPENSE.id]: EXPENSE,
  [EQUITY.id]: EQUITY,
}

export interface EntryView {
  accountId: string
  amountCents: bigint
  direction: Direction
}

export const accountBalance = (entries: EntryView[], account: Account): bigint => {
  let dr = 0n
  let cr = 0n
  for (const e of entries) {
    if (e.accountId !== account.id) continue
    if (e.direction === 'debit') dr += e.amountCents
    else cr += e.amountCents
  }
  return NORMAL_BALANCE[account.type] === 'debit' ? dr - cr : cr - dr
}
