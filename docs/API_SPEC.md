# API_SPEC.md — Especificacion API REST

> **Base URL:** `/api/v1`
> **Content-Type:** `application/json`
> **Auth:** Bearer JWT token en header `Authorization`
> **Moneda:** COP (pesos colombianos)
> **Docs:** Swagger en `http://localhost:8000/docs`

---

## Autenticacion

### POST `/auth/register`
Registra un nuevo usuario y retorna tokens.

**Request:**
```json
{
  "email": "user@email.com",
  "name": "Nombre",
  "password": "minimo6chars"
}
```

**Response (201):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### POST `/auth/login`
Login con credenciales.

**Request:**
```json
{
  "email": "user@email.com",
  "password": "password"
}
```

**Response (200):** Mismo que register.

### POST `/auth/refresh`
Renueva tokens usando refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response (200):** Mismo que register.

### GET `/auth/me`
Retorna el perfil del usuario autenticado.

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@email.com",
  "name": "Nombre",
  "role": "owner",
  "household_id": "uuid",
  "created_at": "2026-01-01T00:00:00"
}
```

---

## Cuentas

### GET `/accounts`
Lista todas las cuentas del hogar.

**Query:** `skip=0`, `limit=100`

**Response (200):**
```json
[
  {
    "id": "uuid",
    "household_id": "uuid",
    "name": "Bancolombia",
    "type": "bank",
    "balance": 2500000.00,
    "currency": "COP",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00"
  }
]
```

### POST `/accounts`
Crea una nueva cuenta.

**Request:**
```json
{
  "name": "Mi Cuenta",
  "type": "bank",
  "balance": 1000000,
  "currency": "COP"
}
```

**Valores validos para `type`:** `cash`, `bank`, `wallet`, `digital_wallet`, `credit_card`

### GET `/accounts/{id}`
Detalle de una cuenta.

### PUT `/accounts/{id}`
Actualiza una cuenta.

### DELETE `/accounts/{id}`
Elimina una cuenta. Solo owners pueden eliminar.

---

## Transacciones

### GET `/transactions`
Lista transacciones del hogar.

**Query:** `skip=0`, `limit=100`, `date_from=YYYY-MM-DD`, `date_to=YYYY-MM-DD`

### POST `/transactions`
Crea una transaccion.

**Request:**
```json
{
  "account_id": "uuid",
  "category_id": "uuid",
  "type": "expense",
  "amount": 50000,
  "description": "Almuerzo",
  "date": "2026-09-15",
  "to_account_id": null
}
```

**Valores validos para `type`:** `income`, `expense`, `transfer`

### GET `/transactions/{id}`
### PUT `/transactions/{id}`
### DELETE `/transactions/{id}`

---

## Categorias

### GET `/categories`
### POST `/categories`
**Request:**
```json
{
  "name": "Alimentacion",
  "type": "expense",
  "icon": "utensils",
  "color": "#22c55e"
}
```
### GET `/categories/{id}`
### PUT `/categories/{id}`
### DELETE `/categories/{id}`

---

## Presupuestos

### GET `/budgets`
Lista presupuestos. **Query:** `month`, `year`

### POST `/budgets`
**Request:**
```json
{
  "category_id": "uuid",
  "amount": 500000,
  "month": 9,
  "year": 2026
}
```

### PUT `/budgets/{id}`
### DELETE `/budgets/{id}`

---

## Deudas

### GET `/debts`
Lista todas las deudas del hogar.

### POST `/debts`
**Request:**
```json
{
  "name": "Tarjeta de credito",
  "creditor": "Bancolombia",
  "total_amount": 5000000,
  "current_balance": 3500000,
  "interest_rate": 24.5,
  "interest_rate_type": "EA",
  "minimum_payment": 150000,
  "due_day": 15,
  "start_date": "2025-01-01",
  "end_date": "2027-12-31"
}
```

**Valores validos para `interest_rate_type`:** `EA`, `EM`, `nominal`, `daily`

### GET `/debts/{id}`
### PUT `/debts/{id}`
### DELETE `/debts/{id}` — Solo owners.

### POST `/debts/{id}/payments`
Registra un pago a una deuda.

**Request:**
```json
{
  "amount": 150000,
  "payment_date": "2026-09-15"
}
```

### DELETE `/debts/{id}/payments/{payment_id}`
Reversa un pago registrado.

### GET `/debts/{id}/payments`
Lista pagos de una deuda.

### POST `/debts/{id}/toggle`
Alterna estado active/paused de una deuda.

### POST `/debts/{id}/mark-paid`
Marca un mes historico como pagado.

**Request:**
```json
{
  "year": 2026,
  "month": 8
}
```

### GET `/debts/{id}/payment-history`
Retorna historial mensual de pagos (paid/pending/reversed).

### GET `/debts/{id}/amortization`
Genera tabla de amortizacion completa.

### GET `/debts/due-alerts`
Alertas de vencimiento de deudas.

---

## Metas de Ahorro

### GET `/savings/goals`
### POST `/savings/goals`
**Request:**
```json
{
  "name": "Fondo de vacaciones",
  "target_amount": 5000000,
  "target_date": "2026-12-31",
  "monthly_contribution": 500000,
  "priority": "high",
  "goal_type": "savings",
  "description": "Vacaciones en diciembre"
}
```

**Valores validos:**
- `priority`: `low`, `medium`, `high`
- `goal_type`: `savings`, `investment`
- Para inversiones: `expected_return_rate` (tasa EA anual), `horizon_months`

### GET `/savings/goals/{id}`
### PUT `/savings/goals/{id}`
### DELETE `/savings/goals/{id}`

### POST `/savings/goals/{id}/contributions`
Registra un aporte a una meta.

**Request:**
```json
{
  "amount": 200000,
  "contribution_date": "2026-09-15"
}
```

### GET `/savings/goals/{id}/contributions`
Historial de aportes.

### POST `/savings/goals/projection`
Calcula proyeccion de una meta.

**Request:**
```json
{
  "current_amount": 1000000,
  "monthly_contribution": 300000,
  "target_amount": 500000,
  "expected_return_rate": 9.0,
  "horizon_months": 24
}
```

---

## Pagos Recurrentes

### GET `/recurring-payments`
### POST `/recurring-payments`
**Request:**
```json
{
  "name": "Netflix",
  "amount": 50000,
  "type": "expense",
  "frequency": "monthly",
  "day_of_month": 15,
  "next_due_date": "2026-10-15",
  "account_id": "uuid"
}
```

**Valores validos para `frequency`:** `weekly`, `biweekly`, `monthly`, `yearly`

### GET `/recurring-payments/{id}`
### PUT `/recurring-payments/{id}`
### DELETE `/recurring-payments/{id}`

---

## Eventos Financieros

### GET `/events`
Lista eventos. Soporta dos modos de consulta:
- **Por mes:** `?year=2026&month=9`
- **Por rango:** `?from_date=2026-09-01&to_date=2026-09-30`

### POST `/events`
**Request:**
```json
{
  "title": "Pago arriendo",
  "type": "payment",
  "amount": 1500000,
  "due_date": "2026-09-30",
  "recommended_date": "2026-09-25",
  "account_id": "uuid",
  "visibility": "confirmed",
  "payment_method": "transfer"
}
```

**Valores validos:**
- `type`: `expense`, `payment`, `debt`, `income`, `goal`
- `visibility`: `confirmed`, `scheduled`, `estimated`
- `payment_method`: `card`, `cash`, `transfer`

### GET `/events/{id}`
### PUT `/events/{id}`
### DELETE `/events/{id}`

### POST `/events/{id}/pay`
Marca un evento como pagado.

### POST `/events/{id}/unpay`
Anula el pago de un evento.

### GET `/events/upcoming`
Eventos proximos. **Query:** `days=30`

### GET `/events/availability`
Disponibilidad de saldo a 7 dias.

---

## Obligaciones

### GET `/obligations`
### POST `/obligations`
**Request:**
```json
{
  "name": "Arriendo",
  "type": "expense",
  "amount": 1500000,
  "frequency": "monthly",
  "anchor_day": 30,
  "recommended_offset_days": 5,
  "generate_months": 12
}
```

### GET `/obligations/{id}`
### PUT `/obligations/{id}`
### DELETE `/obligations/{id}`

---

## Dashboard

### GET `/dashboard`
Retorna resumen financiero completo.

**Response (200):**
```json
{
  "total_balance": 5000000,
  "monthly_income": 8000000,
  "monthly_expenses": 5500000,
  "net_monthly": 2500000,
  "total_debt": 15000000,
  "total_savings": 3000000,
  "net_worth": 12000000,
  "recent_transactions": [...],
  "budget_status": [
    {
      "category": "Alimentacion",
      "budgeted": 800000,
      "spent": 650000,
      "status": "ok",
      "message": "Alimentacion esta dentro del presupuesto.",
      "projected_spent": 780000,
      "projected_remaining": 20000,
      "will_exceed": false
    }
  ],
  "budget_projection": {
    "total_projected_spent": 4800000,
    "total_projected_remaining": 200000,
    "total_will_exceed": false
  },
  "upcoming_payments": [...],
  "savings_summary": {
    "total": 3000000,
    "goals": [...]
  },
  "financial_alert": null
}
```

---

## Coach Financiero

### GET `/coach/suggestions`
Sugerencias basadas en patrones detectados.

### GET `/coach/patterns`
Patrones de gasto detectados.

---

## Preparacion del Mes

### GET `/month/prepare`
Prepara la vista del mes actual (sugerencias, eventos, disponibilidad).

---

## Proyecciones

### POST `/projections`
Calcula proyeccion financiera.

**Request:**
```json
{
  "months": 12,
  "monthly_income": 8000000,
  "monthly_expenses": 5500000,
  "current_debt": 15000000,
  "monthly_debt_payment": 500000,
  "current_savings": 3000000
}
```

---

## Notificaciones

### GET `/notifications`
Notificaciones del usuario autenticado.

### PUT `/notifications/{id}/read`
Marca una notificacion como leida.

---

## Preferencias

### GET `/preferences`
### PUT `/preferences`

---

## Patrimonio

### GET `/household`
Datos del hogar y miembros.

### GET `/reports`
Reportes financieros.

---

## Auditoria

### GET `/audit`
Logs de auditoria del hogar.

---

## Health Check

### GET `/health`
Sin autenticacion.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

## Errores

Todos los errores siguen este formato:

```json
{
  "error": "HTTPError",
  "detail": "Mensaje amigable en espanol"
}
```

**Mensajes por status code:**
| Codigo | Mensaje |
|--------|---------|
| 400 | Los datos enviados no son correctos. |
| 401 | Necesitas iniciar sesion para continuar. |
| 403 | No tienes permiso para hacer esta accion. |
| 404 | No encontramos lo que buscas. |
| 422 | Revisa los campos marcados. Algo esta mal. |
| 500 | Algo salio mal de nuestro lado. |

**Errores de validacion (422):**
```json
{
  "error": "ValidationError",
  "detail": "Los datos enviados no son validos",
  "fields": [
    {"field": "body -> amount", "message": "Input should be greater than 0"}
  ]
}
```

---

## Rate Limiting

**No implementado actualmente.** Pendiente para endpoints publicos (`/auth/login`, `/auth/register`).

---

## CORS

**Origenes permitidos:**
- `http://localhost:5173` (Vite dev)
- `http://localhost:3000`

**Metodos permitidos:** GET, POST, PUT, DELETE, PATCH

**Headers permitidos:** Authorization, Content-Type, Accept
