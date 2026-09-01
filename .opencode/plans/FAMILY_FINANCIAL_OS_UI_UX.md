# Family Financial OS - UI/UX Design System

> **Nombre del Design System**: Financial OS  
> **Filosofía**: Claridad, Calma, Contexto, Colaboración, Velocidad  
> **Estado**: Planificación

---

## Índice

1. [Filosofía de Diseño](#1-filosofía-de-diseño)
2. [Inspiraciones](#2-inspiraciones)
3. [Design Tokens](#3-design-tokens)
4. [Tipografía](#4-tipografía)
5. [Colores](#5-colores)
6. [Componentes](#6-componentes)
7. [Patrones de Diseño](#7-patrones-de-diseño)
8. [Layout y Estructura](#8-layout-y-estructura)
9. [Interacciones y Animaciones](#9-interacciones-y-animaciones)
10. [Modo Claro y Oscuro](#10-modo-claro-y-oscuro)
11. [Responsive Design](#11-responsive-design)
12. [Storybook](#12-storybook)
13. [Figma](#13-figma)

---

## 1. Filosofía de Diseño

### 1.1 Principios Fundamentales

| Principio | Descripción | Ejemplo |
|-----------|-------------|---------|
| **Claridad** | La información importante siempre visible | Saldo total siempre visible en dashboard |
| **Calma** | Evitar uso excesivo de colores de alerta | Verde para positivos, solo rojo en errores |
| **Contexto** | Mostrar el impacto de cada decisión | "Este gasto representa 13% del presupuesto" |
| **Colaboración** | Evidenciar quién hizo qué | Avatar del usuario en cada transacción |
| **Velocidad** | Acciones frecuentes con mínimo esfuerzo | Ctrl+K para acciones rápidas |

### 1.2 Lo que NO es Financial OS

```
❌ NO es un clon de Notion
❌ NO es un clon de Excel
❌ NO es una wallet tradicional
❌ NO es un sistema bancario lleno de tablas

✅ ES un Sistema Operativo Financiero
✅ ES una experiencia de productividad
✅ ES una herramienta de toma de decisiones
```

### 1.3 Lenguaje Visual

```
NO: Tablas densas y formularios pesados
SÍ: Tarjetas con aire y claridad

NO: Colores de alerta por todos lados
SÍ: Indicadores sutiles con contexto

NO: Navegación confusa
SÍ: Sidebar persistente y comandos rápidos
```

---

## 2. Inspiraciones

### 2.1 macOS

| Elemento | Inspiración | Aplicación en Financial OS |
|----------|-------------|---------------------------|
| **Espacio** | Mucho aire entre elementos | Tarjetas con padding generoso |
| **Jerarquía** | Títulos claros, contenido organizado | Títulos de sección prominentes |
| **Elegancia** | Minimalismo refinado | Tipografía limpia, sin ruido visual |
| **Paneles** | Sidebar persistente | Navegación lateral siempre visible |
| **Glassmorphism** | Efecto de vidrio sutil | Tarjetas con backdrop-filter ligero |

### 2.2 Windows 11

| Elemento | Inspiración | Aplicación en Financial OS |
|----------|-------------|---------------------------|
| **Widgets** | Módulos independientes | Dashboard configurable con widgets |
| **Snap Layouts** | Organización de paneles | Layout flexible de componentes |
| **Centro de notificaciones** | Notificaciones agrupadas | Alertas de vencimiento y pagos |
| **Configuración modular** | Personalización | Widgets reordenables |

### 2.3 iOS

| Elemento | Inspiración | Aplicación en Financial OS |
|----------|-------------|---------------------------|
| **Minimalismo** | Poco ruido visual | Interfaz limpia y enfocada |
| **Espacios** | Respiración entre elementos | Margenes y paddings generosos |
| **Animaciones** | Transiciones suaves | Navegación fluida |
| **Tipografía** | SF Pro, jerarquía clara | Sistema tipográfico consistente |

### 2.4 Material Design 3

| Elemento | Inspiración | Aplicación en Financial OS |
|----------|-------------|---------------------------|
| **Personalización** | Temas adaptables | Modo claro/oscuro |
| **Accesibilidad** | Contraste, tamaños | WCAG 2.1 AA compliance |
| **Componentes adaptables** | Responsive | Cards que se adaptan al contexto |

### 2.5 VisionOS (La más importante)

| Elemento | Inspiración | Aplicación en Financial OS |
|----------|-------------|---------------------------|
| **Tarjetas flotantes** | Profundidad visual | Cards con sombras sutiles |
| **Contenido con profundidad** | Capas visuales | Z-index consciente |
| **Espacio y aire** | Nada se siente pesado | Layout open y breathing |
| **Minimalismo extremo** | Solo lo esencial | Información priorizada |

### 2.6 Linear

| Elemento | Inspiración | Aplicación en Financial OS |
|----------|-------------|---------------------------|
| **Velocidad** | Todo responde al instante | Optimistic updates |
| **Atajos** | Productividad | Ctrl+K command palette |
| **Animaciones mínimas** | Sin distracciones | Transiciones sutiles |

### 2.7 Raycast

| Elemento | Inspiración | Aplicación en Financial OS |
|----------|-------------|---------------------------|
| **Command palette** | Ctrl+K para todo | Acciones rápidas |
| **Productividad extrema** | Mínimos clicks | Workflows eficientes |

### 2.8 Notion

| Elemento | Inspiración | Aplicación en Financial OS |
|----------|-------------|---------------------------|
| **Editor modular** | Bloques de contenido | Dashboard configurable |
| **Paneles** | Organización | Layout flexible |

### 2.9 Arc Browser

| Elemento | Inspiración | Aplicación en Financial OS |
|----------|-------------|---------------------------|
| **Transiciones suaves** | Navegación fluida | Router transitions |
| **Sidebar** | Navegación lateral | Panel de navegación |

---

## 3. Design Tokens

### 3.1 Estructura de Tokens

```json
{
  "colors": {
    "primary": { ... },
    "secondary": { ... },
    "neutral": { ... },
    "semantic": { ... },
    "financial": { ... }
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
    "3xl": "64px"
  },
  "borderRadius": {
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
    "full": "9999px"
  },
  "shadows": {
    "sm": "...",
    "md": "...",
    "lg": "...",
    "xl": "...",
    "glass": "..."
  },
  "typography": { ... },
  "transitions": { ... }
}
```

### 3.2 Espaciado

```
Espaciado base: 4px

4px   - xs: Iconos, elementos inline
8px   - sm: Padding interno de botones pequeños
16px  - md: Padding estándar de componentes
24px  - lg: Separación entre secciones
32px  - xl: Margen de tarjetas grandes
48px  - 2xl: Separación entre secciones del dashboard
64px  - 3xl: Margen exterior del layout
```

### 3.3 Border Radius

```
4px   - sm: Botones pequeños, inputs
8px   - md: Tarjetas estándar, modals
12px  - lg: Tarjetas grandes, paneles
16px  - xl: Dashboard cards
9999px - full: Avatares, badges
```

### 3.4 Sombras (Inspiración VisionOS)

```css
/* Sombra sutil - Tarjetas */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);

/* Sombra media - Paneles */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
             0 2px 4px -1px rgba(0, 0, 0, 0.06);

/* Sombra grande - Modals, dropdowns */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
             0 4px 6px -2px rgba(0, 0, 0, 0.05);

/* Sombra XL - Elementos flotantes */
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
             0 10px 10px -5px rgba(0, 0, 0, 0.04);

/* Glassmorphism */
--shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.08);
--backdrop-glass: blur(12px) saturate(180%);
--bg-glass: rgba(255, 255, 255, 0.72);
```

---

## 4. Tipografía

### 4.1 Familia Tipográfica

```css
/* Principal - Inter para UI */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Mono - JetBrains Mono para números */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Display - Para títulos grandes */
--font-display: 'Inter', sans-serif;
```

### 4.2 Escala Tipográfica

| Token | Tamaño | Peso | Uso |
|-------|--------|------|-----|
| `display-xl` | 48px | 700 | Títulos de página |
| `display-lg` | 36px | 700 | Secciones principales |
| `display-md` | 30px | 600 | Subtítulos |
| `display-sm` | 24px | 600 | Encabezados de tarjeta |
| `heading-lg` | 20px | 600 | Títulos de sección |
| `heading-md` | 16px | 600 | Títulos de componente |
| `heading-sm` | 14px | 600 | Labels, encabezados de tabla |
| `body-lg` | 16px | 400 | Texto principal |
| `body-md` | 14px | 400 | Texto estándar |
| `body-sm` | 12px | 400 | Texto secundario, captions |
| `mono-lg` | 16px | 500 | Montos grandes |
| `mono-md` | 14px | 500 | Montos estándar |
| `mono-sm` | 12px | 500 | Montos pequeños |

### 4.3 Ejemplo de Uso

```css
/* Saldo total */
.amount-display {
  font-family: var(--font-mono);
  font-size: 48px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* Nombre de categoría */
.category-name {
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 500;
}

/* Monto en tabla */
.table-amount {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}
```

---

## 5. Colores

### 5.1 Paleta Primaria

```css
:root {
  /* Primary - Azul profesional, confiable */
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-200: #bfdbfe;
  --color-primary-300: #93c5fd;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  --color-primary-800: #1e40af;
  --color-primary-900: #1e3a8a;

  /* Secondary - Violeta para acentos */
  --color-secondary-500: #8b5cf6;

  /* Neutros */
  --color-neutral-0: #ffffff;
  --color-neutral-50: #f9fafb;
  --color-neutral-100: #f3f4f6;
  --color-neutral-200: #e5e7eb;
  --color-neutral-300: #d1d5db;
  --color-neutral-400: #9ca3af;
  --color-neutral-500: #6b7280;
  --color-neutral-600: #4b5563;
  --color-neutral-700: #374151;
  --color-neutral-800: #1f2937;
  --color-neutral-900: #111827;
}
```

### 5.2 Colores Semánticos

```css
:root {
  /* Éxito - Verde calmado (no agresivo) */
  --color-success-50: #f0fdf4;
  --color-success-100: #dcfce7;
  --color-success-500: #22c55e;
  --color-success-600: #16a34a;

  /* Advertencia - Ámbar suave */
  --color-warning-50: #fffbeb;
  --color-warning-100: #fef3c7;
  --color-warning-500: #f59e0b;
  --color-warning-600: #d97706;

  /* Error - Rojo moderado (no alarmante) */
  --color-error-50: #fef2f2;
  --color-error-100: #fee2e2;
  --color-error-500: #ef4444;
  --color-error-600: #dc2626;

  /* Info - Azul claro */
  --color-info-50: #eff6ff;
  --color-info-100: #dbeafe;
  --color-info-500: #3b82f6;
}
```

### 5.3 Colores Financieros

```css
:root {
  /* Ingresos - Verde positivo */
  --color-income: #22c55e;
  --color-income-bg: #f0fdf4;

  /* Gastos - Neutro (no rojo) */
  --color-expense: #6b7280;
  --color-expense-bg: #f9fafb;

  /* Transferencias - Azul */
  --color-transfer: #3b82f6;
  --color-transfer-bg: #eff6ff;

  /* Presupuesto OK */
  --color-budget-ok: #22c55e;
  --color-budget-ok-bg: #f0fdf4;

  /* Presupuesto Advertencia */
  --color-budget-warning: #f59e0b;
  --color-budget-warning-bg: #fffbeb;

  /* Presupuesto Excedido */
  --color-budget-exceeded: #ef4444;
  --color-budget-exceeded-bg: #fef2f2;
}
```

### 5.4 Modo Oscuro

```css
[data-theme="dark"] {
  --color-neutral-0: #0f0f0f;
  --color-neutral-50: #1a1a1a;
  --color-neutral-100: #262626;
  --color-neutral-200: #333333;
  --color-neutral-300: #404040;
  --color-neutral-400: #525252;
  --color-neutral-500: #737373;
  --color-neutral-600: #a3a3a3;
  --color-neutral-700: #d4d4d4;
  --color-neutral-800: #e5e5e5;
  --color-neutral-900: #f5f5f5;

  /* Glass en modo oscuro */
  --bg-glass: rgba(15, 15, 15, 0.72);
  --shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.4);
}
```

---

## 6. Componentes

### 6.1 Tarjetas Financieras

```vue
<!-- FinancialCard.vue -->
<template>
  <div class="financial-card" :class="variant">
    <div class="card-header">
      <span class="card-icon">
        <slot name="icon" />
      </span>
      <span class="card-label">{{ label }}</span>
    </div>
    <div class="card-value">
      <span class="currency">$</span>
      <span class="amount">{{ formattedAmount }}</span>
    </div>
    <div v-if="subtitle" class="card-subtitle">
      {{ subtitle }}
    </div>
  </div>
</template>

<style scoped>
.financial-card {
  background: var(--bg-glass);
  backdrop-filter: var(--backdrop-glass);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-md);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.financial-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.card-value {
  font-family: var(--font-mono);
  font-size: 32px;
  font-weight: 700;
  color: var(--color-neutral-900);
  margin-top: var(--spacing-sm);
}

.card-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-neutral-500);
  margin-top: var(--spacing-xs);
}
</style>
```

**Variantes:**
- `income` - Borde izquierdo verde
- `expense` - Borde izquierdo neutro
- `savings` - Borde izquierdo azul
- `debt` - Borde izquierdo ámbar
- `net-worth` - Borde izquierdo violeta

### 6.2 Indicadores de Progreso

```vue
<!-- ProgressIndicator.vue -->
<template>
  <div class="progress-indicator">
    <div class="progress-header">
      <span class="progress-label">{{ label }}</span>
      <span class="progress-percentage">{{ percentage }}%</span>
    </div>
    <div class="progress-bar">
      <div 
        class="progress-fill"
        :style="{ width: `${percentage}%` }"
        :class="status"
      />
    </div>
    <div class="progress-footer">
      <span class="progress-current">{{ formatCurrency(current) }}</span>
      <span class="progress-target">de {{ formatCurrency(target) }}</span>
    </div>
  </div>
</template>

<style scoped>
.progress-bar {
  height: 8px;
  background: var(--color-neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

.progress-fill.ok { background: var(--color-budget-ok); }
.progress-fill.warning { background: var(--color-budget-warning); }
.progress-fill.exceeded { background: var(--color-budget-exceeded); }
</style>
```

### 6.3 Widget de Patrimonio

```vue
<!-- NetWorthWidget.vue -->
<template>
  <div class="net-worth-widget">
    <div class="widget-header">
      <h3>Patrimonio Neto</h3>
      <button class="widget-menu">···</button>
    </div>
    
    <div class="widget-content">
      <div class="net-worth-display">
        <span class="net-worth-amount">
          {{ formatCurrency(netWorth) }}
        </span>
        <span class="net-worth-change" :class="changeClass">
          {{ changePercentage }}% este mes
        </span>
      </div>
      
      <div class="assets-liabilities">
        <div class="assets">
          <span class="label">Activos</span>
          <span class="amount positive">
            {{ formatCurrency(assets) }}
          </span>
        </div>
        <div class="liabilities">
          <span class="label">Pasivos</span>
          <span class="amount negative">
            {{ formatCurrency(liabilities) }}
          </span>
        </div>
      </div>
      
      <div class="chart-mini">
        <!-- Mini sparkline chart -->
      </div>
    </div>
  </div>
</template>

<style scoped>
.net-worth-widget {
  background: var(--bg-glass);
  backdrop-filter: var(--backdrop-glass);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-md);
}

.net-worth-amount {
  font-family: var(--font-mono);
  font-size: 36px;
  font-weight: 700;
}
</style>
```

### 6.4 Timeline de Actividad

```vue
<!-- ActivityTimeline.vue -->
<template>
  <div class="activity-timeline">
    <div class="timeline-header">
      <h3>Actividad Reciente</h3>
      <button class="see-all">Ver todo</button>
    </div>
    
    <div class="timeline-list">
      <div 
        v-for="activity in activities" 
        :key="activity.id"
        class="timeline-item"
      >
        <div class="timeline-avatar">
          <img :src="activity.user.avatar" :alt="activity.user.name" />
        </div>
        <div class="timeline-content">
          <p class="timeline-description">
            <strong>{{ activity.user.name }}</strong>
            {{ activity.description }}
          </p>
          <span class="timeline-time">{{ activity.time }}</span>
        </div>
        <div class="timeline-amount" :class="activity.type">
          {{ formatCurrency(activity.amount) }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  transition: background 0.15s ease;
}

.timeline-item:hover {
  background: var(--color-neutral-50);
}

.timeline-avatar img {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
}
</style>
```

### 6.5 Calendario Financiero

```vue
<!-- FinancialCalendar.vue -->
<template>
  <div class="financial-calendar">
    <div class="calendar-header">
      <button @click="prevMonth">←</button>
      <h3>{{ monthName }} {{ year }}</h3>
      <button @click="nextMonth">→</button>
    </div>
    
    <div class="calendar-grid">
      <div class="day-header" v-for="day in weekDays" :key="day">
        {{ day }}
      </div>
      
      <div 
        v-for="date in calendarDays"
        :key="date.key"
        class="day-cell"
        :class="{
          'today': date.isToday,
          'has-events': date.events.length > 0
        }"
      >
        <span class="day-number">{{ date.day }}</span>
        <div class="day-events">
          <div 
            v-for="event in date.events.slice(0, 2)"
            :key="event.id"
            class="event-dot"
            :class="event.type"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.day-cell {
  aspect-ratio: 1;
  padding: var(--spacing-xs);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.day-cell.today {
  background: var(--color-primary-100);
}

.day-cell.has-events {
  background: var(--color-neutral-50);
}
</style>
```

### 6.6 Barras de Presupuesto

```vue
<!-- BudgetBar.vue -->
<template>
  <div class="budget-bar">
    <div class="budget-info">
      <span class="budget-category">{{ category }}</span>
      <span class="budget-amounts">
        {{ formatCurrency(spent) }} / {{ formatCurrency(budget) }}
      </span>
    </div>
    <div class="bar-container">
      <div 
        class="bar-fill"
        :style="{ width: `${percentage}%` }"
        :class="status"
      />
    </div>
    <div class="budget-context">
      <span class="context-text">{{ contextMessage }}</span>
    </div>
  </div>
</template>

<script setup>
const percentage = computed(() => (props.spent / props.budget) * 100);

const status = computed(() => {
  if (percentage.value <= 80) return 'ok';
  if (percentage.value <= 100) return 'warning';
  return 'exceeded';
});

const contextMessage = computed(() => {
  if (status.value === 'ok') {
    return `Tiene $${remaining} disponibles`;
  } else if (status.value === 'warning') {
    return `Cerca del límite - $${remaining} restantes`;
  } else {
    return `Excedido por $${Math.abs(remaining)}`;
  }
});
</script>
```

### 6.7 Simulador de Escenarios

```vue
<!-- ScenarioSimulator.vue -->
<template>
  <div class="scenario-simulator">
    <div class="simulator-header">
      <h3>Simulador de Escenarios</h3>
      <p class="subtitle">¿Qué pasaría si...?</p>
    </div>
    
    <div class="simulator-controls">
      <div class="control-group">
        <label>Aumento de ingresos</label>
        <input type="range" v-model="incomeIncrease" min="0" max="50" />
        <span>{{ incomeIncrease }}%</span>
      </div>
      
      <div class="control-group">
        <label>Reducción de gastos</label>
        <input type="range" v-model="expenseReduction" min="0" max="50" />
        <span>{{ expenseReduction }}%</span>
      </div>
      
      <div class="control-group">
        <label>Pago extra deudas</label>
        <input type="number" v-model="extraDebtPayment" />
      </div>
    </div>
    
    <div class="simulator-results">
      <div class="result-card">
        <span class="result-label">Ahorro mensual</span>
        <span class="result-value">{{ projectedSavings }}</span>
      </div>
      <div class="result-card">
        <span class="result-label">Fecha fin de deudas</span>
        <span class="result-value">{{ debtFreeDate }}</span>
      </div>
      <div class="result-card">
        <span class="result-label">Patrimonio en 1 año</span>
        <span class="result-value">{{ projectedNetWorth }}</span>
      </div>
    </div>
  </div>
</template>
```

### 6.8 Command Palette (Ctrl+K)

```vue
<!-- CommandPalette.vue -->
<template>
  <Teleport to="body">
    <div v-if="isOpen" class="command-overlay" @click="close">
      <div class="command-palette" @click.stop>
        <div class="command-input-wrapper">
          <span class="command-icon">⌘</span>
          <input 
            ref="inputRef"
            v-model="query"
            placeholder="Escriba un comando..."
            class="command-input"
          />
        </div>
        
        <div class="command-results">
          <div class="command-group">
            <span class="group-label">Acciones Rápidas</span>
            <div 
              v-for="command in filteredCommands"
              :key="command.id"
              class="command-item"
              @click="executeCommand(command)"
            >
              <span class="command-icon">{{ command.icon }}</span>
              <span class="command-name">{{ command.name }}</span>
              <span class="command-shortcut">{{ command.shortcut }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.command-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 20vh;
  z-index: 9999;
}

.command-palette {
  width: 640px;
  background: var(--bg-glass);
  backdrop-filter: var(--backdrop-glass);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
}

.command-input {
  width: 100%;
  padding: var(--spacing-lg);
  font-size: 18px;
  border: none;
  background: transparent;
  outline: none;
}
</style>
```

---

## 7. Patrones de Diseño

### 7.1 Panel Lateral Persistente

```
┌─────────────────────────────────────────────────────────────┐
│ ┌──────────┐ ┌────────────────────────────────────────────┐ │
│ │          │ │                                            │ │
│ │  Logo    │ │  Contenido Principal                       │ │
│ │          │ │                                            │ │
│ ├──────────┤ │                                            │ │
│ │          │ │                                            │ │
│ │ Dashboard│ │                                            │ │
│ │ Cuentas  │ │                                            │ │
│ │ Transacc.│ │                                            │ │
│ │ Presup.  │ │                                            │ │
│ │ Deudas   │ │                                            │ │
│ │ Ahorro   │ │                                            │ │
│ │ Patrimon.│ │                                            │ │
│ │          │ │                                            │ │
│ ├──────────┤ │                                            │ │
│ │ Familia  │ │                                            │ │
│ │ Config.  │ │                                            │ │
│ │          │ │                                            │ │
│ └──────────┘ └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Características:**
- Ancho fijo: 260px
- Colapsable en tablet: 72px (solo iconos)
- Oculto en móvil: drawer overlay
- Glassmorphism sutil
- Iconos de Lucide Icons

### 7.2 Dashboard Configurable

```vue
<!-- Dashboard.vue -->
<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Buenos días, {{ userName }}</h1>
      <div class="header-actions">
        <button class="btn-icon" @click="openCommandPalette">
          <Search size="20" />
        </button>
        <button class="btn-primary" @click="openQuickAction">
          + Nueva Transacción
        </button>
      </div>
    </header>
    
    <div class="widgets-grid">
      <WidgetBalance class="widget-balance" />
      <WidgetIncome class="widget-income" />
      <WidgetExpenses class="widget-expenses" />
      <WidgetSavings class="widget-savings" />
      
      <WidgetBudget class="widget-budget span-2" />
      <WidgetDebts class="widget-debts" />
      
      <WidgetActivity class="widget-activity span-2" />
      <WidgetCalendar class="widget-calendar" />
    </div>
  </div>
</template>

<style scoped>
.widgets-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-lg);
}

.widget-balance { grid-column: span 2; }
.widget-budget { grid-column: span 2; }
.widget-activity { grid-column: span 2; }

@media (max-width: 1024px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .widgets-grid {
    grid-template-columns: 1fr;
  }
}
</style>
```

### 7.3 Acciones Rápidas

```
Botón Flotante (+)
    │
    ├── + Transacción
    ├── + Pago de Deuda
    ├── + Aporte Ahorro
    ├── + Transferencia
    └── Ver Command Palette (Ctrl+K)
```

### 7.4 Navegación Consistente

| Dispositivo | Navegación |
|-------------|------------|
| **Desktop** | Sidebar izquierdo persistente |
| **Tablet** | Sidebar colapsado (iconos) |
| **Móvil** | Bottom navigation + drawer |

---

## 8. Layout y Estructura

### 8.1 Layout Principal

```
┌─────────────────────────────────────────────────────────────┐
│ Header (48px)                                               │
│ [Logo] [Search] [Notifications] [User Avatar]               │
├──────────┬──────────────────────────────────────────────────┤
│ Sidebar  │ Main Content                                     │
│ (260px)  │                                                  │
│          │  ┌─────────────────────────────────────────────┐ │
│ Nav      │  │ Page Header                                 │ │
│ Items    │  │ [Breadcrumb] [Actions]                      │ │
│          │  ├─────────────────────────────────────────────┤ │
│          │  │                                             │ │
│          │  │ Content Area                                │ │
│          │  │                                             │ │
│          │  │                                             │ │
│          │  └─────────────────────────────────────────────┘ │
├──────────┴──────────────────────────────────────────────────┤
│ Status Bar (24px) - Opcional                                │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Breakpoints

```css
/* Mobile */
@media (max-width: 640px) { ... }

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) { ... }

/* Desktop */
@media (min-width: 1025px) { ... }

/* Wide */
@media (min-width: 1440px) { ... }
```

---

## 9. Interacciones y Animaciones

### 9.1 Principios

- **Rápido**: 150-200ms para la mayoría de transiciones
- **Suave**: ease-out para entradas, ease-in para salidas
- **Con propósito**: Cada animación tiene una razón

### 9.2 Transiciones

```css
/* Transición estándar */
--transition-fast: 150ms ease;
--transition-normal: 200ms ease;
--transition-slow: 300ms ease;

/* Hover en tarjetas */
.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* Router transitions */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.15s ease;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}

/* List animations */
.list-enter-active,
.list-leave-active {
  transition: all 0.2s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
```

### 9.3 Micro-interacciones

```
Click en botón    → Scale 0.98 durante 100ms
Hover en tarjeta  → translateY(-2px) + sombra
Focus en input    → Borde azul + sombra sutil
Agregar elemento  → Slide down + fade in
Eliminar elemento → Slide up + fade out
Loading           → Skeleton shimmer
```

---

## 10. Modo Claro y Oscuro

### 10.1 Toggle

```vue
<!-- ThemeToggle.vue -->
<template>
  <button @click="toggleTheme" class="theme-toggle">
    <Sun v-if="isDark" size="20" />
    <Moon v-else size="20" />
  </button>
</template>

<script setup>
const isDark = useDark();
const toggleTheme = useToggle(isDark);
</script>
```

### 10.2 Detección de Preferencia

```javascript
// Detect system preference
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

// Save preference
localStorage.setItem('theme', isDark ? 'dark' : 'light');
```

---

## 11. Responsive Design

### 11.1 Estrategia Mobile-First

```css
/* Base: Mobile */
.container {
  padding: var(--spacing-md);
}

/* Tablet */
@media (min-width: 641px) {
  .container {
    padding: var(--spacing-lg);
  }
}

/* Desktop */
@media (min-width: 1025px) {
  .container {
    padding: var(--spacing-xl);
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

### 11.2 Adaptaciones por Dispositivo

| Elemento | Mobile | Tablet | Desktop |
|----------|--------|--------|---------|
| Sidebar | Drawer | Colapsado | Expandido |
| Dashboard | 1 columna | 2 columnas | 4 columnas |
| Cards | Full width | Half width | Quarter width |
| Tablas | Cards | Scroll horizontal | Tabla completa |
| Modals | Full screen | Centered | Centered |

---

## 12. Storybook

### 12.1 Estructura

```
src/stories/
├── foundations/
│   ├── Colors.stories.js
│   ├── Typography.stories.js
│   └── Spacing.stories.js
├── components/
│   ├── FinancialCard.stories.js
│   ├── ProgressIndicator.stories.js
│   ├── BudgetBar.stories.js
│   └── CommandPalette.stories.js
├── patterns/
│   ├── Dashboard.stories.js
│   └── Sidebar.stories.js
└── pages/
    ├── Home.stories.js
    └── Budget.stories.js
```

### 12.2 Ejemplo de Story

```javascript
// FinancialCard.stories.js
export default {
  title: 'Components/FinancialCard',
  component: FinancialCard,
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['income', 'expense', 'savings', 'debt', 'net-worth']
    }
  }
};

export const Default = {
  args: {
    label: 'Saldo Total',
    amount: 12500000,
    variant: 'net-worth'
  }
};

export const Income = {
  args: {
    label: 'Ingresos del Mes',
    amount: 4800000,
    subtitle: '+12% vs mes anterior',
    variant: 'income'
  }
};
```

---

## 13. Figma

### 13.1 Estructura del Archivo

```
Family Financial OS - Design System
├── 🎨 Foundations
│   ├── Colors
│   ├── Typography
│   ├── Spacing
│   ├── Icons
│   └── Shadows
├── 🧩 Components
│   ├── Buttons
│   ├── Cards
│   ├── Inputs
│   ├── Modals
│   └── Navigation
├── 📐 Patterns
│   ├── Dashboard
│   ├── Sidebar
│   └── Command Palette
├── 📱 Responsive
│   ├── Mobile
│   ├── Tablet
│   └── Desktop
└── 🌙 Themes
    ├── Light
    └── Dark
```

### 13.2 Design Tokens en Figma

```json
{
  "colors": {
    "primary": { "500": "#3b82f6" },
    "success": { "500": "#22c55e" },
    "warning": { "500": "#f59e0b" }
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px"
  }
}
```

---

## 14. Checklist de Implementación

### Fase 1: Fundamentos
- [ ] Design tokens definidos
- [ ] Paleta de colores (light/dark)
- [ ] Escala tipográfica
- [ ] Sistema de espaciado
- [ ] Iconografía (Lucide Icons)

### Fase 2: Componentes Base
- [ ] Button
- [ ] Input
- [ ] Card
- [ ] Modal
- [ ] Avatar
- [ ] Badge

### Fase 3: Componentes Financieros
- [ ] FinancialCard
- [ ] ProgressIndicator
- [ ] BudgetBar
- [ ] DebtCard
- [ ] SavingsGoalCard
- [ ] NetWorthWidget

### Fase 4: Patrones
- [ ] Sidebar
- [ ] Header
- [ ] Dashboard Grid
- [ ] Command Palette
- [ ] Activity Timeline

### Fase 5: Páginas
- [ ] Dashboard
- [ ] Accounts
- [ ] Transactions
- [ ] Budget
- [ ] Debts
- [ ] Savings
- [ ] Assets
- [ ] Projections

---

## 15. Recursos

### 15.1 Herramientas

| Herramienta | Uso |
|-------------|-----|
| **Figma** | Diseño visual |
| **Storybook** | Documentación de componentes |
| **Tailwind CSS** | Utility-first CSS |
| **Radix UI** | Componentes accesibles |
| **Framer Motion** | Animaciones |
| **Lucide Icons** | Iconografía |

### 15.2 Referencias

- [VisionOS Design Guidelines](https://developer.apple.com/visionos/)
- [Material Design 3](https://m3.material.io/)
- [Linear Design](https://linear.app/)
- [Raycast Design](https://raycast.com/)
- [Arc Browser](https://arc.net/)

---

**Fin del Design System**
