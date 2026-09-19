# Architectural Design Review — Backend Family Financial OS

> **Skill:** software-design-architect
> **Fecha:** 2026-09-17
> **Baseline:** Post-FASE 4, 147 tests pasando

---

## Executive Summary

El backend sigue **Clean Architecture** con separacion clara en 4 capas. El dominio esta bien modelado con Value Objects inmutables (`Money`, `InterestRate`). El **Financial Engine** es la capa mas solida: 12 motores de calculo puros, deterministicos y testeables.

**Hallazgo principal:** La arquitectura es correcta y proporcional al problema. No hay sobreingenieria significativa. Los problemas identificados son de **deuda tecnica acumulada**, no de diseno fundamental.

| Criterio | Score |
|----------|-------|
| Separacion de responsabilidades | 8/10 |
| Bajo acoplamiento | 7/10 |
| Cohesion | 7/10 |
| Testabilidad | 6/10 |
| Mantenibilidad | 7/10 |
| Seguridad | 5/10 |
| Extensibilidad | 7/10 |
| **Overall** | **6.7/10** |

---

## Current Architecture

```
+-----------------------------------------------------------+
|                   PRESENTATION (HTTP)                      |
|  Routers FastAPI + Schemas Pydantic + DI (deps.py)        |
|  19 routers, ~50 schemas, error_handlers.py               |
+-----------------------------------------------------------+
|                 APPLICATION (Use Cases)                    |
|  Services + Repository Interfaces (Ports)                 |
|  15 services, 18 interfaces                               |
+-----------------------------------------------------------+
|               INFRASTRUCTURE (Persistence)                 |
|  SQLAlchemy Models + Repository Implementations            |
|  19 models, 20 repos                                     |
+-----------------------------------------------------------+
|                    DOMAIN (Core)                           |
|  Value Objects + Entities + Exceptions                    |
|  Money, InterestRate, 14 entities, 3 exceptions           |
+-----------------------------------------------------------+
|              FINANCIAL ENGINE (Computation)                |
|  Pure calculation engines                                 |
|  12 engines: amortization, debt, savings, projections     |
+-----------------------------------------------------------+
```

**Dependency Flow:**
```
Presentation -> Application -> Domain <- Infrastructure
                                    ^
                            Financial Engine
```

---

## Problems Identified

### PROBLEM-001: Services Importan Concrete Repositories Directamente

**Principle:** Dependency Inversion Principle (DIP)
**Severity:** High
**Impact:** Los services crean repositorios concretos en `__init__`, acoplándose a SQLAlchemy.

```python
# ACTUAL (dashboard_service.py, line 20-28)
class DashboardService:
    def __init__(self, db: AsyncSession):
        self.account_repo = SQLAlchemyAccountRepository(db)  # Concrete
        self.tx_repo = SQLAlchemyTransactionRepository(db)   # Concrete
        self.debt_repo = SQLAlchemyDebtRepository(db)        # Concrete
        # 8 repos concretos mas
```

**Consecuencia:**
- Imposible testear service sin DB real
- Cambiar de SQLAlchemy a otro ORM requiere modificar cada service
- La interface `AccountRepository` existe pero no se usa como tipo

**Recommendation:**
```python
# PROPUESTO
class DashboardService:
    def __init__(
        self,
        account_repo: AccountRepository,      # Interface
        tx_repo: TransactionRepository,       # Interface
        debt_repo: DebtRepository,            # Interface
    ):
        self.account_repo = account_repo
```

---

### PROBLEM-002: Repositories Retornan `dict` en Lugar de Entidades de Dominio

**Principle:** Anemic Domain Model vs Rich Domain Model
**Severity:** Medium
**Impact:** Las entidades de dominio existen pero no se usan. Los repos retornan `dict`.

```python
# ACTUAL (account_repository.py, line 94-105)
@staticmethod
def _to_dict(model: AccountModel) -> dict:
    return {
        "id": model.id,
        "household_id": model.household_id,
        "name": model.name,
        "balance": Decimal(str(model.balance)),
    }
```

**Consecuencia:**
- Entidades de dominio son dataclasses sin comportamiento (Anemic Domain Model)
- Services acceden a datos via string keys (`debt["current_balance"]`)
- Sin compilacion de errores por typos en keys
- Logica de validacion dispersa en services

