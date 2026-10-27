import json
import random
import string
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import query_db

class UserModel:
    @staticmethod
    def find_by_email(email):
        return query_db("SELECT * FROM users WHERE email = %s", (email.strip().lower(),), one=True)

    @staticmethod
    def find_by_phone(phone):
        return query_db("SELECT * FROM users WHERE phone = %s", (phone.strip(),), one=True)

    @staticmethod
    def find_by_id(user_id):
        return query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)

    @staticmethod
    def create(email, phone, password, role='patient'):
        pwd_hash = generate_password_hash(password)
        user_id = query_db(
            "INSERT INTO users (email, phone, password_hash, role) VALUES (%s, %s, %s, %s)",
            (email.strip().lower(), phone.strip(), pwd_hash, role),
            commit=True
        )
        return user_id

    @staticmethod
    def verify_password(stored_hash, password):
        # Support both standard werkzeug hashes and legacy quick-testing
        if stored_hash == password:
            return True
        try:
            return check_password_hash(stored_hash, password)
        except Exception:
            return False

class PatientModel:
    @staticmethod
    def find_by_user_id(user_id):
        return query_db("SELECT * FROM patients WHERE user_id = %s", (user_id,), one=True)

    @staticmethod
    def find_by_id(patient_id):
        return query_db("SELECT * FROM patients WHERE id = %s", (patient_id,), one=True)

    @staticmethod
    def create(user_id, full_name, age=None, gender=None, blood_group='O+', address=None, emergency_contact=None):
        patient_id = query_db(
            """INSERT INTO patients (user_id, full_name, age, gender, blood_group, address, emergency_contact)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (user_id, full_name.strip(), age, gender, blood_group, address, emergency_contact),
            commit=True
        )
        return patient_id

    @staticmethod
    def update_profile(patient_id, full_name, age, gender, blood_group, address, emergency_contact):
        query_db(
            """UPDATE patients 
               SET full_name = %s, age = %s, gender = %s, blood_group = %s, address = %s, emergency_contact = %s
               WHERE id = %s""",
            (full_name, age, gender, blood_group, address, emergency_contact, patient_id),
            commit=True
        )

class HospitalModel:
    @staticmethod
    def get_all(location=None, department_id=None, search=None):
        query = """
            SELECT DISTINCT h.*, 
                   COUNT(DISTINCT d.id) as doctor_count,
                   GROUP_CONCAT(DISTINCT dept.name) as department_names
            FROM hospitals h
            LEFT JOIN doctors d ON d.hospital_id = h.id
            LEFT JOIN departments dept ON dept.hospital_id = h.id
            WHERE 1=1
        """
        params = []
        if location and location != 'all':
            query += " AND h.location LIKE %s"
            params.append(f"%{location}%")
        if department_id and department_id != 'all':
            query += " AND dept.id = %s"
            params.append(department_id)
        if search:
            query += " AND (h.name LIKE %s OR h.location LIKE %s OR h.description LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            
        query += " GROUP BY h.id ORDER BY h.rating DESC, h.name ASC"
        return query_db(query, params)

    @staticmethod
    def get_by_id(hospital_id):
        hospital = query_db("SELECT * FROM hospitals WHERE id = %s", (hospital_id,), one=True)
        if hospital:
            departments = query_db("SELECT * FROM departments WHERE hospital_id = %s", (hospital_id,))
            doctors = query_db("SELECT d.*, dept.name as department_name FROM doctors d JOIN departments dept ON d.department_id = dept.id WHERE d.hospital_id = %s", (hospital_id,))
            hospital['departments'] = departments
            hospital['doctors'] = doctors
        return hospital

class DepartmentModel:
    @staticmethod
    def get_by_hospital(hospital_id):
        return query_db("SELECT * FROM departments WHERE hospital_id = %s ORDER BY name ASC", (hospital_id,))

    @staticmethod
    def get_all_distinct():
        return query_db("SELECT DISTINCT name, icon FROM departments ORDER BY name ASC")

class DoctorModel:
    @staticmethod
    def get_all(hospital_id=None, department_id=None, search=None):
        query = """
            SELECT d.*, h.name as hospital_name, h.location as hospital_location, 
                   dept.name as department_name, dept.icon as department_icon
            FROM doctors d
            JOIN hospitals h ON d.hospital_id = h.id
            JOIN departments dept ON d.department_id = dept.id
            WHERE 1=1
        """
        params = []
        if hospital_id and hospital_id != 'all':
            query += " AND d.hospital_id = %s"
            params.append(hospital_id)
        if department_id and department_id != 'all':
            query += " AND (d.department_id = %s OR dept.name LIKE %s)"
            params.extend([department_id, f"%{department_id}%"])
        if search:
            query += " AND (d.full_name LIKE %s OR d.specialization LIKE %s OR dept.name LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            
        query += " ORDER BY d.rating DESC, d.experience_years DESC"
        return query_db(query, params)

    @staticmethod
    def get_by_id(doctor_id):
        query = """
            SELECT d.*, 
                   COALESCE(h.name, 'Network Hospital') as hospital_name, 
                   COALESCE(h.location, 'Central') as hospital_location, 
                   COALESCE(h.address, '') as hospital_address, 
                   COALESCE(h.phone, '') as hospital_phone,
                   COALESCE(dept.name, 'General Medicine') as department_name, 
                   COALESCE(dept.icon, 'fa-user-doctor') as department_icon
            FROM doctors d
            LEFT JOIN hospitals h ON d.hospital_id = h.id
            LEFT JOIN departments dept ON d.department_id = dept.id
            WHERE d.id = %s
        """
        return query_db(query, (doctor_id,), one=True)

    @staticmethod
    def create(user_id, full_name, hospital_id=1, department_id=1,
               qualification='MBBS, MD', specialization='General Medicine Specialist',
               experience_years=5, consultation_fee=500.0,
               available_days='Mon, Tue, Wed, Thu, Fri, Sat',
               bio=None, image_url='/static/images/doctor-1.png',
               cabin_number='Cabin 101', rating=5.0):
        if not bio:
            bio = f"Dedicated physician specialized in clinical consultations and patient health management."

        doc_id = query_db(
            """INSERT INTO doctors (user_id, hospital_id, department_id, full_name, qualification, 
                                   specialization, experience_years, consultation_fee, available_days, 
                                   bio, image_url, cabin_number, rating)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_id, hospital_id, department_id, full_name.strip(), qualification.strip(),
             specialization.strip(), experience_years, consultation_fee, available_days.strip(),
             bio.strip(), image_url, cabin_number.strip(), rating),
            commit=True
        )

        default_slots = json.dumps([
            "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", 
            "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM", 
            "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"
        ])
        query_db(
            """INSERT INTO doctor_schedules (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes, slots_json)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (doc_id, 'ALL', '09:00 AM', '05:00 PM', 30, default_slots),
            commit=True
        )
        return doc_id

    @staticmethod
    def update_profile(doctor_id, full_name, qualification, specialization,
                       hospital_id, department_id, experience_years,
                       consultation_fee, available_days, cabin_number, bio, image_url=None):
        params = [
            full_name.strip(), qualification.strip(), specialization.strip(),
            hospital_id, department_id, experience_years, consultation_fee,
            available_days.strip(), cabin_number.strip(), bio.strip()
        ]
        
        sql = """UPDATE doctors 
                 SET full_name = %s, qualification = %s, specialization = %s, 
                     hospital_id = %s, department_id = %s, experience_years = %s, 
                     consultation_fee = %s, available_days = %s, cabin_number = %s, bio = %s"""
        
        if image_url:
            sql += ", image_url = %s"
            params.append(image_url)
            
        sql += " WHERE id = %s"
        params.append(doctor_id)

        query_db(sql, params, commit=True)

    @staticmethod
    def update_photo(doctor_id, image_url):
        query_db("UPDATE doctors SET image_url = %s WHERE id = %s", (image_url, doctor_id), commit=True)

    @staticmethod
    def find_by_user_id(user_id):
        query = """
            SELECT d.*, 
                   COALESCE(h.name, 'Network Hospital') as hospital_name, 
                   COALESCE(dept.name, 'General Medicine') as department_name
            FROM doctors d
            LEFT JOIN hospitals h ON d.hospital_id = h.id
            LEFT JOIN departments dept ON d.department_id = dept.id
            WHERE d.user_id = %s
        """
        return query_db(query, (user_id,), one=True)

    @staticmethod
    def get_availability(doctor_id, target_date_str):
        """
        Returns schedule with slot statuses (available or booked) for the target date.
        """
        schedule = query_db("SELECT * FROM doctor_schedules WHERE doctor_id = %s", (doctor_id,), one=True)
        default_slots = [
            "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", 
            "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM", 
            "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"
        ]
        
        all_slots = default_slots
        if schedule and schedule.get('slots_json'):
            try:
                all_slots = json.loads(schedule['slots_json'])
            except Exception:
                pass

        # Query all active appointments for this doctor on target date
        booked_rows = query_db(
            "SELECT appointment_time FROM appointments WHERE doctor_id = %s AND appointment_date = %s AND status != 'Cancelled'",
            (doctor_id, target_date_str)
        )
        booked_slots = set(r['appointment_time'] for r in booked_rows) if booked_rows else set()

        slots_status = []
        for s in all_slots:
            slots_status.append({
                'time': s,
                'is_available': s not in booked_slots
            })

        return {
            'doctor_id': doctor_id,
            'date': target_date_str,
            'slots': slots_status,
            'total_slots': len(all_slots),
            'available_count': len([s for s in slots_status if s['is_available']])
        }

class AppointmentModel:
    @staticmethod
    def generate_appointment_number():
        chars = ''.join(random.choices(string.digits, k=5))
        year = datetime.now().year
        return f"APT-{year}-{chars}"

    @staticmethod
    def is_slot_booked(doctor_id, apt_date, apt_time, exclude_id=None):
        query = "SELECT id FROM appointments WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s AND status != 'Cancelled'"
        params = [doctor_id, apt_date, apt_time]
        if exclude_id:
            query += " AND id != %s"
            params.append(exclude_id)
        existing = query_db(query, params, one=True)
        return existing is not None

    @staticmethod
    def create(patient_id, doctor_id, hospital_id, department_id, appointment_date, appointment_time, reason):
        apt_number = AppointmentModel.generate_appointment_number()
        
        # Check slot availability
        if AppointmentModel.is_slot_booked(doctor_id, appointment_date, appointment_time):
            raise ValueError("The selected time slot is already booked for this doctor. Please pick another slot.")

        apt_id = query_db(
            """INSERT INTO appointments (appointment_number, patient_id, doctor_id, hospital_id, department_id, appointment_date, appointment_time, reason_for_visit, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Confirmed')""",
            (apt_number, patient_id, doctor_id, hospital_id, department_id, appointment_date, appointment_time, reason),
            commit=True
        )

        # Log history
        query_db(
            """INSERT INTO appointment_history (appointment_id, action, old_date, old_time, new_date, new_time, remarks)
               VALUES (%s, 'Created', NULL, NULL, %s, %s, %s)""",
            (apt_id, appointment_date, appointment_time, 'Online booking via patient portal'),
            commit=True
        )

        return apt_id, apt_number

    @staticmethod
    def get_by_id(appointment_id):
        query = """
            SELECT a.*, 
                   p.full_name as patient_name, p.age as patient_age, p.gender as patient_gender,
                   u.phone as patient_phone, u.email as patient_email,
                   d.full_name as doctor_name, d.qualification as doctor_qualification, 
                   d.specialization as doctor_specialization, d.consultation_fee, d.cabin_number,
                   d.image_url as doctor_image,
                   h.name as hospital_name, h.location as hospital_location, h.address as hospital_address,
                   h.phone as hospital_phone, h.email as hospital_email,
                   dept.name as department_name,
                   pay.id as payment_id, pay.payment_number, pay.amount as payment_amount,
                   pay.additional_charges, pay.total_amount as payment_total,
                   pay.payment_method, pay.payment_status, pay.transaction_id, pay.created_at as payment_date
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN users u ON p.user_id = u.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN hospitals h ON a.hospital_id = h.id
            JOIN departments dept ON a.department_id = dept.id
            LEFT JOIN payments pay ON pay.appointment_id = a.id
            WHERE a.id = %s
        """
        return query_db(query, (appointment_id,), one=True)

    @staticmethod
    def get_by_number(appointment_number):
        query = """
            SELECT a.*, 
                   p.full_name as patient_name, p.age as patient_age, p.gender as patient_gender,
                   u.phone as patient_phone, u.email as patient_email,
                   d.full_name as doctor_name, d.qualification as doctor_qualification, 
                   d.specialization as doctor_specialization, d.consultation_fee, d.cabin_number,
                   d.image_url as doctor_image,
                   h.name as hospital_name, h.location as hospital_location, h.address as hospital_address,
                   h.phone as hospital_phone, h.email as hospital_email,
                   dept.name as department_name,
                   pay.id as payment_id, pay.payment_number, pay.amount as payment_amount,
                   pay.additional_charges, pay.total_amount as payment_total,
                   pay.payment_method, pay.payment_status, pay.transaction_id, pay.created_at as payment_date
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN users u ON p.user_id = u.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN hospitals h ON a.hospital_id = h.id
            JOIN departments dept ON a.department_id = dept.id
            LEFT JOIN payments pay ON pay.appointment_id = a.id
            WHERE a.appointment_number = %s
        """
        return query_db(query, (appointment_number,), one=True)

    @staticmethod
    def get_patient_appointments(patient_id, status_filter=None):
        query = """
            SELECT a.*, 
                   d.full_name as doctor_name, d.specialization as doctor_specialization,
                   d.qualification as doctor_qualification, d.image_url as doctor_image,
                   h.name as hospital_name, h.location as hospital_location,
                   dept.name as department_name,
                   pay.total_amount, pay.payment_status, pay.payment_number
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            JOIN hospitals h ON a.hospital_id = h.id
            JOIN departments dept ON a.department_id = dept.id
            LEFT JOIN payments pay ON pay.appointment_id = a.id
            WHERE a.patient_id = %s
        """
        params = [patient_id]
        if status_filter:
            if status_filter == 'Upcoming':
                query += " AND a.status IN ('Confirmed', 'Rescheduled') AND a.appointment_date >= date('now')"
            elif status_filter == 'Completed':
                query += " AND (a.status = 'Completed' OR (a.status != 'Cancelled' AND a.appointment_date < date('now')))"
            elif status_filter == 'Cancelled':
                query += " AND a.status = 'Cancelled'"
                
        query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
        return query_db(query, params)

    @staticmethod
    def get_doctor_appointments(doctor_id, date_filter=None):
        query = """
            SELECT a.*, 
                   p.full_name as patient_name, p.age as patient_age, p.gender as patient_gender,
                   u.phone as patient_phone, u.email as patient_email,
                   h.name as hospital_name, dept.name as department_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN users u ON p.user_id = u.id
            JOIN hospitals h ON a.hospital_id = h.id
            JOIN departments dept ON a.department_id = dept.id
            WHERE a.doctor_id = %s
        """
        params = [doctor_id]
        if date_filter:
            query += " AND a.appointment_date = %s"
            params.append(date_filter)
            
        query += " ORDER BY a.appointment_date ASC, a.appointment_time ASC"
        return query_db(query, params)

    @staticmethod
    def reschedule(appointment_id, new_date, new_time):
        apt = query_db("SELECT * FROM appointments WHERE id = %s", (appointment_id,), one=True)
        if not apt:
            raise ValueError("Appointment not found.")
        if apt['status'] == 'Cancelled':
            raise ValueError("Cannot reschedule a cancelled appointment.")

        # Check if slot is taken
        if AppointmentModel.is_slot_booked(apt['doctor_id'], new_date, new_time, exclude_id=appointment_id):
            raise ValueError("The requested date and time slot is already booked. Please choose a different slot.")

        old_date = apt['appointment_date']
        old_time = apt['appointment_time']

        query_db(
            """UPDATE appointments 
               SET appointment_date = %s, appointment_time = %s, status = 'Rescheduled'
               WHERE id = %s""",
            (new_date, new_time, appointment_id),
            commit=True
        )

        query_db(
            """INSERT INTO appointment_history (appointment_id, action, old_date, old_time, new_date, new_time, remarks)
               VALUES (%s, 'Rescheduled', %s, %s, %s, %s, %s)""",
            (appointment_id, old_date, old_time, new_date, new_time, 'Rescheduled by patient'),
            commit=True
        )
        return True

    @staticmethod
    def cancel(appointment_id, reason="Cancelled by patient"):
        apt = query_db("SELECT * FROM appointments WHERE id = %s", (appointment_id,), one=True)
        if not apt:
            raise ValueError("Appointment not found.")
        if apt['status'] == 'Cancelled':
            raise ValueError("Appointment is already cancelled.")

        query_db(
            "UPDATE appointments SET status = 'Cancelled' WHERE id = %s",
            (appointment_id,),
            commit=True
        )

        # Update payment status to Refunded if paid
        query_db(
            "UPDATE payments SET payment_status = 'Refunded' WHERE appointment_id = %s",
            (appointment_id,),
            commit=True
        )

        query_db(
            """INSERT INTO appointment_history (appointment_id, action, old_date, old_time, new_date, new_time, remarks)
               VALUES (%s, 'Cancelled', %s, %s, NULL, NULL, %s)""",
            (appointment_id, apt['appointment_date'], apt['appointment_time'], reason),
            commit=True
        )
        return True

class PaymentModel:
    @staticmethod
    def generate_payment_number():
        chars = ''.join(random.choices(string.digits, k=5))
        return f"PAY-MED-{chars}"

    @staticmethod
    def create(appointment_id, patient_id, amount, additional_charges, total_amount, payment_method, transaction_id):
        pay_number = PaymentModel.generate_payment_number()
        pay_id = query_db(
            """INSERT INTO payments (payment_number, appointment_id, patient_id, amount, additional_charges, total_amount, payment_method, payment_status, transaction_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'Success', %s)""",
            (pay_number, appointment_id, patient_id, amount, additional_charges, total_amount, payment_method, transaction_id),
            commit=True
        )
        return pay_id, pay_number

class NotificationModel:
    @staticmethod
    def create(user_id, title, message):
        return query_db(
            "INSERT INTO notifications (user_id, title, message) VALUES (%s, %s, %s)",
            (user_id, title, message),
            commit=True
        )

    @staticmethod
    def get_by_user(user_id):
        return query_db("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 10", (user_id,))
