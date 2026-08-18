// family-financial-os/js/app.js

// ── State ──────────────────────────────────
let state = {
    currentPage: "dashboard",
    transactions: [],
    accounts: [],
    categories: [],
    budgets: [],
    debts: [],
    goals: [],
    user: null,
    householdId: null,
};

// ── Nav ──────────────────────────────────
function navigate(page) {
    state.currentPage = page;
    document.querySelectorAll(".page").forEach((el) => el.classList.remove("active"));
    const target = document.getElementById(`page-${page}`);
    if (target) target.classList.add("active");

    document.querySelectorAll(".nav-link").forEach((el) => {
        el.classList.toggle("active", el.dataset.page === page);
    });

    if (page === "dashboard") refreshDashboard();
    if (page === "transactions") refreshTransactions();
    if (page === "budgets") refreshBudgets();
    if (page === "debts") refreshDebts();
    if (page === "goals") refreshGoals();
    if (page === "accounts") refreshAccounts();
    if (page === "categories") refreshCategories();
    if (page === "assets") refreshAssets();
    if (page === "recurring") refreshRecurring();
    if (page === "members") refreshMembers();
}

// ── Format Currency ──────────────────────
function formatCurrency(amount, currency = "COP") {
    const num = parseFloat(amount);
    return num.toLocaleString("es-CO") + " " + currency;
}

// ── Dashboard ──────────────────────────────
async function refreshDashboard() {
    try {
        const [accounts, transactions, goals, debts] = await Promise.all([
            api.getAccounts(),
            api.getTransactions(),
            api.getGoals(),
            api.getDebts(),
        ]);
        state.accounts = accounts;
        state.transactions = transactions;
        state.goals = goals;
        state.debts = debts;
        renderDashboard(accounts, transactions, goals, debts);
    } catch (e) {
        console.error("Dashboard error:", e);
    }
}

function renderDashboard(accounts, transactions, goals, debts) {
    // Net worth
    const totalAssets = accounts
        .filter(a => a.nature === "asset")
        .reduce((s, a) => s + parseFloat(a.balance), 0);
    const totalLiabilities = debts
        .filter(d => d.status === "active")
        .reduce((s, d) => s + parseFloat(d.balance), 0);
    const netWorth = totalAssets - totalLiabilities;
    
    const nwEl = document.getElementById("net-worth");
    if (nwEl) {
        nwEl.textContent = formatCurrency(netWorth);
        nwEl.className = "stat-value " + (netWorth >= 0 ? "positive" : "negative");
    }

    // Cash flow (this month)
    const now = new Date();
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split("T")[0];
    const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split("T")[0];
    
    const monthTxs = transactions.filter(t => t.date >= monthStart && t.date <= monthEnd);
    const totalIncome = monthTxs
        .filter(t => t.type === "income")
        .reduce((s, t) => s + parseFloat(t.amount), 0);
    const totalExpense = monthTxs
        .filter(t => t.type === "expense")
        .reduce((s, t) => s + parseFloat(t.amount), 0);
    const cashFlow = totalIncome - totalExpense;
    
    const cfEl = document.getElementById("cash-flow");
    if (cfEl) {
        cfEl.textContent = formatCurrency(cashFlow);
        cfEl.className = "stat-value " + (cashFlow >= 0 ? "positive" : "negative");
    }

    // Savings rate
    const savingsRate = totalIncome > 0
        ? ((totalIncome - totalExpense) / totalIncome * 100).toFixed(1)
        : "0%";
    const sEl = document.getElementById("savings");
    if (sEl) sEl.textContent = savingsRate + "%";

    // Goals progress
    const goalsEl = document.getElementById("goals-summary");
    if (goalsEl) {
        const activeGoals = goals.filter(g => !g.is_completed);
        goalsEl.innerHTML = activeGoals.slice(0, 3).map(g => {
            const pct = g.percentage || 0;
            return `
                <div class="budget-row">
                    <span class="label">${g.name}</span>
                    <span class="amount">${Math.round(pct)}%</span>
                </div>
            `;
        }).join("") || "<div class='empty-state'>No hay metas activas</div>";
    }

    // Recent transactions
    const list = document.getElementById("transactions-list");
    if (list) {
        list.innerHTML = transactions.slice(0, 10).map(t => `
            <tr>
                <td>${t.date}</td>
                <td>${t.description || '-'}</td>
                <td class="${t.type === 'income' ? 'positive' : 'negative'}">${formatCurrency(t.amount)}</td>
                <td><span class="status-badge ${t.type === 'income' ? 'status-healthy' : 'status-warning'}">${t.type === 'income' ? 'Ingreso' : 'Gasto'}</span></td>
            </tr>
        `).join("") || "<tr><td colspan='4'>No hay transacciones</td></tr>";
    }
}

