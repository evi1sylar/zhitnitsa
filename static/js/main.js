document.addEventListener('DOMContentLoaded', () => {
    // Анимация появления элементов при скролле
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });

    document.querySelectorAll('.product-card, .review-card, .feature-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Выпадающее меню "Изменить"
    const adminDropdown = document.querySelector('.nav__dropdown');
    if (adminDropdown) {
        const toggle = adminDropdown.querySelector('.nav__dropdown-toggle');
        if (toggle) {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                adminDropdown.classList.toggle('active');
            });

            // Закрыть меню при клике вне его
            document.addEventListener('click', (e) => {
                if (!adminDropdown.contains(e.target)) {
                    adminDropdown.classList.remove('active');
                }
            });
        }
    }

    // Отзывы — AJAX отправка
    const reviewForm = document.querySelector('.review-form form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(reviewForm);
            try {
                const resp = await fetch(reviewForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                });
                if (resp.ok) {
                    reviewForm.reset();
                    showToast('Спасибо за отзыв! Он появится на странице.');
                    setTimeout(() => location.reload(), 1000);
                }
            } catch (err) {
                showToast('Ошибка отправки. Попробуйте ещё раз.', true);
            }
        });
    }

    // Рейтинг — звёздочки
    const ratingInputs = document.querySelectorAll('.rating-stars input');
    if (ratingInputs.length) {
        const labels = document.querySelectorAll('.rating-stars label');
        labels.forEach(label => {
            label.addEventListener('click', () => {
                const starEl = label.closest('.rating-stars');
                starEl.querySelectorAll('label').forEach(l => l.classList.remove('selected'));
                label.classList.add('selected');
                let prev = label.previousElementSibling;
                while (prev) {
                    if (prev.tagName === 'LABEL') prev.classList.add('selected');
                    prev = prev.previousElementSibling;
                }
            });
        });
    }

    // Плавный скролл для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Удаление продукта — подтверждение
    document.querySelectorAll('.btn--danger[data-confirm]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (!confirm('Точно удалить этот продукт?')) {
                e.preventDefault();
            }
        });
    });
});

function showToast(message, isError = false) {
    const toast = document.createElement('div');
    toast.className = 'toast' + (isError ? ' toast--error' : '');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed; bottom: 30px; right: 30px;
        background: ${isError ? '#e74c3c' : '#27ae60'};
        color: white; padding: 14px 24px; border-radius: 12px;
        font-weight: 600; z-index: 9999;
        box-shadow: 0 6px 24px rgba(0,0,0,0.2);
        animation: toastIn 0.3s ease, toastOut 0.3s ease 2.7s forwards;
    `;
    document.body.appendChild(toast);
    setTimeout(() => document.body.removeChild(toast), 3200);
}

// CSS-анимация тоста (вставляется динамически)
const toastStyles = document.createElement('style');
toastStyles.textContent = `
    @keyframes toastIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes toastOut { from { opacity: 1; transform: translateY(0); } to { opacity: 0; transform: translateY(20px); } }
`;
document.head.appendChild(toastStyles);
