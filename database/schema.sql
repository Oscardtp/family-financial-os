-- ============================================================
-- Family Financial OS - MySQL Schema
-- ============================================================
-- Versión: 0.1.0
-- Base de datos: family_financial_os
-- Motor: InnoDB
-- Charset: utf8mb4
-- ============================================================

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS family_financial_os
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE family_financial_os;

-- ============================================================
-- 01. USERS
-- ============================================================
-- Usuarios del sistema. Cada usuario pertenece a un household.
-- Un usuario puede pertenecer a múltiples hogares (futuro).
-- ============================================================

CREATE TABLE users (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    phone           VARCHAR(20) NULL,
    avatar_url      VARCHAR(500) NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    email_verified  BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at   TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    UNIQUE KEY uk_users_email (email),
    INDEX idx_users_active (is_active),
    INDEX idx_users_created (created_at)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 02. HOUSEHOLDS
-- ============================================================
-- Hogares/familias. Un usuario principal crea el hogar.
-- Otros usuarios son invitados a unirse.
-- ============================================================

CREATE TABLE households (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    slug            VARCHAR(100) NOT NULL,
    country         CHAR(2) NOT NULL DEFAULT 'CO',
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    timezone        VARCHAR(50) NOT NULL DEFAULT 'America/Bogota',
    owner_id        BIGINT UNSIGNED NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    UNIQUE KEY uk_households_slug (slug),
    INDEX idx_households_owner (owner_id),
    INDEX idx_households_active (is_active),
    
    -- Foreign Keys
    CONSTRAINT fk_households_owner 
        FOREIGN KEY (owner_id) REFERENCES users(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 03. HOUSEHOLD_MEMBERS
-- ============================================================
-- Relación muchos a muchos entre hogares y usuarios.
-- Un usuario puede pertenecer a múltiples hogares.
-- Un hogar tiene múltiples miembros.
-- ============================================================

CREATE TABLE household_members (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    user_id         BIGINT UNSIGNED NOT NULL,
    role            ENUM('administrator', 'adult', 'child', 'other') NOT NULL DEFAULT 'adult',
    status          ENUM('active', 'inactive', 'pending') NOT NULL DEFAULT 'active',
    joined_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    invited_by      BIGINT UNSIGNED NULL,
    
    -- Índices
    UNIQUE KEY uk_household_members (household_id, user_id),
    INDEX idx_hm_household (household_id),
    INDEX idx_hm_user (user_id),
    INDEX idx_hm_role (role),
    INDEX idx_hm_status (status),
    
    -- Foreign Keys
    CONSTRAINT fk_hm_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_hm_user 
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_hm_invited_by 
        FOREIGN KEY (invited_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 04. ACCOUNT_TYPES
-- ============================================================
-- Tipos de cuentas disponibles en el sistema.
-- Tabla de configuración/lookup.
-- ============================================================

CREATE TABLE account_types (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    code            VARCHAR(30) NOT NULL,
    name            VARCHAR(50) NOT NULL,
    nature          ENUM('asset', 'liability') NOT NULL DEFAULT 'asset',
    description     VARCHAR(200) NULL,
    icon            VARCHAR(50) NULL,
    color           VARCHAR(7) NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order      INT NOT NULL DEFAULT 0,
    
    -- Índices
    UNIQUE KEY uk_account_types_code (code),
    INDEX idx_at_nature (nature),
    INDEX idx_at_active (is_active)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar tipos de cuenta predefinidos
INSERT INTO account_types (code, name, nature, description, icon, color, sort_order) VALUES
('cash', 'Efectivo', 'asset', 'Dinero en efectivo', 'wallet', '#10B981', 1),
('bank', 'Cuenta Bancaria', 'asset', 'Cuenta de ahorro o corriente bancaria', 'building-columns', '#3B82F6', 2),
('digital_wallet', 'Billetera Digital', 'asset', 'Nequi, Daviplata, etc.', 'smartphone', '#8B5CF6', 3),
('savings', 'Ahorros', 'asset', 'Cuentas de ahorro', 'piggy-bank', '#059669', 4),
('investment', 'Inversión', 'asset', 'Fondos, acciones, etc.', 'chart-line', '#F59E0B', 5),
('credit_card', 'Tarjeta de Crédito', 'liability', 'Tarjetas de crédito', 'credit-card', '#EF4444', 6),
('other', 'Otro', 'asset', 'Otros tipos de cuenta', 'question-circle', '#6B7280', 7);

-- ============================================================
-- 05. ACCOUNTS
-- ============================================================
-- Cuentas financieras del hogar.
-- Cada cuenta pertenece a un household y opcionalmente a un miembro.
-- El saldo se calcula desde ledger_entries (no se almacena directamente).
-- ============================================================

CREATE TABLE accounts (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    account_type_id INT UNSIGNED NOT NULL,
    member_id       BIGINT UNSIGNED NULL,
    name            VARCHAR(100) NOT NULL,
    account_number  VARCHAR(50) NULL,
    institution     VARCHAR(100) NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    initial_balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    current_balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    status          ENUM('active', 'inactive', 'closed') NOT NULL DEFAULT 'active',
    notes           TEXT NULL,
    color           VARCHAR(7) NULL,
    icon            VARCHAR(50) NULL,
    sort_order      INT NOT NULL DEFAULT 0,
    last_synced_at  TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_accounts_household (household_id),
    INDEX idx_accounts_type (account_type_id),
    INDEX idx_accounts_member (member_id),
    INDEX idx_accounts_status (status),
    INDEX idx_accounts_currency (currency),
    
    -- Foreign Keys
    CONSTRAINT fk_accounts_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_accounts_type 
        FOREIGN KEY (account_type_id) REFERENCES account_types(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_accounts_member 
        FOREIGN KEY (member_id) REFERENCES household_members(id)
        ON DELETE SET NULL ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 06. CATEGORIES
-- ============================================================
-- Categorías para transacciones (ingresos y gastos).
-- Soporta jerarquía con parent_id.
-- ============================================================

CREATE TABLE categories (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NULL,
    parent_id       BIGINT UNSIGNED NULL,
    name            VARCHAR(100) NOT NULL,
    type            ENUM('income', 'expense', 'both') NOT NULL DEFAULT 'expense',
    icon            VARCHAR(50) NULL,
    color           VARCHAR(7) NULL,
    is_system       BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order      INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_categories_household (household_id),
    INDEX idx_categories_parent (parent_id),
    INDEX idx_categories_type (type),
    INDEX idx_categories_active (is_active),
    
    -- Foreign Keys
    CONSTRAINT fk_categories_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_categories_parent 
        FOREIGN KEY (parent_id) REFERENCES categories(id)
        ON DELETE SET NULL ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar categorías predefinidas
INSERT INTO categories (name, type, icon, color, is_system, sort_order) VALUES
-- Ingresos
('Salario', 'income', 'briefcase', '#059669', TRUE, 1),
('Freelance', 'income', 'laptop', '#059669', TRUE, 2),
('Inversiones', 'income', 'trending-up', '#059669', TRUE, 3),
('Otros Ingresos', 'income', 'plus-circle', '#059669', TRUE, 4),

-- Gastos
('Alimentación', 'expense', 'utensils', '#16A34A', TRUE, 10),
('Transporte', 'expense', 'car', '#2563EB', TRUE, 11),
('Servicios', 'expense', 'zap', '#9333EA', TRUE, 12),
('Entretenimiento', 'expense', 'film', '#EC4899', TRUE, 13),
('Salud', 'expense', 'heart', '#EF4444', TRUE, 14),
('Educación', 'expense', 'book', '#3B82F6', TRUE, 15),
('Vivienda', 'expense', 'home', '#F59E0B', TRUE, 16),
('Ropa', 'expense', 'shirt', '#8B5CF6', TRUE, 17),
('Otros Gastos', 'expense', 'shopping-cart', '#6B7280', TRUE, 18);

-- Subcategorías
INSERT INTO categories (parent_id, name, type, icon, color, is_system, sort_order) VALUES
-- Alimentación
(5, 'Mercado', 'expense', 'shopping-cart', '#16A34A', TRUE, 1),
(5, 'Restaurantes', 'expense', 'utensils', '#16A34A', TRUE, 2),
(5, 'Domicilios', 'expense', 'truck', '#16A34A', TRUE, 3),

-- Transporte
(6, 'Combustible', 'expense', 'gas-pump', '#2563EB', TRUE, 1),
(6, 'Transporte Público', 'expense', 'bus', '#2563EB', TRUE, 2),
(6, 'Mantenimiento', 'expense', 'wrench', '#2563EB', TRUE, 3),

-- Servicios
(7, 'Internet', 'expense', 'wifi', '#9333EA', TRUE, 1),
(7, 'Teléfono', 'expense', 'phone', '#9333EA', TRUE, 2),
(7, 'Luz', 'expense', 'zap', '#9333EA', TRUE, 3),
(7, 'Agua', 'expense', 'droplet', '#9333EA', TRUE, 4),
(7, 'Gas', 'expense', 'flame', '#9333EA', TRUE, 5);

-- ============================================================
-- 07. TRANSACTIONS
-- ============================================================
-- Transacciones financieras (ingresos y gastos).
-- Cada transacción es un hecho económico inmutable.
-- El efecto en saldo se registra en ledger_entries.
-- ============================================================

CREATE TABLE transactions (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    account_id      BIGINT UNSIGNED NOT NULL,
    category_id     BIGINT UNSIGNED NULL,
    member_id       BIGINT UNSIGNED NULL,
    type            ENUM('income', 'expense') NOT NULL,
    amount          DECIMAL(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    date            DATE NOT NULL,
    description     VARCHAR(255) NULL,
    notes           TEXT NULL,
    reference       VARCHAR(100) NULL,
    status          ENUM('pending', 'processed', 'cancelled') NOT NULL DEFAULT 'processed',
    is_recurring    BOOLEAN NOT NULL DEFAULT FALSE,
    recurring_id    BIGINT UNSIGNED NULL,
    tags            JSON NULL,
    attachments     JSON NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by      BIGINT UNSIGNED NULL,
    
    -- Índices
    INDEX idx_transactions_household (household_id),
    INDEX idx_transactions_account (account_id),
    INDEX idx_transactions_category (category_id),
    INDEX idx_transactions_member (member_id),
    INDEX idx_transactions_type (type),
    INDEX idx_transactions_date (date),
    INDEX idx_transactions_status (status),
    INDEX idx_transactions_recurring (is_recurring),
    
    -- Foreign Keys
    CONSTRAINT fk_transactions_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_transactions_account 
        FOREIGN KEY (account_id) REFERENCES accounts(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_transactions_category 
        FOREIGN KEY (category_id) REFERENCES categories(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_transactions_member 
        FOREIGN KEY (member_id) REFERENCES household_members(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_transactions_created_by 
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 08. LEDGER_ENTRIES
-- ============================================================
-- Registro contable inmutable (libro mayor).
-- Cada transacción genera una o más entradas en el ledger.
-- El saldo de una cuenta se calcula: initial_balance + SUM(credit) - SUM(debit)
-- ============================================================

CREATE TABLE ledger_entries (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    transaction_id  BIGINT UNSIGNED NOT NULL,
    account_id      BIGINT UNSIGNED NOT NULL,
    household_id    BIGINT UNSIGNED NOT NULL,
    type            ENUM('income', 'expense', 'transfer') NOT NULL,
    amount          DECIMAL(15,2) NOT NULL,
    balance_before  DECIMAL(15,2) NOT NULL,
    balance_after   DECIMAL(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    description     VARCHAR(255) NULL,
    reference       VARCHAR(100) NULL,
    date            DATE NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_ledger_transaction (transaction_id),
    INDEX idx_ledger_account (account_id),
    INDEX idx_ledger_household (household_id),
    INDEX idx_ledger_type (type),
    INDEX idx_ledger_date (date),
    INDEX idx_ledger_account_date (account_id, date),
    
    -- Foreign Keys
    CONSTRAINT fk_ledger_transaction 
        FOREIGN KEY (transaction_id) REFERENCES transactions(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ledger_account 
        FOREIGN KEY (account_id) REFERENCES accounts(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_ledger_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 09. TRANSFERS
-- ============================================================
-- Transferencias entre cuentas.
-- Una transferencia genera 2 entradas en ledger_entries:
--   1. Débito en cuenta origen (type: transfer, amount negativo)
--   2. Crédito en cuenta destino (type: transfer, amount positivo)
-- ============================================================

CREATE TABLE transfers (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    from_account_id BIGINT UNSIGNED NOT NULL,
    to_account_id   BIGINT UNSIGNED NOT NULL,
    amount          DECIMAL(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    date            DATE NOT NULL,
    description     VARCHAR(255) NULL,
    reference       VARCHAR(100) NULL,
    status          ENUM('pending', 'completed', 'cancelled') NOT NULL DEFAULT 'completed',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by      BIGINT UNSIGNED NULL,
    
    -- Índices
    INDEX idx_transfers_household (household_id),
    INDEX idx_transfers_from_account (from_account_id),
    INDEX idx_transfers_to_account (to_account_id),
    INDEX idx_transfers_date (date),
    INDEX idx_transfers_status (status),
    
    -- Foreign Keys
    CONSTRAINT fk_transfers_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_transfers_from_account 
        FOREIGN KEY (from_account_id) REFERENCES accounts(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_transfers_to_account 
        FOREIGN KEY (to_account_id) REFERENCES accounts(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_transfers_created_by 
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 10. BUDGETS
-- ============================================================
-- Presupuestos por categoría y período.
-- ============================================================

CREATE TABLE budgets (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    category_id     BIGINT UNSIGNED NOT NULL,
    amount          DECIMAL(15,2) NOT NULL,
    spent           DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    period          ENUM('weekly', 'monthly', 'yearly') NOT NULL DEFAULT 'monthly',
    year            YEAR NOT NULL,
    month           TINYINT UNSIGNED NULL,
    week            TINYINT UNSIGNED NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_budgets_household (household_id),
    INDEX idx_budgets_category (category_id),
    INDEX idx_budgets_period (period, year, month),
    INDEX idx_budgets_active (is_active),
    
    -- Unique: un presupuesto por categoría por período
    UNIQUE KEY uk_budgets_period (household_id, category_id, period, year, month),
    
    -- Foreign Keys
    CONSTRAINT fk_budgets_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_budgets_category 
        FOREIGN KEY (category_id) REFERENCES categories(id)
        ON DELETE CASCADE ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 11. RECURRING_PAYMENTS
-- ============================================================
-- Pagos recurrentes (arriendo, servicios, suscripciones, etc.)
-- ============================================================

CREATE TABLE recurring_payments (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    account_id      BIGINT UNSIGNED NOT NULL,
    category_id     BIGINT UNSIGNED NULL,
    name            VARCHAR(100) NOT NULL,
    amount          DECIMAL(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    frequency       ENUM('weekly', 'biweekly', 'monthly', 'yearly') NOT NULL DEFAULT 'monthly',
    day_of_month    TINYINT UNSIGNED NULL,
    day_of_week     TINYINT UNSIGNED NULL,
    next_due_date   DATE NULL,
    last_executed   DATE NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    auto_execute    BOOLEAN NOT NULL DEFAULT FALSE,
    notes           TEXT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_rp_household (household_id),
    INDEX idx_rp_account (account_id),
    INDEX idx_rp_category (category_id),
    INDEX idx_rp_next_due (next_due_date),
    INDEX idx_rp_active (is_active),
    
    -- Foreign Keys
    CONSTRAINT fk_rp_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_rp_account 
        FOREIGN KEY (account_id) REFERENCES accounts(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_rp_category 
        FOREIGN KEY (category_id) REFERENCES categories(id)
        ON DELETE SET NULL ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 12. DEBTS
-- ============================================================
-- Deudas del hogar (préstamos, créditos, etc.)
-- ============================================================

CREATE TABLE debts (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    account_id      BIGINT UNSIGNED NULL,
    name            VARCHAR(100) NOT NULL,
    creditor        VARCHAR(100) NULL,
    principal       DECIMAL(15,2) NOT NULL,
    balance         DECIMAL(15,2) NOT NULL,
    interest_rate   DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    monthly_payment DECIMAL(15,2) NOT NULL,
    installments    INT UNSIGNED NULL,
    paid_installments INT UNSIGNED NOT NULL DEFAULT 0,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    start_date      DATE NOT NULL,
    due_date        DATE NULL,
    status          ENUM('active', 'paid', 'defaulted', 'restructured') NOT NULL DEFAULT 'active',
    notes           TEXT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_debts_household (household_id),
    INDEX idx_debts_account (account_id),
    INDEX idx_debts_status (status),
    INDEX idx_debts_due_date (due_date),
    
    -- Foreign Keys
    CONSTRAINT fk_debts_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_debts_account 
        FOREIGN KEY (account_id) REFERENCES accounts(id)
        ON DELETE SET NULL ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 13. DEBT_PAYMENTS
-- ============================================================
-- Pagos realizados a deudas.
-- ============================================================

CREATE TABLE debt_payments (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    debt_id         BIGINT UNSIGNED NOT NULL,
    account_id      BIGINT UNSIGNED NULL,
    amount          DECIMAL(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    date            DATE NOT NULL,
    installment     INT UNSIGNED NULL,
    principal_part  DECIMAL(15,2) NULL,
    interest_part   DECIMAL(15,2) NULL,
    notes           TEXT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_dp_debt (debt_id),
    INDEX idx_dp_account (account_id),
    INDEX idx_dp_date (date),
    
    -- Foreign Keys
    CONSTRAINT fk_dp_debt 
        FOREIGN KEY (debt_id) REFERENCES debts(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_dp_account 
        FOREIGN KEY (account_id) REFERENCES accounts(id)
        ON DELETE SET NULL ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 14. GOALS
-- ============================================================
-- Metas financieras del hogar.
-- ============================================================

CREATE TABLE goals (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    name            VARCHAR(100) NOT NULL,
    target_amount   DECIMAL(15,2) NOT NULL,
    current_amount  DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    target_date     DATE NULL,
    is_completed    BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    notes           TEXT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_goals_household (household_id),
    INDEX idx_goals_active (is_active),
    INDEX idx_goals_completed (is_completed),
    INDEX idx_goals_target_date (target_date),
    
    -- Foreign Keys
    CONSTRAINT fk_goals_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 15. GOAL_CONTRIBUTIONS
-- ============================================================
-- Aportes realizados a metas financieras.
-- ============================================================

CREATE TABLE goal_contributions (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    goal_id         BIGINT UNSIGNED NOT NULL,
    account_id      BIGINT UNSIGNED NULL,
    amount          DECIMAL(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    date            DATE NOT NULL,
    notes           TEXT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_gc_goal (goal_id),
    INDEX idx_gc_account (account_id),
    INDEX idx_gc_date (date),
    
    -- Foreign Keys
    CONSTRAINT fk_gc_goal 
        FOREIGN KEY (goal_id) REFERENCES goals(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_gc_account 
        FOREIGN KEY (account_id) REFERENCES accounts(id)
        ON DELETE SET NULL ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 16. ASSETS
-- ============================================================
-- Activos del patrimonio (vivienda, vehículo, inversiones, etc.)
-- ============================================================

CREATE TABLE assets (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    name            VARCHAR(100) NOT NULL,
    value           DECIMAL(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    acquired_date   DATE NULL,
    description     TEXT NULL,
    notes           TEXT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_assets_household (household_id),
    INDEX idx_assets_active (is_active),
    
    -- Foreign Keys
    CONSTRAINT fk_assets_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 17. LIABILITIES
-- ============================================================
-- Pasivos del patrimonio (deudas, préstamos, etc.)
-- ============================================================

CREATE TABLE liabilities (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    debt_id         BIGINT UNSIGNED NULL,
    name            VARCHAR(100) NOT NULL,
    amount          DECIMAL(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'COP',
    creditor        VARCHAR(100) NULL,
    interest_rate   DECIMAL(5,2) NULL,
    due_date        DATE NULL,
    description     TEXT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_liabilities_household (household_id),
    INDEX idx_liabilities_debt (debt_id),
    INDEX idx_liabilities_active (is_active),
    INDEX idx_liabilities_due_date (due_date),
    
    -- Foreign Keys
    CONSTRAINT fk_liabilities_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_liabilities_debt 
        FOREIGN KEY (debt_id) REFERENCES debts(id)
        ON DELETE SET NULL ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 18. NOTIFICATIONS
-- ============================================================
-- Notificaciones del sistema para el usuario.
-- ============================================================

CREATE TABLE notifications (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    user_id         BIGINT UNSIGNED NULL,
    title           VARCHAR(200) NOT NULL,
    message         TEXT NOT NULL,
    type            ENUM('info', 'warning', 'success', 'error') NOT NULL DEFAULT 'info',
    link            VARCHAR(500) NULL,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    read_at         TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_notifications_household (household_id),
    INDEX idx_notifications_user (user_id),
    INDEX idx_notifications_type (type),
    INDEX idx_notifications_read (is_read),
    INDEX idx_notifications_created (created_at),
    
    -- Foreign Keys
    CONSTRAINT fk_notifications_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_notifications_user 
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 19. AUDIT_LOG
-- ============================================================
-- Registro de auditoría para todas las operaciones importantes.
-- Tabla inmutable - solo INSERT, nunca UPDATE o DELETE.
-- ============================================================

CREATE TABLE audit_log (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    household_id    BIGINT UNSIGNED NOT NULL,
    user_id         BIGINT UNSIGNED NULL,
    entity_type     VARCHAR(50) NOT NULL,
    entity_id       BIGINT UNSIGNED NOT NULL,
    action          ENUM('create', 'update', 'delete', 'restore') NOT NULL,
    old_values      JSON NULL,
    new_values      JSON NULL,
    ip_address      VARCHAR(45) NULL,
    user_agent      VARCHAR(500) NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_audit_household (household_id),
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_entity (entity_type, entity_id),
    INDEX idx_audit_action (action),
    INDEX idx_audit_created (created_at),
    
    -- Foreign Keys
    CONSTRAINT fk_audit_household 
        FOREIGN KEY (household_id) REFERENCES households(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_audit_user 
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- VISTAS ÚTILES
-- ============================================================

-- Vista: Saldo actual de cuentas
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

-- Vista: Resumen patrimonial
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

-- Vista: Transacciones del mes actual
CREATE VIEW v_current_month_transactions AS
SELECT 
    t.*,
    a.name AS account_name,
    c.name AS category_name,
    m.name AS member_name
FROM transactions t
LEFT JOIN accounts a ON t.account_id = a.id
LEFT JOIN categories c ON t.category_id = c.id
LEFT JOIN household_members hm ON t.member_id = hm.id
LEFT JOIN users m ON hm.user_id = m.id
WHERE YEAR(t.date) = YEAR(CURDATE())
    AND MONTH(t.date) = MONTH(CURDATE())
    AND t.status = 'processed';

-- ============================================================
-- PROCEDIMIENTOS ALMACENADOS
-- ============================================================

-- Procedimiento: Actualizar saldo de cuenta después de transacción
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
    
    -- Obtener saldo actual
    SELECT current_balance INTO v_current_balance
    FROM accounts WHERE id = p_account_id;
    
    -- Calcular nuevo saldo
    IF p_is_credit THEN
        SET v_new_balance = v_current_balance + p_amount;
    ELSE
        SET v_new_balance = v_current_balance - p_amount;
    END IF;
    
    -- Actualizar saldo
    UPDATE accounts 
    SET current_balance = v_new_balance,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_account_id;
    
    -- Retornar nuevo saldo
    SELECT v_new_balance AS new_balance;
END //
DELIMITER ;

-- Procedimiento: Registrar entrada en ledger
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
