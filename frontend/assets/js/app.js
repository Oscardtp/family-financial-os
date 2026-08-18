/**
 * app.js - Main Application Entry Point
 * Inicialización y coordinación de módulos
 */

// Format currency helper
function formatCurrency(amount, currency = 'COP') {
    const num = parseFloat(amount);
    return num.toLocaleString('es-CO') + ' ' + currency;
}

// Page handlers
const pageHandlers = {
    dashboard: async () => {
        await dashboard.refresh();
        await dashboard.initQuickExpense();
    },
    transactions: () => transactions.refresh(),
    budgets: () => refreshBudgets(),
    debts: () => refreshDebts(),
    goals: () => refreshGoals(),
    accounts: () => refreshAccounts(),
    categories: () => refreshCategories(),
    assets: () => refreshAssets(),
    recurring: () => refreshRecurring(),
    members: () => refreshMembers(),
    reports: () => {},
    export: () => {}
};

// Refresh functions for each module
async function refreshBudgets() {
    try {
        const [budgets, categories] = await Promise.all([
            api.getBudgets(),
            api.getCategories(),
        ]);
        const tbody = document.getElementById('budgets-list');
        if (tbody) {
            tbody.innerHTML = budgets.map(b => {
                const cat = categories.find(c => c.id === b.category_id);
                const catName = cat ? cat.name : 'Sin categoría';
                const pct = b.percentage || 0;
                const barClass = pct >= 100 ? 'danger' : pct >= 80 ? 'warning' : 'success';
                return `
                    <tr>
                        <td>${catName}</td>
                        <td>${formatCurrency(b.amount)}</td>
                        <td>${formatCurrency(b.spent)}</td>
                        <td>${formatCurrency(b.remaining)}</td>
                        <td>
                            <div class="progress">
                                <div class="progress-bar ${barClass}" style="width:${Math.min(pct, 100)}%"></div>
                            </div>
                            <span class="badge badge-${barClass}">${Math.round(pct)}%</span>
                        </td>
                    </tr>
                `;
            }).join('') || '<tr><td colspan="5">No hay presupuestos</td></tr>';
        }
    } catch (e) {
        console.error('Budgets error:', e);
    }
}

async function refreshDebts() {
    try {
        const debts = await api.getDebts();
        const list = document.getElementById('debts-list');
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
                        <span class="badge ${d.status === 'paid' ? 'badge-success' : 'badge-danger'}">${d.status === 'paid' ? 'Pagada' : 'Activa'}</span>
                    </div>
                    <div class="budget-row"><span class="budget-label">Saldo</span><span class="budget-amount">${formatCurrency(d.balance)}</span></div>
                    <div class="budget-row"><span class="budget-label">Interés</span><span class="budget-amount">${d.interest_rate}%</span></div>
                    <div class="budget-row"><span class="budget-label">Pago mensual</span><span class="budget-amount">${formatCurrency(d.monthly_payment)}</span></div>
                    <div class="budget-row"><span class="budget-label">Cuotas</span><span class="budget-amount">${d.paid_installments}/${d.installments || '?'}</span></div>
                    <div class="progress">
                        <div class="progress-bar ${progress >= 100 ? 'success' : 'warning'}" style="width:${progress}%"></div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error('Debts error:', e);
    }
}

async function refreshGoals() {
    try {
        const goals = await api.getGoals();
        const list = document.getElementById('goals-list');
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
                    <p style="font-size:0.85rem;color:var(--text-secondary);">
                        ${formatCurrency(g.current_amount)} / ${formatCurrency(g.target_amount)} (${Math.round(progress)}%)
                    </p>
                    <div class="progress">
                        <div class="progress-bar ${progress >= 100 ? 'success' : 'warning'}" style="width:${progress}%"></div>
                    </div>
                    <p style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;">
                        ${g.target_date ? 'Meta: ' + g.target_date : 'Sin fecha límite'}
                    </p>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error('Goals error:', e);
    }
}

async function refreshAccounts() {
    try {
        const accounts = await api.getAccounts();
        const list = document.getElementById('accounts-list');
        if (!list) return;
        
        list.innerHTML = accounts.map(a => `
            <div class="card">
                <h3>${a.name}</h3>
                <p style="font-size:0.85rem;color:var(--text-secondary);">${a.type_label}</p>
                <p class="budget-amount" style="font-size:1.25rem;margin-top:8px;">${formatCurrency(a.balance)}</p>
            </div>
        `).join('') || '<div class="empty-state">No hay cuentas</div>';
    } catch (e) {
        console.error('Accounts error:', e);
    }
}

