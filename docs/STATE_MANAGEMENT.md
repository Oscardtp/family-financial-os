# STATE_MANAGEMENT.md — Gestion de Estado Frontend

## Resumen

El frontend usa **Pinia** como store global y **Composition API** con `ref()`/`computed()` para estado local. No hay Redux ni Vuex.

---

## Stores Pinia (3)

### 1. `auth` (`stores/auth.js`)

**Responsabilidad:** Autenticacion, sesion de usuario, tokens.

**Estado:**
```javascript
{
  user: ref(null),           // Objeto usuario { id, email, name, role, household_id }
  token: ref(null),          // JWT access token
  loading: ref(false),       // Estado de carga
  error: ref(null),          // Mensaje de error
}
```

**Getters:**
```javascript
isAuthenticated: computed(() => !!token.value)
```

**Acciones:**
```javascript
register(email, name, password)  // POST /auth/register, guarda tokens, fetchUser()
login(email, password)           // POST /auth/login, guarda tokens, fetchUser()
fetchUser()                      // GET /auth/me, actualiza user
logout()                         // Limpia tokens de localStorage y user
```

**Persistencia:**
- `access_token` y `refresh_token` en `localStorage`
- Al instanciar, si hay token, llama `fetchUser()` automaticamente

**Uso:**
```javascript
const auth = useAuthStore()
auth.isAuthenticated  // boolean
auth.user             // objeto usuario o null
auth.login(email, password)
auth.logout()
```

---

### 2. `goals` (`stores/goals.js`)

**Responsabilidad:** Metas de ahorro, contribuciones, proyecciones.

**Estado:**
```javascript
{
  goals: ref([]),                    // Lista de metas
  loading: ref(false),
  error: ref(null),
  expandedGoal: ref(null),           // ID de meta expandida
  highlightedGoalId: ref(null),      // ID de meta resaltada (nueva)
  filterType: ref('all'),            // Filtro: all, savings, investment
  sortBy: ref('name'),               // Orden: name, priority, progress, date
  contributionGoalId: ref(null),     // Meta en modo contribucion
  editingGoalId: ref(null),          // Meta en modo edicion
  deletingGoalId: ref(null),         // Meta en modo eliminacion
  isContributing: ref(false),
  isEditing: ref(false),
  isDeleting: ref(false),
  projectionCache: ref(new Map()),   // Cache de proyecciones
  projectionLoading: ref(new Map()),
  projectionError: ref(new Map()),
}
```

**Getters:**
```javascript
activeGoals        // Metas incompletas, filtradas y ordenadas
completedGoals     // Metas completadas
totalCurrent       // Suma de current_amount de todas las metas
totalTarget        // Suma de target_amount de todas las metas
overallProgress    // Porcentaje general de progreso
```

**Acciones principales:**
```javascript
fetchGoals()                          // GET /savings/goals
createGoal(data)                      // POST /savings/goals
editGoal(id, data)                    // PUT /savings/goals/{id}
deleteGoal(id)                        // DELETE /savings/goals/{id}
contributeGoal(id, amount, date)      // POST /savings/goals/{id}/contributions
fetchProjection(goal)                 // Calcula proyeccion y cachea
```

**Patron de UI:**
- `openContribution(goal)` -> `submitContribution(amount, date)` -> `closeContribution()`
- `openEdit(goal)` -> `submitEdit(data)` -> `closeEdit()`
- `confirmDelete(goal)` -> `submitDelete()` -> `closeDelete()`

**Uso:**
```javascript
const goalsStore = useGoalsStore()
goalsStore.activeGoals    // metas activas filtradas
goalsStore.fetchGoals()   // cargar metas
goalsStore.createGoal(data) // crear meta
```

---

### 3. `calendar` (`stores/useCalendar.js`)

**Responsabilidad:** Eventos financieros, obligaciones, calendario.

**Estado:**
```javascript
{
  events: ref([]),              // Lista de eventos
  obligations: ref([]),         // Lista de obligaciones
  loading: ref(false),
  error: ref(null),
  year: ref(new Date().getFullYear()),
  month: ref(new Date().getMonth() + 1),
  selectedEvent: ref(null),     // Evento seleccionado
  detailOpen: ref(false),       // Si el detalle esta abierto
  accounts: ref([]),            // Cuentas para formularios
  members: ref([]),             // Miembros del hogar
}
```

**Acciones:**
```javascript
fetchRange(y, m)                // GET /events?from_date=&to_date=
fetchMonth(y, m)                // Alias de fetchRange
fetchObligations()              // GET /obligations
fetchAccounts()                 // GET /accounts
fetchMembers()                  // GET /household
openEvent(event)                // Abre detalle
closeDetail()                   // Cierra detalle
markPaid(event)                 // POST /events/{id}/pay
unpayEvent(event)               // POST /events/{id}/unpay
createEvent(data)               // POST /events
editEvent(eventId, data)        // PUT /events/{id}
deleteEvent(eventId)            // DELETE /events/{id}
toggleObligationActive(obId)    // PUT /obligations/{id}
deleteObligation(obId)          // DELETE /obligations/{id}
createObligation(data)          // POST /obligations
```

**Uso:**
```javascript
const calendarStore = useCalendarStore()
calendarStore.events           // eventos cargados
calendarStore.fetchRange()     // cargar eventos del rango
calendarStore.markPaid(event)  // marcar como pagado
```

---

## Composables (17)

Los composables encapsulan logica reutilizable y estado local. **No son stores globales** — se instancian por componente.

