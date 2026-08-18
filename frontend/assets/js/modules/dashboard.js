/**
 * dashboard.js - Dashboard Module
 * Lógica del dashboard principal
 */
const dashboard = {
    async refresh() {
        try {
            const data = await api.getDashboard();
            this.render(data);
        } catch (e) {
            console.error('Dashboard error:', e);
            toast.error('Error al cargar dashboard');
        }
    },

    render(data) {
        const summary = data.summary || {};
        const accounts = data.accounts || [];
        const transactions = data.transactions || [];
        const goals = data.goals || [];
        const debts = data.debts || [];

        const netWorth = parseFloat(summary.net_worth || 0);
        const nwEl = document.getElementById('net-worth');
        if (nwEl) {
            nwEl.textContent = formatCurrency(netWorth);
            nwEl.className = 'stat-value ' + (netWorth >= 0 ? 'positive' : 'negative');
        }

        const incomeEl = document.getElementById('income');
        if (incomeEl) incomeEl.textContent = formatCurrency(parseFloat(summary.income || 0));

        const expensesEl = document.getElementById('expenses');
        if (expensesEl) expensesEl.textContent = formatCurrency(parseFloat(summary.expenses || 0));

        const savingsRate = summary.income && parseFloat(summary.income) > 0
            ? ((parseFloat(summary.income) - parseFloat(summary.expenses)) / parseFloat(summary.income) * 100).toFixed(1)
            : '0%';
        const sEl = document.getElementById('savings-rate');
        if (sEl) sEl.textContent = savingsRate + '%';

        const goalsEl = document.getElementById('dashboard-goals');
        if (goalsEl) {
            const activeGoals = goals.filter(g => !g.is_completed);
            goalsEl.innerHTML = activeGoals.slice(0, 3).map(g => {
                const pct = g.percentage || 0;
                return `
                    <div class="budget-row">
                        <span class="budget-label">${g.name}</span>
                        <span class="budget-amount">${Math.round(pct)}%</span>
                    </div>
                `;
            }).join('') || '<div class="empty-state">No hay metas activas</div>';
        }

        const list = document.getElementById('dashboard-transactions');
        if (list) {
            list.innerHTML = transactions.slice(0, 10).map(t => `
                <tr>
                    <td>${t.date}</td>
                    <td>${t.description || '-'}</td>
                    <td class="${t.type === 'income' ? 'positive' : 'negative'}">${formatCurrency(t.amount)}</td>
                    <td><span class="badge ${t.type === 'income' ? 'badge-success' : 'badge-warning'}">${t.type === 'income' ? 'Ingreso' : 'Gasto'}</span></td>
                </tr>
            `).join('') || '<tr><td colspan="4">No hay transacciones</td></tr>';
        }

        const cashFlowEl = document.getElementById('cash-flow-chart');
        if (cashFlowEl && data.cash_flow) {
            cashFlowEl.innerHTML = data.cash_flow.map(m => `
                <div class="cash-flow-bar">
                    <span class="cf-month">${m.month}</span>
                    <div class="cf-values">
                        <span class="cf-income">${formatCurrency(parseFloat(m.income))}</span>
                        <span class="cf-expense">${formatCurrency(parseFloat(m.expenses))}</span>
                    </div>
                </div>
            `).join('');
        }

        const upcomingEl = document.getElementById('upcoming-payments');
        if (upcomingEl && data.upcoming_payments) {
            upcomingEl.innerHTML = data.upcoming_payments.slice(0, 5).map(p => `
                <div class="upcoming-item">
                    <span class="upcoming-name">${p.name}</span>
                    <span class="upcoming-amount">${formatCurrency(parseFloat(p.amount))}</span>
                    <span class="upcoming-date">${p.next_due_date}</span>
                </div>
            `).join('') || '<div class="empty-state">No hay pagos próximos</div>';
        }
    },

    async initQuickExpense() {
        const btn = document.getElementById('btn-quick-expense');
        const form = document.getElementById('quick-expense-form');
        if (!btn || !form) return;

        const categories = await api.getCategories();
        const catSelect = document.getElementById('qe-category');
        if (catSelect) {
            catSelect.innerHTML = categories
                .filter(c => c.type === 'expense')
                .map(c => `<option value="${c.id}">${c.name}</option>`)
                .join('');
        }

        btn.addEventListener('click', async () => {
            const amount = document.getElementById('qe-amount').value;
            const category_id = document.getElementById('qe-category').value;
            if (!amount || !category_id) {
                toast.error('Monto y categoría son requeridos');
                return;
            }
            try {
                await api.createQuickExpense({ amount, category_id });
                toast.success('Gasto rápido registrado');
                form.reset();
                this.refresh();
            } catch (e) {
                toast.error('Error al registrar gasto');
            }
        });
    }
};