// ── Transactions ──────────────────────────
async function refreshTransactions() {
    try {
        const [transactions, accounts, categories] = await Promise.all([
            api.getTransactions(),
            api.getAccounts(),
            api.getCategories(),
        ]);
        state.transactions = transactions;
        state.accounts = accounts;
        state.categories = categories;
        renderTransactions(transactions, accounts, categories);
    } catch (e) {
        console.error("Transactions error:", e);
    }
}

function renderTransactions(transactions, accounts, categories) {
    const list = document.getElementById("transactions-list");
    if (list) {
        list.innerHTML = transactions.map(t => `
            <tr>
                <td>${t.date}</td>
                <td>${t.description || '-'}</td>
                <td class="${t.type === 'income' ? 'positive' : 'negative'}">${formatCurrency(t.amount)}</td>
                <td><span class="status-badge ${t.type === 'income' ? 'status-healthy' : 'status-warning'}">${t.type === 'income' ? 'Ingreso' : 'Gasto'}</span></td>
            </tr>
        `).join("") || "<tr><td colspan='4'>No hay transacciones</td></tr>";
    }

    // Populate account select
    const accountSelect = document.getElementById("tx-account");
    if (accountSelect) {
        accountSelect.innerHTML = accounts.map(a => 
            `<option value="${a.id}">${a.name}</option>`
        ).join("");
    }

    // Populate category select
    const categorySelect = document.getElementById("tx-category");
    if (categorySelect) {
        categorySelect.innerHTML = categories.map(c => 
            `<option value="${c.id}">${c.name}</option>`
        ).join("");
    }

    // Set default date
    const dateInput = document.getElementById("tx-date");
    if (dateInput) {
        dateInput.value = new Date().toISOString().split("T")[0];
    }
}

// ── Budgets ───────────────────────────────
async function refreshBudgets() {
    try {
        const [budgets, categories] = await Promise.all([
            api.getBudgets(),
            api.getCategories(),
        ]);
        state.budgets = budgets;
        state.categories = categories;
        renderBudgets(budgets, categories);
    } catch (e) {
        console.error("Budgets error:", e);
    }
}

function renderBudgets(budgets, categories) {
    const tbody = document.getElementById("budget-table");
    if (tbody) {
        tbody.innerHTML = budgets.map(b => {
            const cat = categories.find(c => c.id === b.category_id);
            const catName = cat ? cat.name : 'Sin categoría';
            const pct = b.percentage || 0;
            const status = pct >= 100 ? "EXCEEDED" : pct >= 80 ? "WARNING" : "HEALTHY";
            const statusClass = status === "HEALTHY" ? "status-healthy" : 
                status === "WARNING" ? "status-warning" : "status-exceeded";
            return `
                <tr>
                    <td>${catName}</td>
                    <td>${formatCurrency(b.amount)}</td>
                    <td>${formatCurrency(b.spent)}</td>
                    <td>${formatCurrency(b.remaining)}</td>
                    <td><span class="status-badge ${statusClass}">${Math.round(pct)}%</span></td>
                </tr>
            `;
        }).join("") || "<tr><td colspan='5'>No hay presupuestos</td></tr>";
    }
}

// ── Debts ─────────────────────────────────
async function refreshDebts() {
    try {
        const debts = await api.getDebts();
        state.debts = debts;
        renderDebts(debts);
    } catch (e) {
        console.error("Debts error:", e);
    }
}

