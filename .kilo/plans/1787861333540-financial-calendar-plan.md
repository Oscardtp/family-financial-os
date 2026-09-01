# Plan: Family Financial Calendar (Calendario Financiero)

## Contexto

El usuario propone convertir **Family Financial OS** en un "sistema operativo financiero" centrado en la pregunta *"¿qué tengo que pagar, cuánto, cuándo y qué pasa si no lo hago?"*. El concepto abarca 25 secciones: calendario visual tipo Google Calendar, obligaciones con 3 fechas (corte / recomendada / límite), eventos por intención con colores de estado, detalle accionable, centro de notificaciones accionables, proyección de dinero (7/30 días, efectivo necesario, presupuesto comprometido), coach de aprendizaje de patrones, colaboración familiar y el flujo "Preparar el mes".

### Estado actual del código (verificado)
- **`FinancialEventModel` ya existe** (`backend/app/infrastructure/models/models.py:224`) con `due_date`, `recommended_date`, `cutoff_date`, `status`, `account_id`, `responsible_member_id`, `is_recurrent`, `recurrence_group_id`, `reminder_days_before`, `confirmed`, `paid_at/paid_by/paid_amount`, `source`, `source_id`, `type`, `notes`, `currency`. Alineado con puntos 2–3, 23. **Faltan**: `obligation_id`, `visibility` (confirmado/programado/estimado), `confidence` (0–100), `payment_method` (para efectivo), y **no hay API** (ni router ni schemas de events).
- **Frontend `Calendar.vue` es un placeholder**; el router ya tiene `/calendar`.
- **`NotificationModel` existe** pero solo como inbox pasivo (`notifications.py`): sin motor de generación, sin accionabilidad, sin vínculo a eventos.
- **`RecurringPayment`** (model+service+router) y **`Debt`** ya existen → son las fuentes naturales que deben alimentar eventos.
- Engines disponibles para reusar: `CashFlowEngine`, `BudgetEngine`, `ProjectionEngine` (`backend/app/financial_engine/`).
- Convenciones: Pydantic v2 con `Decimal` para Money (`schemas.py`); repos devuelven `dict`; auth vía `require_viewer`/`require_member`/`require_owner` (`deps.py`); TDD estricto; migraciones Alembic forward-only con columnas nullable/default.

### Decisiones del usuario (bloqueadas)
1. **Alcance**: por fases, visión completa.
2. **Modelo**: entidad **`FinancialObligation`** (plantilla) que **genera** `FinancialEvent`s (punto 24).
3. **UI**: grilla propia inspirada en Google Calendar (replicar su lenguaje visual, estilizado a lo financiero). Referencia de diseño validada vía websearch: month grid con celdas de día separadas/redondeadas (Material 3 Expressive), "today pill", event chips como barras de color (no puntos), FAB `+`, color labels por intención, modo claro/oscuro. (El app live de calendar.google.com requiere auth; se replica el lenguaje documentado, no se scrapea sesión.)
4. **Coach**: incluir MVP de detección de patrones (puntos 12–16, 22).

---

## Regla de diseño transversal
**"El usuario registra una vez; Family Financial OS conecta ese dato con todo lo demás."** Deuda/Recurrente/Transacción/Meta → deben aparecer en Calendario + Notificaciones + Proyección + Presupuesto sin re-escribir la info. Esto se logra mediante `FinancialObligation` como plantilla única y servicios de sync.

**Integridad de datos / copy honesto (crítico)**:
- Nunca afirmar mora/intereses solo por conocer una fecha. El campo `consequence_note` solo se muestra/persiste si viene de los términos de la obligación o lo introduce el usuario.
- Notificaciones tipo *"tienes $X disponibles"* solo si hay datos reales de cuentas.
- `confidence` (0–100) y `visibility` (confirmed/scheduled/estimated) evitan presentar predicciones del coach como hechos.

---

## Fase 0 — Fundaciones y modelo de datos

### Migración Alembic (nueva: `alembic/versions/xxxx_financial_obligations.py`)
- Nueva tabla **`financial_obligations`** (`backend/app/infrastructure/models/models.py`):
  - `id`, `household_id` (FK, index), `source` (USER/SYSTEM/IMPORTED/LEARNED), `source_id` (FK opcional a debt/recurring/goal), `name`, `type` (expense/payment/debt/income/goal), `amount` Numeric(15,2), `currency`, `frequency` (monthly/weekly/biweekly/yearly), `anchor_day` (int, día del mes del vencimiento), `recommended_offset_days` (int, default 5), `cutoff_offset_days` (int, nullable), `reminder_days_before` (int, default 3), `account_id` (FK nullable), `category_id` (FK nullable), `responsible_member_id` (FK nullable), `is_active` (bool default true), `confidence` (int default 100), `notes` Text, `created_at`, `updated_at`.
