# UI/UX Specification — Family Financial OS

## Principio Fundamental

```
El frontend muestra y solicita; el backend decide y ejecuta.
```

El frontend es una **capa de presentación**, no el lugar donde vive la lógica financiera.

### Ejemplo

Operación: "Registrar gasto de $85.000 desde cuenta Bancolombia en categoría Alimentación"

**Frontend envía:**
```json
{
  "account_id": 3,
  "category_id": 7,
  "amount": 85000,
  "type": "expense",
  "description": "Mercado"
}
```

**Backend ejecuta:**
1. Autenticar al usuario
2. Verificar que pertenece al hogar
3. Verificar que tiene permiso sobre la cuenta
4. Validar el importe
5. Validar la categoría
6. Registrar el movimiento
7. Actualizar/recalcular el saldo correspondiente
8. Registrar auditoría si corresponde
9. Devolver el resultado mediante JSON

---

## Arquitectura

```
┌─────────────────────────────────────────────┐
│                  FRONTEND                   │
│                                             │
│ HTML5 + CSS3 + JavaScript moderno           │
│                                             │
│ • Formularios                               │
│ • Dashboard                                 │
│ • Tablas                                    │
│ • Gráficos                                  │
│ • Interacciones                             │
│ • Validaciones de UX                        │
└─────────────────────┬───────────────────────┘
                      │
                  HTTP / JSON
                      │
┌─────────────────────▼───────────────────────┐
│                   API                       │
│                                             │
│ Autenticación                               │
│ Autorización                                │
│ Validación                                  │
│ Reglas de negocio                           │
│ Operaciones financieras                     │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│                MYSQL                        │
│                                             │
│ Hogares                                     │
│ Usuarios                                    │
│ Cuentas                                     │
│ Movimientos                                 │
│ Deudas                                      │
│ Metas                                       │
│ Presupuestos                                │
│ Patrimonio                                  │
└─────────────────────────────────────────────┘
```

### Evolución Futura

```
                    API
                     │
        ┌────────────┼────────────┐
        │            │            │
     Web App      Android       iOS
        │            │            │
        └────────────┼────────────┘
                     │
              Misma lógica
              financiera
```

---

## Stack Tecnológico

| Capa | Tecnología | Versión |
|------|------------|---------|
| Estructura | HTML5 | Semantic HTML5 |
| Estilos | CSS3 | Custom Properties, Grid, Flexbox |
| Lógica | JavaScript | ES6+ (sin framework) |
| Comunicación | Fetch API | REST/JSON |
| Servidor | PHP | 8.2+ |
| Base de datos | MySQL | 8.4+ |

---

## Estructura de Archivos

### Frontend

```
frontend/
├── assets/
│   ├── css/
│   │   ├── variables.css      # Custom properties (colores, spacing, etc.)
│   │   ├── base.css           # Reset, tipografía, elementos base
│   │   ├── layout.css         # Header, sidebar, main, grid system
│   │   ├── components.css     # Botones, cards, tablas, formularios, badges
│   │   └── pages.css          # Estilos específicos de páginas
│   │
│   ├── js/
│   │   ├── core/
│   │   │   ├── api.js         # Cliente HTTP para llamadas a la API
│   │   │   ├── auth.js        # Manejo de autenticación y sesiones
│   │   │   ├── router.js      # Enrutamiento SPA (single-page)
│   │   │   └── storage.js     # Almacenamiento local (localStorage)
│   │   │
│   │   ├── components/
│   │   │   ├── modal.js       # Componente modal reutilizable
│   │   │   ├── dropdown.js    # Menús desplegables
│   │   │   ├── toast.js       # Notificaciones toast
│   │   │   └── table.js       # Tablas con ordenamiento y paginación
│   │   │
│   │   ├── modules/
│   │   │   ├── dashboard.js   # Lógica del dashboard principal
│   │   │   ├── transactions.js # CRUD de transacciones
│   │   │   ├── accounts.js    # Gestión de cuentas
│   │   │   ├── budgets.js     # Presupuestos
│   │   │   ├── debts.js       # Control de deudas
│   │   │   ├── goals.js       # Metas de ahorro
│   │   │   ├── assets.js      # Activos
│   │   │   ├── recurring.js   # Pagos recurrentes
│   │   │   ├── categories.js  # Categorías
│   │   │   ├── members.js     # Miembros del hogar
│   │   │   ├── reports.js     # Reportes y análisis
│   │   │   └── export.js      # Exportación de datos
│   │   │
│   │   └── app.js             # Punto de entrada, inicialización
│   │
│   └── img/
│       └── icons/
│
├── index.html                 # SPA entry point
│
└── favicon.ico
```

### Backend (referencia)

