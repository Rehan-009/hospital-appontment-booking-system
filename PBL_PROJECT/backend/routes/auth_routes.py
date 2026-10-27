from flask import Blueprint, request, jsonify, session, redirect, url_for
from functools import wraps
from backend.models import UserModel, PatientModel, DoctorModel

auth_bp = Blueprint('auth_bp', __name__)

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': 'Authentication required. Please log in.'}), 401
                return redirect(url_for('home') + '?login=required')
            if role and session.get('role') != role:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': 'Access forbidden: Insufficient permissions.'}), 403
                # Redirect based on user's actual role
                if session.get('role') == 'doctor':
                    return redirect(url_for('doctor_dashboard_page'))
                return redirect(url_for('patient_dashboard_page'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        
        full_name = data.get('fullName', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirmPassword', '')
        age = data.get('age')
        gender = data.get('gender', 'Other')
        role = data.get('role', 'patient').lower()

        # Validation
        if not full_name or not email or not phone or not password:
            return jsonify({'success': False, 'message': 'All required fields must be filled.'}), 400

        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match.'}), 400

        if len(password) < 4:
            return jsonify({'success': False, 'message': 'Password must be at least 4 characters.'}), 400

        if role not in ['patient', 'doctor']:
            role = 'patient'

        # Check duplicates
        if UserModel.find_by_email(email):
            return jsonify({'success': False, 'message': 'An account with this email address already exists.'}), 409

        if UserModel.find_by_phone(phone):
            return jsonify({'success': False, 'message': 'An account with this phone number already exists.'}), 409

        # Create user
        user_id = UserModel.create(email, phone, password, role)
        
        patient_id = None
        doctor_id = None

        if role == 'patient':
            try:
                age_val = int(age) if age else None
            except (ValueError, TypeError):
                age_val = None
            patient_id = PatientModel.create(user_id, full_name, age_val, gender)
        else:
            # Check if doctor already exists or create new doctor profile
            doc = DoctorModel.find_by_user_id(user_id)
            if doc:
                doctor_id = doc['id']
                full_name = doc['full_name']
            else:
                doc_name = full_name if (full_name.startswith('Dr. ') or full_name.startswith('Dr ')) else f"Dr. {full_name}"
                doctor_id = DoctorModel.create(user_id=user_id, full_name=doc_name)
                full_name = doc_name

        # Set Session
        session.clear()
        session['user_id'] = user_id
        session['email'] = email
        session['role'] = role
        session['full_name'] = full_name
        session['patient_id'] = patient_id
        session['doctor_id'] = doctor_id

        redirect_url = '/doctor/dashboard' if role == 'doctor' else '/patient'

        return jsonify({
            'success': True,
            'message': 'Registration successful! Welcome to MediCare.',
            'role': role,
            'redirect': redirect_url,
            'user': {
                'id': user_id,
                'email': email,
                'name': full_name,
                'role': role
            }
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        identifier = data.get('email', '').strip()
        password = data.get('password', '')

        if not identifier or not password:
            return jsonify({'success': False, 'message': 'Please provide email/phone and password.'}), 400

        # Support identifier as email or phone
        user = UserModel.find_by_email(identifier)
        if not user:
            user = UserModel.find_by_phone(identifier)

        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials. User not found.'}), 401

        if not UserModel.verify_password(user['password_hash'], password):
            return jsonify({'success': False, 'message': 'Invalid password. Please try again.'}), 401

        # Populate user session details
        session.clear()
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['role'] = user['role']

        full_name = "User"
        patient_id = None
        doctor_id = None

        if user['role'] == 'patient':
            patient = PatientModel.find_by_user_id(user['id'])
            if patient:
                full_name = patient['full_name']
                patient_id = patient['id']
            redirect_url = '/patient'
        else:
            doctor = DoctorModel.find_by_user_id(user['id'])
            if doctor:
                full_name = doctor['full_name']
                doctor_id = doctor['id']
            else:
                raw_name = user.get('email', 'Doctor').split('@')[0].replace('.', ' ').capitalize()
                doc_name = f"Dr. {raw_name}"
                doctor_id = DoctorModel.create(user_id=user['id'], full_name=doc_name)
                full_name = doc_name
            redirect_url = '/doctor/dashboard'

        session['full_name'] = full_name
        session['patient_id'] = patient_id
        session['doctor_id'] = doctor_id

        return jsonify({
            'success': True,
            'message': 'Login successful! Redirecting...',
            'role': user['role'],
            'redirect': redirect_url,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': full_name,
                'role': user['role']
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error during login: {str(e)}'}), 500

@auth_bp.route('/api/auth/status', methods=['GET'])
def auth_status():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user_id': session.get('user_id'),
            'email': session.get('email'),
            'role': session.get('role'),
            'name': session.get('full_name'),
            'patient_id': session.get('patient_id'),
            'doctor_id': session.get('doctor_id')
        })
    return jsonify({'logged_in': False})

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})