- Tabla **`financial_events`** — añadir columnas (todas nullable + default, según regla AGENTS):
  - `obligation_id` FK → financial_obligations.id (nullable)
  - `visibility` String(12) default `'confirmed'` (confirmed/scheduled/estimated)
  - `confidence` Integer default 100
  - `payment_method` String(12) nullable (card/cash/transfer) — para proyección de efectivo (punto 21)
  - `consequence_note` Text nullable — solo si el usuario/términos lo proveen
- Repo `financial_event_repository._to_dict`: devolver `amount`/`paid_amount` como **`Decimal`** (no float) para consistencia con `Money`/Pydantic; actualizar tests afectados.

### Dominio (`backend/app/domain/entities/entities.py`)
- Nuevo dataclass `FinancialObligation`.
- Extender `FinancialEvent` con `obligation_id`, `visibility`, `confidence`, `payment_method`, `consequence_note`.

### Repositorios
- Nuevo `application/interfaces/obligation_repository.py` + `infrastructure/repositories/obligation_repository.py` (CRUD + `get_active_by_household`, `get_by_source`).
- Extender `FinancialEventRepository`: `get_upcoming(household_id, as_of, days)`, `list_by_visibility`, `create_from_obligation(obligation, due_date, recommended_date, cutoff_date)`.

### Schemas (`presentation/schemas/schemas.py`)
- `ObligationCreate/Update/Response` (Pydantic v2, `Decimal` para money, `UUID`).
- Extender `EventCreate/Update/Response` con nuevos campos.

---

## Fase 1 — Núcleo del calendario (vertical slice usable)
**Backend**
- Nuevo router `presentation/v1/events.py` (prefix `/events`):
  - `GET /events?year=&month=` → eventos del mes (grilla).
  - `GET /events?from=&to=` → rango (para proyecciones 7/30 días).
  - `GET /events/{id}`, `POST /events` (source=USER), `PUT /events/{id}`, `DELETE /events/{id}`.
  - `POST /events/{id}/pay` → `status=paid`, `paid_at`, `paid_by=current_user`; crea **notificación familiar** (punto 18) para los otros miembros del household (NotificationModel). `require_member`.
  - `POST /events/{id}/unpay` → revierte.
- Nuevo router `presentation/v1/obligations.py` (prefix `/obligations`):
  - `POST /obligations` → crea obligación y **genera eventos** para los próximos N meses (default 12) vía `ObligationService`.
  - `GET /obligations`, `PUT /obligations/{id}`, `DELETE /obligations/{id}`.
- `application/services/obligation_service.py`: calcula `due_date`/`recommended_date`/`cutoff_date` a partir de `anchor_day` + offsets; crea eventos con `visibility` según source (USER→confirmed, LEARNED→estimated).
- Registrar routers en `main.py`.

**Frontend**
- Reemplazar `frontend/src/views/Calendar.vue` (placeholder) por grilla **month view** propia, inspirada en Google Calendar:
  - Header: `<mes año>` + nav `‹ ›` + FAB `＋` (lucide). Celda "today" con pill resaltado. Celdas de día redondeadas/separadas.
  - Event chips como barras de color por **intención/estado** (punto 5): 🟢 normal/ok, 🟡 próximo (dentro de ventana de recordatorio), 🔴 vencido/hoy/requiere atención, 🔵 ingreso, 🟣 meta. Mapeo en componente (no por categoría).
  - Tap en evento → **bottom sheet / panel de detalle** (punto 6): título, monto (COP vía `useCurrency`), fecha límite, estado, cuenta, recordatorio, responsable, `consequence_note` (solo si existe), botón **"Marcar como pagado"**, enlace **"Ver obligación →"**.
  - Empty state y loading state (SkeletonLoader ya existe).
- `frontend/src/services/events.js` (axios wrapper) + `frontend/src/stores/useCalendar.js` (Pinia) + `useObligations.js`.
- Mobile-first (coherente con `BottomTabBar`).

**Tests (TDD)**: `tests/test_events_service.py`, `tests/test_events_api.py`, `tests/test_obligation_service.py` (fixtures de household). Cobertura ≥80% en paths críticos.

---

## Fase 2 — Integración de fuentes ("registra una vez")
- `application/services/obligation_sync_service.py`: al crear/actualizar **Debt** (`debt_service`) y **RecurringPayment** (`recurring_payment_service`), crea/actualiza la `FinancialObligation` correspondiente (source=SYSTEM, `source_id`) y regenera eventos futuros. Enganchar desde los routers de `debts.py` y `recurring_payments.py` (o desde los services) tras `db.commit()`.
- Deudas: cada cuota vence → evento `type=debt` con `anchor_day=debt.due_day`.
- `payment_method` de eventos derivado del `type` de la cuenta (cuenta `cash` → `cash`) para la proyección de efectivo.
- Decision de no duplicar plantillas: `RecurringPayment` y `Debt` se reflejan en `FinancialObligation` vía `source_id`; `ObligationSyncService` es la única fuente de eventos generados. (Opcional, fuera de alcance: consolidar RecurringPayment en Obligation más adelante.)

