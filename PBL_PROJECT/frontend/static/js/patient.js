/**
 * MediCare Hospital Appointment Booking System (HABS)
 * Patient Dashboard Client Logic: Reschedule, Cancel, Tabs & Profile
 */

document.addEventListener('DOMContentLoaded', () => {
    initDashboardTabs();
    initRescheduleModal();
    initCancelModal();
    initProfileForm();
});

/* ================= DASHBOARD TABS FILTERING ================= */
function initDashboardTabs() {
    const tabBtns = document.querySelectorAll('.dash-tab-btn');
    const aptItems = document.querySelectorAll('.appointment-item-card');
    const emptyState = document.getElementById('dashEmptyState');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;
            let visibleCount = 0;

            aptItems.forEach(item => {
                const itemStatus = item.dataset.status;
                const isUpcoming = item.dataset.isUpcoming === 'true';

                let show = false;
                if (filter === 'all') {
                    show = true;
                } else if (filter === 'upcoming') {
                    show = isUpcoming && (itemStatus === 'Confirmed' || itemStatus === 'Rescheduled');
                } else if (filter === 'completed') {
                    show = itemStatus === 'Completed' || (!isUpcoming && itemStatus !== 'Cancelled');
                } else if (filter === 'cancelled') {
                    show = itemStatus === 'Cancelled';
                }

                if (show) {
                    item.style.display = 'grid';
                    visibleCount++;
                } else {
                    item.style.display = 'none';
                }
            });

            if (emptyState) {
                emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
            }
        });
    });
}

/* ================= RESCHEDULE MODAL LOGIC ================= */
let activeRescheduleAptId = null;
let activeDoctorId = null;

function openRescheduleModal(aptId, docId, docName, hospName, curDate, curTime) {
    activeRescheduleAptId = aptId;
    activeDoctorId = docId;

    const modal = document.getElementById('rescheduleModal');
    if (!modal) return;

    document.getElementById('rescheduleDocName').textContent = docName;
    document.getElementById('rescheduleHospName').textContent = hospName;
    document.getElementById('rescheduleCurrentDateTime').textContent = `${curDate} at ${curTime}`;

    const dateInput = document.getElementById('rescheduleNewDate');
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
    dateInput.value = today;

    document.getElementById('selectedRescheduleTime').value = '';
    loadRescheduleSlots(docId, dateInput.value);

    dateInput.onchange = () => {
        document.getElementById('selectedRescheduleTime').value = '';
        loadRescheduleSlots(docId, dateInput.value);
    };

    modal.classList.add('active');
}

async function loadRescheduleSlots(docId, dateStr) {
    const grid = document.getElementById('rescheduleSlotsGrid');
    const submitBtn = document.getElementById('confirmRescheduleBtn');
    if (submitBtn) submitBtn.disabled = true;

    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 20px;"><i class="fa-solid fa-spinner fa-spin"></i> Checking slots...</div>';

    try {
        const res = await fetch(`/api/doctors/${docId}/availability?date=${dateStr}`);
        const data = await res.json();

        if (res.ok && data.success) {
            grid.innerHTML = '';
            data.data.slots.forEach(slot => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = `slot-btn ${slot.is_available ? 'available' : 'booked'}`;
                btn.disabled = !slot.is_available;
                btn.textContent = slot.time;

                if (slot.is_available) {
                    btn.onclick = () => {
                        grid.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                        btn.classList.add('selected');
                        document.getElementById('selectedRescheduleTime').value = slot.time;
                        if (submitBtn) submitBtn.disabled = false;
                    };
                }

                grid.appendChild(btn);
            });
        }
    } catch (e) {
        grid.innerHTML = '<div style="color: #ef4444; grid-column: 1/-1;">Could not load slots.</div>';
    }
}

