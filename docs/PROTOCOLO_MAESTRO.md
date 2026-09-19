# PROTOCOLO MAESTRO DE RECUPERACIÓN, DESARROLLO Y QA

## Family Financial OS

## 1. ROL DEL AGENTE

Actúas como **Agente de Implementación y Verificación Técnica** de Family Financial OS.

Tu responsabilidad no es solamente escribir código.

Debes:

1. Analizar antes de modificar.
2. Proteger la información financiera existente.
3. Mantener la persistencia real de los datos.
4. Mantener aislamiento entre hogares (`household_id`).
5. Mantener consistencia matemática.
6. Evitar duplicación de lógica financiera.
7. Ejecutar pruebas después de cada cambio relevante.
8. Verificar migraciones antes de aplicarlas.
9. Verificar que el frontend nunca sea la fuente de verdad financiera.
10. No declarar una tarea como terminada sin ejecutar el QA Gate correspondiente.

### Regla fundamental

**"Código implementado" NO significa "funcionalidad terminada".**

Una funcionalidad solamente puede considerarse:

```text
READY
```

cuando haya pasado todos los controles aplicables.

Si algún control crítico falla:

```text
NOT READY
```

y debes detener el avance de nuevas funcionalidades relacionadas hasta resolverlo.

---

# 2. PRINCIPIO DE SEGURIDAD

La base de datos contiene información financiera.

Por lo tanto:

> La prioridad es preservar la integridad de los datos antes que avanzar rápidamente con funcionalidades.

Nunca debes sacrificar:

* datos históricos
* consistencia financiera
* aislamiento de hogares
* trazabilidad
* recuperación
* integridad referencial

para hacer que una prueba pase o para completar una funcionalidad.

---

# 3. ESTADO ACTUAL: RECUPERACIÓN DE BASE DE DATOS

Hasta completar esta fase debes considerar el proyecto en:

```text
DATABASE RECOVERY MODE
```

No desarrollar nuevas funcionalidades financieras mientras existan dudas sobre:

* esquema
* migraciones
* persistencia
* integridad
* recuperación
* seguridad
* datos importados

---

# 4. FASE 0 — CONGELAR CAMBIOS

Antes de modificar la base de datos:

### CHECKLIST

* [ ] No ejecutar `DROP DATABASE`.
* [ ] No ejecutar `DROP TABLE` sobre información existente.
* [ ] No ejecutar migraciones destructivas.
* [ ] No modificar datos históricos para solucionar tests.
* [ ] No borrar registros para resolver inconsistencias.
* [ ] No ejecutar scripts de limpieza desconocidos.
* [ ] No importar Excel todavía.
* [ ] No ejecutar scripts de seed sobre una DB que contenga datos reales.
* [ ] Identificar todas las conexiones a PostgreSQL.
* [ ] Identificar qué `.env` utiliza cada entorno.
* [ ] Identificar qué base de datos utiliza cada proceso.
* [ ] Identificar si existen credenciales de producción disponibles para el agente.

### Si encuentras credenciales reales expuestas

NO simplemente las muevas a `.env`.

Debes recomendar:

```text
REVOKE / ROTATE CREDENTIAL
```

y documentarlo.

---

# 5. FASE 1 — NUEVA BASE DE DATOS

Crear una nueva base de datos limpia para desarrollo/recuperación.

Debe existir separación clara:

```text
DEV
STAGING
PROD
```

Como mínimo:

```text
AI AGENT → DEV
```

El agente NO debe disponer de credenciales de producción.

---

## CHECKLIST DE NUEVA DB

* [ ] PostgreSQL disponible.
* [ ] DB nueva creada.
* [ ] Usuario específico de aplicación.
* [ ] Usuario de migraciones separado cuando sea posible.
* [ ] Credenciales fuera del código.
* [ ] `.env` correctamente configurado.
* [ ] `DATABASE_URL` apunta a la nueva DB.
* [ ] Backend conecta correctamente.
* [ ] Frontend no contiene credenciales.
* [ ] La DB antigua permanece intacta.
* [ ] La DB antigua queda considerada como fuente histórica/recovery evidence.
* [ ] No se modificó la DB antigua.

---

# 6. FASE 2 — ESQUEMA LIMPIO

Construir el esquema exclusivamente mediante:

```text
SQLAlchemy Models
        ↓
Alembic
        ↓
PostgreSQL
```

No crear manualmente tablas que luego no estén representadas por migraciones.

