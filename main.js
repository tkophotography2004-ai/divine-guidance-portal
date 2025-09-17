// Divine Talks with Zahrah Imani - Main JavaScript
// Mobile-optimized interactive functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive components
    initializeAnimations();
    initializeMobileOptimizations();
    initializeFormValidation();
    initializeBookingSystem();
    initializePaymentHandling();

    console.log('Divine Talks application initialized ✨');
});

// Animation and Visual Effects
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe all animated elements
    document.querySelectorAll('.animate-fadeInUp, .animate-float, .spiritual-card').forEach(el => {
        observer.observe(el);
    });

    // Pulse glow effect for CTAs
    const pulseElements = document.querySelectorAll('.animate-pulse-glow');
    pulseElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            el.style.transform = 'scale(1.05)';
            el.style.boxShadow = '0 0 30px rgba(255, 215, 0, 0.6)';
        });

        el.addEventListener('mouseleave', () => {
            el.style.transform = 'scale(1)';
            el.style.boxShadow = 'none';
        });
    });
}

// Mobile Optimizations
function initializeMobileOptimizations() {
    const isMobile = window.innerWidth <= 768;

    if (isMobile) {
        // Optimize touch interactions
        document.body.classList.add('mobile-optimized');

        // Add touch-friendly hover states
        document.querySelectorAll('.btn, .card, .nav-link').forEach(el => {
            el.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            });

            el.addEventListener('touchend', function() {
                setTimeout(() => this.classList.remove('touch-active'), 300);
            });
        });

        // Optimize navbar for mobile
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            let lastScrollY = window.scrollY;

            window.addEventListener('scroll', () => {
                const currentScrollY = window.scrollY;

                if (currentScrollY > lastScrollY && currentScrollY > 100) {
                    navbar.style.transform = 'translateY(-100%)';
                } else {
                    navbar.style.transform = 'translateY(0)';
                }

                lastScrollY = currentScrollY;
            });
        }
    }

    // Handle orientation changes
    window.addEventListener('orientationchange', () => {
        setTimeout(() => {
            window.scrollTo(0, window.scrollY + 1);
            window.scrollTo(0, window.scrollY - 1);
        }, 500);
    });
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showFormErrors(this);
            }
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => clearFieldError(input));
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    // Custom validations
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });

    return isValid;
}

function validateField(field) {
    clearFieldError(field);

    if (field.hasAttribute('required') && !field.value.trim()) {
        showFieldError(field, 'This field is required');
        return false;
    }

    if (field.type === 'email' && field.value && !isValidEmail(field.value)) {
        showFieldError(field, 'Please enter a valid email address');
        return false;
    }

    return true;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');

    let errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        field.parentNode.appendChild(errorElement);
    }

    errorElement.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showFormErrors(form) {
    const firstError = form.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
    }
}

// Booking System
function initializeBookingSystem() {
    const bookingForm = document.getElementById('booking-form');
    if (!bookingForm) return;

    const sessionButtons = document.querySelectorAll('.select-session');
    const dateInput = document.getElementById('booking_date');
    const timeSelect = document.getElementById('booking_time');

    // Set minimum date to today
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.min = today;

        // Update available times when date changes
        dateInput.addEventListener('change', updateAvailableTimes);
    }

    // Session type selection
    sessionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sessionType = this.dataset.session;
            const price = this.dataset.price;

            // Update form
            const sessionSelect = document.getElementById('session_type');
            if (sessionSelect) {
                sessionSelect.value = sessionType;
            }

            // Update UI
            sessionButtons.forEach(btn => {
                btn.closest('.card').classList.remove('border-divine-gold', 'selected');
            });

            this.closest('.card').classList.add('border-divine-gold', 'selected');

            // Show selection feedback
            showNotification(`Selected: ${sessionType.replace('_', ' ').replace(/\w/g, l => l.toUpperCase())} Session - $${price}`, 'success');
        });
    });
}

function updateAvailableTimes() {
    const dateInput = document.getElementById('booking_date');
    const timeSelect = document.getElementById('booking_time');

    if (!dateInput || !timeSelect) return;

    const selectedDate = new Date(dateInput.value);
    const dayOfWeek = selectedDate.getDay(); // 0 = Sunday, 6 = Saturday

    // Clear existing options
    timeSelect.innerHTML = '<option value="">Select a time...</option>';

    let startHour, endHour;

    // Tina's schedule: Weekdays 5:30-10pm, Weekends 8am-10pm CST
    if (dayOfWeek === 0 || dayOfWeek === 6) { // Weekend
        startHour = 8;
        endHour = 22;
    } else { // Weekday
        startHour = 17.5; // 5:30 PM
        endHour = 22;
    }

    // Generate 30-minute time slots
    for (let hour = startHour; hour < endHour; hour += 0.5) {
        const wholeHour = Math.floor(hour);
        const minutes = (hour % 1) === 0.5 ? 30 : 0;

        const time24 = `${wholeHour.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;

        // Convert to 12-hour format for display
        const displayTime = formatTime12Hour(wholeHour, minutes);

        const option = document.createElement('option');
        option.value = time24;
        option.textContent = `${displayTime} CST`;
        timeSelect.appendChild(option);
    }
}

function formatTime12Hour(hour, minutes) {
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour > 12 ? hour - 12 : (hour === 0 ? 12 : hour);
    return `${displayHour}:${minutes.toString().padStart(2, '0')} ${period}`;
}

// Payment Handling
function initializePaymentHandling() {
    const paymentForm = document.getElementById('payment-form');
    if (!paymentForm) return;

    // Add loading states to payment buttons
    const submitButton = document.getElementById('submit-payment');
    if (submitButton) {
        submitButton.addEventListener('click', function() {
            if (!this.disabled) {
                this.disabled = true;
                const originalText = this.innerHTML;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

                // Re-enable after timeout as fallback
                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = originalText;
                }, 10000);
            }
        });
    }
}

// Utility Functions
function showNotification(message, type = 'info', duration = 3000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} notification-toast`;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <span class="me-2">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
        animation: slideInRight 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Loading states
function showLoading(element, message = 'Loading...') {
    element.innerHTML = `
        <div class="d-flex align-items-center justify-content-center">
            <div class="spinner-border text-divine-gold me-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <span>${message}</span>
        </div>
    `;
}

function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
}

// Add CSS animations if not already present
if (!document.getElementById('divine-animations')) {
    const style = document.createElement('style');
    style.id = 'divine-animations';
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }

        .animate-in {
            animation: fadeInUp 0.6s ease-out forwards;
        }

        .touch-active {
            transform: scale(0.95);
            transition: transform 0.1s ease;
        }

        .mobile-optimized .btn {
            min-height: 44px;
            font-size: 16px;
        }

        .mobile-optimized .form-control {
            min-height: 44px;
            font-size: 16px;
        }

        .selected {
            transform: scale(1.02);
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
            transition: all 0.3s ease;
        }
    `;
    document.head.appendChild(style);
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Divine Talks Error:', e.error);
    showNotification('Something went wrong. Please try again.', 'error');
});

// Service worker for offline capabilities (if needed)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(error => console.log('SW registration failed'));
    });
}
