export const DEFAULT_CATEGORIES = [
  { name: 'Comida', emoji: '🍎', type: 'expense', color: '#ef4444' },
  { name: 'Casa', emoji: '🏠', type: 'expense', color: '#f97316' },
  { name: 'Transporte', emoji: '🚗', type: 'expense', color: '#eab308' },
  { name: 'Servicios', emoji: '💡', type: 'expense', color: '#84cc16' },
  { name: 'Salud', emoji: '💊', type: 'expense', color: '#22c55e' },
  { name: 'Educacion', emoji: '🎓', type: 'expense', color: '#14b8a6' },
  { name: 'Gustos', emoji: '🎮', type: 'expense', color: '#06b6d4' },
  { name: 'Compras', emoji: '👕', type: 'expense', color: '#3b82f6' },
  { name: 'Deudas', emoji: '💳', type: 'expense', color: '#8b5cf6' },
  { name: 'Familia', emoji: '❤️', type: 'expense', color: '#ec4899' },
  { name: 'Otros', emoji: '📦', type: 'expense', color: '#6b7280' },
  { name: 'Salario', emoji: '💰', type: 'income', color: '#22c55e' },
  { name: 'Freelance', emoji: '💻', type: 'income', color: '#3b82f6' },
  { name: 'Inversiones', emoji: '📈', type: 'income', color: '#8b5cf6' },
]

export const getCategoryByName = (name) => {
  return DEFAULT_CATEGORIES.find(c => c.name === name)
}

export const getCategoriesByType = (type) => {
  return DEFAULT_CATEGORIES.filter(c => c.type === type)
}

export const getExpenseCategories = () => getCategoriesByType('expense')
export const getIncomeCategories = () => getCategoriesByType('income')