```
backend/php/
├── public/
│   └── app.php               # Router + entry point API
├── src/
│   ├── Api/
│   │   ├── Middlewares/
│   │   │   └── AuthMiddleware.php
│   │   └── Router.php
│   ├── Domain/
│   │   ├── Account/
│   │   ├── Transaction/
│   │   ├── Ledger/
│   │   ├── Money/
│   │   ├── Services/
│   │   └── ...
│   └── Infrastructure/
│       ├── Database/
│       │   └── Connection.php
│       └── Repository/
│           └── ...
└── tests/
```

---

## Design System

### Variables CSS

```css
:root {
    /* Colores - Tema Claro */
    --color-primary: #2563eb;
    --color-success: #16a34a;
    --color-danger: #dc2626;
    --color-warning: #d97706;
    --color-info: #0891b2;

    /* Superficies */
    --color-bg: #f8fafc;
    --color-surface: #ffffff;
    --color-elevated: #f1f5f9;

    /* Texto */
    --color-text: #0f172a;
    --color-text-secondary: #475569;
    --color-muted: #64748b;
    --color-text-inverse: #ffffff;

    /* Bordes */
    --color-border: #e2e8f0;

    /* Border Radius */
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 16px;
    --radius-full: 9999px;

    /* Spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;

    /* Tipografía */
    --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'SF Mono', 'Fira Code', 'Consolas', monospace;

    --text-xs: 0.75rem;
    --text-sm: 0.875rem;
    --text-base: 1rem;
    --text-lg: 1.125rem;
    --text-xl: 1.25rem;
    --text-2xl: 1.5rem;
    --text-3xl: 2rem;

    /* Sombras */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

    /* Transiciones */
    --transition-fast: 150ms ease;
    --transition-normal: 250ms ease;
}
```

### Tema Oscuro

```css
[data-theme="dark"] {
    --color-bg: #0f172a;
    --color-surface: #1e293b;
    --color-elevated: #334155;

    --color-text: #f1f5f9;
    --color-text-secondary: #cbd5e1;
    --color-muted: #64748b;

    --color-border: #334155;
}
```

---

## Componentes UI

### Botones

```html
<!-- Primario -->
<button class="btn btn-primary">Guardar</button>

<!-- Secundario -->
<button class="btn btn-outline">Cancelar</button>

<!-- Peligro -->
<button class="btn btn-danger">Eliminar</button>

<!-- Pequeño -->
<button class="btn btn-sm btn-primary">Acción</button>

<!-- Bloque -->
<button class="btn btn-primary btn-block">Enviar</button>
```

### Cards

```html
<article class="card">
    <header class="card-header">
        <h3>Título</h3>
    </header>
    <div class="card-body">
        Contenido
    </div>
</article>
```

### Tablas

```html
<table class="data-table">
    <thead>
        <tr>
            <th scope="col">Columna</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Dato</td>
        </tr>
    </tbody>
</table>
```

### Formularios

```html
<form class="form">
    <div class="form-row">
        <div class="form-group">
            <label for="field">Campo</label>
            <input type="text" id="field" required>
        </div>
    </div>
    <button type="submit" class="btn btn-primary">Enviar</button>
</form>
```

### Badges

```html
<span class="badge badge-success">Activo</span>
<span class="badge badge-warning">Pendiente</span>
<span class="badge badge-danger">Inactivo</span>
```

### Progress Bar

```html
<div class="progress">
    <div class="progress-bar success" style="width: 75%"></div>
</div>
```

---

## Layout

### Header

- Altura fija: `64px`
- Fijo en la parte superior
- Contiene: brand, theme toggle, user menu

### Sidebar

- Ancho: `260px`
- Fijo a la izquierda
- Contiene: navegación principal
- Colapsable en móvil

### Main

- Margen izquierdo: `260px`
- Margen superior: `64px`
- Padding: `24px`

### Grid System

```css
/* Dashboard */
.dashboard-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 24px;
}

/* Stats */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 24px;
}

/* Cards */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 24px;
}
```

---

## Responsive Breakpoints

```css
/* Tablet */
@media (max-width: 1024px) {
    .dashboard-grid { grid-template-columns: 1fr; }
    .two-columns { grid-template-columns: 1fr; }
}

/* Móvil */
@media (max-width: 768px) {
    .sidebar { transform: translateX(-100%); }
    .sidebar.open { transform: translateX(0); }
    .main { margin-left: 0; }
    .stats-grid { grid-template-columns: 1fr 1fr; }
}

/* Móvil pequeño */
@media (max-width: 480px) {
    .stats-grid { grid-template-columns: 1fr; }
}
```

---

## Navegación SPA

### Páginas

