# Plan: Family Financial Calendar

## Estado actual

El backend ya tiene casi toda la arquitectura propuesta:
- `FinancialObligationModel` con `anchor_day`, `recommended_offset_days`, `cutoff_offset_days`, `responsible_member_id`, `confidence`, `source`
- `FinancialEventModel` con `due_date`, `recommended_date`, `cutoff_date`, `status`, `responsible_member_id`, `obligation_id`, `visibility`, `confidence`, `payment_method`, `consequence_note`, `paid_at`, `paid_amount`, `paid_by`
- `obligation_service.generate_events_for_obligation` crea 12 meses de eventos automáticamente
- `calendar_service.availability` calcula proyecciones 7/30 días, cash needed, expected income/expenses
- `notification_service.get_upcoming` agrupa por today/this_week con niveles Próximamente/Se acerca/Mañana/Hoy/Pendiente
- Frontend: `Calendar.vue` con grid mensual, legend, colores por estado, detalle de evento, panel de disponibilidad
- `NotificationBell.vue` con tabs inbox/upcoming/coach
- `event_service.mark_as_paid` notifica a otros miembros de familia

## Fases

### Fase 1: Cerrar gaps de UI del calendario
1. Ampliar formulario de creación/edición de eventos con `recommended_date`, `cutoff_date`, `account_id`, `responsible_member_id`, `consequence_note`
2. Mejorar chips del grid: mostrar `recommended_date` como subtítulo, `cutoff_date` como indicador de urgencia, icono por tipo más distintivo
3. Añadir indicador visual de `confidence` (eventos aprendidos vs confirmados)
4. Mejorar detalle de evento: mostrar cuenta asociada, forma de pago, responsable, consecuencia en tarjetas separadas con iconos

### Fase 2: Vista "Hoy" (Home)
1. Crear `views/Home.vue` con layout del punto 26 del diseño:
   - Saludo + fecha actual
   - Tarjeta "Disponible" grande
   - Sección "Hoy" (eventos del día)
   - Sección "Próximamente" (próximos 3-5 días)
   - Sección "Este mes" (ingresos, gastos, ahorrado)
   - Sección "Family Coach" (sugerencias)
2. Conectar con `calendar_service.availability`, `notification_service.get_upcoming`, `coach_service`
3. Añadir ruta `/` apuntando a Home (actualmente Dashboard)

### Fase 3: Notificaciones accionables
1. Añadir botones inline en `NotificationBell.vue` para acciones rápidas:
   - "Registrar pago" → abre sheet de marcar como pagado
   - "Convertir en recurrente" → crea `FinancialObligation` desde el evento
   - "Ver obligación" → navega a detalle
2. Mejorar formato de mensajes para incluir monto y días restantes como en el diseño

### Fase 4: Flujo "Preparar el mes"
1. Crear endpoint `POST /calendar/month-prep` que retorne resumen del mes (pagos programados, ingresos, metas, deudas)
2. Crear UI tipo wizard en `Calendar.vue` o componente separado accesible desde toolbar
3. Permitir editar valores, añadir pagos nuevos, confirmar deudas

### Fase 5: Coach avanzado (detección de patrones)
1. Crear `coach_service.detect_patterns(household_id)` que analice eventos históricos agrupados por título+método+pago
2. Umbrales: ≥3 ocurrencias en últimos 6 meses, variación <20% en monto, desviación ≤3 días en fecha
3. Generar sugerencias tipo: "Parece que [X] se paga alrededor del día [Y]..."
4. Exponer en `NotificationBell.vue` tab coach y en vista Home

## Riesgos

- El backend ya usa `confidence` pero el frontend no lo muestra; ignorar eventos con confidence < 70 en vistas principales para evitar ruido
- `calendar_service.availability` actualmente usa `financial_events` via `get_upcoming`; validar que incluya incomes y budgets comprometidos
- Las migraciones ya aplicaron `financial_obligations` y `financial_events`; no requiere nuevas migraciones para Fases 1-3

## Criterios de validación

- Calendario muestra `recommended_date` y `cutoff_date` en chips y detalle
- Formulario de evento captura las 3 fechas + responsable + cuenta + consecuencia
- Vista Home carga en <500ms, muestra disponibilidad real, próximos 3 eventos, resumen del mes, 1 sugerencia del coach
- NotificationBell tiene botones de acción rápida funcionales
- "Preparar el mes" genera resumen correcto en <1s
- Coach detecta al menos 1 patrón después de 3 eventos similares registrados
