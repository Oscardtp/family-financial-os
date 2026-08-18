/**
 * API Client para Family Financial OS.
 * Maneja todas las llamadas HTTP al backend.
 */
class ApiClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async request(method, path, data = null) {
        const url = `${this.baseUrl}${path}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Para enviar cookies de sesión
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        const json = await response.json();

        if (!response.ok || !json.success) {
            throw new Error(json.error?.message || 'Error desconocido');
        }

        return json.data;
    }

    // ═══════════════════════════════════════════════════
    // AUTH
    // ═══════════════════════════════════════════════════

    async login(email, password) {
        return this.request('POST', '/api/v1/auth/login', { email, password });
    }

    async logout() {
        return this.request('POST', '/api/v1/auth/logout');
    }

    async me() {
        return this.request('GET', '/api/v1/auth/me');
    }

    // ═══════════════════════════════════════════════════
    // ACCOUNTS
    // ═══════════════════════════════════════════════════

    async getAccounts(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request('GET', `/api/v1/accounts${params ? '?' + params : ''}`);
    }

    async getAccount(id) {
        return this.request('GET', `/api/v1/accounts/${id}`);
    }

    async createAccount(data) {
        return this.request('POST', '/api/v1/accounts', data);
    }

    async getAccountBalance(id) {
        return this.request('GET', `/api/v1/accounts/${id}/balance`);
    }

    // ═══════════════════════════════════════════════════
    // TRANSACTIONS
    // ═══════════════════════════════════════════════════

    async getTransactions(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request('GET', `/api/v1/transactions${params ? '?' + params : ''}`);
    }

    async createTransaction(data) {
        return this.request('POST', '/api/v1/transactions', data);
    }

    // ═══════════════════════════════════════════════════
    // TRANSFERS
    // ═══════════════════════════════════════════════════

    async createTransfer(data) {
        return this.request('POST', '/api/v1/transfers', data);
    }

    // ═══════════════════════════════════════════════════
    // CATEGORIES
    // ═══════════════════════════════════════════════════

    async getCategories() {
        return this.request('GET', '/api/v1/categories');
    }

    async createCategory(data) {
        return this.request('POST', '/api/v1/categories', data);
    }

    async updateCategory(id, data) {
        return this.request('PUT', `/api/v1/categories/${id}`, data);
    }

    async deleteCategory(id) {
        return this.request('DELETE', `/api/v1/categories/${id}`);
    }

    // ═══════════════════════════════════════════════════
    // BUDGETS
    // ═══════════════════════════════════════════════════

    async getBudgets(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request('GET', `/api/v1/budgets${params ? '?' + params : ''}`);
    }

    async createBudget(data) {
        return this.request('POST', '/api/v1/budgets', data);
    }

    async deleteBudget(id) {
        return this.request('DELETE', `/api/v1/budgets/${id}`);
    }

    // ═══════════════════════════════════════════════════
    // DEBTS
    // ═══════════════════════════════════════════════════

    async getDebts(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request('GET', `/api/v1/debts${params ? '?' + params : ''}`);
    }

    async createDebt(data) {
        return this.request('POST', '/api/v1/debts', data);
    }

    async addDebtPayment(id, amount) {
        return this.request('POST', `/api/v1/debts/${id}/payment`, { amount });
    }

    async deleteDebt(id) {
        return this.request('DELETE', `/api/v1/debts/${id}`);
    }

    // ═══════════════════════════════════════════════════
    // GOALS
    // ═══════════════════════════════════════════════════

    async getGoals(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request('GET', `/api/v1/goals${params ? '?' + params : ''}`);
    }

    async createGoal(data) {
        return this.request('POST', '/api/v1/goals', data);
    }

    async addGoalContribution(id, data) {
        return this.request('POST', `/api/v1/goals/${id}/contributions`, data);
    }

    async deleteGoal(id) {
        return this.request('DELETE', `/api/v1/goals/${id}`);
    }

    // ═══════════════════════════════════════════════════
    // DASHBOARD
    // ═══════════════════════════════════════════════════

    async getDashboard(from, to) {
        const params = new URLSearchParams({ from, to }).toString();
        return this.request('GET', `/api/v1/dashboard?${params}`);
    }

    async getNetWorth() {
        return this.request('GET', '/api/v1/net-worth');
    }

    // ═══════════════════════════════════════════════════
    // MEMBERS
    // ═══════════════════════════════════════════════════

    async getMembers(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request('GET', `/api/v1/members${params ? '?' + params : ''}`);
    }

    async getMember(id) {
        return this.request('GET', `/api/v1/members/${id}`);
    }

    async createMember(data) {
        return this.request('POST', '/api/v1/members', data);
    }

    async updateMember(id, data) {
        return this.request('PUT', `/api/v1/members/${id}`, data);
    }

    async deleteMember(id) {
        return this.request('DELETE', `/api/v1/members/${id}`);
    }

    // ═══════════════════════════════════════════════════
    // RECURRING PAYMENTS
    // ═══════════════════════════════════════════════════

    async getRecurringPayments(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request('GET', `/api/v1/recurring-payments${params ? '?' + params : ''}`);
    }

    async getRecurringPayment(id) {
        return this.request('GET', `/api/v1/recurring-payments/${id}`);
    }

    async createRecurringPayment(data) {
        return this.request('POST', '/api/v1/recurring-payments', data);
    }

    async deleteRecurringPayment(id) {
        return this.request('DELETE', `/api/v1/recurring-payments/${id}`);
    }

    // ═══════════════════════════════════════════════════
    // ASSETS
    // ═══════════════════════════════════════════════════

    async getAssets() {
        return this.request('GET', '/api/v1/assets');
    }

    async getAsset(id) {
        return this.request('GET', `/api/v1/assets/${id}`);
    }

    async createAsset(data) {
        return this.request('POST', '/api/v1/assets', data);
    }

    async updateAsset(id, data) {
        return this.request('PUT', `/api/v1/assets/${id}`, data);
    }

    async deleteAsset(id) {
        return this.request('DELETE', `/api/v1/assets/${id}`);
    }

    // ═══════════════════════════════════════════════════
    // LIABILITIES
    // ═══════════════════════════════════════════════════

    async getLiabilities() {
        return this.request('GET', '/api/v1/liabilities');
    }

    async getLiability(id) {
        return this.request('GET', `/api/v1/liabilities/${id}`);
    }

    async createLiability(data) {
        return this.request('POST', '/api/v1/liabilities', data);
    }

    async updateLiability(id, data) {
        return this.request('PUT', `/api/v1/liabilities/${id}`, data);
    }

    async deleteLiability(id) {
        return this.request('DELETE', `/api/v1/liabilities/${id}`);
    }
}

// Instancia global
const api = new ApiClient();
