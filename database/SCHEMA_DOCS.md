# Esquema MySQL - Family Financial OS

## Resumen

### 19 Tablas Implementadas

| # | Tabla | Descripción |
|---|-------|-------------|
| 01 | `users` | Usuarios del sistema |
| 02 | `households` | Hogares/familias |
| 03 | `household_members` | Relación usuarios-hogares |
| 04 | `account_types` | Tipos de cuentas (lookup) |
| 05 | `accounts` | Cuentas financieras |
| 06 | `categories` | Categorías de transacciones |
| 07 | `transactions` | Transacciones (ingresos/gastos) |
| 08 | `ledger_entries` | Registro contable inmutable |
| 09 | `transfers` | Transferencias entre cuentas |
| 10 | `budgets` | Presupuestos |
| 11 | `recurring_payments` | Pagos recurrentes |
| 12 | `debts` | Deudas |
| 13 | `debt_payments` | Pagos a deudas |
| 14 | `goals` | Metas financieras |
| 15 | `goal_contributions` | Aportes a metas |
| 16 | `assets` | Activos del patrimonio |
| 17 | `liabilities` | Pasivos del patrimonio |
| 18 | `notifications` | Notificaciones |
| 19 | `audit_log` | Registro de auditoría |

## Diagrama de Relaciones

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│    users    │────<│household_members│>────│ households  │
└─────────────┘     └─────────────────┘     └─────────────┘
                           │
                           │
                    ┌──────┴──────┐
                    │             │
               ┌────┴────┐  ┌────┴────┐
               │accounts │  │ members │
               └────┬────┘  └─────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
   ┌────┴────┐ ┌────┴────┐ ┌────┴────┐
   │ledger   │ │transfers│ │budgets  │
   │entries  │ │         │ │         │
   └─────────┘ └─────────┘ └─────────┘

┌─────────────┐     ┌─────────────────┐
│transactions │────<│ ledger_entries  │
└─────────────┘     └─────────────────┘
        │
        ├───────────────┐
        │               │
   ┌────┴────┐    ┌─────┴─────┐
   │debts    │    │goals      │
   └────┬────┘    └─────┬─────┘
        │               │
   ┌────┴────┐    ┌─────┴─────┐
   │debt     │    │goal       │
   │payments │    │contributions│
   └─────────┘    └───────────┘
```

## Reglas Financieras en MySQL

### 1. Account Nature (Naturaleza de Cuenta)

```sql
-- Asset accounts: bank, cash, digital_wallet, savings, investment
-- Liability accounts: credit_card

-- Para determinar naturaleza:
SELECT at.nature 
FROM accounts a
JOIN account_types at ON a.account_type_id = at.id
WHERE a.id = account_id;
```

### 2. Balance Calculation (Cálculo de Saldo)

```sql
-- Saldo actual = Saldo inicial + Σ(créditos) - Σ(débitos)
-- 
-- Para cuentas ACTIVO:
--   income: +amount (crédito)
--   expense: -amount (débito)
--   transfer: ±amount (según dirección)
--
-- Para cuentas PASIVO:
--   income: -amount (disminuye deuda)
--   expense: +amount (aumenta deuda)

-- Ejemplo: Calcular saldo desde ledger
SELECT 
    a.initial_balance + 
    COALESCE(SUM(CASE 
        WHEN le.type = 'income' THEN le.amount
        WHEN le.type = 'expense' THEN -le.amount
        WHEN le.type = 'transfer' AND le.account_id = a.id THEN le.amount
        ELSE 0
    END), 0) AS calculated_balance
FROM accounts a
LEFT JOIN ledger_entries le ON a.id = le.account_id
WHERE a.id = ?;
```

### 3. Transaction Processing (Procesamiento de Transacción)

```sql
-- Flujo para crear una transacción:
--
-- 1. VALIDAR
--    - Cuenta existe y está activa
--    - Categoría es válida para el tipo
--    - Monto > 0
--    - Fecha es válida
--
-- 2. REGISTRAR EN LEDGER
--    INSERT INTO ledger_entries (...)
--    VALUES (..., balance_before, balance_after, ...);
--
-- 3. ACTUALIZAR SALDO
--    UPDATE accounts 
--    SET current_balance = balance_after
--    WHERE id = account_id;
--
-- 4. REGISTRAR AUDITORÍA
--    INSERT INTO audit_log (...)
--    VALUES (...);
```

### 4. Transfer Processing (Procesamiento de Transferencia)

```sql
-- Flujo para crear una transferencia:
--
-- 1. VALIDAR
--    - Ambas cuentas existen y están activas
--    - Ambas pertenecen al mismo household
--    - Son diferentes cuentas
--    - Monto > 0
--    - Cuenta origen tiene saldo suficiente (si es ACTIVO)
--
-- 2. REGISTRAR TRANSFERENCIA
--    INSERT INTO transfers (...)
--    VALUES (...);
--
-- 3. REGISTRAR EN LEDGER (2 entradas)
--    -- Entrada 1: Cuenta origen (débito)
--    INSERT INTO ledger_entries (...)
--    VALUES (..., 'transfer', amount, balance_before, balance_after, ...);
--    
--    -- Entrada 2: Cuenta destino (crédito)
--    INSERT INTO ledger_entries (...)
--    VALUES (..., 'transfer', amount, balance_before, balance_after, ...);
--
-- 4. ACTUALIZAR SALDOS (2 actualizaciones)
--    UPDATE accounts SET current_balance = balance_after WHERE id = from_account_id;
--    UPDATE accounts SET current_balance = balance_after WHERE id = to_account_id;
--
-- 5. REGISTRAR AUDITORÍA
```

## Vistas Útiles

### Vista: Saldo de Cuentas
```sql
CREATE VIEW v_account_balances AS
SELECT 
    a.id,
    a.household_id,
    a.name AS account_name,
    at.code AS account_type,
    at.nature AS account_nature,
    a.currency,
    a.initial_balance,
    a.current_balance,
    a.status
