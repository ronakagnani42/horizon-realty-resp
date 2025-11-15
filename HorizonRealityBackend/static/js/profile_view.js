 document.addEventListener('DOMContentLoaded', function() {
            // Auto-dismiss alerts after 5 seconds
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 5000);
            });

            // Add subtle animation to info cards
            const infoCards = document.querySelectorAll('.info-card');
            infoCards.forEach((card, index) => {
                card.style.animation = `slideInUp 0.6s ease-out ${index * 0.1}s both`;
            });
        });

        // CSS Animation for slide in effect
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);