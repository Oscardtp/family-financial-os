# DATABASE SAFETY PROTOCOL

## 🎯 Objetivo

La base de datos contiene información financiera real. Ningún agente de IA puede asumir que una modificación de esquema o datos es segura simplemente porque la aplicación compila o los tests unitarios pasan.

La prioridad es:
1. Preservar datos.
2. Preservar integridad financiera.
3. Preservar trazabilidad.
4. Preservar compatibilidad.
5. **Después** implementar cambios.

---

## 🛑 REGLA 1 — Nunca modificar producción directamente

El agente **NO** debe ejecutar directamente contra producción:
- `DROP TABLE`
- `DROP COLUMN`
- `TRUNCATE`
- `DELETE` masivo
- `UPDATE` masivo
- `ALTER` destructivo
- `alembic downgrade`
- `alembic upgrade head`
- `create_all()`
- `drop_all()`

...sin pasar por el **Migration Gate** y autorización explícita.

---

## 🌐 REGLA 2 — Separación de entornos

Debe existir separación estricta entre:
- `development`
- `test`
- `production`

Las migraciones deben probarse primero sobre una base temporal o clonada.

---

## 🔍 REGLA 3 — Migraciones primero se analizan

Antes de ejecutar una migración:
1. Obtener revisión actual.
2. Obtener revisiones pendientes.
3. Generar/inspeccionar SQL.
4. Detectar operaciones destructivas.
5. Detectar cambios de datos.
6. Detectar cambios irreversibles.
7. Ejecutar pruebas sobre una base temporal.
8. Ejecutar invariantes financieras.
9. Crear backup.
10. Solicitar autorización si afecta producción.

---

## 🚫 REGLA 4 — Operaciones destructivas bloquean automáticamente

Se consideran destructivas:
- `DROP TABLE`
- `DROP COLUMN`
- `TRUNCATE`
- `DELETE` sin condición segura
- `UPDATE` masivo
- `ALTER COLUMN` con posible pérdida de datos
- Cambios irreversibles de tipos
- Eliminación de constraints
- Eliminación de índices críticos
- Migraciones que sobrescriban datos financieros.

Ante cualquiera de estas operaciones:  
**STOP.**  
No continuar automáticamente.

---

## 📊 REGLA 5 — Nunca usar datos financieros para arreglar tests

Está prohibido modificar, eliminar o falsificar datos financieros históricos para hacer pasar una prueba.  
Si existe una inconsistencia:
1. Identificar la causa.
2. Identificar la fuente de verdad.
3. Corregir la lógica.
4. Crear una corrección financiera trazable si realmente corresponde.
5. Registrar el cambio.

---

## ⚖️ REGLA 6 — Financial invariants son obligatorios

Después de cambios estructurales ejecutar:
- Balance invariant
- Debt invariant
- Transfer invariant
- Credit card invariant
- Recurrence invariant
- Household isolation
- Projection invariant

---

## ✅ REGLA 7 — Una migración no está terminada cuando termina Alembic

Después de aplicar una migración:
1. Verificar revisión.
2. Verificar schema.
3. Ejecutar DB Doctor.
4. Ejecutar tests.
5. Ejecutar financial invariants.
6. Ejecutar smoke tests.
7. Verificar que la aplicación arranca.
8. Verificar datos críticos.
9. Registrar resultado.

---

## 🔄 REGLA 8 — Schema migration != Data migration

No mezclar cambios estructurales y transformaciones complejas de datos en una única migración, salvo justificación explícita.  
Las transformaciones de datos deben poder probarse y validarse independientemente.

---

## 🤖 REGLA 9 — No asumir que autogenerate es correcto

Alembic `autogenerate` solamente genera una propuesta.  
Toda migración generada automáticamente debe ser revisada antes de ejecutarse. Especialmente revisar:
- `DROP`
- `RENAME`
- `NULL` / `NOT NULL`
- `defaults`
- `foreign keys`
- `indexes`
- `enums`
- Cambios de tipos
- `backfills`
- `deletes`
- `updates`

---

## 🚨 REGLA 10 — Recovery mode

Si el agente detecta posible corrupción:  
**NO reparar inmediatamente.**  
Primero producir un **Database Incident Report**:

- Revisión actual
- Última revisión conocida sana
- Migraciones ejecutadas
- Migraciones pendientes
- Tablas afectadas
- Columnas afectadas
- Filas afectadas (si puede determinarse)
- Operaciones ejecutadas
- Errores encontrados
- Backups disponibles
- Hipótesis de causa
- Nivel de riesgo
- Plan de recuperación

Después, esperar autorización para modificar datos.

---

## 🔑 REGLA 11 — Principio de mínima autoridad

El agente debe trabajar con las credenciales de menor privilegio necesarias.  
El agente de desarrollo **no** debe tener credenciales administrativas de producción.

---

## 🛑 REGLA 12 — Regla de parada

El agente debe detener el trabajo y reportar el problema si detecta:
- Pérdida potencial de datos
- Schema drift inesperado
- Migration head inconsistente
- Migración parcialmente aplicada
- Discrepancia matemática
- Duplicación financiera
- Pérdida de household isolation
- Foreign keys inválidas
- Datos financieros que no cuadran
- Backup inexistente antes de una operación destructiva.

**Nunca** debe intentar ocultar o compensar silenciosamente el problema.

---

## 🔄 FLUJO OBLIGATORIO

```text
TASK
 ↓
READ CONTEXT
 ↓
INSPECT DATABASE STATE
 ↓
INSPECT MIGRATIONS
 ↓
DESIGN CHANGE
 ↓
GENERATE MIGRATION
 ↓
STATIC SAFETY CHECK
 ↓
TEMP DATABASE
 ↓
APPLY MIGRATION
 ↓
DB DOCTOR
 ↓
FINANCIAL INVARIANTS
 ↓
TESTS
 ↓
SMOKE TEST
 ↓
BACKUP
 ↓
HUMAN APPROVAL
 ↓
PRODUCTION
 ↓
POST-MIGRATION VALIDATION
 ↓
AUDIT LOG
```

---

## 💡 Principio final

> La IA puede proponer cambios en la base de datos.  
> La IA puede probar cambios en una base aislada.  
> **La IA no debe tener autoridad implícita para destruir o alterar datos financieros reales.**