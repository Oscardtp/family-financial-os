# Issues Abiertas — Family Financial OS

> **Fecha de auditoría:** 2026-09-17
> **Estado:** Post-FASE 4, 147 tests pasando

---

## ISSUE-001: Rate Limiting en Endpoints de Autenticación

**Tipo:** security / enhancement
**Prioridad:** P1 (Alta)
**Estado:** Abierto
**Archivos afectados:**
- `backend/app/presentation/v1/auth.py` (lines 11-28)
- `backend/app/main.py` (middleware)

---

### Descripción del Problema

Los endpoints `/api/v1/auth/login` y `/api/v1/auth/register` no tienen rate limiting. Un atacante puede hacer fuerza bruta contra contraseñas o crear miles de cuentas falsas sin restricción alguna.

### Pasos para Reproducir

```bash
# Ejecutar 100 peticiones de login en loop
for i in $(seq 1 100); do
  curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@familia.com","password":"wrong"}'
done

# Todas retornarán 401 (Unauthorized) sin ningún bloqueo
```

### Comportamiento Esperado

- Después de N intentos fallidos (ej. 5) desde la misma IP, el endpoint debe retornar `429 Too Many Requests`.
- El bloqueo debe durar un tiempo progresivo (ej. 1 min, 5 min, 15 min).
- El endpoint `/register` debe limitar creación de cuentas (ej. 3 por IP por hora).

### Comportamiento Actual

- Todas las peticiones son procesadas sin límite.
- No hay header `Retry-After` en la respuesta.
- No hay logging de intentos sospechosos.
- El servidor no tiene protección contra credential stuffing.

### Entorno / Datos Técnicos

- **Backend:** FastAPI 0.104+, Python 3.12
- **Archivos:** `backend/app/presentation/v1/auth.py` (router sin dependencia de rate limit)
- **Middleware actual:** Solo CORS (`backend/app/main.py` line 47-53)

### Corrección Propuesta

**Opción A: `slowapi` (Recomendada)**

```bash
pip install slowapi
```

```python
# backend/app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

```python
# backend/app/presentation/v1/auth.py
from app.main import limiter

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, data: UserLogin, db: AsyncSession = Depends(get_db)):
    ...

@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("3/hour")
async def register(request: Request, data: UserRegister, db: AsyncSession = Depends(get_db)):
    ...
```

**Opción B: Middleware manual con in-memory store**

```python
# backend/app/middleware/rate_limit.py
from collections import defaultdict
from time import time

_rate_store = defaultdict(list)

def check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    now = time()
    _rate_store[key] = [t for t in _rate_store[key] if now - t < window_seconds]
    if len(_rate_store[key]) >= max_requests:
        return False
    _rate_store[key].append(now)
    return True
```

### Qué Puede Fallar

| Riesgo | Mitigación |
|--------|------------|
| `slowapi` incompatible con async | Usar `slowapi>=0.1.9` que soporta async |
| Rate limit en desarrollo molesta | Agregar `DEBUG=True` para deshabilitar en dev |
| Proxy reverso (nginx) no pasa IP real | Configurar `X-Forwarded-For` en trusted hosts |
| Almacén in-memory se resetea al reiniciar | Usar Redis en producción (futuro) |

### Testing

```python
# tests/test_rate_limit.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_rate_limit(client: AsyncClient):
    for _ in range(6):
        await client.post("/api/v1/auth/login", json={
            "email": "test@test.com",
            "password": "wrong"
        })
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@test.com",
        "password": "wrong"
    })
    assert response.status_code == 429
    assert "Retry-After" in response.headers
```

---

## ISSUE-002: Dividir `schemas.py` por Dominio

**Tipo:** enhancement / refactor
**Prioridad:** P2 (Media)
**Estado:** Abierto
**Archivos afectados:**
- `backend/app/presentation/schemas/schemas.py` (672 líneas)

---

### Descripción del Problema

El archivo `schemas.py` contiene ~50 schemas Pydantic de TODOS los dominios (auth, accounts, transactions, debts, savings, budgets, events, obligations, dashboard) en un solo archivo de 672 líneas. Esto dificulta:
- Encontrar un schema específico
- Entender las dependencias entre schemas
- Merge conflicts cuando dos personas editan domains diferentes
- Tests unitarios de schemas

### Pasos para Reproducir

```bash
# Abrir el archivo y contar líneas
wc -l backend/app/presentation/schemas/schemas.py
# Output: 672

