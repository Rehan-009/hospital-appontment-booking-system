import os
import sys
from datetime import datetime, date

# Add parent directory to path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from backend.config import Config
from backend.database import init_db, query_db
from backend.models import (
    HospitalModel, DepartmentModel, DoctorModel, 
    PatientModel, AppointmentModel, UserModel
)
from backend.routes import auth_bp, hospital_bp, appointment_bp, dashboard_bp

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, 'frontend', 'templates'),
        static_folder=os.path.join(BASE_DIR, 'frontend', 'static'),
        static_url_path='/static'
    )
    
    app.config.from_object(Config)

    # Initialize Database
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            print(f"[APP ERROR] Database initialization issue: {e}")

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(hospital_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(dashboard_bp)

    # Context Processor for Global Template Variables
    @app.context_processor
    def inject_global_data():
        user_info = None
        if 'user_id' in session:
            user_info = {
                'id': session.get('user_id'),
                'email': session.get('email'),
                'role': session.get('role'),
                'name': session.get('full_name', 'User'),
                'patient_id': session.get('patient_id'),
                'doctor_id': session.get('doctor_id')
            }
        return {
            'current_user': user_info,
            'current_year': datetime.now().year,
            'today_date': date.today().strftime('%Y-%m-%d')
        }

    # ================= PAGE ROUTES =================

    @app.route('/')
    def home():
        hospitals = HospitalModel.get_all()
        departments = DepartmentModel.get_all_distinct()
        doctors = DoctorModel.get_all()[:4] # Featured doctors
        return render_template(
            'index.html',
            hospitals=hospitals,
            departments=departments,
            doctors=doctors
        )

    @app.route('/hospitals')
    def hospitals_page():
        if session.get('role') == 'doctor':
            return redirect(url_for('doctor_dashboard_page'))

        location = request.args.get('location')
        department_id = request.args.get('department_id')
        search = request.args.get('search')
        
        hospitals = HospitalModel.get_all(location=location, department_id=department_id, search=search)
        departments = DepartmentModel.get_all_distinct()
        return render_template(
            'hospitals.html',
            hospitals=hospitals,
            departments=departments,
            selected_location=location,
            selected_department=department_id,
            search_query=search
        )

    @app.route('/doctors')
    def doctors_page():
        if session.get('role') == 'doctor':
            return redirect(url_for('doctor_dashboard_page'))

        hospital_id = request.args.get('hospital_id')
        department_id = request.args.get('department_id')
        search = request.args.get('search')

        doctors = DoctorModel.get_all(hospital_id=hospital_id, department_id=department_id, search=search)
        hospitals = HospitalModel.get_all()
        departments = DepartmentModel.get_all_distinct()
        
        selected_hospital = None
        if hospital_id:
            selected_hospital = HospitalModel.get_by_id(hospital_id)

        return render_template(
            'doctors.html',
            doctors=doctors,
            hospitals=hospitals,
            departments=departments,
            selected_hospital_id=hospital_id,
            selected_hospital=selected_hospital,
            selected_department_id=department_id,
            search_query=search
        )

    @app.route('/appointment')
    @app.route('/book/schedule')
    def appointment_page():
        if session.get('role') == 'doctor':
            return redirect(url_for('doctor_dashboard_page'))

        doctor_id = request.args.get('doctor_id')
        hospital_id = request.args.get('hospital_id')
        department_id = request.args.get('department_id')

        doctor = None
        if doctor_id:
            doctor = DoctorModel.get_by_id(doctor_id)
            if doctor and not hospital_id:
                hospital_id = doctor['hospital_id']
            if doctor and not department_id:
                department_id = doctor['department_id']

        hospital = HospitalModel.get_by_id(hospital_id) if hospital_id else None
        
        return render_template(
            'appointment.html',
            doctor=doctor,
            hospital=hospital,
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            department_id=department_id
        )

    @app.route('/summary')
    @app.route('/book/summary')
    def summary_page():
        if session.get('role') == 'doctor':
            return redirect(url_for('doctor_dashboard_page'))

        doctor_id = request.args.get('doctor_id')
        apt_date = request.args.get('date')
        apt_time = request.args.get('time')
        reason = request.args.get('reason', 'General Medical Consultation')

        if not doctor_id or not apt_date or not apt_time:
            return redirect(url_for('hospitals_page'))

        doctor = DoctorModel.get_by_id(doctor_id)
        if not doctor:
            return redirect(url_for('hospitals_page'))

        fee = float(doctor['consultation_fee'])
        facility_charges = 50.00
        total_amount = fee + facility_charges

        # Fetch patient profile if logged in
        patient = None
        user = None
        if 'user_id' in session:
            user = UserModel.find_by_id(session['user_id'])
            patient = PatientModel.find_by_user_id(session['user_id'])

        return render_template(
            'summary.html',
            doctor=doctor,
            date=apt_date,
            time=apt_time,
            reason=reason,
            fee=fee,
            facility_charges=facility_charges,
            total_amount=total_amount,
            patient=patient,
            user=user
        )

    @app.route('/payment')
    @app.route('/book/payment')
    def payment_page():
        if session.get('role') == 'doctor':
            return redirect(url_for('doctor_dashboard_page'))

        apt_id = request.args.get('appointment_id')
        if not apt_id:
            return redirect(url_for('patient_dashboard_page'))

        appointment = AppointmentModel.get_by_id(apt_id)
        if not appointment:
            return redirect(url_for('patient_dashboard_page'))

        fee = float(appointment['consultation_fee'])
        facility_charges = 50.00
        total_amount = fee + facility_charges

        return render_template(
            'payment.html',
            appointment=appointment,
            fee=fee,
            facility_charges=facility_charges,
            total_amount=total_amount
        )

    @app.route('/confirmation/<int:appointment_id>')
    @app.route('/book/confirmation/<int:appointment_id>')
    def confirmation_page(appointment_id):
        appointment = AppointmentModel.get_by_id(appointment_id)
        if not appointment:
            return redirect(url_for('home'))
        return render_template('confirmation.html', appointment=appointment)

    @app.route('/patient')
    def patient_dashboard_page():
        if 'user_id' not in session:
            return redirect(url_for('home') + '?login=required&next=patient')
        if session.get('role') == 'doctor':
            return redirect(url_for('doctor_dashboard_page'))

        patient = PatientModel.find_by_user_id(session['user_id'])
        return render_template('patient.html', patient=patient)

    @app.route('/doctor/dashboard')
    def doctor_dashboard_page():
        if 'user_id' not in session:
            return redirect(url_for('home') + '?login=required&next=doctor')
        if session.get('role') != 'doctor':
            return redirect(url_for('patient_dashboard_page'))

        doctor = DoctorModel.find_by_user_id(session['user_id'])
        if not doctor:
            user = UserModel.find_by_id(session['user_id'])
            name = session.get('full_name') or (user['email'].split('@')[0].capitalize() if user else 'Doctor')
            doc_name = name if (name.startswith('Dr. ') or name.startswith('Dr ')) else f"Dr. {name}"
            doc_id = DoctorModel.create(user_id=session['user_id'], full_name=doc_name)
            session['doctor_id'] = doc_id
            session['full_name'] = doc_name
            doctor = DoctorModel.find_by_user_id(session['user_id'])

        hospitals = HospitalModel.get_all()
        departments = DepartmentModel.get_all_distinct()

        return render_template('doctor_dashboard.html', doctor=doctor, hospitals=hospitals, departments=departments)

    # Fallback Direct Auth Pages
    @app.route('/login')
    def login_page():
        if 'user_id' in session:
            return redirect(url_for('doctor_dashboard_page' if session.get('role') == 'doctor' else 'patient_dashboard_page'))
        return redirect(url_for('home') + '?login=open')

    @app.route('/register')
    def register_page():
        if 'user_id' in session:
            return redirect(url_for('patient_dashboard_page'))
        return redirect(url_for('home') + '?register=open')

    return app

app = create_app()

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print(" MediCare Hospital Appointment Booking System (HABS)")
    print(" Running at: http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
