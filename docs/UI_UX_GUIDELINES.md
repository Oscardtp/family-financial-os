# UI_UX_GUIDELINES.md — Directrices UI/UX

## Identidad Visual

**Inspiracion:** Tyba (app colombiana de finanzas personales)
**Tono:** Cercano, claro, profesional pero no corporativo
**Publico:** Familias colombianos, nivel tecnico bajo a medio

---

## Design Tokens

Ubicacion: `frontend/src/assets/design-tokens.css`

### Colores

**Primario (Azul Tyba):**
```
--color-primary-50:  #f0f5ff    (fondo claro)
--color-primary-100: #dce8fd
--color-primary-200: #bdd4fc
--color-primary-300: #93b8f9
--color-primary-400: #6096f5
--color-primary-500: #2f71e5    (principal)
--color-primary-600: #1e5cd4    (hover)
--color-primary-700: #1a4fb8
--color-primary-800: #0c4da2
--color-primary-900: #0a3a7a
```

**Neutros:**
```
--color-neutral-0:   #ffffff    (fondo principal)
--color-neutral-50:  #f8fafb    (fondo de pagina)
--color-neutral-100: #f2f2f2
--color-neutral-200: #eaeef0    (bordes)
--color-neutral-300: #d5d9de
--color-neutral-400: #a1a8b0    (texto secundario)
--color-neutral-500: #6b7a85    (texto muted)
--color-neutral-600: #536170
--color-neutral-700: #3a4550    (sidebar bg)
--color-neutral-800: #202d39    (sidebar bg)
--color-neutral-900: #141b1f    (texto principal)
```

**Semanticos:**
```
--color-success-500: #22c55e    (ingresos, pagado)
--color-warning-500: #f59e0b    (alertas, presupuesto)
--color-error-500:   #ef4444    (errores, gastos excedidos)
--color-info-500:    #3b82f6    (informativo)
```

**Financieros:**
```
--color-income:  #22c55e    (ingresos)
--color-expense: #6b7280    (gastos)
--color-transfer: #3b82f6   (transferencias)
```

**Calendario:**
```
--color-calendar-income:   #2f71e5  (azul)
--color-calendar-expense:  #cc3366  (rosa)
--color-calendar-debt:     #765600  (mostaza)
--color-calendar-goal:     #fcd579  (dorado)
--color-calendar-paid:     #25d366  (verde)
--color-calendar-overdue:  #cc3366  (rojo)
--color-calendar-upcoming: #fcd579  (amarillo)
```

**Superficies Tintadas:**
```
--color-surface-tinted-blue:   #f5f8ff
--color-surface-tinted-teal:   #f2fffc
--color-surface-tinted-yellow: #fefbe8
--color-surface-tinted-orange: #fff5eb
--color-surface-tinted-pink:   #fff0f6
--color-surface-tinted-lime:   #f4fce8
```

### Gradientes

```
--gradient-primary: linear-gradient(135deg, #2f71e5, #1a4fb8)
--gradient-blue:    linear-gradient(135deg, #0693e3, #2f71e5)
--gradient-teal:    linear-gradient(135deg, #4aeaDC, #7adcb4)
--gradient-gold:    linear-gradient(135deg, #fcb900, #ffcd75)
--gradient-peach:   linear-gradient(135deg, #ffcd75, #ff6900)
--gradient-pink:    linear-gradient(135deg, #ffceec, #f78da7)
--gradient-lime:    linear-gradient(135deg, #caf880, #7bdcb5)
```

### Espaciado

```
--spacing-xs:  4px
--spacing-sm:  8px
--spacing-md:  16px
--spacing-lg:  24px
--spacing-xl:  32px
--spacing-2xl: 48px
--spacing-3xl: 64px
```

### Border Radius

```
--radius-xs:   3px
--radius-sm:   5px
--radius-md:   8px
--radius-lg:   12px
--radius-xl:   16px
--radius-2xl:  20px
--radius-pill: 29px
--radius-full: 9999px
```

### Sombras

```
--shadow-xs:   0 1px 2px rgba(0,0,0,0.06)
--shadow-sm:   0 2px 4px rgba(0,0,0,0.08)
--shadow-md:   0 2px 6px 3px rgba(0,0,0,0.1)
--shadow-lg:   0 4px 15px rgba(0,0,0,0.15)
--shadow-xl:   0 5px 15px rgba(0,0,0,0.25)
--shadow-glow: 0 0 10px rgba(47,113,229,0.15)
```

### Tipografia

```
--font-sans:    'Inter', -apple-system, BlinkMacSystemFont, sans-serif
--font-display: 'Poppins', 'Inter', sans-serif
--font-mono:    'JetBrains Mono', monospace

--font-size-xs:     0.75rem   (12px)
--font-size-sm:     0.875rem  (14px)
--font-size-base:   1rem      (16px)
--font-size-lg:     1.125rem  (18px)
--font-size-xl:     1.5rem    (24px)
--font-size-2xl:    1.75rem   (28px)
```

### Transiciones

```
--transition-fast:   150ms ease
--transition-normal: 200ms ease
--transition-slow:   300ms ease
```

---

## Dark Mode

Activado via `data-theme="dark"` en `<html>`. Los tokens se sobreescriben en el mismo archivo CSS.

**Cambios principales en dark mode:**
- Neutros invertidos (0 es oscuro, 900 es claro)
- Sombras mas opacas
- Superficies tintadas oscuras
- Backgrounds financieros ajustados

---

## Layout