# Contar clases
grep -c "class.*BaseModel" backend/app/presentation/schemas/schemas.py
# Output: ~50
```

### Comportamiento Esperado

Estructura modular por dominio:

```
backend/app/presentation/schemas/
├── __init__.py              # Re-export todo para compatibilidad
├── auth.py                  # UserRegister, UserLogin, TokenResponse, TokenRefresh, UserResponse
├── accounts.py              # AccountCreate, AccountUpdate, AccountResponse
├── transactions.py          # TransactionCreate, TransactionResponse
├── categories.py            # CategoryCreate, CategoryUpdate, CategoryResponse
├── budgets.py               # BudgetCreate, BudgetUpdate, BudgetResponse, BudgetStatusItem
├── debts.py                 # DebtCreate, DebtUpdate, DebtResponse, DebtPaymentCreate, DebtPaymentResponse, MarkPaidRequest, PaymentMonthHistory
├── savings.py               # SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalResponse, SavingsContributionCreate, SavingsContributionResponse
├── events.py                # EventCreate, EventUpdate, EventResponse
├── obligations.py           # ObligationCreate, ObligationUpdate, ObligationResponse
├── dashboard.py             # DashboardResponse, SavingsSummary, SavingsGoalSummary
├── projections.py           # GoalProjectionRequest, GoalProjectionResponse
├── recurring_payments.py    # RecurringPaymentCreate, RecurringPaymentUpdate, RecurringPaymentResponse
├── preferences.py           # CategoryAccountPreferenceCreate, CategoryAccountPreferenceResponse
└── household.py             # HouseholdUpdate
```

### Comportamiento Actual

```
backend/app/presentation/schemas/
├── __init__.py
└── schemas.py              # 672 líneas, TODO junto
```

### Corrección Propuesta

**Paso 1: Crear archivos por dominio**

```python
# backend/app/presentation/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr = Field(..., min_length=5, max_length=255)
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    role: str
    household_id: Optional[UUID] = None
    created_at: datetime
```

**Paso 2: Actualizar `__init__.py` para re-export**

```python
# backend/app/presentation/schemas/__init__.py
from .auth import UserRegister, UserLogin, TokenResponse, TokenRefresh, UserResponse
from .accounts import AccountCreate, AccountUpdate, AccountResponse
from .debts import DebtCreate, DebtUpdate, DebtResponse
# ... etc
```

**Paso 3: Actualizar imports en routers**

```python
# ANTES
from app.presentation.schemas.schemas import UserRegister, UserLogin

# DESPUÉS
from app.presentation.schemas import UserRegister, UserLogin
# O directamente:
from app.presentation.schemas.auth import UserRegister, UserLogin
```

### Qué Puede Fallar

| Riesgo | Mitigación |
|--------|------------|
| Circular imports entre schemas | `__init__.py` solo re-export, no importa de otros módulos |
| Tests rompen por import path | Buscar `from app.presentation.schemas.schemas import` y reemplazar |
| Router olvida actualizar import | `grep -r "schemas.schemas" backend/` antes de commit |
| Schema referenciado por nombre de archivo | Mantener `schemas.py` como stub temporal con re-exports |

### Testing

```bash
# Verificar que no hay imports rotos
cd backend
python -c "from app.presentation.schemas import *; print('OK')"

# Ejecutar tests
python -m pytest tests/ -x -q