FROM accounts a
JOIN account_types at ON a.account_type_id = at.id
WHERE a.status = 'active';
```

### Vista: Patrimonio Neto
```sql
CREATE VIEW v_net_worth AS
SELECT 
    household_id,
    SUM(CASE WHEN at.nature = 'asset' THEN a.current_balance ELSE 0 END) AS total_assets,
    SUM(CASE WHEN at.nature = 'liability' THEN a.current_balance ELSE 0 END) AS total_liabilities,
    SUM(CASE WHEN at.nature = 'asset' THEN a.current_balance ELSE 0 END) 
        - SUM(CASE WHEN at.nature = 'liability' THEN a.current_balance ELSE 0 END) AS net_worth
FROM accounts a
JOIN account_types at ON a.account_type_id = at.id
WHERE a.status = 'active'
GROUP BY household_id;
```

## Procedimientos Almacenados

### 1. Actualizar Saldo de Cuenta
```sql
DELIMITER //
CREATE PROCEDURE sp_update_account_balance(
    IN p_account_id BIGINT UNSIGNED,
    IN p_amount DECIMAL(15,2),
    IN p_type ENUM('income', 'expense', 'transfer'),
    IN p_is_credit BOOLEAN
)
BEGIN
    DECLARE v_new_balance DECIMAL(15,2);
    DECLARE v_current_balance DECIMAL(15,2);
    
    SELECT current_balance INTO v_current_balance
    FROM accounts WHERE id = p_account_id;
    
    IF p_is_credit THEN
        SET v_new_balance = v_current_balance + p_amount;
    ELSE
        SET v_new_balance = v_current_balance - p_amount;
    END IF;
    
    UPDATE accounts 
    SET current_balance = v_new_balance,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_account_id;
    
    SELECT v_new_balance AS new_balance;
END //
DELIMITER ;
```

### 2. Registrar Entrada en Ledger
```sql
DELIMITER //
CREATE PROCEDURE sp_create_ledger_entry(
    IN p_transaction_id BIGINT UNSIGNED,
    IN p_account_id BIGINT UNSIGNED,
    IN p_household_id BIGINT UNSIGNED,
    IN p_type ENUM('income', 'expense', 'transfer'),
    IN p_amount DECIMAL(15,2),
    IN p_balance_before DECIMAL(15,2),
    IN p_balance_after DECIMAL(15,2),
    IN p_currency CHAR(3),
    IN p_description VARCHAR(255),
    IN p_date DATE
)
BEGIN
    INSERT INTO ledger_entries (
        transaction_id, account_id, household_id, type,
        amount, balance_before, balance_after, currency,
        description, date
    ) VALUES (
        p_transaction_id, p_account_id, p_household_id, p_type,
        p_amount, p_balance_before, p_balance_after, p_currency,
        p_description, p_date
    );
END //
DELIMITER ;
```

## Índices Clave

```sql
-- Búsquedas frecuentes
CREATE INDEX idx_transactions_household_date ON transactions(household_id, date);
CREATE INDEX idx_transactions_account_date ON transactions(account_id, date);
CREATE INDEX idx_transactions_category_date ON transactions(category_id, date);
CREATE INDEX idx_ledger_account_date ON ledger_entries(account_id, date);
CREATE INDEX idx_budgets_household_period ON budgets(household_id, period, year, month);
CREATE INDEX idx_debts_household_status ON debts(household_id, status);
CREATE INDEX idx_goals_household_active ON goals(household_id, is_active);
```

## Próximos Pasos

1. **Crear base de datos**: Ejecutar `schema.sql` en MySQL
2. **Implementar conexión PDO**: En PHP
3. **Implementar repositorios**: Para cada tabla
4. **Implementar lógica financiera**: En la capa de dominio
5. **Crear migraciones**: Para futuros cambios

## Notas

- Todos los montos usan `DECIMAL(15,2)` - nunca FLOAT o DOUBLE
- Las fechas usan `DATE` o `TIMESTAMP` nativos de MySQL
- El `audit_log` es inmutable (solo INSERT)
- Los saldos se calculan desde `ledger_entries`
- Las transferencias generan 2 entradas en el ledger
