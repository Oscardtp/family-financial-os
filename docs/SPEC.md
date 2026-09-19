# SPEC.md — Especificacion del Proyecto

## Nombre
**Family Financial OS**

## Vision
Sistema operativo financiero familiar para hogares colombianos. Administrar economia real de manera simple, privada y rapida.

## Problema
Las familias colombianas no tienen una herramienta unificada para gestionar sus finanzas personales que:
- Maneje pesos colombianos (COP) nativamente
- Entienda tasas de interes colombianas (EA, EM, nominal)
- Sea simple de usar sin conocimiento financiero avanzado
- Sea privada (datos locales o auto-hospedados)
- Funcione offline o con conectividad limitada

## Solucion
Aplicacion web completa (SPA) con backend Python y frontend Vue.js que permite:
- Gestionar cuentas bancarias, efectivo, tarjetas de credito
- Registrar transacciones (ingresos, gastos, transferencias)
- Crear y dar seguimiento a metas de ahorro con proyecciones
- Gestionar deudas con tabla de amortizacion y alertas de vencimiento
- Presupuestos por categoria con proyeccion de gasto
- Calendario financiero con eventos recurrentes y obligaciones
- Panel de control con resumen financiero completo
- Multi-usuario por hogar con roles (Owner, Member, Viewer)

## Publico Objetivo
- Familias colombianas (1-5 miembros)
- Personas que manejan sus finanzas personales en COP
- Usuarios con nivel tecnico bajo a medio

## Moneda
- **COP (Pesos Colombianos)** — unico soporte
- Todos los montos usan `Decimal` con precision a 2 decimales
- Formato de visualizacion: `$1.500.000` (punto como separador de miles, coma para decimales)

## Tasas de Interes
El sistema soporta 4 tipos de tasa:
| Tipo | Sigla | Descripcion |
|------|-------|-------------|
| Efectiva Anual | EA | Tasa nominal anual compuesta |
| Efectiva Mensual | EM | Tasa efectiva mensual |
| Nominal | nominal | Tasa nominal anual (se divide entre 12) |
| Diaria | daily | Tasa diaria (se convierte a mensual) |

Conversion: `RateEngine.to_monthly_rate(InterestRate)` en `backend/app/financial_engine/rate_engine.py`

## Funcionalidades Principales

### 1. Autenticacion
- Registro con email + password
- Login con JWT (access + refresh tokens)
- Perfil de usuario con rol por hogar
- Tokens: access (30 min) + refresh (7 dias)

### 2. Cuentas
- Tipos: cash, bank, wallet, digital_wallet, credit_card
- Balance en COP
- CRUD completo con validacion por hogar

### 3. Transacciones
- Tipos: income, expense, transfer
- Asociadas a cuenta, categoria y usuario
- Filtro por rango de fechas
- Totales por categoria para presupuestos

### 4. Categorias
- Tipos: income, expense
- Icono y color personalizables
- Preferencia de cuenta por categoria

### 5. Presupuestos
- Por categoria, mes y ano
- Estado: ok (<80%), warning (80-100%), exceeded (>100%)
- Proyeccion de gasto al cierre del mes

### 6. Deudas
- Campos: nombre, acreedor, monto total, balance actual, tasa de interes, pago minimo, dia de vencimiento
- Historial de pagos con reversión
- Marcar meses como pagados (override)
- Tabla de amortizacion completa
- Alertas de vencimiento (overdue, due_today, upcoming)
- Toggle active/paused

### 7. Metas de Ahorro
- Tipos: savings, investment
- Prioridad: low, medium, high
- Proyeccion con tasa de retorno (para inversiones)
- Historial de aportes
- Meses restantes estimados

### 8. Pagos Recurrentes
- Frecuencia: weekly, biweekly, monthly, yearly
- Generacion automatica de eventos en calendario
- Siguiente fecha de vencimiento

### 9. Eventos Financieros
- Fuentes: debt, recurring, user, obligation
- Estados: pending, paid
- Visibilidad: confirmed, scheduled, estimated
- Marcas de pago: pay, unpay
- Recordatorios configurables

### 10. Obligaciones
- Plantillas recurrentes que generan eventos
- Fuentes: USER, DEBT, RECURRING
- Offset de dias para fecha recomendada y de corte

### 11. Dashboard
- Balance total, ingreso mensual, gasto mensual, neto
- Total de deudas, ahorros, patrimonio neto
- Transacciones recientes
- Estado de presupuestos con proyeccion
- Pagos proximos
- Resumen de metas de ahorro
- Alertas financieras (criticas, warning, info)

### 12. Calendario
- Vista mensual con FullCalendar 6
- Eventos por rango de fechas
- Disponibilidad de saldo (7 dias)
- Preparacion del mes (sugerencias)

### 13. Coach Financiero
- Sugerencias basadas en patrones
- Deteccion de patrones de gasto
- Crear obligaciones desde sugerencias

### 14. Patrimonio
- Activos (propiedades, vehiculos, inversiones)
- Pasivos (deudas, prestamos)
- Net worth = Activos - Pasivos

### 15. Notificaciones
- Por hogar y usuario
- Tipos: alert, reminder, info
- Marcar como leidas

### 16. Auditoria
- Log de acciones CRUD por usuario
- Entity type, entity ID, detalles
- Consulta por hogar

### 17. Preferencias
- Dark mode toggle
- Idioma
- Notificaciones

## No Incluido (Por Ahora)
- Soporte multi-moneda
- Importacion de extractos bancarios
- Inversiones en bolsa
- Impuestos colombianos (DIAN)
- App movil nativa
- Sincronizacion entre dispositivos

## Stack Tecnologico

### Backend
- Python 3.12
- FastAPI
- SQLAlchemy 2.0 (async)
- Alembic (migraciones)
- Pydantic v2 (validacion)
- JWT (python-jose)
- bcrypt 4.0.1
- SQLite (dev) / PostgreSQL 16 (prod)

### Frontend
- Vue.js 3 (Composition API `<script setup>`)
- Pinia (estado global)
- Vue Router (navegacion)
- Vite 5 (bundler)
- Chart.js + vue-chartjs (graficos)
- FullCalendar 6 (calendario)
- Lucide Vue Next 0.303.0 (iconos)
- VeeValidate 4 + Yup 1 (formularios)
- date-fns 3 (fechas)
- Axios (HTTP client)

### Testing
- Backend: pytest + pytest-asyncio + httpx (147 tests)
- Frontend: Vitest + Vue Test Utils (15 archivos)

### Infraestructura
- Docker + docker-compose
- PostgreSQL 16 (produccion)
- SQLite (desarrollo local)

## Datos de Prueba
- Email: `admin@familia.com`
- Password: `familia123`
- Cuenta ya configurada con transacciones, deudas, metas y presupuestos