function initRescheduleModal() {
    const modal = document.getElementById('rescheduleModal');
    const closeBtn = document.getElementById('closeRescheduleModal');
    const form = document.getElementById('rescheduleForm');

    if (closeBtn) closeBtn.onclick = () => modal.classList.remove('active');
    if (modal) {
        modal.onclick = (e) => {
            if (e.target === modal) modal.classList.remove('active');
        };
    }

    if (form) {
        form.onsubmit = async (e) => {
            e.preventDefault();
            const newDate = document.getElementById('rescheduleNewDate').value;
            const newTime = document.getElementById('selectedRescheduleTime').value;
            const submitBtn = document.getElementById('confirmRescheduleBtn');

            if (!newDate || !newTime) {
                showToast('Slot Selection', 'Please pick a new date and available time slot.', 'warning');
                return;
            }

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Rescheduling...';

                const res = await fetch(`/api/appointments/${activeRescheduleAptId}/reschedule`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ newDate, newTime })
                });

                const data = await res.json();

                if (res.ok && data.success) {
                    showToast('Rescheduled', data.message, 'success');
                    modal.classList.remove('active');
                    setTimeout(() => window.location.reload(), 900);
                } else {
                    showToast('Reschedule Failed', data.message, 'error');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Confirm New Schedule';
                }
            } catch (err) {
                showToast('Error', 'Server failure. Please try again.', 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Confirm New Schedule';
            }
        };
    }
}

/* ================= CANCEL MODAL LOGIC ================= */
let activeCancelAptId = null;

function openCancelModal(aptId, aptNumber, docName, aptDate, aptTime) {
    activeCancelAptId = aptId;
    const modal = document.getElementById('cancelModal');
    if (!modal) return;

    document.getElementById('cancelAptNumber').textContent = aptNumber;
    document.getElementById('cancelDocName').textContent = docName;
    document.getElementById('cancelDateTime').textContent = `${aptDate} at ${aptTime}`;

    modal.classList.add('active');
}

function initCancelModal() {
    const modal = document.getElementById('cancelModal');
    const keepBtn = document.getElementById('keepAptBtn');
    const confirmBtn = document.getElementById('confirmCancelBtn');

    if (keepBtn) keepBtn.onclick = () => modal.classList.remove('active');
    if (modal) {
        modal.onclick = (e) => {
            if (e.target === modal) modal.classList.remove('active');
        };
    }

    if (confirmBtn) {
        confirmBtn.onclick = async () => {
            try {
                confirmBtn.disabled = true;
                confirmBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Cancellation...';

                const res = await fetch(`/api/appointments/${activeCancelAptId}/cancel`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' }
                });

                const data = await res.json();

                if (res.ok && data.success) {
                    showToast('Appointment Cancelled', data.message, 'success', 3500);
                    modal.classList.remove('active');
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    showToast('Cancellation Failed', data.message, 'error');
                    confirmBtn.disabled = false;
                    confirmBtn.innerHTML = 'Yes, Cancel Appointment';
                }
            } catch (err) {
                showToast('Error', 'Could not cancel appointment.', 'error');
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = 'Yes, Cancel Appointment';
            }
        };
    }
}

/* ================= PROFILE FORM ================= */
function initProfileForm() {
    const form = document.getElementById('patientProfileForm');
    if (!form) return;

    form.onsubmit = async (e) => {
        e.preventDefault();
        const submitBtn = form.querySelector('button[type="submit"]');

        const fullName = document.getElementById('profFullName').value.trim();
        const age = document.getElementById('profAge').value;
        const gender = document.getElementById('profGender').value;
        const bloodGroup = document.getElementById('profBloodGroup').value;
        const address = document.getElementById('profAddress').value.trim();
        const emergencyContact = document.getElementById('profEmergencyContact').value.trim();

        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving Profile...';

            const res = await fetch('/api/patient/profile', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fullName, age: parseInt(age) || null, gender, bloodGroup, address, emergencyContact
                })
            });

            const data = await res.json();

            if (res.ok && data.success) {
                showToast('Profile Saved', 'Your medical records profile has been updated.', 'success');
            } else {
                showToast('Update Failed', data.message, 'error');
            }
        } catch (err) {
            showToast('Error', 'Connection error.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Save Profile Changes';
        }
    };
}