function renderDebts(debts) {
    const list = document.getElementById("debts-list");
    if (!list) return;
    
    if (!debts || debts.length === 0) {
        list.innerHTML = '<div class="empty-state">No hay deudas registradas</div>';
        return;
    }
    
    list.innerHTML = debts.map(d => {
        const progress = d.progress || 0;
        return `
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <h3>${d.name}</h3>
                    <span class="status-badge ${d.status === 'paid' ? 'status-healthy' : 'status-exceeded'}">${d.status === 'paid' ? 'Pagada' : 'Activa'}</span>
                </div>
                <div class="budget-row"><span class="label">Saldo</span><span class="amount">${formatCurrency(d.balance)}</span></div>
                <div class="budget-row"><span class="label">Interés mensual</span><span class="amount">${d.interest_rate}%</span></div>
                <div class="budget-row"><span class="label">Pago mensual</span><span class="amount">${formatCurrency(d.monthly_payment)}</span></div>
                <div class="budget-row"><span class="label">Cuotas</span><span class="amount">${d.paid_installments}/${d.installments || '?'}</span></div>
                <div class="progress-bar">
                    <div class="progress-fill ${progress >= 100 ? 'status-healthy' : 'status-warning'}" style="width:${progress}%"></div>
                </div>
            </div>
        `;
    }).join("");
}

// ── Goals ──────────────────────────────────
async function refreshGoals() {
    try {
        const goals = await api.getGoals();
        state.goals = goals;
        renderGoals(goals);
    } catch (e) {
        console.error("Goals error:", e);
    }
}

function renderGoals(goals) {
    const list = document.getElementById("goals-list");
    if (!list) return;
    
    if (!goals || goals.length === 0) {
        list.innerHTML = '<div class="empty-state">No hay metas registradas</div>';
        return;
    }
    
    list.innerHTML = goals.map(g => {
        const progress = g.percentage || 0;
        return `
            <div class="card">
                <h3>${g.name}</h3>
                <p style="font-size:0.85rem;color:var(--text-light);">
                    ${formatCurrency(g.current_amount)} / ${formatCurrency(g.target_amount)} (${Math.round(progress)}%)
                </p>
                <div class="progress-bar">
                    <div class="progress-fill ${progress >= 100 ? 'status-healthy' : 'status-warning'}" style="width:${progress}%"></div>
                </div>
                <p style="font-size:0.8rem;color:var(--text-light);margin-top:4px;">
                    ${g.target_date ? 'Meta: ' + g.target_date : 'Sin fecha límite'}
                </p>
            </div>
        `;
    }).join("");
}

// ── Accounts ──────────────────────────────
async function refreshAccounts() {
    try {
        const accounts = await api.getAccounts();
        state.accounts = accounts;
        renderAccounts(accounts);
    } catch (e) {
        console.error("Accounts error:", e);
    }
}

function renderAccounts(accounts) {
    const list = document.getElementById("accounts-list");
    if (!list) return;
    
    list.innerHTML = accounts.map(a => `
        <div class="budget-row">
            <span class="label">${a.name} <span style="font-size:0.7rem;color:var(--text-light);">(${a.type_label})</span></span>
            <span class="amount">${formatCurrency(a.balance)}</span>
        </div>
    `).join("") || "<div class='empty-state'>No hay cuentas</div>";
}

// ── Categories ────────────────────────────
async function refreshCategories() {
    try {
        const categories = await api.getCategories();
        state.categories = categories;
        renderCategories(categories);
    } catch (e) {
        console.error("Categories error:", e);
    }
}