### Composables de Formateo

| Composable | Archivo | Funcion |
|------------|---------|---------|
| `useCurrency` | `useCurrency.js` | Formateo COP: `fmt()`, `fmtFull()`, `fmtDate()`, `fmtMonth()` |
| `useFormattedNumber` | `useFormattedNumber.js` | Inputs numericos formateados con `$` y separadores |

### Composables de Datos

| Composable | Archivo | Funcion |
|------------|---------|---------|
| `useDashboard` | `useDashboard.js` | Carga datos del dashboard, computed para metrics |
| `useGoals` | `useGoals.js` | Logica de metas (compartida con store) |
| `useGoalProjection` | `useGoalProjection.js` | Calculo de proyecciones |
| `useGoalDate` | `useGoalDate.js` | Calculo de fechas de metas |
| `useBudgets` | `useBudgets.js` | Logica de presupuestos |
| `useNotifications` | `useNotifications.js` | Logica de notificaciones |
| `useProjections` | `useProjections.js` | Proyecciones financieras |

### Composables de Calendario

| Composable | Archivo | Funcion |
|------------|---------|---------|
| `useAgenda` | `useAgenda.js` | Agenda y vista de calendario |
| `useCalendarFilters` | `useCalendarFilters.js` | Filtros del calendario |
| `useCalendarHelpers` | `useCalendarHelpers.js` | Helpers (colores, formatos) |
| `useCalendarNavigation` | `useCalendarNavigation.js` | Navegacion mes/anterior/siguiente |

### Composables de UI

| Composable | Archivo | Funcion |
|------------|---------|---------|
| `useToast` | `useToast.js` | Sistema de notificaciones toast |
| `useConfirm` | `useConfirm.js` | Dialogo de confirmacion |
| `useSmartCalculator` | `useSmartCalculator.js` | Calculadora inteligente |
| `useFinancialHelpers` | `useFinancialHelpers.js` | Helpers financieros generales |

---

## Estado Local (Componentes)

Cada componente maneja su propio estado local con `ref()` y `computed()`:

```vue
<script setup>
// Estado local
const loading = ref(false)
const showModal = ref(false)
const form = ref({ name: '', amount: 0 })

// Computed local
const isValid = computed(() => form.value.name && form.value.amount > 0)

// Methods
async function handleSubmit() {
  loading.value = true
  await api.post('/debts', form.value)
  loading.value = false
  showModal.value = false
}
</script>
```

---

## Datos Globales vs Locales

### Globales (Pinia Store)
- `auth`: Token y usuario (compartido entre todas las vistas)
- `goals`: Metas de ahorro (compartido entre Goals.vue y componentes hijos)
- `calendar`: Eventos y obligaciones (compartido entre vistas del calendario)

### Locales (Component/Composable)
- `loading`, `error`, `showModal`, `form` — por componente
- `useDashboard()` — se instancia en Resumen.vue
- `useBudgets()` — se instancia en el componente de presupuesto
- `useFormattedNumber()` — se instancia por input

---

## Flujo de Datos

```
API Response
  -> Store/Composable (ref)
    -> Component Template (render)
      -> User Interaction
        -> Composable Method
          -> API Call
            -> Store/Composable Update
              -> Reactive Render
```

### Ejemplo: Dashboard

```javascript
// useDashboard.js
const d = ref({ total_balance: 0, ... })

async function loadData() {
  loading.value = true
  const [dashboardRes, debtsRes] = await Promise.all([
    api.get('/dashboard'),
    api.get('/debts'),
  ])
  d.value = dashboardRes.data
  debts.value = debtsRes.data
  loading.value = false
}
```

```vue
<!-- Resumen.vue -->
<script setup>
import { useDashboard } from '@/composables/useDashboard'
const { d, loading, loadData } = useDashboard()
onMounted(loadData)
</script>

<template>
  <div v-if="loading">Cargando...</div>
  <div v-else>
    <span>{{ fmtFull(d.total_balance) }}</span>
  </div>
</template>
```

---

## Persistencia

### LocalStorage
- `access_token` — JWT access token
- `refresh_token` — JWT refresh token

### No Persistido
- Datos de usuario (se recargan en cada sesion via `fetchUser()`)
- Metas, eventos, cuentas (se cargan al montar cada vista)
- Estado de UI (modales, filtros, etc.)

---

## Sincronizacion entre Componentes

### Via Store
Los stores Pinia son reactivos. Si un componente modifica el store, todos los componentes que usan ese store se actualizan automaticamente.

### Via Props/Emits
Para componentes padre-hijo:
- Props: datos del padre al hijo
- Emits: eventos del hijo al padre

### Via Event Bus (Parcial)
Hay un `events.js` que exporta servicios API, pero no se usa como event bus para comunicacion entre componentes. La comunicacion es via stores o props/emit.

---

## Gotchas Conocidos

1. **`useFormattedNumber`**: `onInput` y `onFocus` requieren el evento nativo. Si llamas sin evento, `event.target` lanza `TypeError`.

2. **NaN en Debts.vue**: Al sumar `current_balance + minimum_payment`, usar `Number(...)` para coercion. La API puede devolver string/null.

3. **`api` es export default**: Siempre importar como `import api from '@/services/api'`, no como named export.

4. **Projection Cache**: Las proyecciones se cachean en `Map`. Si los datos cambian, la cache no se invalida automaticamente.

5. **`fmt()` sin valor**: `useCurrency().fmt(null)` retorna `"0"`. Usar `fmt(value || 0)` si se necesita fallback.