async function refreshCategories() {
    try {
        const categories = await api.getCategories();
        const tbody = document.getElementById('categories-list');
        if (!tbody) return;
        
        tbody.innerHTML = categories.map(c => `
            <tr>
                <td>${c.color ? `<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${c.color};margin-right:8px;"></span>` : ''}</td>
                <td>${c.name}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="editCategory(${c.id})">Editar</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteCategory(${c.id})">Eliminar</button>
                </td>
            </tr>
        `).join('') || '<tr><td colspan="3">No hay categorías</td></tr>';
    } catch (e) {
        console.error('Categories error:', e);
    }
}

async function refreshAssets() {
    try {
        const assets = await api.getAssets();
        const list = document.getElementById('assets-list');
        if (!list) return;
        
        if (!assets || assets.length === 0) {
            list.innerHTML = '<div class="empty-state">No hay activos registrados</div>';
            return;
        }
        
        list.innerHTML = assets.map(a => `
            <div class="card">
                <h3>${a.name}</h3>
                <div class="budget-row"><span class="budget-label">Valor</span><span class="budget-amount">${formatCurrency(a.value)}</span></div>
                ${a.acquired_date ? `<div class="budget-row"><span class="budget-label">Fecha</span><span class="budget-amount">${a.acquired_date}</span></div>` : ''}
            </div>
        `).join('');
    } catch (e) {
        console.error('Assets error:', e);
    }
}

async function refreshRecurring() {
    try {
        const recurring = await api.getRecurringPayments();
        const list = document.getElementById('recurring-list');
        if (!list) return;
        
        if (!recurring || recurring.length === 0) {
            list.innerHTML = '<div class="empty-state">No hay pagos recurrentes</div>';
            return;
        }
        
        list.innerHTML = recurring.map(r => `
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <h3>${r.name}</h3>
                    <span class="badge ${r.is_active ? 'badge-success' : 'badge-danger'}">${r.is_active ? 'Activo' : 'Inactivo'}</span>
                </div>
                <div class="budget-row"><span class="budget-label">Monto</span><span class="budget-amount">${formatCurrency(r.amount)}</span></div>
                <div class="budget-row"><span class="budget-label">Frecuencia</span><span class="budget-amount">${r.frequency}</span></div>
                <div class="budget-row"><span class="budget-label">Próximo vencimiento</span><span class="budget-amount">${r.next_due_date || 'N/A'}</span></div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Recurring error:', e);
    }
}

async function refreshMembers() {
    try {
        const members = await api.getMembers();
        const list = document.getElementById('members-list');
        if (!list) return;
        
        if (!members || members.length === 0) {
            list.innerHTML = '<div class="empty-state">No hay miembros</div>';
            return;
        }
        
        list.innerHTML = members.map(m => `
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <h3>Usuario #${m.user_id}</h3>
                    <span class="badge ${m.status === 'active' ? 'badge-success' : 'badge-danger'}">${m.status}</span>
                </div>
                <div class="budget-row"><span class="budget-label">Rol</span><span class="budget-amount">${m.role}</span></div>
                <div class="budget-row"><span class="budget-label">Unido</span><span class="budget-amount">${m.joined_at || 'N/A'}</span></div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Members error:', e);
    }
}

// Category helpers
async function editCategory(id) {
    const name = prompt('Nuevo nombre:');
    if (name) {
        await api.updateCategory(id, { name });
        await refreshCategories();
        toast.success('Categoría actualizada');
    }
}

async function deleteCategory(id) {
    if (confirm('¿Eliminar esta categoría?')) {
        await api.deleteCategory(id);
        await refreshCategories();
        toast.success('Categoría eliminada');
    }
}

// Theme toggle
function initTheme() {
    const savedTheme = storage.get('theme', 'light');
    document.documentElement.dataset.theme = savedTheme;
    
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = document.documentElement.dataset.theme;
            const next = current === 'light' ? 'dark' : 'light';
            document.documentElement.dataset.theme = next;
            storage.set('theme', next);
        });
    }
}

// Mobile menu
function initMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
        
        // Close on navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                sidebar.classList.remove('open');
            });
        });
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    initTheme();
    initMobileMenu();
    
    // Check session
    const isLoggedIn = await auth.checkSession();
    if (!isLoggedIn) {
        // Show login or redirect
        console.log('Not logged in');
        return;
    }
    
    // Update user display
    const user = auth.getUser();
    const userNameEl = document.getElementById('userName');
    if (userNameEl && user) {
        userNameEl.textContent = user.name;
    }
    
    // Listen for page changes
    window.addEventListener('pageChange', (e) => {
        const page = e.detail.page;
        if (pageHandlers[page]) {
            pageHandlers[page]();
        }
    });
    
    // Load initial page
    const initialPage = window.location.hash.slice(1) || 'dashboard';
    router.navigate(initialPage);
    
    // Transaction form
    const txForm = document.getElementById('transaction-form');
    if (txForm) {
        txForm.addEventListener('submit', transactions.handleSubmit.bind(transactions));
    }
});