---

## VALIDACIÓN OBLIGATORIA

Para cada entidad:

```text
Domain
 ↓
Schema
 ↓
Service
 ↓
Repository
 ↓
ORM Model
 ↓
Alembic Migration
 ↓
PostgreSQL
 ↓
API
 ↓
Frontend
 ↓
Tests
```

Debe existir coherencia.

---

# 7. ENTIDADES MÍNIMAS DEL MVP

Verificar la existencia y persistencia correcta de:

### Household

* id
* name
* base_currency
* timezone
* status
* created_at
* updated_at

### User

* id
* email
* password_hash
* name
* status
* created_at
* updated_at
* last_login_at

### HouseholdMember

* id
* household_id
* user_id
* role
* status
* joined_at

### Account

* id
* household_id
* name
* type
* institution
* currency
* opening_balance
* current_balance
* credit_limit
* status
* created_at
* updated_at

### Category

* id
* household_id
* name
* type
* parent_id
* is_active
* created_at
* updated_at

### Transaction

* id
* household_id
* account_id
* category_id
* type
* amount
* currency
* transaction_date
* description
* status
* created_by
* created_at
* updated_at

### Transfer

* id
* household_id
* from_account_id
* to_account_id
* amount
* currency
* transaction_date
* description
* created_by
* created_at

### Debt

* id
* household_id
* name
* type
* original_principal
* current_principal
* interest_rate
* interest_rate_type
* minimum_payment
* due_day
* start_date
* end_date
* account_id
* status
* created_at
* updated_at

### DebtPayment

* id
* household_id
* debt_id
* transaction_id
* payment_date
* amount
* principal_amount
* interest_amount
* fees_amount
* created_by
* created_at

### RecurringPayment

* id
* household_id
* name
* type
* amount
* frequency
* interval
* start_date
* next_due_date
* end_date
* account_id
* category_id
* status
* created_by
* created_at
* updated_at

### FinancialEvent

* id
* household_id
* source
* source_id
* type
* title
* amount
* due_date
* recommended_date
* cutoff_date
* account_id
* is_recurrent
* recurrence_group_id
* confirmed
* status
* created_at
* updated_at

### Budget

* id
* household_id
* category_id
* period
* year
* month
* planned_amount
* created_at
* updated_at

### SavingsGoal

* id
* household_id
* name
* target_amount
* current_amount
* start_date
* target_date
* contribution_frequency
* planned_contribution
* account_id
* status
* created_at
* updated_at

### GoalContribution

* id
* household_id
* goal_id
* transaction_id
* amount
* contribution_date
* created_by
* created_at

### Asset

* id
* household_id
* name
* type
* current_value
* currency
* valuation_date
* account_id
* status

### Liability

* id
* household_id
* name
* type
* current_value
* currency
* valuation_date
* status

### AuditLog

* id
* household_id
* user_id
* action
* entity_type
* entity_id
* details
* created_at

### ImportBatch

* id
* household_id
* source_file
* imported_at
* status
* records_detected
* records_imported
* records_rejected
* error_report

---

# 8. DINERO: REGLA ABSOLUTA

Toda lógica monetaria debe utilizar:

```python
Decimal
```

y PostgreSQL:

```text
NUMERIC
```

Nunca:

```python
float
```

para dinero.

Buscar:

```text
float(
-> float
Float
DOUBLE
```

en:

* domain
* services
* repositories
* schemas
* financial_engine
* API
* tests
* projections
* calendar
* dashboard

Si aparece float relacionado con dinero:

```text
NOT READY
```

hasta revisar su propósito.

---

# 9. TASAS DE INTERÉS

Todas las tasas deben pasar por:

```text
InterestRate
RateEngine
```

No duplicar conversiones.

No introducir fórmulas independientes como:

```text
rate / 1200
```

sin justificación explícita.

Validar:

* EA
* EM
* NOMINAL
* DAILY

y conversiones correspondientes.

---

# 10. DebtModel.notes

El problema:

```text
DebtModel.notes
```

no debe solucionarse únicamente agregando una columna.

Primero verificar:

```text
Domain Debt
 ↓
DebtModel
 ↓
Migration
 ↓
PostgreSQL
 ↓
Schema
 ↓
Service
 ↓
Repository
 ↓
API
 ↓
Frontend
 ↓
Tests
```

### CHECKLIST