| ID | Nombre | Icono | Descripción |
|----|--------|-------|-------------|
| dashboard | Dashboard | 📊 | Resumen financiero principal |
| transactions | Transacciones | 📋 | CRUD de transacciones |
| accounts | Cuentas | 🏦 | Gestión de cuentas |
| budgets | Presupuesto | 💎 | Control de presupuestos |
| debts | Deudas | 📉 | Seguimiento de deudas |
| goals | Metas | 🎯 | Metas de ahorro |
| assets | Activos | 🏠 | Bienes y propiedades |
| recurring | Recurrentes | 🔄 | Pagos recurrentes |
| categories | Categorías | 🏷️ | Organización de categorías |
| members | Miembros | 👥 | Personas del hogar |
| reports | Reportes | 📈 | Análisis y reportes |
| export | Exportar | 📤 | Descarga de datos |

### Comportamiento

- Navegación sin recarga de página (SPA)
- Actualización de URL con History API
- Carga lazy de datos por página
- Animación de transición entre páginas

---

## API Client

### Uso

```javascript
// Instancia global
const api = new ApiClient();

// Ejemplos
const accounts = await api.getAccounts();
const transaction = await api.createTransaction({
    account_id: 3,
    type: 'expense',
    amount: 85000,
    date: '2026-08-13'
});
```

### Endpoints Soportados

```javascript
// Auth
api.login(email, password)
api.logout()
api.me()

// Accounts
api.getAccounts(filters)
api.getAccount(id)
api.createAccount(data)

// Transactions
api.getTransactions(filters)
api.createTransaction(data)

// Transfers
api.createTransfer(data)

// Categories
api.getCategories()
api.createCategory(data)
api.updateCategory(id, data)
api.deleteCategory(id)

// Budgets
api.getBudgets(filters)
api.createBudget(data)
api.deleteBudget(id)

// Debts
api.getDebts(filters)
api.createDebt(data)
api.addDebtPayment(id, amount)
api.deleteDebt(id)

// Goals
api.getGoals(filters)
api.createGoal(data)
api.addGoalContribution(id, data)
api.deleteGoal(id)

// Members
api.getMembers(filters)
api.getMember(id)
api.createMember(data)
api.updateMember(id, data)
api.deleteMember(id)

// Recurring Payments
api.getRecurringPayments(filters)
api.getRecurringPayment(id)
api.createRecurringPayment(data)
api.deleteRecurringPayment(id)

// Assets
api.getAssets()
api.getAsset(id)
api.createAsset(data)
api.updateAsset(id, data)
api.deleteAsset(id)

// Liabilities
api.getLiabilities()
api.getLiability(id)
api.createLiability(data)
api.updateLiability(id, data)
api.deleteLiability(id)

// Dashboard
api.getDashboard(from, to)
api.getNetWorth()

// Reports
api.getMonthlyReport(year, month)
api.getExpensesByCategory(from, to)
api.getIncomeVsExpenses(from, to)
api.getNetWorthReport(from, to)

// Export
api.exportTransactions(format)
api.exportAccounts(format)
api.exportAll(format)
```

---

## Estado de la Aplicación

```javascript
const state = {
    currentPage: 'dashboard',
    user: null,
    householdId: null,
    accounts: [],
    transactions: [],
    categories: [],
    budgets: [],
    debts: [],
    goals: [],
    assets: [],
    recurring: [],
    members: [],
};
```

---

## Validaciones de UX

### Formularios

- Campos requeridos marcados con `required`
- Validación en tiempo real al enviar
- Mensajes de error claros y específicos
- Deshabilitar botón durante envío
- Éxito: toast de confirmación
- Error: toast de error con mensaje

### Tablas

- Columnas ordenables (futuro)
- Paginación (futuro)
- Estado vacío: "No hay datos"
- Loading spinner durante carga

### Navegación

- Indicador de página activa en sidebar
- Transiciones suaves entre páginas
- Historial de navegación (back/forward)

---

## Accesibilidad

- Semantic HTML5 (`header`, `nav`, `main`, `section`, `article`)
- ARIA labels en botones interactivos
- Contraste de colores WCAG AA
- Navegación por teclado
- Focus visible en elementos interactivos

---

## Rendimiento

- Carga lazy de datos por página
- Debounce en búsquedas (futuro)
- Cache de datos en estado local
- Imágenes optimizadas (futuro)

---

## Futuras Mejoras

- [ ] Gráficos con Chart.js o D3.js
- [ ] PWA (Progressive Web App)
- [ ] Modo offline
- [ ] Notificaciones push
- [ ] Exportación a PDF
- [ ] Importación de datos
- [ ] Multi-moneda
- [ ] Soporte i18n (internacionalización)
