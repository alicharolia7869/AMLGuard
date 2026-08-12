// AMLGuard Interactive Pop Effect Suite
document.addEventListener("DOMContentLoaded", function() {
    // 1. Add tactile click pop scale effect to all buttons
    const buttons = document.querySelectorAll('.btn, .risk-pill, .nav-item a');
    buttons.forEach(btn => {
        btn.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.94)';
        });
        btn.addEventListener('mouseup', function() {
            this.style.transform = '';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });

    // 2. Add entrance pop delay for staggered grid cards
    const cards = document.querySelectorAll('.grid-4 .card, .grid-2 .card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.08}s`;
    });
});
