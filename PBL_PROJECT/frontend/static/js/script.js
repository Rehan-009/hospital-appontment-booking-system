/**
 * MediCare Hospital Appointment Booking System (HABS)
 * Core Client-side Interactivity & Authentication
 */

document.addEventListener('DOMContentLoaded', () => {
    initAuthModal();
    initUrlParams();
    initPasswordToggles();
});

/* ================= TOAST NOTIFICATION SYSTEM ================= */
function showToast(title, message, type = 'info', duration = 4000) {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const iconMap = {
        success: 'fa-circle-check',
        error: 'fa-circle-xmark',
        warning: 'fa-triangle-exclamation',
        info: 'fa-circle-info'
    };

    const icon = iconMap[type] || 'fa-bell';

    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fa-solid ${icon}"></i>
        </div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button type="button" class="toast-close" onclick="this.parentElement.remove()">
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        if (toast && toast.parentElement) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

/* ================= AUTHENTICATION MODAL ================= */
function initAuthModal() {
    const modalOverlay = document.getElementById('authModal');
    if (!modalOverlay) return;

    const openBtns = document.querySelectorAll('.open-login-btn');
    const closeBtn = document.getElementById('closeAuthModal');
    const tabBtns = document.querySelectorAll('.modal-tab-btn');
    const loginForm = document.getElementById('modalLoginForm');
    const registerForm = document.getElementById('modalRegisterForm');

    // Open Modal
    openBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const tab = btn.dataset.tab || 'login';
            openModal(tab);
        });
    });

    // Close Modal
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });

    // Tab Switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            const targetTab = btn.dataset.tab;
            const targetPane = document.getElementById(`${targetTab}TabPane`);
            if (targetPane) targetPane.classList.add('active');
        });
    });

    // Demo Fill Buttons
    const demoPatientBtn = document.getElementById('demoPatientBtn');
    const demoDoctorBtn = document.getElementById('demoDoctorBtn');

    if (demoPatientBtn) {
        demoPatientBtn.addEventListener('click', () => {
            document.getElementById('loginIdentifier').value = 'patient@gmail.com';
            document.getElementById('loginPassword').value = '1234';
            showToast('Demo Credential Filled', 'Filled Patient: patient@gmail.com / 1234', 'info', 2500);
        });
    }

    if (demoDoctorBtn) {
        demoDoctorBtn.addEventListener('click', () => {
            document.getElementById('loginIdentifier').value = 'doctor@gmail.com';
            document.getElementById('loginPassword').value = '1234';
            showToast('Demo Credential Filled', 'Filled Doctor: doctor@gmail.com / 1234', 'info', 2500);
        });
    }

    // Login Form Submit
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            const identifier = document.getElementById('loginIdentifier').value.trim();
            const password = document.getElementById('loginPassword').value;

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Authenticating...';

                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: identifier, password: password })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    showToast('Login Successful', data.message || 'Redirecting to your dashboard...', 'success', 2000);
                    setTimeout(() => {
                        window.location.href = data.redirect || '/patient';
                    }, 800);
                } else {
                    showToast('Login Failed', data.message || 'Invalid credentials.', 'error');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            } catch (err) {
                showToast('Network Error', 'Could not reach server. Please try again.', 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    // Register Form Submit
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            const fullName = document.getElementById('regFullName').value.trim();
            const email = document.getElementById('regEmail').value.trim();
            const phone = document.getElementById('regPhone').value.trim();
            const role = document.getElementById('regRole').value;
            const age = document.getElementById('regAge').value;
            const gender = document.getElementById('regGender').value;
            const password = document.getElementById('regPassword').value;
            const confirmPassword = document.getElementById('regConfirmPassword').value;

            if (password !== confirmPassword) {
                showToast('Password Mismatch', 'Password and Confirm Password must match.', 'warning');
                return;
            }

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creating Account...';

                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        fullName, email, phone, role, age, gender, password, confirmPassword
                    })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    showToast('Welcome to MediCare', 'Account registered successfully! Redirecting...', 'success', 2000);
                    setTimeout(() => {
                        window.location.href = data.redirect || '/patient';
                    }, 800);
                } else {
                    showToast('Registration Error', data.message || 'Could not complete registration.', 'error');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            } catch (err) {
                showToast('Network Error', 'Server error. Please try again.', 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }
}

function openModal(tab = 'login') {
    const modalOverlay = document.getElementById('authModal');
    if (!modalOverlay) return;
    
    modalOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Switch to target tab
    const targetTabBtn = document.querySelector(`.modal-tab-btn[data-tab="${tab}"]`);
    if (targetTabBtn) targetTabBtn.click();
}

function closeModal() {
    const modalOverlay = document.getElementById('authModal');
    if (!modalOverlay) return;
    modalOverlay.classList.remove('active');
    document.body.style.overflow = 'auto';
}

/* ================= URL PARAMETERS CHECK ================= */
function initUrlParams() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('login') === 'open') {
        openModal('login');
    } else if (params.get('register') === 'open') {
        openModal('register');
    } else if (params.get('login') === 'required') {
        openModal('login');
        showToast('Login Required', 'Please sign in or create an account to proceed.', 'warning', 4000);
    }
}

/* ================= PASSWORD VISIBILITY TOGGLE ================= */
function initPasswordToggles() {
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.previousElementSibling;
            if (!input) return;
            const icon = btn.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                if (icon) {
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                }
            } else {
                input.type = 'password';
                if (icon) {
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            }
        });
    });
}