* [ ] Campo definido donde corresponda.
* [ ] Tipo consistente.
* [ ] Nullable correctamente definido.
* [ ] Migration creada.
* [ ] Migration ejecutada sobre DEV.
* [ ] `alembic upgrade head` exitoso.
* [ ] DB contiene la columna.
* [ ] ORM puede leerla.
* [ ] ORM puede escribirla.
* [ ] API puede devolverla si corresponde.
* [ ] API puede recibirla si corresponde.
* [ ] Test de persistencia.
* [ ] Test después de reiniciar backend.

---

# 11. FASE 3 — DATABASE DOCTOR

Crear una herramienta:

```text
Database Doctor
```

Su función es diagnosticar, NO modificar automáticamente.

Debe poder verificar:

### Schema

* [ ] Alembic version
* [ ] tablas esperadas
* [ ] tablas inesperadas
* [ ] columnas faltantes
* [ ] columnas inesperadas
* [ ] tipos incorrectos
* [ ] índices
* [ ] foreign keys
* [ ] constraints
* [ ] unique constraints

### Integridad

* [ ] registros huérfanos
* [ ] foreign keys inválidas
* [ ] household_id faltante
* [ ] datos duplicados
* [ ] valores NULL inesperados
* [ ] montos inválidos
* [ ] saldos negativos no permitidos
* [ ] fechas inválidas

### Seguridad

* [ ] usuario DB
* [ ] permisos
* [ ] entorno
* [ ] credenciales
* [ ] conexión utilizada

### Resultado

Debe devolver:

```text
HEALTHY
DEGRADED
CRITICAL
```

y una lista:

```text
P0
P1
P2
P3
```

No modificar automáticamente la DB para solucionar problemas.

---

# 12. FASE 4 — BACKUP Y RECOVERY

No basta con crear un backup.

Hay que comprobar que puede restaurarse.

### CHECKLIST

* [ ] `pg_dump` configurado.
* [ ] Backup generado.
* [ ] Backup almacenado fuera del código.
* [ ] `backups/` incluido en `.gitignore`.
* [ ] Verificar si backups antiguos ya están trackeados por Git.
* [ ] Restaurar backup en una DB temporal.
* [ ] Ejecutar Database Doctor sobre DB restaurada.
* [ ] Ejecutar tests sobre DB restaurada.
* [ ] Comparar conteos de registros.
* [ ] Verificar datos financieros.
* [ ] Documentar procedimiento de recovery.

Resultado:

```text
BACKUP VERIFIED
```

solo si la restauración realmente funciona.

---

# 13. FASE 5 — SEGURIDAD

## Household isolation

Todo recurso financiero debe comprobar:

```text
resource.household_id == current_user.household_id
```

antes de devolver, modificar o eliminar información.

Probar explícitamente:

```text
User A → Household A
User B → Household B
```

User A no puede:

* leer datos B
* modificar datos B
* eliminar datos B
* acceder a IDs de B
* modificar deudas B
* modificar transacciones B
* acceder a eventos B

### Si falla:

```text
P0
NOT READY
```

---

# 14. AUTENTICACIÓN

Revisar:

* [ ] password hashing seguro
* [ ] expiración de access token
* [ ] refresh token
* [ ] revocación de refresh token
* [ ] logout
* [ ] invalidación
* [ ] rate limiting en login
* [ ] rate limiting en register
* [ ] CORS
* [ ] secrets fuera del código
* [ ] no credentials hardcoded

---

# 15. FASE 6 — MIGRACIÓN DEL EXCEL

El Excel es una fuente de datos histórica.

Nunca:

```text
Excel → INSERT directo → producción
```

Debe utilizar:

```text
Excel
 ↓
ImportBatch
 ↓
Staging
 ↓
Normalización
 ↓
Validación
 ↓
Revisión de ambiguos
 ↓
Aprobación
 ↓
Importación
 ↓
Reconciliación
 ↓
Invariantes
 ↓
Backup
```

### Prohibido

Inventar:

* categorías
* cuentas
* fechas
* saldos
* montos
* deudas
* relaciones

Si un registro es ambiguo:

```text
REQUIRES_REVIEW
```

No auto-clasificar.

---

# 16. RECONCILIACIÓN

Después de importar:

Comparar:

```text
Excel
vs
```

Debe existir:

* registros detectados
* registros importados
* rechazados
* ambiguos
* duplicados
* diferencias monetarias

El resultado debe ser explícito:

```text
MATCH
```

o:

```text
MISMATCH
```

Nunca ocultar diferencias.

---

# 17. INVARIANTES FINANCIEROS

Crear y mantener pruebas de invariantes.

## Balance

Verificar:

```text
Opening Balance
+ Income
- Expenses
+/- Transfers
=
Calculated Balance
```

según el modelo elegido.

---

## Transferencias

Una transferencia:

```text
Cuenta A - X
Cuenta B + X
```

No debe convertirse en:

```text
Income
```

ni:

```text
Expense
```

El patrimonio total no debe cambiar por una transferencia interna.

---

## Deudas

Verificar:

```text
saldo inicial
+ intereses
- principal pagado
=
saldo actual
```

según la convención financiera implementada.

Nunca:

* doble interés
* doble pago
* doble descuento
* pago sin registro
* registro de pago sin trazabilidad

---

## Tarjetas

Compra:

```text
Expense
```

Pago de tarjeta:

```text
Debt reduction
```

No contabilizar ambos como gasto.

---

## Recurrencias

Una recurrencia es:

```text
RULE
```

Un evento futuro es:

```text
FinancialEvent
```

Una operación realizada es:

```text
Transaction
```

No mezclar los tres conceptos.

---

# 18. PERSISTENCIA REAL

Toda entidad financiera debe superar esta prueba:

```text
CREATE
 ↓
SAVE DB
 ↓
READ DB
 ↓
RESTART BACKEND
 ↓
READ DB
 ↓
RESTART FRONTEND
 ↓
READ DB
```

El resultado debe permanecer.

No aceptar como prueba:

```text
Pinia
localStorage
sessionStorage
frontend state
mock data
hardcoded data
```

---

# 19. PRUEBA DE RECONSTRUCCIÓN

La prueba más importante:

> El estado financiero debe poder reconstruirse desde la base de datos sin depender del frontend.

Ejemplo:

```text
DB
 ↓
Transactions
 ↓
DebtPayments
 ↓
Transfers
 ↓
Accounts
 ↓
Goals
 ↓
FinancialEvents
 ↓
Financial Engine
 ↓
Financial State
```

Si al borrar/reiniciar el estado del frontend el sistema produce otro resultado:

```text
NOT READY
```

---

# 20. CALENDARIO

El calendario es una visualización temporal.

No debe convertirse en otra fuente de verdad.

Reglas:

```text
Debt → Mis Deudas
Recurring → regla recurrente
Transaction → movimiento real
FinancialEvent → evento futuro
GoalContribution → Metas
Calendar → visualización
```

El calendario no debe duplicar entidades financieras.

---

# 21. RESUMEN

El Resumen debe distinguir claramente:

```text
REAL
PROGRAMADO
PROYECTADO
```

Nunca presentar una proyección como dinero disponible real.

Validar conceptos como:

* dinero actual
* ingresos confirmados
* gastos confirmados
* compromisos próximos
* dinero comprometido
* dinero disponible
* proyección

---

# 22. REGLA DE UNA SOLA FUENTE DE VERDAD

Cada concepto financiero debe tener un propietario.

Ejemplo:

```text
Debt
→ Mis Deudas

Transaction
→ Movimientos

RecurringPayment
→ Recurrencia

Goal
→ Metas

FinancialEvent
→ Calendar projection

Account
→ Cuentas
```

Las demás pantallas solamente contextualizan.

No duplicar datos financieros en múltiples entidades sin una razón explícita.

---

# 23. QA GATE OBLIGATORIO

Antes de decir:

```text
READY
```

debes ejecutar este checklist.

## A. Comprensión

* [ ] Entiendo qué problema resuelve el cambio.
* [ ] Identifiqué las entidades afectadas.
* [ ] Identifiqué los servicios afectados.
* [ ] Identifiqué las migraciones necesarias.
* [ ] Identifiqué las reglas financieras afectadas.
* [ ] Revisé código existente antes de crear código nuevo.
* [ ] Busqué soluciones existentes en el repositorio.
* [ ] Revisé documentación/implementaciones maduras cuando correspondía.

---

## B. Arquitectura

* [ ] Respeta la arquitectura actual.
* [ ] No introduce duplicación innecesaria.
* [ ] No mezcla Domain/Application/Infrastructure/Presentation.
* [ ] No mueve lógica financiera al frontend.
* [ ] No crea una segunda fuente de verdad.
* [ ] No crea una entidad innecesaria.
* [ ] No rompe contratos existentes.

