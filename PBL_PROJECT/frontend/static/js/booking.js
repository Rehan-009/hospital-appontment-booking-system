/**
 * MediCare Hospital Appointment Booking System (HABS)
 * Booking Flow & Simulated Payment Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    initSchedulePage();
    initPaymentPage();
});

/* ================= SCHEDULE APPOINTMENT PAGE ================= */
function initSchedulePage() {
    const dateInput = document.getElementById('appointmentDateInput');
    const slotsGrid = document.getElementById('slotsGrid');
    const doctorId = document.getElementById('doctorIdHolder')?.value;
    const selectedTimeInput = document.getElementById('selectedTimeInput');
    const continueBtn = document.getElementById('continueToSummaryBtn');

    if (!dateInput || !doctorId) return;

    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
    if (!dateInput.value) {
        dateInput.value = today;
    }

    // Load initial slots
    loadSlots(doctorId, dateInput.value);

    // Date change listener
    dateInput.addEventListener('change', () => {
        const pickedDate = new Date(dateInput.value);
        const dayOfWeek = pickedDate.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        const dateDisplay = document.getElementById('selectedDateDisplay');
        if (dateDisplay) {
            dateDisplay.innerHTML = `<i class="fa-regular fa-calendar-check"></i> <span>${dayOfWeek}</span>`;
        }
        selectedTimeInput.value = '';
        if (continueBtn) continueBtn.disabled = true;
        loadSlots(doctorId, dateInput.value);
    });

    async function loadSlots(docId, dateStr) {
        if (!slotsGrid) return;
        slotsGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 30px; color: #64748b;">
                <i class="fa-solid fa-spinner fa-spin fa-2x"></i>
                <p style="margin-top: 10px; font-size: 14px;">Checking doctor's real-time schedule...</p>
            </div>
        `;

        try {
            const res = await fetch(`/api/doctors/${docId}/availability?date=${dateStr}`);
            const data = await res.json();

            if (res.ok && data.success) {
                renderSlots(data.data.slots);
            } else {
                slotsGrid.innerHTML = `
                    <div style="grid-column: 1/-1; text-align: center; padding: 24px; color: #ef4444; background: #fee2e2; border-radius: 8px;">
                        <i class="fa-solid fa-triangle-exclamation"></i> ${data.message || 'Unable to load slots.'}
                    </div>
                `;
            }
        } catch (err) {
            slotsGrid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 24px; color: #ef4444;">
                    Failed to fetch available time slots. Please try refreshing.
                </div>
            `;
        }
    }

    function renderSlots(slots) {
        if (!slots || slots.length === 0) {
            slotsGrid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 30px; color: #64748b;">
                    No consultation slots available for this doctor on selected date.
                </div>
            `;
            return;
        }

        slotsGrid.innerHTML = '';
        slots.forEach(slot => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `slot-btn ${slot.is_available ? 'available' : 'booked'}`;
            btn.disabled = !slot.is_available;
            btn.innerHTML = `<i class="fa-regular fa-clock" style="margin-right: 4px; font-size: 12px;"></i> ${slot.time}`;
            
            if (slot.is_available) {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                    btn.classList.add('selected');
                    selectedTimeInput.value = slot.time;
                    if (continueBtn) continueBtn.disabled = false;
                });
            }

            slotsGrid.appendChild(btn);
        });
    }

    // Schedule form validation
    const scheduleForm = document.getElementById('scheduleForm');
    if (scheduleForm) {
        scheduleForm.addEventListener('submit', (e) => {
            if (!selectedTimeInput.value) {
                e.preventDefault();
                showToast('Time Slot Required', 'Please select an available appointment time slot.', 'warning');
            }
        });
    }
}

/* ================= SUMMARY PAGE CONFIRM & CREATE ================= */
async function proceedToPaymentFromSummary(btn) {
    const doctorId = document.getElementById('summaryDoctorId').value;
    const hospitalId = document.getElementById('summaryHospitalId').value;
    const departmentId = document.getElementById('summaryDepartmentId').value;
    const dateVal = document.getElementById('summaryDate').value;
    const timeVal = document.getElementById('summaryTime').value;
    const reasonVal = document.getElementById('summaryReason').value;

    const originalText = btn.innerHTML;

    try {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Reserving Appointment Slot...';

        const res = await fetch('/api/appointments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doctorId,
                hospitalId,
                departmentId,
                date: dateVal,
                time: timeVal,
                reason: reasonVal
            })
        });

        const data = await res.json();

        if (res.status === 401) {
            // Not logged in -> open modal
            btn.disabled = false;
            btn.innerHTML = originalText;
            openModal('login');
            showToast('Sign In Required', 'Please log in to reserve and pay for your appointment.', 'info');
            return;
        }

        if (res.ok && data.success) {
            showToast('Slot Reserved', 'Redirecting to secure simulated payment...', 'success', 1500);
            setTimeout(() => {
                window.location.href = `/book/payment?appointment_id=${data.appointmentId}`;
            }, 600);
        } else {
            showToast('Booking Error', data.message || 'Slot could not be booked.', 'error');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    } catch (err) {
        showToast('Network Error', 'Server connection failure.', 'error');
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

/* ================= PAYMENT SIMULATION PAGE ================= */
function initPaymentPage() {
    const payTabs = document.querySelectorAll('.pay-tab-btn');
    const payPanels = document.querySelectorAll('.payment-panel');
    const payForm = document.getElementById('paymentForm');

    if (!payForm) return;

    // Payment method tabs
    payTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            payTabs.forEach(t => t.classList.remove('active'));
            payPanels.forEach(p => p.style.display = 'none');

            tab.classList.add('active');
            const targetMethod = tab.dataset.method;
            const targetPanel = document.getElementById(`${targetMethod}Panel`);
            if (targetPanel) targetPanel.style.display = 'block';

            const methodInput = document.getElementById('selectedPaymentMethod');
            if (methodInput) methodInput.value = tab.dataset.label;
        });
    });

    // Card Input Auto Formatters & Live Card Preview
    const cardNumInput = document.getElementById('cardNumberInput');
    const cardHolderInput = document.getElementById('cardHolderInput');
    const cardExpInput = document.getElementById('cardExpiryInput');

    const cardNumDisplay = document.getElementById('cardNumPreview');
    const cardHolderDisplay = document.getElementById('cardHolderPreview');
    const cardExpDisplay = document.getElementById('cardExpiryPreview');

    if (cardNumInput) {
        cardNumInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').substring(0, 16);
            let formatted = val.match(/.{1,4}/g)?.join(' ') || '';
            e.target.value = formatted;
            if (cardNumDisplay) {
                cardNumDisplay.textContent = formatted || '•••• •••• •••• ••••';
            }
        });
    }

    if (cardHolderInput && cardHolderDisplay) {
        cardHolderInput.addEventListener('input', (e) => {
            cardHolderDisplay.textContent = e.target.value.toUpperCase() || 'YOUR NAME';
        });
    }

    if (cardExpInput && cardExpDisplay) {
        cardExpInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').substring(0, 4);
            if (val.length >= 2) {
                val = val.substring(0, 2) + '/' + val.substring(2);
            }
            e.target.value = val;
            cardExpDisplay.textContent = val || 'MM/YY';
        });
    }

    // Submit Simulated Payment
    payForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const appointmentId = document.getElementById('payAppointmentId').value;
        const paymentMethod = document.getElementById('selectedPaymentMethod').value;
        const totalAmount = document.getElementById('payTotalAmount').value;

        const overlay = document.getElementById('paymentProcessingOverlay');
        const statusText = document.getElementById('processingStatusText');

        if (overlay) overlay.classList.add('active');

        // Step 1: Gateway Simulation
        if (statusText) statusText.textContent = "Connecting to Secure Healthcare Payment Gateway...";

        await new Promise(r => setTimeout(r, 1200));

        if (statusText) statusText.textContent = `Authorizing ${paymentMethod} Transaction...`;

        await new Promise(r => setTimeout(r, 1000));

        if (statusText) statusText.textContent = "Verifying doctor schedule & confirming booking...";

        try {
            const res = await fetch('/api/payment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    appointmentId: parseInt(appointmentId),
                    paymentMethod: paymentMethod,
                    totalAmount: parseFloat(totalAmount)
                })
            });

            const data = await res.json();

            if (res.ok && data.success) {
                if (statusText) statusText.textContent = "Payment Successful! Generating Official Receipt...";
                await new Promise(r => setTimeout(r, 800));
                window.location.href = data.redirect;
            } else {
                if (overlay) overlay.classList.remove('active');
                showToast('Payment Failed', data.message || 'Payment processing was rejected.', 'error');
            }
        } catch (err) {
            if (overlay) overlay.classList.remove('active');
            showToast('Gateway Error', 'Simulated gateway timeout. Please retry.', 'error');
        }
    });
}
