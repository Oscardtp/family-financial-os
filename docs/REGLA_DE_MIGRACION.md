# REGLA DE MIGRACIÓN DE DATOS FINANCIEROS

La importación inicial desde Excel es una migración de datos financieros reales.

## Prohibido

El agente NO debe:

* importar directamente a producción;
* modificar la base anterior;
* eliminar la base anterior;
* sobrescribir registros existentes sin identificación explícita;
* inventar categorías;
* inventar cuentas;
* inventar fechas;
* inventar saldos;
* convertir automáticamente datos ambiguos;
* crear transacciones a partir de datos que no representen movimientos reales;
* convertir automáticamente pagos recurrentes en transacciones;
* convertir proyecciones en transacciones reales;
* alterar cantidades para hacer coincidir un total esperado.

## Proceso obligatorio

```text
Excel original
    ↓
Archivo preservado sin modificar
    ↓
Lectura / inventario
    ↓
Normalización
    ↓
Staging
    ↓
Validación
    ↓
Reporte de registros ambiguos
    ↓
Aprobación
    ↓
Importación
    ↓
Reconciliación
    ↓
Financial Invariants
    ↓
Backup
```

## Registros ambiguos

Si un registro no puede clasificarse con seguridad:

```text
NO IMPORTAR AUTOMÁTICAMENTE
```

Debe aparecer en un reporte:

```text
ROW 152
Descripción: Pago Éxito
Valor: 350.000
Fecha: 15/08/2026

Problema:
No se puede determinar si representa:
- gasto
- pago de tarjeta
- transferencia

Estado:
REQUIERE REVISIÓN
```

## Reconciliación

Después de importar:

```text
Total Excel
        =
Total importado
        +
Total rechazado
        +
Total pendiente de revisión
```

Debe ser matemáticamente explicable.

## Snapshot

Antes de considerar terminada la migración, generar:

* número de cuentas
* número de transacciones
* ingresos
* gastos
* transferencias
* deudas
* pagos de deuda
* ahorros
* inversiones
* metas
* saldos

Comparar estos valores con el Excel original.

## Regla final

El agente no debe considerar la migración exitosa porque "la aplicación funciona".

La migración solamente es exitosa cuando:

```text
DATA PERSISTENCE = PASS
DATA INTEGRITY = PASS
FINANCIAL RECONCILIATION = PASS
HOUSEHOLD ISOLATION = PASS
BACKUP = PASS
RECOVERY TEST = PASS
```