**Recommendation:** Los repos deben retornar entidades de dominio, no dicts. Los repos ya tienen el patron `_to_dict` - cambiarlo a `_to_domain` que retorne `Account(...)` en lugar de `{"id": ...}`.

---

### PROBLEM-003: `schemas.py` Monolitico (672 lineas)

**Principle:** Single Responsibility Principle (SRP)
**Severity:** Medium
**Impact:** Dificulta mantenimiento, genera merge conflicts.

**Recommendation:** Dividir por dominio (documentado en ISSUE-002).

---

### PROBLEM-004: `dashboard_service.py` Acumula Responsabilidades

**Principle:** Single Responsibility Principle (SRP)
**Severity:** Medium
**Impact:** 240 lineas, 8 repos, logica de budget + alert + savings + net worth.

```python
class DashboardService:
    # 8 repos inyectados
    # get_summary() ejecuta 10+ queries
    # _build_budget_status() duplica logica de BudgetEngine
    # _build_financial_alert() tiene logica de negocio
```

**Recommendation:** Dividir en:
- `DashboardQueryService` (lectura)
- `BudgetAdvisorService` (logica de budget/alertas)
- `NetWorthService` (calculode patrimonio)

---

### PROBLEM-005: DebtService Crea Services Internos (Service Locator)

**Principle:** Single Responsibility / Law of Demeter
**Severity:** Medium
**Impact:** DebtService instancia CalendarDebtSyncService internamente.

```python
# ACTUAL (debt_service.py, line 99-102)
from app.application.services.calendar_debt_sync_service import CalendarDebtSyncService
sync = CalendarDebtSyncService(self.db)
await sync.on_debt_payment(debt_id, payment_date, payment_amount, ...)
```

**Consecuencia:**
- Acoplamiento oculto entre services
- Duplicacion de instanciacion (`self.db` se pasa a otro service)
- Dificulta testing de DebtService aisladamente

**Recommendation:** Usar eventos de dominio o inyectar el sync service como dependencia.

---

### PROBLEM-006: Sin Rate Limiting en Auth

**Principle:** Security
**Severity:** High
**Impact:** Vulnerabilidad a brute-force.

**Recommendation:** slowapi (documentado en ISSUE-001).

---

### PROBLEM-007: Entities son Anemic (Sin Comportamiento)

**Principle:** Domain-Driven Design
**Severity:** Medium
**Impact:** 14 entidades dataclass sin metodos de negocio.

```python
# ACTUAL
@dataclass
class Debt:
    id: uuid.UUID
    current_balance: Money
    minimum_payment: Money
    interest_rate: Decimal
    status: str
    # Sin metodos: calculate_payment(), is_overdue(), etc.
```

**Consecuencia:**
- Toda logica de negocio vive en services
- Entidades son solo contenedores de datos
- Dificulta reutilizar comportamiento

**Recommendation:** Agregar comportamiento a las entidades donde sea natural:

```python
@dataclass
class Debt:
    # ... campos ...
    def is_overdue(self, today: date) -> bool:
        return self.due_day < today.day and self.status == "active"

    def calculate_interest(self, monthly_rate: Decimal) -> Money:
        return Money(self.current_balance.amount * monthly_rate, self.current_balance.currency)
```

---

### PROBLEM-008: `RateEngine` Usa `lru_cache` en Metodo Estatico

**Principle:** Immutability / Testability
**Severity:** Low
**Impact:** Cache global puede causar efectos secundarios en tests.

```python
class RateEngine:
    @staticmethod
    @functools.lru_cache(maxsize=128)
    def to_monthly_rate(rate: InterestRate) -> Decimal:
        ...
```

**Consecuencia:**
- Tests pueden interferirse entre si por cache compartido
- InterestRate es frozen dataclass (hashable) - funciona, pero es un riesgo

**Recommendation:** OK para produccion. Agregar `RateEngine.to_monthly_rate.cache_clear()` en `conftest.py` si hay tests con diferentes rates.

---

### PROBLEM-009: `get_db()` No Confirma Automaticamente

**Principle:** Transaction Management
**Severity:** Medium
**Impact:** El patron actual depende de que cada handler haga `await db.commit()` explicito.

```python
# ACTUAL (database.py, line 34-45)
async def get_db():
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**Consecuencia:**
- Algunos handlers hacen `commit()` explicito (auth.py line 15)
- Otros dependen del `expire_on_commit=False` y no commitean
- Riesgo de datos no persistidos silenciosamente

**Recommendation:** Agregar commit automatico post-yield:

```python
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except HTTPException:
            await session.rollback()
            raise
        except Exception:
            await session.rollback()
            raise
