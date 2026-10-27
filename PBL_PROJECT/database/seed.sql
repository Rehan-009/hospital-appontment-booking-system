-- ===================================================
-- Hospital Appointment Booking System (HABS)
-- Sample Seed Data for Demo & Testing
-- ===================================================

USE hospital_db;

-- 1. Insert Demo Users
-- Passwords below are Werkzeug scrypt/pbkdf2 hashes for '1234' and 'password123'
-- Also verified in Python backend with standard check_password_hash
INSERT INTO users (id, email, phone, password_hash, role) VALUES
(1, 'patient@gmail.com', '9876543210', 'pbkdf2:sha256:600000$demo$1234', 'patient'),
(2, 'doctor@gmail.com', '9876543211', 'pbkdf2:sha256:600000$demo$1234', 'doctor'),
(3, 'patient2@gmail.com', '9876543212', 'pbkdf2:sha256:600000$demo$1234', 'patient');

-- 2. Insert Patients
INSERT INTO patients (id, user_id, full_name, age, gender, blood_group, address, emergency_contact) VALUES
(1, 1, 'Vamshi Kumar', 28, 'Male', 'O+', '45 Metro Avenue, Tech City', '9876543299'),
(2, 3, 'Sarah Jenkins', 34, 'Female', 'A+', '12 Lake View Road, Green Park', '9876543288');

-- 3. Insert Hospitals
INSERT INTO hospitals (id, name, tagline, location, address, phone, email, rating, total_reviews, image_url, description, emergency_hours) VALUES
(1, 'ApexCare Multi-Speciality Hospital', 'Excellence in Tertiary Healthcare & Research', 'Downtown Medical District', '108 Healthcare Blvd, Central District', '+91 (040) 4567-8901', 'contact@apexcare.org', 4.9, 342, '/static/images/hospital-1.png', 'ApexCare is a premier JCI-accredited tertiary care medical center known for robotic cardiology, neurosurgery, and world-class inpatient care.', '24/7 Level 1 Trauma & Emergency'),
(2, 'St. Jude Memorial Healthcare', 'Compassionate Care, Advanced Medical Technology', 'Westside Health Corridor', '74 West Park Ave, Westside Suburb', '+91 (040) 7890-1234', 'info@stjudememorial.org', 4.8, 285, '/static/images/hospital-2.png', 'St. Jude Memorial provides holistic, patient-centered clinical services featuring leading oncology, dermatology, and comprehensive wellness programs.', '24/7 Emergency & Critical Care'),
(3, 'Horizon Children & Family Hospital', 'Dedicated to Next-Generation Family Wellness', 'North City Campus', '22 North Ring Road, North Campus', '+91 (040) 2345-6789', 'care@horizonhealth.org', 4.9, 198, '/static/images/hospital-3.png', 'Horizon Hospital is specialized in pediatric critical care, radiology diagnostics, and comprehensive maternal-family medicine with specialized child facilities.', '24/7 Pediatric Emergency Care');

-- 4. Insert Departments
INSERT INTO departments (id, hospital_id, name, icon, description) VALUES
-- ApexCare Departments
(1, 1, 'Cardiology', 'fa-heart-pulse', 'Comprehensive heart care, catheterization lab, bypass surgery, and non-invasive cardiac imaging.'),
(2, 1, 'Neurology & Neurosurgery', 'fa-brain', 'Advanced diagnostics and microscopic surgical interventions for brain and spine disorders.'),
(3, 1, 'Orthopedics & Joint Care', 'fa-bone', 'Total joint replacements, sports injuries, arthroscopic surgeries, and musculoskeletal rehab.'),
(4, 1, 'General Medicine', 'fa-stethoscope', 'Primary care, preventive health check-ups, chronic lifestyle disease management, and internal medicine.'),

