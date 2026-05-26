/**
 * BookHive — Main JavaScript
 * INF2003 Group 11
 */

document.addEventListener('DOMContentLoaded', function () {

    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm destructive actions
    const confirmForms = document.querySelectorAll('form[onsubmit]');
    confirmForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const message = form.getAttribute('onsubmit').replace("return confirm('", '').replace("');", '');
            if (!confirm(message || 'Are you sure?')) {
                e.preventDefault();
            }
        });
    });

    // Active nav link highlighting
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Search input focus on '/' keypress
    document.addEventListener('keydown', function (e) {
        if (e.key === '/' && document.activeElement.tagName !== 'INPUT' &&
            document.activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) searchInput.focus();
        }
    });

    console.log('📚 BookHive ready!');
});