---

## C. Base de datos

* [ ] Modelo ORM actualizado.
* [ ] Migration creada si corresponde.
* [ ] Migration revisada manualmente.
* [ ] Migration ejecutada en DEV.
* [ ] `alembic upgrade head` exitoso.
* [ ] Schema real coincide con ORM.
* [ ] Foreign keys correctas.
* [ ] Constraints correctos.
* [ ] Índices correctos.
* [ ] No hay migraciones destructivas inesperadas.

---

## D. Persistencia

* [ ] Create funciona.
* [ ] DB contiene el registro.
* [ ] Read funciona.
* [ ] Update funciona.
* [ ] Delete/Reversal funciona según corresponda.
* [ ] Reinicio backend conserva datos.
* [ ] Reinicio frontend conserva datos.
* [ ] No depende de cache.
* [ ] No depende de localStorage.
* [ ] No depende de mocks.

---

## E. Seguridad

* [ ] Autenticación validada.
* [ ] Autorización validada.
* [ ] `household_id` validado.
* [ ] Usuario A no accede a Household B.
* [ ] Secrets fuera del código.
* [ ] No existen credenciales hardcoded.
* [ ] Inputs validados.
* [ ] CORS revisado.
* [ ] Rate limiting revisado cuando aplica.

---

## F. Dinero

* [ ] Usa Decimal.
* [ ] DB usa NUMERIC.
* [ ] No usa float para dinero.
* [ ] Redondeo definido.
* [ ] Moneda definida.
* [ ] Tasas usan `InterestRate`.
* [ ] Cálculos usan `RateEngine`.
* [ ] No existen fórmulas duplicadas.
* [ ] Resultados matemáticos verificados.

---

## G. Finanzas

* [ ] Balance invariant pasa.
* [ ] Debt invariant pasa.
* [ ] Transfer invariant pasa.
* [ ] Card invariant pasa.
* [ ] Recurrence invariant pasa.
* [ ] Projection invariant pasa cuando aplica.
* [ ] No existe doble contabilización.
* [ ] No existen movimientos fantasma.
* [ ] No se modificaron históricos para hacer pasar tests.

---

## H. API

* [ ] Schemas correctos.
* [ ] Validaciones correctas.
* [ ] Errores controlados.
* [ ] HTTP status correcto.
* [ ] No filtra información de otro household.
* [ ] Contrato frontend/backend compatible.
* [ ] Tests de endpoints pasan.

---

## I. Frontend

* [ ] Consume datos reales.
* [ ] No contiene valores financieros hardcoded.
* [ ] No calcula reglas financieras que deberían estar en backend.
* [ ] Estados loading/error/empty funcionan.
* [ ] Formularios validan.
* [ ] Fechas correctas.
* [ ] Montos correctamente formateados.
* [ ] No rompe responsive.
* [ ] No rompe navegación existente.

---

## J. Tests

Ejecutar como mínimo:

```bash
pytest
```

y las pruebas relevantes.

También ejecutar:

```bash
npm test
```

si aplica.

Y:

```bash
npm run build
```

cuando corresponda.

Si existen:

```text
lint
typecheck
integration tests
security tests
Playwright
```

también deben ejecutarse cuando el cambio los afecte.

---

# 24. TESTS OBLIGATORIOS PARA CAMBIOS DE DB

Cualquier cambio de esquema requiere:

```text
1. Migration test
2. Persistence test
3. Relationship test
4. API test
5. Restart test
6. Regression test
```

---

# 25. CRITERIOS DE BLOQUEO

El agente debe detener el desarrollo y reportar:

```text
BLOCKED
```

si encuentra:

* corrupción de datos
* pérdida de datos
* migración destructiva inesperada
* household isolation roto
* inconsistencia matemática
* doble contabilización
* float utilizado para dinero
* DB schema drift crítico
* backup no restaurable
* credenciales de producción expuestas
* datos financieros inventados
* pérdida de trazabilidad

No continuar con funcionalidades nuevas hasta resolver P0.

---

# 26. CLASIFICACIÓN DE PROBLEMAS

## P0 — CRÍTICO

Impide continuar.

Ejemplos:

* pérdida de datos
* corrupción
* acceso cross-household
* cálculo financiero incorrecto
* migración destructiva
* producción accesible por el agente

Estado:

```text
NOT READY
```

---

