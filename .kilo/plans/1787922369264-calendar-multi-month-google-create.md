# Plan: Calendario multi-mes, creación estilo Google y eliminación de FAB

## Objetivo
- Mostrar eventos del mes actual y de los meses siguientes sin pantallas vacías.
- Eliminar el botón de acción rápida `+` y reemplazarlo por creación de eventos al hacer click en una celda del calendario, estilo Google Calendar.
- Eliminar el warning/error `Invalid Date` en el flujo de fechas del calendario.

## Alcance
- Backend: sin cambios. Los endpoints necesarios ya existen (`GET /events`, `POST /events`, `GET /events/upcoming`, `GET /month/prepare`).
- Frontend: cambios en `Calendar.vue` y `useCalendar.js`.

## Tareas

### 1. Pre-cargar rango de 3 meses en el store
- En `useCalendar.js`, cambiar `fetchMonth` por `fetchRange`:
  - Calcular `from_date = primer día del mes anterior`.
  - Calcular `to_date = último día del mes siguiente`.
  - Llamar `eventsService.listRange(from_date, to_date)`.
  - Guardar el resultado en `events`.
- Mantener `year` y `month` para la vista actual, pero filtrar eventos por rango.
- En `Calendar.vue`, cambiar `onMounted` para llamar a `store.fetchRange()` en lugar de `store.fetchMonth()`.

### 2. Mostrar eventos multi-mes en el grid actual
- En `Calendar.vue`, mantener el grid mensual actual, pero asignar eventos a celdas aunque `due_date` no esté en el mes visualizado.
- Los eventos de meses adyacentes se muestran en sus celdas correspondientes cuando el usuario navega con `prevMonth`/`nextMonth`.
- No se requiere UI de 3 meses simultáneos; la precarga es transparente.

### 3. Eliminar FAB y crear evento al hacer click en celda
- Eliminar el botón FAB (`<button class="fab">`) de `Calendar.vue`.
- Agregar `@click="openCreateOnDate(cell.dateStr)"` en la celda del calendario, solo si la celda no tiene eventos o si se hace click en el fondo vacío de la celda.
- Abrir el mismo sheet de creación, pero prellenar `form.due_date` con la fecha clickeada.
- Si el usuario clickea un evento existente, seguir abriendo el detalle.

### 4. Arreglar `Invalid Date`
- En `Calendar.vue`, proteger todas las funciones que consumen fechas:
  - `daysUntil(dateStr)`: si `dateStr` es nulo/vacío, retornar `null`.
  - `eventColor(ev)`: si `daysUntil(ev.due_date)` es `null`, no evaluar color por antigüedad.
  - `statusLabel(ev)`: idem.
  - `statusClass(ev)`: idem.
  - `fmtDateShort(dateStr)`: ya tiene guard, validar que no entre string vacío.
- En `useCurrency.js`, `fmtDate` ya tiene guard para `null`, pero asegurar que el template nunca pase `undefined`/`""` sin control.

## Criterios de validación
1. Al abrir el calendario, se ven eventos de deudas sincronizadas para el mes actual y para los meses siguiente sin recargar.
2. No aparece el botón FAB.
3. Click en celda vacía abre formulario con fecha preseleccionada.
4. No hay warnings `Invalid Date` en consola al navegar meses ni al abrir el detalle.
5. `npm run build` pasa sin errores.

## Archivos afectados
- `frontend/src/stores/useCalendar.js`
- `frontend/src/views/Calendar.vue`
- `frontend/src/services/events.js` (solo si se requiere un helper `listRange`; si ya existe, sin cambios)

## Riesgos
- Si `listRange` no existe o no está implementado en backend, se debe usar `listMonth` múltiples veces. Según `events.py`, el endpoint `/events` soporta `from_date` y `to_date`, así que `listRange` ya existe en el servicio frontend.
- La UI puede saturar si se muestran demasiados chips por celda; se mantiene el diseño actual de chips con scroll hidden.
