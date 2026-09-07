import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useCalendarStore } from './useCalendar'
import { useToast } from '@/composables/useToast'

export const useRecurringStore = defineStore('recurring', () => {
  const calendarStore = useCalendarStore()
  const toast = useToast()

  const recurrentesOpen = ref(false)
  const showRecurringForm = ref(false)
  const recurringSaving = ref(false)
  const newRecurring = ref({
    name: '',
    amount: null,
    account_id: '',
    day_of_month: 1,
    next_due_date: '',
  })

  function openRecurrentes() {
    recurrentesOpen.value = true
  }

  function closeRecurrentes() {
    recurrentesOpen.value = false
    showRecurringForm.value = false
    resetForm()
  }

  function resetForm() {
    newRecurring.value = { name: '', amount: null, account_id: '', day_of_month: 1, next_due_date: '' }
  }

  async function onCreateRecurring() {
    const f = newRecurring.value
    if (!f.name || !f.amount || !f.account_id || !f.next_due_date) return
    recurringSaving.value = true
    const res = await calendarStore.createObligation({
      name: f.name,
      amount: f.amount,
      account_id: f.account_id,
      day_of_month: f.day_of_month,
      next_due_date: f.next_due_date,
    })
    recurringSaving.value = false
    if (res.error) {
      toast.error(res.error)
    } else {
      toast.success('Recurrente creado.')
      showRecurringForm.value = false
      resetForm()
    }
  }

  async function onToggleObligation(ob) {
    const res = await calendarStore.toggleObligationActive(ob.id)
    if (res.error) toast.error(res.error)
    else toast.success(`${ob.name} quedó ${ob.is_active ? 'activo' : 'inactivo'}.`)
  }

  return {
    recurrentesOpen,
    showRecurringForm,
    recurringSaving,
    newRecurring,
    openRecurrentes,
    closeRecurrentes,
    onCreateRecurring,
    onToggleObligation,
  }
})
