/**
 * transactions.js - Transactions Module
 * CRUD de transacciones
 */
const transactions = {
    async refresh() {
        try {
            const [transactionsList, accounts, categories] = await Promise.all([
                api.getTransactions(),
                api.getAccounts(),
                api.getCategories(),
            ]);
            this.render(transactionsList, accounts, categories);
        } catch (e) {
            console.error('Transactions error:', e);
            toast.error('Error al cargar transacciones');
        }
    },

    render(transactionsList, accounts, categories) {
        const list = document.getElementById('transactions-list');
        if (list) {
            list.innerHTML = transactionsList.map(t => `
                <tr>
                    <td>${t.date}</td>
                    <td>${t.description || '-'}</td>
                    <td class="${t.type === 'income' ? 'positive' : 'negative'}">${formatCurrency(t.amount)}</td>
                    <td><span class="badge ${t.type === 'income' ? 'badge-success' : 'badge-warning'}">${t.type === 'income' ? 'Ingreso' : 'Gasto'}</span></td>
                </tr>
            `).join('') || '<tr><td colspan="4">No hay transacciones</td></tr>';
        }

        // Populate account select
        const accountSelect = document.getElementById('tx-account');
        if (accountSelect) {
            accountSelect.innerHTML = accounts.map(a => 
                `<option value="${a.id}">${a.name}</option>`
            ).join('');
        }

        // Populate category select
        const categorySelect = document.getElementById('tx-category');
        if (categorySelect) {
            categorySelect.innerHTML = '<option value="">Sin categoría</option>' + categories.map(c => 
                `<option value="${c.id}">${c.name}</option>`
            ).join('');
        }

        // Set default date
        const dateInput = document.getElementById('tx-date');
        if (dateInput) {
            dateInput.value = new Date().toISOString().split('T')[0];
        }
    },

    async handleSubmit(e) {
        e.preventDefault();
        const type = document.getElementById('tx-type').value;
        const accountId = document.getElementById('tx-account').value;
        const categoryId = document.getElementById('tx-category').value;
        const amount = document.getElementById('tx-amount').value;
        const description = document.getElementById('tx-description').value;
        const date = document.getElementById('tx-date').value;

        if (!amount) {
            toast.warning('Ingrese un monto');
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
            toast.success('Transacción registrada correctamente');
            document.getElementById('transaction-form').reset();
            await dashboard.refresh();
        } catch (e) {
            toast.error('Error al registrar: ' + e.message);
        }
    }
};