-- St. Jude Departments
(5, 2, 'Oncology & Cancer Care', 'fa-ribbon', 'Precision chemotherapy, surgical oncology, immunotherapy, and dedicated patient support.'),
(6, 2, 'Dermatology & Cosmetology', 'fa-hand-dots', 'Specialized skin, hair, and nail treatments, cosmetic lasers, and allergy diagnostics.'),
(7, 2, 'Cardiology', 'fa-heart-pulse', 'Preventive cardiac checkups, ECG/Echo, hypertension management, and heart failure clinics.'),
(8, 2, 'General Medicine', 'fa-stethoscope', 'General physician consultation, infectious diseases, fever clinics, and elderly healthcare.'),

-- Horizon Departments
(9, 3, 'Pediatrics & Neonatology', 'fa-baby', 'Specialized neonatal ICU, child vaccination, growth monitoring, and pediatric surgery.'),
(10, 3, 'Radiology & Imaging', 'fa-x-ray', 'High-field MRI 3.0T, 128-slice CT scans, ultrasound 4D, and digital mammography.'),
(11, 3, 'General Medicine', 'fa-stethoscope', 'Family healthcare, seasonal flu treatments, diagnostic screenings, and outpatient checkups.'),
(12, 3, 'Dermatology', 'fa-hand-dots', 'Pediatric eczema, general dermatology, and rash treatment center.');

-- 5. Insert Doctors (8 Doctors with rich profiles)
INSERT INTO doctors (id, user_id, hospital_id, department_id, full_name, qualification, specialization, experience_years, consultation_fee, available_days, bio, image_url, cabin_number, rating) VALUES
(1, 2, 1, 1, 'Dr. Rajesh Sharma', 'MD, DM (Cardiology), FACC', 'Senior Consultant Interventional Cardiologist', 16, 750.00, 'Mon, Tue, Wed, Thu, Fri, Sat', 'Dr. Rajesh Sharma has performed over 4,500 coronary interventions and specializes in complex angioplasties and preventative cardiology.', '/static/images/doctor-1.png', 'Cabin 204, 2nd Floor', 4.9),

(2, NULL, 1, 2, 'Dr. Priya Patel', 'MD, DNB (Neurology), DM', 'Chief Neurologist & Spine Specialist', 13, 800.00, 'Mon, Tue, Wed, Thu, Fri', 'Dr. Priya Patel is an internationally recognized expert in stroke rehabilitation, epilepsy management, and neuromuscular disorders.', '/static/images/doctor-2.png', 'Cabin 308, 3rd Floor', 4.9),

(3, NULL, 1, 3, 'Dr. Vikram Reddy', 'MS (Ortho), M.Ch (UK), Fellowship in Joint Replacement', 'Senior Orthopedic & Joint Replacement Surgeon', 15, 700.00, 'Mon, Wed, Fri, Sat', 'Specialist in robotic knee and hip arthroplasty, complex trauma, and sports medicine with over 15 years of surgical excellence.', '/static/images/doctor-3.png', 'Cabin 112, 1st Floor', 4.8),

(4, NULL, 1, 4, 'Dr. Arjun Mehta', 'MBBS, MD (Internal Medicine)', 'Consultant Physician & Diabetologist', 9, 500.00, 'Mon, Tue, Wed, Thu, Fri, Sat', 'Expert in comprehensive adult medicine, metabolic disorders, hypertension, and preventive health screenings.', '/static/images/doctor-4.png', 'Cabin 105, 1st Floor', 4.7),

(5, NULL, 2, 5, 'Dr. David Miller', 'MD, DM (Medical Oncology), ESMO', 'Director of Clinical Oncology', 18, 900.00, 'Tue, Wed, Thu, Fri, Sat', 'Pioneer in targeted therapies and immunotherapy with fellowship training from Memorial Sloan Kettering.', '/static/images/doctor-5.png', 'Cabin 401, 4th Floor', 4.9),

(6, NULL, 2, 6, 'Dr. Sneha Kulkarni', 'MD (Dermatology, Venereology & Leprosy)', 'Consultant Dermatologist & Dermato-Surgeon', 8, 600.00, 'Mon, Tue, Thu, Fri, Sat', 'Specialized in clinical dermatology, acne scarring, laser procedures, and pediatric skin conditions.', '/static/images/doctor-1.png', 'Cabin 210, 2nd Floor', 4.8),

