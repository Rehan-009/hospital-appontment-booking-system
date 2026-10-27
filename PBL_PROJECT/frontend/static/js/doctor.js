/**
 * MediCare Hospital Appointment Booking System (HABS)
 * Doctor Dashboard Operations & Schedule Manager
 */

document.addEventListener('DOMContentLoaded', () => {
    initDoctorAppointmentActions();
    initDoctorProfileForm();
    initDoctorPhotoUpload();
});

function initDoctorAppointmentActions() {
    document.querySelectorAll('.mark-completed-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const aptId = btn.dataset.aptId;
            const originalText = btn.innerHTML;

            if (!confirm('Mark this appointment as Completed?')) return;

            try {
                btn.disabled = true;
                btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Updating...';

                const res = await fetch(`/api/doctor/appointments/${aptId}/status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: 'Completed' })
                });

                const data = await res.json();

                if (res.ok && data.success) {
                    showToast('Status Updated', 'Appointment marked as Completed.', 'success');
                    setTimeout(() => window.location.reload(), 800);
                } else {
                    showToast('Update Failed', data.message, 'error');
                    btn.disabled = false;
                    btn.innerHTML = originalText;
                }
            } catch (err) {
                showToast('Error', 'Server error while updating status.', 'error');
                btn.disabled = false;
                btn.innerHTML = originalText;
            }
        });
    });
}

function initDoctorProfileForm() {
    const profileForm = document.getElementById('doctorProfileForm');
    if (!profileForm) return;

    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = document.getElementById('saveDoctorProfileBtn');
        const statusMsg = document.getElementById('docProfileStatusMsg');
        const originalText = submitBtn.innerHTML;

        const fullName = document.getElementById('docProfileFullName').value.trim();
        const qualification = document.getElementById('docProfileQualification').value.trim();
        const specialization = document.getElementById('docProfileSpecialization').value.trim();
        const hospitalId = document.getElementById('docProfileHospital').value;
        const departmentId = document.getElementById('docProfileDepartment').value;
        const experienceYears = parseInt(document.getElementById('docProfileExperience').value) || 0;
        const consultationFee = parseFloat(document.getElementById('docProfileFee').value) || 500;
        const availableDays = document.getElementById('docProfileDays').value.trim();
        const cabinNumber = document.getElementById('docProfileCabin').value.trim();
        const bio = document.getElementById('docProfileBio').value.trim();
        const imgInput = document.getElementById('docProfileImageUrl');
        const imageUrl = imgInput ? imgInput.value.trim() : null;

        if (!fullName || !qualification || !specialization) {
            showToast('Validation Error', 'Full name, qualifications, and specialization are required.', 'error');
            return;
        }

        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
            if (statusMsg) statusMsg.textContent = 'Saving modifications...';

            const payload = {
                fullName,
                qualification,
                specialization,
                hospitalId,
                departmentId,
                experienceYears,
                consultationFee,
                availableDays,
                cabinNumber,
                bio,
                imageUrl
            };

            const res = await fetch('/api/doctor/profile', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (res.ok && data.success) {
                showToast('Profile Updated', 'Doctor details and credentials updated successfully!', 'success');
                if (statusMsg) {
                    statusMsg.textContent = 'Saved successfully!';
                    statusMsg.style.color = '#10b981';
                }

                const doc = data.doctor;
                if (doc) {
                    // Update DOM elements across dashboard
                    const sidebarName = document.getElementById('sidebarDoctorName');
                    if (sidebarName) sidebarName.textContent = doc.full_name;

                    const sidebarDept = document.getElementById('sidebarDoctorDept');
                    if (sidebarDept) sidebarDept.textContent = doc.department_name;

                    const topbarName = document.getElementById('topbarDoctorName');
                    if (topbarName) topbarName.textContent = doc.full_name;

                    const topbarSub = document.getElementById('topbarDoctorSubtitle');
                    if (topbarSub) topbarSub.textContent = `${doc.specialization} • ${doc.hospital_name} (${doc.cabin_number})`;

                    // Update summary badges
                    const badgeHosp = document.getElementById('badgeHospitalName');
                    if (badgeHosp) badgeHosp.textContent = doc.hospital_name;

                    const badgeDept = document.getElementById('badgeDeptName');
                    if (badgeDept) badgeDept.textContent = doc.department_name;

                    const badgeFee = document.getElementById('badgeConsultationFee');
                    if (badgeFee) badgeFee.textContent = `₹${parseFloat(doc.consultation_fee).toFixed(2)}`;

                    const badgeCabin = document.getElementById('badgeCabinNumber');
                    if (badgeCabin) badgeCabin.textContent = doc.cabin_number;

                    const nameInput = document.getElementById('docProfileFullName');
                    if (nameInput) nameInput.value = doc.full_name;

                    if (doc.image_url) {
                        const sidebarAvatar = document.getElementById('sidebarDoctorAvatarContainer');
                        if (sidebarAvatar) {
                            sidebarAvatar.innerHTML = `<img id="sidebarDoctorAvatarImg" src="${doc.image_url}" alt="Doctor Avatar" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`;
                        }
                        const photoDisplay = document.getElementById('profilePhotoDisplay');
                        if (photoDisplay) {
                            photoDisplay.innerHTML = `<img id="doctorCurrentPhoto" src="${doc.image_url}" alt="Doctor Photo" style="width: 100%; height: 100%; object-fit: cover;">`;
                        }
                    }
                }
            } else {
                showToast('Update Failed', data.message || 'Unable to update doctor profile.', 'error');
                if (statusMsg) {
                    statusMsg.textContent = data.message || 'Update failed.';
                    statusMsg.style.color = '#ef4444';
                }
            }
        } catch (err) {
            console.error('Doctor profile update error:', err);
            showToast('Error', 'Server connection error while saving profile.', 'error');
            if (statusMsg) {
                statusMsg.textContent = 'Network or server error.';
                statusMsg.style.color = '#ef4444';
            }
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
            setTimeout(() => {
                if (statusMsg) statusMsg.textContent = '';
            }, 4000);
        }
    });
}

function initDoctorPhotoUpload() {
    const photoInput = document.getElementById('doctorPhotoInput');
    const selectBtn = document.getElementById('selectPhotoBtn');
    const triggerBtn = document.getElementById('triggerPhotoUploadBtn');
    const fileNameSpan = document.getElementById('photoFileName');
    const feedback = document.getElementById('photoUploadFeedback');

    if (!photoInput) return;

    if (selectBtn) {
        selectBtn.addEventListener('click', () => photoInput.click());
    }

    if (triggerBtn) {
        triggerBtn.addEventListener('click', () => photoInput.click());
    }

    photoInput.addEventListener('change', async () => {
        const file = photoInput.files[0];
        if (!file) return;

        const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif'];
        if (!validTypes.includes(file.type)) {
            showToast('Invalid File', 'Please select a valid image file (PNG, JPG, WEBP, GIF).', 'error');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            showToast('File Too Large', 'Maximum allowed image size is 5MB.', 'error');
            return;
        }

        if (fileNameSpan) {
            fileNameSpan.textContent = file.name;
        }

        // Preview locally
        const photoDisplay = document.getElementById('profilePhotoDisplay');
        const localPreviewUrl = URL.createObjectURL(file);
        if (photoDisplay) {
            photoDisplay.innerHTML = `<img id="doctorCurrentPhoto" src="${localPreviewUrl}" alt="Preview" style="width: 100%; height: 100%; object-fit: cover;">`;
        }

        const originalBtnHtml = selectBtn ? selectBtn.innerHTML : '';
        try {
            if (selectBtn) {
                selectBtn.disabled = true;
                selectBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Uploading...';
            }
            if (feedback) {
                feedback.textContent = 'Uploading photo...';
                feedback.style.color = 'var(--primary)';
            }

            const formData = new FormData();
            formData.append('photo', file);

            const res = await fetch('/api/doctor/upload-photo', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();

            if (res.ok && data.success) {
                showToast('Photo Uploaded', 'Doctor profile photo updated successfully!', 'success');
                if (feedback) {
                    feedback.textContent = 'Photo uploaded successfully!';
                    feedback.style.color = '#10b981';
                }

                if (photoDisplay) {
                    photoDisplay.innerHTML = `<img id="doctorCurrentPhoto" src="${data.imageUrl}" alt="Doctor Photo" style="width: 100%; height: 100%; object-fit: cover;">`;
                }

                const imgInput = document.getElementById('docProfileImageUrl');
                if (imgInput) {
                    imgInput.value = data.imageUrl;
                }

                const sidebarAvatar = document.getElementById('sidebarDoctorAvatarContainer');
                if (sidebarAvatar) {
                    sidebarAvatar.innerHTML = `<img id="sidebarDoctorAvatarImg" src="${data.imageUrl}" alt="Doctor Avatar" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`;
                }
            } else {
                showToast('Upload Failed', data.message || 'Could not upload photo.', 'error');
                if (feedback) {
                    feedback.textContent = data.message || 'Upload failed.';
                    feedback.style.color = '#ef4444';
                }
            }
        } catch (err) {
            console.error('Doctor photo upload error:', err);
            showToast('Error', 'Server connection error during photo upload.', 'error');
            if (feedback) {
                feedback.textContent = 'Server upload error.';
                feedback.style.color = '#ef4444';
            }
        } finally {
            if (selectBtn) {
                selectBtn.disabled = false;
                selectBtn.innerHTML = originalBtnHtml;
            }
            setTimeout(() => {
                if (feedback) feedback.textContent = '';
            }, 4500);
        }
    });
}

window.initDoctorAppointmentActions = initDoctorAppointmentActions;
window.initDoctorProfileForm = initDoctorProfileForm;
window.initDoctorPhotoUpload = initDoctorPhotoUpload;
