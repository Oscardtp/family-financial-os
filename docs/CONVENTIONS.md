# CONVENTIONS.md — Convenciones de Codigo

## General

- **Idioma:** Todo el copy de la UI y mensajes de error en **espanol colombiano natural**
- **Moneda:** COP siempre. `Decimal` para dinero. Nunca `Float`.
- **UUIDs:** `String(36)` en la DB. `uuid.UUID` en Python. `string` en JavaScript.
- **Timezone:** UTC para todos los timestamps.

---

## Backend (Python)

### Estilo de Codigo
- **PEP 8** como guia base
- **Type hints** en signatures de funciones
- **Max lineas:** 120 por linea (preferido < 100)
- **Imports:** stdlib, third-party, local (separados por lineas en blanco)

### Naming

| Elemento | Convencion | Ejemplo |
|----------|-----------|---------|
| Archivos | `snake_case.py` | `debt_service.py` |
| Classes | `PascalCase` | `DashboardService`, `DebtEngine` |
| Functions | `snake_case()` | `get_summary()`, `calculate_net_worth()` |
| Variables | `snake_case` | `monthly_income`, `total_balance` |
| Constants | `UPPER_SNAKE_CASE` | `DB_FILE`, `PROJECT_ROOT` |
| Private | `_prefix` | `_to_dict()`, `_build_budget_status()` |
| Router prefixes | `snake_case` | `/api/v1/savings/goals` |
| Schema names | `PascalCase` + suffix | `DebtCreate`, `DebtResponse` |

### Estructura de Archivos

```
# Orden de imports en un archivo tipico:
from decimal import Decimal                    # stdlib
from fastapi import APIRouter, Depends         # third-party
from app.domain.value_objects.money import Money  # local
```

### Clean Architecture

```python
# Router -> Service -> Repository -> Model
#       -> Financial Engine (para calculos)

# Los routers NO tienen logica de negocio
# Los services orquestan repos y engines
# Los repos acceden a la DB
# Los engines son funciones puras
```

### Patterns

**Service Pattern:**
```python
class DebtService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SQLAlchemyDebtRepository(db)
        self.payment_repo = SQLAlchemyDebtPaymentRepository(db)

    async def list(self, household_id: str, skip=0, limit=100):
        return await self.repo.get_all(household_id, skip, limit)
```

**Repository Pattern:**
```python
class SQLAlchemyDebtRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, household_id: str, skip=0, limit=100):
        result = await self.db.execute(
            select(DebtModel).where(DebtModel.household_id == household_id)
        )
        return [self._to_dict(m) for m in result.scalars().all()]
```

**Router Pattern:**
```python
router = APIRouter(prefix="/debts", tags=["Debts"])

@router.get("", response_model=list[DebtResponse])
async def list_debts(
    current_user: dict = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    service = DebtService(db)
    return await service.list(current_user["household_id"])
```

**Dependency Injection:**
```python
# Siempre usar Depends para:
# - get_db (sesion de DB)
# - require_viewer / require_member / require_owner (autorizacion)
# - get_current_user (usuario actual)
```

**Error Handling:**
```python
# HTTPException con mensajes en espanol
raise HTTPException(status_code=404, detail="No encontramos esta deuda")

# Errores de negocio con ValueError
try:
    result = await service.create(data, household_id)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

**Auditoria:**
```python
await log_action(
    db, current_user["household_id"], current_user["id"], current_user["email"],
    "create", "account", result["id"], result["name"],
)
await db.commit()
```

### Financial Engine

```python
# Funciones puras: mismo input -> mismo output
# Sin side effects (no DB, no HTTP)
# Decimal precision siempre
# Usar Money VO para operaciones monetarias

class DebtEngine:
    def calculate_summary(self, debts: list[dict]) -> DebtSummaryResult:
        # Calculo puro, sin DB
        pass