(7, NULL, 3, 9, 'Dr. Ananya Sen', 'MD (Pediatrics), DCH, FAAP', 'Senior Pediatrician & Neonatologist', 12, 650.00, 'Mon, Tue, Wed, Thu, Fri, Sat', 'Compassionate pediatric specialist caring for child developmental milestones, immunizations, and newborn critical care.', '/static/images/doctor-2.png', 'Cabin 108, Pediatric Wing', 5.0),

(8, NULL, 3, 10, 'Dr. Kavita Nair', 'MD (Radiodiagnosis), FICR', 'Senior Consultant Radiologist', 11, 550.00, 'Mon, Tue, Wed, Thu, Fri', 'Extensive expertise in advanced neuro-imaging, musculoskeletal MRI, fetal ultrasound, and image-guided procedures.', '/static/images/doctor-3.png', 'Cabin B-04, Radiology Center', 4.8);

-- 6. Insert Doctor Schedules (Slots in JSON)
INSERT INTO doctor_schedules (id, doctor_id, day_of_week, start_time, end_time, slot_duration_minutes, slots_json) VALUES
(1, 1, 'ALL', '09:00 AM', '05:00 PM', 30, '["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"]'),
(2, 2, 'ALL', '09:00 AM', '05:00 PM', 30, '["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"]'),
(3, 3, 'ALL', '09:00 AM', '05:00 PM', 30, '["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"]'),
(4, 4, 'ALL', '09:00 AM', '05:00 PM', 30, '["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"]'),
(5, 5, 'ALL', '09:00 AM', '05:00 PM', 30, '["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"]'),
(6, 6, 'ALL', '09:00 AM', '05:00 PM', 30, '["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"]'),
(7, 7, 'ALL', '09:00 AM', '05:00 PM', 30, '["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"]'),
(8, 8, 'ALL', '09:00 AM', '05:00 PM', 30, '["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"]');

-- 7. Insert Initial Demo Appointment for Patient 1 (Upcoming Appointment)
INSERT INTO appointments (id, appointment_number, patient_id, doctor_id, hospital_id, department_id, appointment_date, appointment_time, reason_for_visit, status) VALUES
(1, 'APT-2026-10492', 1, 1, 1, 1, CURDATE() + INTERVAL 2 DAY, '10:30 AM', 'Routine cardiac health screening and blood pressure consultation', 'Confirmed'),
(2, 'APT-2026-09281', 1, 4, 1, 4, CURDATE() - INTERVAL 10 DAY, '02:30 PM', 'Annual executive physical examination and fasting lipid profile', 'Completed');

-- 8. Insert Payments for Demo Appointments
INSERT INTO payments (id, payment_number, appointment_id, patient_id, amount, additional_charges, total_amount, payment_method, payment_status, transaction_id) VALUES
(1, 'PAY-MED-77102', 1, 1, 750.00, 50.00, 800.00, 'UPI', 'Success', 'TXN_UPI_882940172'),
(2, 'PAY-MED-66104', 2, 1, 500.00, 50.00, 550.00, 'Credit Card', 'Success', 'TXN_CC_449201938');

-- 9. Insert Appointment History
INSERT INTO appointment_history (id, appointment_id, action, old_date, old_time, new_date, new_time, remarks) VALUES
(1, 1, 'Created', NULL, NULL, CURDATE() + INTERVAL 2 DAY, '10:30 AM', 'Initial appointment booked via online portal'),
(2, 2, 'Created', NULL, NULL, CURDATE() - INTERVAL 10 DAY, '02:30 PM', 'Appointment booked and completed successfully');

-- 10. Insert Demo Notifications
INSERT INTO notifications (id, user_id, title, message, is_read) VALUES
(1, 1, 'Appointment Confirmed', 'Your appointment with Dr. Rajesh Sharma for Cardiology has been confirmed for 10:30 AM.', 0),
(2, 1, 'Welcome to MediCare', 'Thank you for registering with MediCare Hospital Connect. Access your medical records anytime.', 1),
(3, 2, 'New Patient Appointment', 'Patient Vamshi Kumar has booked a consultation slot on your schedule.', 0);