# Buscar imports antiguos
grep -r "from app.presentation.schemas.schemas" backend/
# Debe retornar vacío (o solo __init__.py)
```

---

## ISSUE-003: Descomponer `Resumen.vue` en Sub-componentes

**Tipo:** enhancement / refactor
**Prioridad:** P2 (Media)
**Estado:** Abierto
**Archivos afectados:**
- `frontend/src/views/Resumen.vue` (573 líneas)

---

### Descripción del Problema

`Resumen.vue` es el componente más grande del frontend (573 líneas). Contiene:
- Header con saludo
- Alerta financiera
- Card de disponible
- Sección "Hoy" (eventos de hoy)
- Sección "Este mes" (ingresos/gastos)
- Panel de presupuesto
- Próximos movimientos
- Top categorías ("¿En qué se fue el dinero?")
- Últimos movimientos
- Sidebar: deudas, metas, coach
- Loading skeleton
- 2 modales (BudgetDetailModal, CalendarBottomSheet)

Esto dificulta mantenimiento, testing y reutilización.

### Pasos para Reproducir

```bash
wc -l frontend/src/views/Resumen.vue
# Output: 573

# Contar secciones lógicas
grep -c "card card-section\|resumen-alert\|available-card\|coach-list" frontend/src/views/Resumen.vue
# Output: 8+ secciones distintas
```

### Comportamiento Esperado

```
frontend/src/views/Resumen.vue              # ~150 líneas (orchestrator)
frontend/src/components/resumen/
├── ResumenHeader.vue                       # Saludo + fecha
├── FinancialAlert.vue                      # Alerta financiera
├── AvailableCard.vue                       # Card de disponible
├── TodayEvents.vue                         # Eventos de hoy
├── MonthSummary.vue                        # Ingresos/gastos del mes
├── UpcomingMovements.vue                   # Próximos movimientos
├── TopCategories.vue                       # ¿En qué se fue el dinero?
├── RecentTransactions.vue                  # Últimos movimientos
├── DebtsSidebarCard.vue                    # sidebar deudas
├── GoalsSidebarCard.vue                    # sidebar metas
└── CoachCard.vue                           # Family Coach
```

### Comportamiento Actual

Un solo archivo de 573 líneas con template, script y scoped styles mezclados.

### Corrección Propuesta

**Paso 1: Extraer componentes pequeños primero**

```vue
<!-- frontend/src/components/resumen/FinancialAlert.vue -->
<script setup>
defineProps({
  alert: { type: Object, required: true }
})
const emit = defineEmits(['dismiss', 'option'])
</script>

<template>
  <div class="resumen-alert" :class="'alert-' + alert.type">
    <div class="alert-content">
      <div class="alert-header">
        <AlertTriangle :size="14" />
        <span>{{ alert.message }}</span>
        <button class="alert-close" @click="emit('dismiss')" aria-label="Cerrar">
          <X :size="12" />
        </button>
      </div>
      <div v-if="alert.options?.length" class="alert-actions">
        <button v-for="opt in alert.options" :key="opt"
          class="alert-action-btn" @click="emit('option', opt)">
          {{ opt }}
        </button>
      </div>
    </div>
  </div>
</template>
```

**Paso 2: Actualizar Resumen.vue para usar sub-componentes**

```vue
<script setup>
import FinancialAlert from '@/components/resumen/FinancialAlert.vue'
import AvailableCard from '@/components/resumen/AvailableCard.vue'
import TodayEvents from '@/components/resumen/TodayEvents.vue'
// ... etc
</script>

<template>
  <div class="resumen-page">
    <ResumenHeader :greeting="greeting" :today-label="todayLabel" />

    <FinancialAlert
      v-if="d.financial_alert && !alertDismissed"
      :alert="d.financial_alert"
      @dismiss="alertDismissed = true"
      @option="handleAlertOption"
    />

    <AvailableCard :availability="availability" :total-balance="d.total_balance" />

    <div class="resumen-grid">
      <div class="resumen-main">
        <TodayEvents :events="todayEvents" @select="goEvent" />
        <!-- ... -->
      </div>
    </div>
  </div>
</template>
```

### Qué Puede Fallar

| Riesgo | Mitigación |
|--------|------------|
| Scoped CSS no aplica en hijo | Mover estilos compartidos a `views.css` o design tokens |
| Props deep nesting | Usar `v-bind` en template, no pasar objetos anidados |
| Performance con muchos componentes | Vue3 tiene tree-shaking, no es problema hasta ~200 componentes |
| Loading skeleton se rompe | Extraer `SkeletonLoader` como prop, no duplicar |

### Testing

```bash
# Verificar que la vista renderiza correctamente
cd frontend
npm run test -- --grep "Resumen"