```

---

## Frontend (Vue.js)

### Estilo de Codigo

- **Composition API** con `<script setup>` en todos los componentes
- **Single File Components (SFC)**: `<template>`, `<script setup>`, `<style scoped>`
- **Max lineas:** 500 por componente (preferido < 300)

### Naming

| Elemento | Convencion | Ejemplo |
|----------|-----------|---------|
| Archivos.vue | `PascalCase.vue` | `DebtCard.vue` |
| Archivos.js | `camelCase.js` | `useCurrency.js` |
| Components | `PascalCase` | `<DebtCard />`, `<QuickAddFab />` |
| Composables | `use` prefix | `useCurrency()`, `useFormattedNumber()` |
| Stores | `use` prefix + `Store` | `useAuthStore()`, `useGoalsStore()` |
| Props | `camelCase` | `:goal-id="goal.id"` |
| Events | `kebab-case` | `@transaction-created="refresh"` |
| CSS classes | `kebab-case` | `.nav-item`, `.card-hover` |
| CSS variables | `--kebab-case` | `--color-primary-500` |

### Estructura de Componente

```vue
<template>
  <!-- Template minimal, delegar logica a composables -->
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCurrency } from '@/composables/useCurrency'

// Props
const props = defineProps({ ... })

// Emits
const emit = defineEmits([...])

// Store
const auth = useAuthStore()

// Composable
const { fmt, fmtFull } = useCurrency()

// State local
const loading = ref(false)

// Computed
const displayName = computed(() => ...)

// Methods
async function loadData() { ... }

// Lifecycle
onMounted(loadData)
</script>

<style scoped>
/* Estilos scoped al componente */
</style>
```

### Composables

```javascript
// Siempre exportar como named export
export function useCurrency() {
  // Logica reutilizable
  return { fmt, fmtFull, fmtDate }
}

// Uso:
import { useCurrency } from '@/composables/useCurrency'
const { fmt, fmtFull } = useCurrency()
```

### Stores (Pinia)

```javascript
// Composition API style
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(email, password) { ... }

  return { user, token, isAuthenticated, login }
})
```

### API Client

```javascript
// Siempre importar como default
import api from '@/services/api'

// Uso
const { data } = await api.get('/accounts')
await api.post('/debts', payload)
```

### Formateo de Moneda

```javascript
import { useCurrency } from '@/composables/useCurrency'
const { fmt, fmtFull } = useCurrency()

// fmt(1500000) -> "1.500.000"
// fmtFull(1500000) -> "$1.500.000"
```

### Formateo de Numeros en Inputs

```javascript
import { useFormattedNumber } from '@/composables/useFormattedNumber'
const { rawValue, displayValue, onInput, onFocus } = useFormattedNumber(0)

// IMPORTANTE: onInput y onFocus requieren el evento nativo
// <input :value="displayValue" @input="onInput" @focus="onFocus" />
```

---

## Testing

### Backend

```python
# Tests en backend/tests/
# Ejecutar: python -m pytest tests/ -x -q

# Patron:
@pytest.mark.asyncio
async def test_create_account(client, auth_headers):
    response = await client.post("/api/v1/accounts", json={...}, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Mi Cuenta"
```

### Frontend

```javascript
// Tests en src/__tests__/
// Ejecutar: npm run test

// Patron:
import { mount } from '@vue/test-utils'
import ComponentName from '@/components/ComponentName.vue'

describe('ComponentName', () => {
  it('renders correctly', () => {
    const wrapper = mount(ComponentName)
    expect(wrapper.text()).toContain('expected text')
  })
})
```

---

## Git

### Commits
```
feat: nueva funcionalidad
fix: correccion de bug
docs: documentacion
refactor: refactorizacion sin cambio de comportamiento
test: agregar/modificar tests
chore: tareas de mantenimiento
```

### Ramas
```
main          # Produccion, estable
develop       # Desarrollo, integracion
feature/*     # Nuevas funcionalidades
fix/*         # Correccion de bugs
```

---

## Seguridad

- **Nunca** hardcodear secrets, API keys, tokens, passwords
- Siempre usar variables de entorno
- `.env` nunca en git
- Queries SQL siempre parametrizadas (SQLAlchemy ORM garantiza esto)
- Passwords hasheados con bcrypt (4.0.1)
- JWT con expiracion (30 min access, 7 dias refresh)
- Rate limiting pendiente en endpoints publicos
