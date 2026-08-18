/**
 * auth.js - Authentication Manager
 * Manejo de autenticación y sesiones
 */
class Auth {
    constructor() {
        this.user = null;
        this.householdId = null;
    }

    async login(email, password) {
        try {
            const result = await api.login(email, password);
            this.user = result.user;
            this.householdId = result.household_id;
            storage.set('user', this.user);
            storage.set('householdId', this.householdId);
            return result;
        } catch (error) {
            throw error;
        }
    }

    async logout() {
        try {
            await api.logout();
            this.user = null;
            this.householdId = null;
            storage.remove('user');
            storage.remove('householdId');
        } catch (error) {
            throw error;
        }
    }

    async checkSession() {
        try {
            const result = await api.me();
            this.user = result.user;
            this.householdId = result.household_id;
            storage.set('user', this.user);
            storage.set('householdId', this.householdId);
            return true;
        } catch (error) {
            this.user = null;
            this.householdId = null;
            storage.remove('user');
            storage.remove('householdId');
            return false;
        }
    }

    isLoggedIn() {
        return this.user !== null;
    }

    getUser() {
        return this.user;
    }

    getHouseholdId() {
        return this.householdId;
    }
}

// Global instance
const auth = new Auth();
