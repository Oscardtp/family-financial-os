/**
 * reports.js - Reports Module
 * Reportes y análisis financiero
 */
const reports = {
    async loadMonthly() {
        const monthInput = document.getElementById('report-month');
        const [year, month] = monthInput.value.split('-');
        
        try {
            const data = await api.getMonthlyReport(year, month);
            const reportDiv = document.getElementById('monthly-report');
            reportDiv.innerHTML = `
                <div class="report-result">
                    <div class="report-row">
                        <span class="report-label">Ingresos</span>
                        <span class="report-value positive">${formatCurrency(data.data.total_income)}</span>
                    </div>
                    <div class="report-row">
                        <span class="report-label">Gastos</span>
                        <span class="report-value negative">${formatCurrency(data.data.total_expenses)}</span>
                    </div>
                    <div class="report-row">
                        <span class="report-label">Neto</span>
                        <span class="report-value ${data.data.net_income >= 0 ? 'positive' : 'negative'}">${formatCurrency(data.data.net_income)}</span>
                    </div>
                </div>
            `;
        } catch (e) {
            console.error('Report error:', e);
            toast.error('Error al cargar reporte');
        }
    },

    async loadByCategory() {
        try {
            const data = await api.getExpensesByCategory(
                new Date().toISOString().split('T')[0].slice(0, 7) + '-01',
                new Date().toISOString().split('T')[0]
            );
            const reportDiv = document.getElementById('category-report');
            reportDiv.innerHTML = `
                <div class="report-result">
                    ${data.data.categories.map(c => `
                        <div class="report-row">
                            <span class="report-label">${c.name}</span>
                            <span class="report-value">${formatCurrency(c.amount)} (${c.percentage}%)</span>
                        </div>
                    `).join('') || '<div class="empty-state">No hay gastos este período</div>'}
                </div>
            `;
        } catch (e) {
            console.error('Report error:', e);
            toast.error('Error al cargar reporte');
        }
    },

    async loadIncomeVsExpenses() {
        try {
            const data = await api.getIncomeVsExpenses(
                new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                new Date().toISOString().split('T')[0]
            );
            const reportDiv = document.getElementById('income-expense-report');
            reportDiv.innerHTML = `
                <div class="report-result">
                    <div class="report-row">
                        <span class="report-label">Total Ingresos</span>
                        <span class="report-value positive">${formatCurrency(data.data.totals.income)}</span>
                    </div>
                    <div class="report-row">
                        <span class="report-label">Total Gastos</span>
                        <span class="report-value negative">${formatCurrency(data.data.totals.expenses)}</span>
                    </div>
                    <div class="report-row">
                        <span class="report-label">Ahorro Total</span>
                        <span class="report-value">${formatCurrency(data.data.totals.savings)}</span>
                    </div>
                </div>
            `;
        } catch (e) {
            console.error('Report error:', e);
            toast.error('Error al cargar reporte');
        }
    },

    async loadNetWorth() {
        try {
            const data = await api.getNetWorthReport(
                new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                new Date().toISOString().split('T')[0]
            );
            const reportDiv = document.getElementById('net-worth-report');
            reportDiv.innerHTML = `
                <div class="report-result">
                    <div class="report-row">
                        <span class="report-label">Activos</span>
                        <span class="report-value positive">${formatCurrency(data.data.assets)}</span>
                    </div>
                    <div class="report-row">
                        <span class="report-label">Pasivos</span>
                        <span class="report-value negative">${formatCurrency(data.data.liabilities)}</span>
                    </div>
                    <div class="report-row">
                        <span class="report-label">Patrimonio Neto</span>
                        <span class="report-value ${data.data.net_worth >= 0 ? 'positive' : 'negative'}">${formatCurrency(data.data.net_worth)}</span>
                    </div>
                </div>
            `;
        } catch (e) {
            console.error('Report error:', e);
            toast.error('Error al cargar reporte');
        }
    }
};
