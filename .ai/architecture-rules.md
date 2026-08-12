# Architecture Rules

Arquitectura **Modular Monolith** (Clean Architecture): un único despliegue, capas bien aisladas
por responsabilidad. No se salta de capa (p. ej. API → repository). Las reglas son *forzables*
por tests pero NO se impone con tooling extra todavía (TDD lo garantiza).

## Capas (ordago → adentro, flechas de dependencia hacia adentro)

```
src/
 ├ api/            — Entrada: HTTP (Next Route Handlers / Controllers) + Zod DTOs
 ├ config/         — Variables de entorno y factoría de inyección (DI root)
 ├ modules/        — Bounded Contexts del dominio (finanzas)
 │   ├ accounts/    (entidad Account)
 │   ├ transactions/(entidades + reglas: Money, Double-Entry, Transfer/Expense)
 │   ├ budgets/
 │   ├ goals/
 │   └ net-worth/   (Patrimonio = assets - liabilities)
 ├ shared/         — Kernel: Money (Dinero.js), errors, Value Objects genéricos
 ├ infrastructure/ — Adaptadores a externos: database/ (Prisma), auth/ (Supabase),
 │                   repositories/ (implementaciones de interfaces de dominio)
 └ lib/            — Utilities, date-fns, logging
```

`@/` mapea a `src/`. `@api/*`, `@modules/*`, `@infra/*`, `@shared/*` son aliases de ruta
TypeScript configurados en `tsconfig.json` (paths) + Next alias (`moduleNameRenderer`). Hasta que
no exista el código, las reglas de ruta se definen aquí y se aplicarán al crear los módulos.

## Rules

**R1. Clean Architecture por bounded context.** Cada módulo de `modules/` es autocontenida:
sus *use-cases*, *entities*, *value objects*, *repository interfaces* y *DTOs*. No importa de
otros contextos; si necesita datos de otro, usa su puerta de enlace (repository o endpoint público).

**R2. Inversión de dependencias.** El dominio no depende de infraestructura. Los repositorios
son **interfaces en el dominio**; las **implementaciones** viven en `infrastructure/repositories`
(Prisma). Se inyectan en las *use-cases* (inyección por constructor).

**R3. Puerto único de entrada: API → Controllers.** Todo request HTTP pasa por `api/` (Controllers),
se valida con Zod, se traduce a un *use-case*, y devuelve el resultado. El Controller es el único
que conoce a los *use-cases* y a los repositorios concretos.

**R4. Transacciones monetarias son atómicas.** Cualquier operación que mueva dinero (transferencia
inter-cuentas, registrar una transacción con su contra-movimiento) se ejecuta dentro de una
transacción de base de datos (`$transaction`). Si falla, nada se persiste (doble entrada o nada).

**R5. Doble entrada contable (invariante de dominio).** Cada movimiento de afecta a **dos**
asientos opuestos en el libro mayor: débito y crédito. La balanza cuadra: `Σ débitos = Σ créditos`.
El engine verifica esto antes de confirmar cualquier lote de transacciones. Se registra
`transaction_id` (UUID v7) y `line_id`.

**R6. Dinero en unidades menores (`bigint`).** Todo importe monetario se almacena y opera en
unidades menores (centavos) usando `bigint` + Dinero.js v2. Nunca `float`/`number` para cálculos
financieros. Conversión a float solo para presentación (no para cálculo).

**R7. Transferencia ≠ Gasto.** Una transferencia entre cuentas propias NO es un gasto; es
una reubicación de patrimonio (debito en una cuenta, crédito en otra; el total no cambia).
Un *gasto* reduce el patrimonio. La categoría de una transacción es *tipo*: Income, Expense,
Transfer, Adjustment. El motor las clasifica y las suma/resta correctamente en el P&L vs el
Balance.

**R8. Estado derivado, no guardado.** Saldo de cuentas, balance, patrimonio neto, presupuestos
gastados — se **derivan** recalculando transacciones. Se puede materializar un *snapshot*
periódico por rendimiento, pero la fuente de la verdad es la tabla de transacciones + asientos.
Ningún saldo se escribe a mano.

**R9. Inmutabilidad de transacciones.** Las transacciones son *append-only*. Si una operación
es incorrecta, se crea una transacción de corrección (con referencia a la original); nunca se
borran/editan las transacciones reales (auditable, ideal para conciliación bancaria).

**R10. Determinismo.** Las fechas/hora se almacenan en UTC. Cálculos de intereses, depreciación
y presupuestos son deterministas (seed fija, reglas explícitas) para que un mismo input produzca
el mismo output (reproducible para tests y auditoría).

## Reglas de capa de infraestructura

- **Database**: `infrastructure/database/prisma.ts` es el único punto de creación del cliente
  Prisma (`@prisma/client`). Repositorios Prisma usan `PrismaClient` singleton.
- **Auth**: `infrastructure/auth/` expone un `AuthService` (interface en dominio) + implementación
  Supabase. El *user id* del auth se pasa al dominio como `UserId` (branded). Nunca se filtra ni
  se loguea.
- **HTTP**: los *Controllers* son *Route Handlers* de Next 16 (`app/api/.../route.ts`). No usan
  `getServerSideProps`; la UI futura consumirá la API.

## Convenciones de naming

- Tablas: `snake_case` (PostgreSQL).
- Columnas: `snake_case`.
- Model Prisma: `PascalCase` (ej. `FinancialAccount`).
- DTOs/Requests: `camelCase` (JSON).
- Eventos de dominio / use-cases: verbos (`RegisterTransaction`, `CreateBudget`).
- IDs: `UUID v7` (orden cronológico, sin revelar secuencia).