---

## Fase 3 — Motor de notificaciones + Centro de notificaciones
- `application/services/notification_service.py` (+ `financial_engine` si aplica): `get_upcoming(household_id, as_of)` calcula notificaciones **accionables** desde eventos pendientes con niveles (punto 9): 7d `Próximamente`, 3d `Se acerca`, 1d `Mañana`, 0d `Hoy`, post `Pendiente`. Cada item incluye payload de acción (`event_id`, monto, fecha límite).
  - Solo incluir frase *"tienes $X disponibles"* si se consultan cuentas reales.
- `GET /notifications/upcoming` (nuevo en `notifications.py`) devuelve items estructurados + agrupación HOY / ESTA SEMANA.
- Persistir notificaciones familiares en `POST /events/{id}/pay` (punto 18): NotificationModel para miembros distintos al que pagó.
- **Frontend**: extender `NotificationBell.vue` para mostrar notificaciones accionables con botón **"Registrar pago"** (llama `POST /events/{id}/pay`); filtros Todos | Pagos | Deudas | Presupuesto | Metas (punto 17).

---

## Fase 4 — Proyección de dinero ("¿tengo dinero para los próximos pagos?")
- `application/services/calendar_service.py` → `availability(household_id, days: 7|30)`:
  - `available` = suma de balances de cuentas activas (`account_repository`).
  - `upcoming_payments` = suma de montos de eventos pendientes en ventana.
  - `projected_available` = available − upcoming_payments (punto 10).
  - `cash_needed` = suma de eventos `payment_method=cash` en ventana − balance de cuentas cash; con etiqueta **"[No verificado] proyección"** (punto 21).
  - `budget_committed` = suma de eventos cuyo `category_id` tiene presupuesto del mes vs total presupuestado (punto 20), reusando `BudgetEngine`.
  - Ingresos previstos (eventos `type=income`) y gastos presupuestados para ventana 30 días (punto 11).
- `GET /events/availability?days=7|30`.
- **Frontend**: panel resumen en `Calendar.vue` (7/30 días) arriba/abajo de la grilla, con copy honesto y badge de proyección.

---

## Fase 5 — Coach de aprendizaje (MVP de patrones)
- `application/services/learning_service.py` → `detect_patterns(household_id)`:
  - Escanea `Transaction` (y events) buscando repeticiones (mismo título/mercante, día ±2, monto ±10%) ≥ 3 ocurrencias → sugiere `Obligation` (source=LEARNED, `visibility=estimated`, `confidence` calculada).
  - Devuelve sugerencias con `confidence` y payload para crear obligación. **Nunca crea automáticamente**: propone (puntos 12–16).
- `GET /coach/suggestions`.
- **Frontend**: tarjeta de sugerencia en calendario/notificaciones; al aceptar → `POST /obligations` (source=LEARNED) + genera eventos `visibility=estimated`.

---

## Fase 6 — "Preparar el mes"
- `GET /month/prepare` (`calendar_service`): resumen de inicio de mes — conteo/monto de pagos programados, ingresos previstos, metas, deudas nuevas detectadas (punto 25).
- **Frontend**: flujo "Preparar mi mes →" (wizard de 5 preguntas: pagos nuevos, cambios de valor, nuevas deudas, ahorro, gastos especiales) reusando stores existentes.

---

## Validación
- **Backend**: `pytest` (TDD) en services + API con fixtures de household/accounts/events. `Money` siempre `Decimal`. `python -m pytest backend/tests` debe pasar; lint/typecheck del proyecto.
- **Frontend**: `vitest` en componentes de calendario (grilla, detalle, mark-as-paid) y store. `npm run test` / `npm run build`.
- **Manual (E2E smoke)**: seed household → crear Deuda + Recurrente → abrir `/calendar` → verificar eventos renderizados con colores de estado → "Marcar como pagado" → estado flip + notificación familiar generada → panel de disponibilidad 7/30 días correcto → aceptar sugerencia del coach y ver evento `estimated`.
- **Regla UX/CX**: cada mensaje/empty/loading pasa 3-Second Test, WhatsApp Test, Bank Test (friendly-fintech-voice).

## Riesgos / preguntas abiertas
- **Sin scheduler/cron** en la app: notificaciones se generan on-demand (MVP). Si se requiere push real, fase posterior con APScheduler/Celery.
- **Duplicación RecurringPayment vs Obligation**: resuelta vía `ObligationSyncService` (source=SYSTEM). Consolidación opcional a futuro.
- **`confidence` vs `confirmed`**: se añade `confidence` (0–100) y `visibility`; se mantiene `confirmed` por compatibilidad (deprecación suave).
- **Formato COP**: serialización en backend con `Decimal`; formato visual en frontend con `useCurrency.js` (ya existe).
- **Multi-tenant**: todo query filtra por `household_id`; auth por rol (viewer/owner/member).