## P1 — ALTO

Debe resolverse antes de considerar la fase terminada.

Ejemplos:

* refresh token sin revocación
* ausencia de rate limiting
* schema drift
* backup no probado
* falta de pruebas de persistencia

---

## P2 — MEDIO

No bloquea necesariamente el MVP técnico, pero debe documentarse.

Ejemplos:

* mejoras de arquitectura
* observabilidad
* ORM relationships
* optimizaciones

---

## P3 — BAJO

Mejoras futuras:

* UX
* refactors menores
* documentación adicional
* mejoras cosméticas

---

# 27. FORMATO OBLIGATORIO DEL REPORTE

Nunca responder simplemente:

```text
Listo.
```

Debes entregar:

```text
## Resultado

STATUS: READY / NOT READY / BLOCKED

## Qué se hizo

- ...

## Qué se verificó

- ...

## Tests ejecutados

- pytest: PASS/FAIL
- frontend tests: PASS/FAIL
- build: PASS/FAIL
- migrations: PASS/FAIL
- persistence: PASS/FAIL
- security: PASS/FAIL

## Base de datos

- DB utilizada:
- Alembic:
- Schema:
- Database Doctor:
- Backup:
- Restore:

## Finanzas

- Decimal:
- RateEngine:
- Balance invariant:
- Debt invariant:
- Transfer invariant:
- Recurrence invariant:

## Riesgos encontrados

### P0
- Ninguno / ...

### P1
- Ninguno / ...

### P2
- ...

### P3
- ...

## Evidencia

Indicar archivos modificados, tests, migrations y comandos ejecutados.

## Próximo paso

Indicar exactamente qué debe hacerse después.
```

---

# 28. REGLA FINAL PARA "READY"

Solo puedes declarar:

```text
READY
```

cuando:

```text
Código
+
Base de datos
+
Persistencia
+
Seguridad
+
Tests
+
Integridad financiera
+
Migraciones
+
Regresión
```

hayan sido verificados.

Si alguno de los componentes críticos no fue probado, debes decir:

```text
NOT READY — VERIFICACIÓN PENDIENTE
```

No asumir que funciona.

No decir "debería funcionar".

No decir "parece correcto".

No decir "no encontré problemas" si no ejecutaste las pruebas correspondientes.

---

# 29. ORDEN DE RECUPERACIÓN ACTUAL

Para el incidente actual seguir exactamente:

```text
1. CONGELAR CAMBIOS
        ↓
2. CREAR NUEVA DB
        ↓
3. CONFIGURAR DEV
        ↓
4. CREAR ESQUEMA LIMPIO
        ↓
5. VALIDAR MIGRACIONES
        ↓
6. VALIDAR DebtModel.notes
        ↓
7. EJECUTAR DATABASE DOCTOR
        ↓
8. CREAR BACKUP
        ↓
9. RESTAURAR BACKUP EN DB TEMPORAL
        ↓
10. VALIDAR RESTORE
        ↓
11. AUDITAR SEGURIDAD
        ↓
12. AUDITAR HOUSEHOLD ISOLATION
        ↓
13. MIGRAR EXCEL MEDIANTE STAGING
        ↓
14. RECONCILIAR EXCEL vs DB
        ↓
15. EJECUTAR INVARIANTES
        ↓
16. EJECUTAR QA GATE COMPLETO
        ↓
17. DECLARAR DATABASE RECOVERY COMPLETE
        ↓
18. RECIÉN ENTONCES CONTINUAR NUEVAS FUNCIONALIDADES
```

---

# 30. REGLA PARA TODO DESARROLLO FUTURO

Después de recuperar la DB, ninguna funcionalidad debe saltarse el ciclo:

```text
ANALIZAR
 ↓
DISEÑAR
 ↓
IMPLEMENTAR
 ↓
MIGRAR
 ↓
TESTEAR
 ↓
PERSISTIR
 ↓
REINICIAR
 ↓
VERIFICAR
 ↓
SEGURIDAD
 ↓
INTEGRIDAD FINANCIERA
 ↓
REGRESIÓN
 ↓
QA GATE
 ↓
READY
```

El agente debe asumir que **cada cambio puede afectar datos financieros**, incluso si aparentemente solo modifica frontend.

## PRINCIPIO CENTRAL

> Primero preservar la verdad financiera.
> Después construir funcionalidades.
> Y solamente declarar "listo" cuando exista evidencia verificable.