### Desktop (> 1024px)
- Sidebar fijo a la izquierda (240px)
- Contenido principal a la derecha
- Sidebar colapsable a 60px

### Tablet (641px - 1024px)
- Sidebar colapsado (60px, solo iconos)
- Contenido principal ocupa el resto

### Mobile (< 640px)
- Sidebar oculto (slide-in con hamburger)
- Bottom tab bar fijo arriba
- Contenido con padding reducido
- Safe area inset para iPhone

---

## Componentes

### Sidebar (`AppLayout.vue`)
- Fondo: `--color-neutral-800`
- Logo "FF" en `--color-primary-400`
- Nav items con hover `--color-neutral-600`
- Nav item activo: fondo `--color-primary-600`, texto blanco
- Secciones: DINERO (Resumen, Deudas), METAS (Metas), CUENTA (Mi Perfil)

### Bottom Tab Bar (`BottomTabBar.vue`)
- Solo visible en mobile (< 640px)
- Fondo: `--color-neutral-0`
- border-top: 1px solid `--color-neutral-200`
- Tabs: Inicio, Deudas, Metas, Perfil
- Activo: `--color-primary-600`
- Safe area inset para iPhone

### Cards
- Fondo: `--color-neutral-0`
- Border: 1px solid `--color-neutral-200`
- Border radius: `--radius-lg` (12px)
- Shadow: `--shadow-sm`
- Hover: `transform: translateY(-2px)`, `shadow-lg`

### Botones
- Primario: fondo `--gradient-primary`, texto blanco
- Secundario: fondo transparente, borde `--color-primary-500`
- Click effect: `transform: scale(0.98)`
- Min touch target: 44x44px

### Formularios
- Inputs con borde `--color-neutral-300`
- Focus: borde `--color-primary-500`, shadow `--shadow-glow`
- Labels en `--color-neutral-700`
- Errores en `--color-error-500`

### Badges/Status
- OK: `--color-success-500` / `--color-success-50`
- Warning: `--color-warning-500` / `--color-warning-50`
- Error: `--color-error-500` / `--color-error-50`
- Info: `--color-info-500` / `--color-info-50`

### Modales
- Overlay: `rgba(0,0,0,0.4)`
- Contenido: fondo `--color-neutral-0`, radius `--radius-xl`
- Z-index: `--z-modal` (300)

### Toast Notifications
- Z-index: `--z-toast` (500)
- Posicion: top-right
- Auto-dismiss

---

## Navegacion

### Rutas
| Ruta | Vista | Descripcion |
|------|-------|-------------|
| `/login` | Login.vue | Pagina de autenticacion |
| `/` | Resumen.vue | Panel principal (dashboard) |
| `/debts` | Debts.vue | Gestion de deudas |
| `/goals` | Goals.vue | Metas de ahorro |
| `/config` | Config.vue | Perfil y configuracion |

### Transiciones
- Page transitions: `opacity 0.15s ease`, `transform 0.15s ease`
- Enter: `translateY(8px)` -> `0`
- Leave: `0` -> `translateY(-8px)`

---

## Responsive Breakpoints

```
--bp-xs:  480px   (movil pequeno)
--bp-sm:  640px   (movil)
--bp-md:  768px   (tablet)
--bp-lg:  1024px  (desktop)
```

**Touch targets:** Minimo 44x44px en mobile.

---

## Animaciones

- `card-hover`: `translateY(-2px)` + `shadow-lg` en hover
- `btn-click`: `scale(0.98)` en active
- `list-enter/leave`: `opacity` + `translateY(-10px)`
- `prefers-reduced-motion`: Desactiva animaciones

---

## Iconos

**Libreria:** Lucide Vue Next 0.303.0

**Iconos usados en navegacion:**
- `LayoutDashboard` — Resumen
- `Receipt` — Deudas
- `Target` — Metas
- `User` — Perfil
- `LogOut` — Salir
- `Menu` — Hamburger
- `PanelLeftClose/PanelLeftOpen` — Colapsar sidebar

---

## Accesibilidad

- `FocusTrap` component para modales
- Keyboard navigation en sidebar y bottom tab bar
- `prefers-reduced-motion` soportado
- Labels en formularios
- Color contrast suficiente (neutros sobre blancos)

---

## Moneda y Formateo

- **Formato COP:** `$1.500.000` (punto separador de miles)
- **Sin decimales** para visualizacion
- **Coma** para decimales si aplica: `$1.500.500,50`
- **Composable:** `useCurrency()` con `fmt()` y `fmtFull()`

---

## Empty States

Cuando no hay datos, mostrar:
- Icono relevante
- Mensaje claro en espanol
- Boton de accion (ej: "Crear primera cuenta")

---

## Loading States

- Skeleton loaders para listas
- Spinner para acciones
- `loading` ref en composables y stores

---

## Mensajes de Error

Todos en espanol colombiano natural:
- "No pudimos cargar tu panel. Revisa tu conexion e intenta de nuevo."
- "No encontramos esta cuenta."
- "Los datos enviados no son correctos."
- "Necesitas iniciar sesion para continuar."

---

## Copy / UX Writing

**Principios:**
- Cercano y conversacional (no bancario)
- Claro y directo
- Sin jerga tecnica
- Accion orientado

**Ejemplos:**
- "Mis Deudas" (no "Gestion de Deudas")
- "Mi Perfil" (no "Configuracion de Cuenta)
- "Crear meta" (no "Nueva meta de ahorro")
- "Pago minimo" (no "Cuota minima mensual")
