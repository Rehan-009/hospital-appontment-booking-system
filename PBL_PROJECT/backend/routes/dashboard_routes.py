import os
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from datetime import datetime, date
from backend.models import (
    PatientModel, DoctorModel, AppointmentModel, 
    NotificationModel, UserModel
)
from backend.database import query_db

dashboard_bp = Blueprint('dashboard_bp', __name__)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@dashboard_bp.route('/api/patient/dashboard', methods=['GET'])
def patient_dashboard_data():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Authentication required.'}), 401

        patient = PatientModel.find_by_user_id(user_id)
        if not patient:
            return jsonify({'success': False, 'message': 'Patient profile not found.'}), 404

        patient_id = patient['id']
        all_apts = AppointmentModel.get_patient_appointments(patient_id)
        
        today_str = date.today().strftime('%Y-%m-%d')
        
        upcoming = []
        completed = []
        cancelled = []

        for a in all_apts:
            if a['status'] == 'Cancelled':
                cancelled.append(a)
            elif a['status'] == 'Completed' or (a['status'] in ['Confirmed', 'Rescheduled'] and a['appointment_date'] < today_str):
                completed.append(a)
            else:
                upcoming.append(a)

        notifications = NotificationModel.get_by_user(user_id)
        user = UserModel.find_by_id(user_id)

        return jsonify({
            'success': True,
            'patient': {
                'id': patient['id'],
                'fullName': patient['full_name'],
                'age': patient['age'],
                'gender': patient['gender'],
                'bloodGroup': patient['blood_group'],
                'address': patient['address'],
                'emergencyContact': patient['emergency_contact'],
                'email': user['email'] if user else '',
                'phone': user['phone'] if user else ''
            },
            'stats': {
                'upcomingCount': len(upcoming),
                'completedCount': len(completed),
                'cancelledCount': len(cancelled),
                'totalCount': len(all_apts)
            },
            'upcomingAppointments': upcoming,
            'pastAppointments': completed,
            'cancelledAppointments': cancelled,
            'allAppointments': all_apts,
            'notifications': notifications
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to load patient dashboard: {str(e)}'}), 500

@dashboard_bp.route('/api/doctor/dashboard', methods=['GET'])
def doctor_dashboard_data():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Authentication required.'}), 401

        doctor = DoctorModel.find_by_user_id(user_id)
        if not doctor:
            # If authenticated user has doctor role, auto-provision profile
            user = UserModel.find_by_id(user_id)
            if user and user.get('role') == 'doctor':
                name = session.get('full_name') or user['email'].split('@')[0].capitalize()
                doc_name = name if (name.startswith('Dr. ') or name.startswith('Dr ')) else f"Dr. {name}"
                doc_id = DoctorModel.create(user_id=user_id, full_name=doc_name)
                session['doctor_id'] = doc_id
                session['full_name'] = doc_name
                doctor = DoctorModel.find_by_user_id(user_id)
            else:
                doctor = DoctorModel.get_by_id(1)

        doctor_id = doctor['id']
        all_apts = AppointmentModel.get_doctor_appointments(doctor_id)
        
        today_str = date.today().strftime('%Y-%m-%d')
        
        today_apts = [a for a in all_apts if a['appointment_date'] == today_str and a['status'] != 'Cancelled']
        upcoming_apts = [a for a in all_apts if a['appointment_date'] > today_str and a['status'] != 'Cancelled']
        completed_apts = [a for a in all_apts if a['status'] == 'Completed']
        
        # Unique patients count
        unique_patients = len(set(a['patient_id'] for a in all_apts))

        return jsonify({
            'success': True,
            'doctor': doctor,
            'stats': {
                'todayCount': len(today_apts),
                'upcomingCount': len(upcoming_apts),
                'completedCount': len(completed_apts),
                'totalPatients': unique_patients
            },
            'todayAppointments': today_apts,
            'upcomingAppointments': upcoming_apts,
            'allAppointments': all_apts
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to load doctor dashboard: {str(e)}'}), 500

@dashboard_bp.route('/api/doctor/profile', methods=['PUT'])
def update_doctor_profile():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Authentication required.'}), 401

        doctor = DoctorModel.find_by_user_id(user_id)
        if not doctor:
            # If doctor profile is not created yet, create it
            user = UserModel.find_by_id(user_id)
            name = session.get('full_name') or (user['email'].split('@')[0].capitalize() if user else 'Doctor')
            doc_name = name if (name.startswith('Dr. ') or name.startswith('Dr ')) else f"Dr. {name}"
            doc_id = DoctorModel.create(user_id=user_id, full_name=doc_name)
            session['doctor_id'] = doc_id
            doctor = DoctorModel.find_by_user_id(user_id)

        data = request.get_json() or {}

        # Extract and format fields
        raw_name = data.get('fullName', doctor['full_name']).strip()
        if raw_name and not (raw_name.startswith('Dr. ') or raw_name.startswith('Dr ')):
            full_name = f"Dr. {raw_name}"
        else:
            full_name = raw_name or doctor['full_name']

        qualification = data.get('qualification', doctor['qualification']).strip() or doctor['qualification']
        specialization = data.get('specialization', doctor['specialization']).strip() or doctor['specialization']

        try:
            hospital_id = int(data.get('hospitalId', doctor['hospital_id']))
        except (ValueError, TypeError):
            hospital_id = doctor['hospital_id']

        try:
            department_id = int(data.get('departmentId', doctor['department_id']))
        except (ValueError, TypeError):
            department_id = doctor['department_id']

        try:
            experience_years = int(data.get('experienceYears', doctor['experience_years']))
        except (ValueError, TypeError):
            experience_years = doctor['experience_years']

        try:
            consultation_fee = float(data.get('consultationFee', doctor['consultation_fee']))
        except (ValueError, TypeError):
            consultation_fee = doctor['consultation_fee']

        available_days = data.get('availableDays', doctor['available_days']).strip() or doctor['available_days']
        cabin_number = data.get('cabinNumber', doctor['cabin_number']).strip() or doctor['cabin_number']
        bio = data.get('bio', doctor['bio']).strip() or doctor['bio']
        image_url = data.get('imageUrl', doctor.get('image_url'))

        DoctorModel.update_profile(
            doctor_id=doctor['id'],
            full_name=full_name,
            qualification=qualification,
            specialization=specialization,
            hospital_id=hospital_id,
            department_id=department_id,
            experience_years=experience_years,
            consultation_fee=consultation_fee,
            available_days=available_days,
            cabin_number=cabin_number,
            bio=bio,
            image_url=image_url
        )

        session['full_name'] = full_name
        updated_doctor = DoctorModel.find_by_user_id(user_id)

        return jsonify({
            'success': True,
            'message': 'Doctor profile details updated successfully.',
            'doctor': updated_doctor
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to update profile: {str(e)}'}), 500

@dashboard_bp.route('/api/doctor/upload-photo', methods=['POST'])
def upload_doctor_photo():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Authentication required. Please log in.'}), 401

        doctor = DoctorModel.find_by_user_id(user_id)
        if not doctor:
            user = UserModel.find_by_id(user_id)
            if user and user.get('role') == 'doctor':
                name = session.get('full_name') or user['email'].split('@')[0].capitalize()
                doc_name = name if (name.startswith('Dr. ') or name.startswith('Dr ')) else f"Dr. {name}"
                doc_id = DoctorModel.create(user_id=user_id, full_name=doc_name)
                session['doctor_id'] = doc_id
                doctor = DoctorModel.find_by_user_id(user_id)
            else:
                return jsonify({'success': False, 'message': 'Doctor profile not found.'}), 404

        if 'photo' not in request.files:
            return jsonify({'success': False, 'message': 'No image file uploaded in the request.'}), 400

        file = request.files['photo']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected image file.'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file format. Allowed: PNG, JPG, JPEG, WEBP, GIF.'}), 400

        upload_folder = os.path.join(current_app.static_folder, 'images', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        ext = file.filename.rsplit('.', 1)[1].lower()
        timestamp = int(datetime.now().timestamp())
        filename = f"doctor_{doctor['id']}_{timestamp}.{ext}"
        filepath = os.path.join(upload_folder, filename)

        file.save(filepath)

        image_url = f"/static/images/uploads/{filename}"
        DoctorModel.update_photo(doctor['id'], image_url)

        return jsonify({
            'success': True,
            'message': 'Doctor photo uploaded and updated successfully!',
            'imageUrl': image_url
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Photo upload failed: {str(e)}'}), 500

@dashboard_bp.route('/api/doctor/appointments/<int:appointment_id>/status', methods=['PUT'])
def update_appointment_status(appointment_id):
    try:
        data = request.get_json() or {}
        new_status = data.get('status', 'Completed')
        
        if new_status not in ['Confirmed', 'Completed', 'Cancelled']:
            return jsonify({'success': False, 'message': 'Invalid status update.'}), 400

        query_db("UPDATE appointments SET status = %s WHERE id = %s", (new_status, appointment_id), commit=True)
        query_db("""INSERT INTO appointment_history (appointment_id, action, remarks) 
                    VALUES (%s, %s, 'Status updated by doctor')""", (appointment_id, new_status), commit=True)

        return jsonify({'success': True, 'message': f"Appointment status updated to '{new_status}'."})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Status update failed: {str(e)}'}), 500

@dashboard_bp.route('/api/patient/profile', methods=['PUT'])
def update_patient_profile():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            
        patient = PatientModel.find_by_user_id(user_id)
        if not patient:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404

        data = request.get_json() or {}
        PatientModel.update_profile(
            patient_id=patient['id'],
            full_name=data.get('fullName', patient['full_name']),
            age=data.get('age', patient['age']),
            gender=data.get('gender', patient['gender']),
            blood_group=data.get('bloodGroup', patient['blood_group']),
            address=data.get('address', patient['address']),
            emergency_contact=data.get('emergencyContact', patient['emergency_contact'])
        )

        session['full_name'] = data.get('fullName', patient['full_name'])
        return jsonify({'success': True, 'message': 'Profile updated successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Update failed: {str(e)}'}), 500
