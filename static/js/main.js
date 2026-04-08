// Auto-submit form when quantity selector changes
document.querySelectorAll('.qty-select').forEach(function(select) {
    select.addEventListener('change', function() {
        this.closest('form').submit();
    });
});