# Verificar que no hay errores de import
npm run build
```

---

## ISSUE-004: Coverage Backend < 80% en Services

**Tipo:** testing / enhancement
**Prioridad:** P2 (Media)
**Estado:** Abierto
**Archivos afectados:**
- `backend/tests/` (147 tests, ~60% coverage estimado)

---

### Descripción del Problema

Aunque hay 147 tests pasando, la cobertura estimada del backend es ~60%. Los servicios con menor cobertura son:
- `calendar_debt_sync_service.py` — 0 tests
- `obligation_sync_service.py` — 0 tests
- `learning_service.py` — tests básicos
- `notification_service.py` — tests básicos
- `event_service.py` — tests de integración, no unitarios

### Pasos para Reproducir

```bash
cd backend
pip install pytest-cov
python -m pytest tests/ --cov=app --cov-report=term-missing

# Salida esperada (estimada):
# app/application/services/calendar_debt_sync_service.py   0%
# app/application/services/obligation_sync_service.py      0%
# app/application/services/learning_service.py            30%
# app/application/services/notification_service.py        40%
# app/application/services/event_service.py               45%
# TOTAL                                                   ~60%
```

### Comportamiento Esperado

- Cobertura mínima 80% en `app/application/services/`
- Cobertura mínima 80% en `app/financial_engine/`
- Cobertura mínima 70% en `app/presentation/v1/`
- Tests unitarios (no solo integración) para lógica de negocio

### Comportamiento Actual

- Solo 5 tests de integración + 25 de API
- Services con 0% coverage: `calendar_debt_sync_service`, `obligation_sync_service`
- Financial engine: parcialmente testeado
- Sin tests para edge cases en la mayoría de services

### Corrección Propuesta

**Prioridad de tests a crear:**

```python
# 1. tests/test_services/test_calendar_sync.py
@pytest.mark.asyncio
async def test_sync_debt_to_calendar_creates_events(session):
    """Deudas con due_day generan eventos en el calendario"""
    ...

@pytest.mark.asyncio
async def test_sync_debt_skips_paid_debts(session):
    """Deudas pagadas no generan eventos"""
    ...

# 2. tests/test_services/test_obligation_sync.py
@pytest.mark.asyncio
async def test_obligation_generates_events_for_next_months(session):
    """Obligación mensual genera 12 eventos"""
    ...

# 3. tests/test_services/test_notification_service.py
@pytest.mark.asyncio
async def test_creates_notification_for_due_debt(session):
    """Crea notificación cuando deuda vence en 3 días"""
    ...

# 4. tests/test_financial_engine/test_projection.py
def test_projection_with_different_rate_types():
    """Proyección con EA, EM, nominal produce resultados distintos"""
    ...
```

### Qué Puede Fallar

| Riesgo | Mitigación |
|--------|------------|
| Tests lentos por DB | Usar SQLite en memoria para tests (`:memory:`) |
| Fixtures complejas | Crear factories (`factory_boy`) para datos de prueba |
| Tests frágiles (flaky) | Evitar dependencia de fecha actual, usar `freezegun` |
| Mock excesivo | Preferir tests de integración con DB real de test |

### Testing

```bash
# Generar reporte de cobertura
python -m pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html

# Verificar cobertura mínima
python -m pytest tests/ --cov=app --cov-fail-under=80
```

---

## ISSUE-005: Migrar Event Bus a Pinia

**Tipo:** maintenance / refactor
**Prioridad:** P3 (Baja)
**Estado:** Abierto (parcialmente resuelto)
**Archivos afectados:**
- `frontend/src/stores/goals.js`
- `frontend/src/stores/useCalendar.js`
- `frontend/src/composables/` (varios)

---

### Descripción del Problema

El patrón actual usa `window.dispatchEvent` / `window.addEventListener` para comunicación entre componentes hermanos. Ejemplo:

```javascript
// ANTES (eliminado en FASE 1)
window.dispatchEvent(new CustomEvent('goal-created', { detail: goal }))