function renderCategories(categories) {
    const list = document.getElementById("categories-list");
    if (!list) return;
    
    list.innerHTML = categories.map(c => `
        <div class="budget-row">
            <span class="label">
                ${c.color ? `<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${c.color};margin-right:8px;"></span>` : ''}
                ${c.name}
            </span>
            <span class="amount">
                <button class="btn-small" onclick="editCategory(${c.id})">Editar</button>
                <button class="btn-small btn-danger" onclick="deleteCategory(${c.id})">Eliminar</button>
            </span>
        </div>
    `).join("") || "<div class='empty-state'>No hay categorías</div>";
}

// ── Init ──────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
    // Check if user is logged in
    try {
        const me = await api.me();
        state.user = me.user;
        state.householdId = me.household_id;
        document.getElementById("user-name").textContent = me.user.name;
    } catch (e) {
        // Not logged in, show login page
        navigate("login");
        return;
    }

    // Load initial page
    await refreshDashboard();

    // Transaction form
    const txForm = document.getElementById("transaction-form");
    if (txForm) {
        txForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const type = document.getElementById("tx-type").value;
            const accountId = document.getElementById("tx-account").value;
            const categoryId = document.getElementById("tx-category").value;
            const amount = document.getElementById("tx-amount").value;
            const description = document.getElementById("tx-description").value;
            const date = document.getElementById("tx-date").value;

            if (!amount) {
                alert("Ingrese un monto");
                return;
            }

            try {
                await api.createTransaction({
                    account_id: parseInt(accountId),
                    category_id: categoryId ? parseInt(categoryId) : null,
                    type: type,
                    amount: amount,
                    description: description,
                    date: date,
                });
                alert("Transacción registrada correctamente");
                await refreshDashboard();
            } catch (e) {
                alert("Error al registrar: " + e.message);
            }
        });
    }

    // Login form
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value;
            const password = document.getElementById("login-password").value;

            try {
                const result = await api.login(email, password);
                state.user = result.user;
                state.householdId = result.household_id;
                document.getElementById("user-name").textContent = result.user.name;
                navigate("dashboard");
            } catch (e) {
                alert("Error al iniciar sesión: " + e.message);
            }
        });
    }
});

// ── Assets ────────────────────────────────
async function refreshAssets() {
    try {
        const assets = await api.getAssets();
        state.assets = assets;
        renderAssets(assets);
    } catch (e) {
        console.error("Assets error:", e);
    }
}

function renderAssets(assets) {
    const list = document.getElementById("assets-list");
    if (!list) return;
    
    if (!assets || assets.length === 0) {
        list.innerHTML = '<div class="empty-state">No hay activos registrados</div>';
        return;
    }
    
    list.innerHTML = assets.map(a => `
        <div class="card">
            <h3>${a.name}</h3>
            <div class="budget-row"><span class="label">Valor</span><span class="amount">${formatCurrency(a.value)}</span></div>
            ${a.acquired_date ? `<div class="budget-row"><span class="label">Fecha de adquisición</span><span class="amount">${a.acquired_date}</span></div>` : ''}
            ${a.description ? `<p style="font-size:0.85rem;color:var(--text-light);margin-top:8px;">${a.description}</p>` : ''}
        </div>
    `).join("");
}

// ── Recurring Payments ────────────────────
async function refreshRecurring() {
    try {
        const recurring = await api.getRecurringPayments();
        state.recurring = recurring;
        renderRecurring(recurring);
    } catch (e) {
        console.error("Recurring error:", e);
    }
}

function renderRecurring(recurring) {
    const list = document.getElementById("recurring-list");
    if (!list) return;
    
    if (!recurring || recurring.length === 0) {
        list.innerHTML = '<div class="empty-state">No hay pagos recurrentes</div>';
        return;
    }
    
    list.innerHTML = recurring.map(r => `
        <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <h3>${r.name}</h3>
                <span class="status-badge ${r.is_active ? 'status-healthy' : 'status-exceeded'}">${r.is_active ? 'Activo' : 'Inactivo'}</span>
            </div>
            <div class="budget-row"><span class="label">Monto</span><span class="amount">${formatCurrency(r.amount)}</span></div>
            <div class="budget-row"><span class="label">Frecuencia</span><span class="amount">${r.frequency}</span></div>
            <div class="budget-row"><span class="label">Próximo vencimiento</span><span class="amount">${r.next_due_date || 'N/A'}</span></div>
            ${r.notes ? `<p style="font-size:0.85rem;color:var(--text-light);margin-top:8px;">${r.notes}</p>` : ''}
        </div>
    `).join("");
}

// ── Members ───────────────────────────────
async function refreshMembers() {
    try {
        const members = await api.getMembers();
        state.members = members;
        renderMembers(members);
    } catch (e) {
        console.error("Members error:", e);
    }
}

function renderMembers(members) {
    const list = document.getElementById("members-list");
    if (!list) return;
    
    if (!members || members.length === 0) {
        list.innerHTML = '<div class="empty-state">No hay miembros</div>';
        return;
    }
    
    list.innerHTML = members.map(m => `
        <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <h3>Usuario #${m.user_id}</h3>
                <span class="status-badge ${m.status === 'active' ? 'status-healthy' : 'status-exceeded'}">${m.status}</span>
            </div>
            <div class="budget-row"><span class="label">Rol</span><span class="amount">${m.role}</span></div>
            <div class="budget-row"><span class="label">Unido</span><span class="amount">${m.joined_at || 'N/A'}</span></div>
        </div>
    `).join("");
}

// ── Helper functions for categories ──────
async function editCategory(id) {
    const name = prompt("Nuevo nombre:");
    if (name) {
        await api.updateCategory(id, { name });
        await refreshCategories();
    }
}

async function deleteCategory(id) {
    if (confirm("¿Eliminar esta categoría?")) {
        await api.deleteCategory(id);
        await refreshCategories();
    }
}

// ── Reports ─────────────────────────────
async function loadMonthlyReport() {
    const monthInput = document.getElementById("report-month");
    const [year, month] = monthInput.value.split("-");
    
    try {
        const response = await fetch(`/api/v1/reports/monthly/${year}/${month}`);
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            const reportDiv = document.getElementById("monthly-report");
            reportDiv.innerHTML = `
                <div class="report-summary">
                    <div class="budget-row">
                        <span class="label">Ingresos</span>
                        <span class="amount positive">${formatCurrency(data.data.total_income)}</span>
                    </div>
                    <div class="budget-row">
                        <span class="label">Gastos</span>
                        <span class="amount negative">${formatCurrency(data.data.total_expenses)}</span>
                    </div>
                    <div class="budget-row">
                        <span class="label">Neto</span>
                        <span class="amount ${data.data.net_income >= 0 ? 'positive' : 'negative'}">${formatCurrency(data.data.net_income)}</span>
                    </div>
                </div>
            `;
        }
    } catch (e) {
        console.error("Report error:", e);
    }
}

async function loadExpensesByCategory() {
    try {
        const response = await fetch("/api/v1/reports/expenses-by-category");
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            const reportDiv = document.getElementById("category-report");
            reportDiv.innerHTML = `
                <div class="report-summary">
                    ${data.data.categories.map(c => `
                        <div class="budget-row">
                            <span class="label">${c.name}</span>
                            <span class="amount">${formatCurrency(c.amount)} (${c.percentage}%)</span>
                        </div>
                    `).join("") || "<div class='empty-state'>No hay gastos este período</div>"}
                </div>
            `;
        }
    } catch (e) {
        console.error("Report error:", e);
    }
}

async function loadIncomeVsExpenses() {
    try {
        const response = await fetch("/api/v1/reports/income-vs-expenses");
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            const reportDiv = document.getElementById("income-expense-report");
            reportDiv.innerHTML = `
                <div class="report-summary">
                    <div class="budget-row">
                        <span class="label">Total Ingresos</span>
                        <span class="amount positive">${formatCurrency(data.data.totals.income)}</span>
                    </div>
                    <div class="budget-row">
                        <span class="label">Total Gastos</span>
                        <span class="amount negative">${formatCurrency(data.data.totals.expenses)}</span>
                    </div>
                    <div class="budget-row">
                        <span class="label">Ahorro Total</span>
                        <span class="amount">${formatCurrency(data.data.totals.savings)}</span>
                    </div>
                </div>
            `;
        }
    } catch (e) {
        console.error("Report error:", e);
    }
}

async function loadNetWorthReport() {
    try {
        const response = await fetch("/api/v1/reports/net-worth");
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            const reportDiv = document.getElementById("net-worth-report");
            reportDiv.innerHTML = `
                <div class="report-summary">
                    <div class="budget-row">
                        <span class="label">Activos</span>
                        <span class="amount positive">${formatCurrency(data.data.assets)}</span>
                    </div>
                    <div class="budget-row">
                        <span class="label">Pasivos</span>
                        <span class="amount negative">${formatCurrency(data.data.liabilities)}</span>
                    </div>
                    <div class="budget-row">
                        <span class="label">Patrimonio Neto</span>
                        <span class="amount ${data.data.net_worth >= 0 ? 'positive' : 'negative'}">${formatCurrency(data.data.net_worth)}</span>
                    </div>
                </div>
            `;
        }
    } catch (e) {
        console.error("Report error:", e);
    }
}

// ── Export ──────────────────────────────
function exportData(type, format) {
    const url = `/api/v1/export/${type}?format=${format}`;
    
    if (format === 'json') {
        // For JSON, open in new window
        window.open(url, '_blank');
    } else {
        // For CSV, trigger download
        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}
