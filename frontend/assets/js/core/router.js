/**
 * router.js - SPA Router
 * Enrutamiento single-page con History API
 */
class Router {
    constructor() {
        this.routes = {};
        this.currentPage = null;
        this.init();
    }

    init() {
        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            this.navigate(window.location.hash.slice(1) || 'dashboard', false);
        });

        // Handle navigation clicks
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                if (page) this.navigate(page);
            });
        });
    }

    navigate(page, pushState = true) {
        if (!page) page = 'dashboard';
        
        // Update URL
        if (pushState) {
            window.history.pushState({ page }, '', `#${page}`);
        }

        // Hide all pages
        document.querySelectorAll('.page').forEach(el => {
            el.classList.remove('active');
        });

        // Show target page
        const target = document.getElementById(`page-${page}`);
        if (target) {
            target.classList.add('active');
        }

        // Update nav
        document.querySelectorAll('.nav-link').forEach(el => {
            el.classList.toggle('active', el.dataset.page === page);
        });

        // Update state
        this.currentPage = page;

        // Emit page change event
        window.dispatchEvent(new CustomEvent('pageChange', { detail: { page } }));
    }

    getCurrentPage() {
        return this.currentPage;
    }
}

// Global instance
const router = new Router();