// Ahora se usa emit pero el patrón persiste en algunos lugares
```

**Estado actual:** La mayoría de la comunicación ya usa Vue emits y Pinia stores. Quedan patrones menores que migrar.

### Pasos para Reproducir

```bash
# Buscar remaining event bus patterns
grep -rn "window.dispatchEvent\|window.addEventListener" frontend/src/
# Resultado: Solo AppLayout.vue (resize listener - OK)

# Buscar comunicación cross-component via emits encadenados
grep -rn "emit('transaction-created')" frontend/src/
# Resultado: QuickAddFab.vue → App.vue (2 niveles)
```

### Comportamiento Esperado

Toda comunicación cross-component debe usar Pinia stores:

```javascript
// frontend/src/stores/transactions.js (nuevo)
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTransactionsStore = defineStore('transactions', () => {
  const lastCreated = ref(null)

  function notifyCreated(transaction) {
    lastCreated.value = transaction
  }

  return { lastCreated, notifyCreated }
})
```

```javascript
// En QuickAddFab.vue
import { useTransactionsStore } from '@/stores/transactions'
const txStore = useTransactionsStore()

async function onTransactionCreated(tx) {
  txStore.notifyCreated(tx)  // En vez de emit
}

// En App.vue (watcher)
import { useTransactionsStore } from '@/stores/transactions'
const txStore = useTransactionsStore()

watch(() => txStore.lastCreated, () => {
  fetchData()  // Refrescar datos
})
```

### Comportamiento Actual

| Comunicación | Patrón Actual | Estado |
|-------------|---------------|--------|
| QuickAddFab → App | `emit('transaction-created')` | 🟡 Funcional pero acoplado |
| BudgetPanel → Resumen | `emit('open-detail')` | ✅ OK (padre-hijo directo) |
| CalendarBottomSheet → Resumen | `emit('showObligationInfo')` | ✅ OK |
| Resize listener | `window.addEventListener` | ✅ OK (nativo, no event bus) |

### Corrección Propuesta

**Crear store compartido para refresh signals:**

```javascript
// frontend/src/stores/refresh.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useRefreshStore = defineStore('refresh', () => {
  const transactionCreated = ref(0)
  const goalCreated = ref(0)
  const debtUpdated = ref(0)

  function notifyTransaction() { transactionCreated.value++ }
  function notifyGoal() { goalCreated.value++ }
  function notifyDebt() { debtUpdated.value++ }

  return { transactionCreated, goalCreated, debtUpdated, notifyTransaction, notifyGoal, notifyDebt }
})
```

### Qué Puede Fallar

| Riesgo | Mitigación |
|--------|------------|
| Watcher no detecta cambios | Usar `watch()` con `{ deep: true }` o incrementar counter |
| Memory leak por watchers | Limpiar watchers en `onBeforeUnmount` |
| Store se crea múltiples instancias | Pinia garantiza singleton por store id |
| Performance con muchos watchers | Limitar a signals necesarios, no abusar |

### Testing

```javascript
// frontend/src/stores/__tests__/refresh.test.js
import { setActivePinia, createPinia } from 'pinia'
import { useRefreshStore } from '../refresh'

beforeEach(() => { setActivePinia(createPinia()) })

test('notifyTransaction increments counter', () => {
  const store = useRefreshStore()
  expect(store.transactionCreated).toBe(0)
  store.notifyTransaction()
  expect(store.transactionCreated).toBe(1)
})
```

---

## Resumen de Prioridades

| Issue | Tipo | Prioridad | Esfuerzo | Riesgo |
|-------|------|-----------|----------|--------|
| ISSUE-001 | Security | P1 🔴 | 2-4 horas | Medio (rate limit puede bloquear usuarios legítimos) |
| ISSUE-002 | Refactor | P2 🟡 | 3-5 horas | Bajo (solo reorganización de imports) |
| ISSUE-003 | Refactor | P2 🟡 | 4-6 horas | Bajo (extracción de componentes) |
| ISSUE-004 | Testing | P2 🟡 | 8-12 horas | Bajo (solo agregar tests) |
| ISSUE-005 | Maintenance | P3 🟢 | 2-3 horas | Bajo (ya parcialmente resuelto) |

**Esfuerzo total estimado:** 19-30 horas