```

---

### PROBLEM-010: Test Coverage Baja en Services

**Principle:** TDD / Testability
**Severity:** Medium
**Impact:** ~60% coverage estimado. Services criticos sin tests unitarios.

**Recommendation:** Documentado en ISSUE-004.

---

## Financial Engine — Fortalezas

El Financial Engine es la **mejor capa** del backend:

```python
# rate_engine.py — 19 lineas, puro, testeable
class RateEngine:
    @staticmethod
    @functools.lru_cache(maxsize=128)
    def to_monthly_rate(rate: InterestRate) -> Decimal:
        # Conversion EA -> Monthly, EM -> Monthly, NOMINAL -> Monthly, DAILY -> Monthly
```

**Fortalezas:**
- Funciones puras sin side effects
- Deterministicas (mismo input = mismo output)
- Decimal precision (sin float)
- Separadas de la logica de aplicacion
- Facilmente testeables

**Score del Financial Engine: 9/10**

---

## Value Objects — Fortalezas

```python
# money.py — VO inmutable, seguro, con validacion
class Money:
    def __init__(self, amount: Decimal | int | float | str, currency: str = "COP"):
        self.amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.currency = currency
```

**Fortalezas:**
- Cuantizacion a 2 decimales siempre
- Chequeo de moneda en operaciones
- `__hash__` para uso en sets/dicts
- `from_cents()` y `zero()` factory methods
- Immutabilidad conceptual (no frozen, pero convention)

**Score de Value Objects: 8/10**

---

## Trade-offs

### Advantages de la Arquitectura Actual

- Clean Architecture bien entendida y aplicada
- Financial Engine separado y puro
- Multi-tenant por `household_id` consistente
- Error handlers amigables en espanol
- Alembic para migraciones versionadas
- Tests con DB aislada

### Costs

- DIP no completamente aplicado (services -> concrete repos)
- Entidades anemicas (sin comportamiento)
- schemas.py monolitico
- Coverage bajo en services

### Risks

- Sin rate limiting (brute-force vulnerable)
- Sin refresh token blacklist
- SECRET_KEY default en desarrollo
- `commit()` explicito inconsistente

---

## Implementation Plan (Priorizado)

### FASE 5: Seguridad + DIP (P1)

1. Agregar `slowapi` para rate limiting en auth
2. Inyectar repos via interfaces en services (DIP)
3. Agregar commit automatico en `get_db()`
4. Tests para auth rate limiting

### FASE 6: Domain Model + Refactor (P2)

1. Dividir `schemas.py` por dominio
2. Agregar comportamiento a entidades (Debt, SavingsGoal)
3. Repos retornar entidades en lugar de dicts
4. Dividir `DashboardService`

### FASE 7: Testing + Coverage (P2)

1. Tests unitarios para `DebtService`, `SavingsService`, `EventService`
2. Tests de integracion para `DashboardService`
3. Coverage minimo 80% en services
4. Tests para financial engine edge cases

### FASE 8: Frontend Refactor (P3)

1. Descomponer `Resumen.vue`
2. Migrar event bus a Pinia stores
3. Tests para componentes criticos

---

## Validation Checklist

- [x] Clean Architecture separada
- [x] Value Objects inmutables
- [x] Financial Engine puro y testeable
- [x] Multi-tenant consistente
- [x] Error handling friendly
- [x] Alembic migrations
- [x] Tests con DB aislada
- [ ] DIP completamente aplicado
- [ ] Entidades con comportamiento
- [ ] Rate limiting
- [ ] Coverage > 80%
- [ ] schemas.py dividido

---

## Self-Critique

> Estoy sobreingenierizando?
> **No.** Los problemas son reales y priorizados.

> Existe una solucion mas simple?
> **Si.** Algunos fixes son incrementales (DIP paso a paso).

> Estoy aplicando un patron solo porque lo conozco?
> **No.** DIP y SRP se justifican por el acoplamiento actual.

> La solucion es testeable?
> **Si.** DIP + repos como interfaces = tests con mocks faciles.

> Es reversible?
> **Si.** Cambios incrementales, no reescrituras.

---

> **La mejor arquitectura no es la mas sofisticada. Es la que resuelve el problema actual con la menor complejidad necesaria y permite evolucionar el sistema sin generar deuda innecesaria.**
