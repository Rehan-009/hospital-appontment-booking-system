from flask import Blueprint, request, jsonify
from datetime import datetime, date
from backend.models import HospitalModel, DepartmentModel, DoctorModel

hospital_bp = Blueprint('hospital_bp', __name__)

@hospital_bp.route('/api/hospitals', methods=['GET'])
def get_hospitals():
    try:
        location = request.args.get('location')
        department_id = request.args.get('department_id')
        search = request.args.get('search')
        
        hospitals = HospitalModel.get_all(location=location, department_id=department_id, search=search)
        return jsonify({'success': True, 'hospitals': hospitals, 'count': len(hospitals)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to retrieve hospitals: {str(e)}'}), 500

@hospital_bp.route('/api/hospitals/<int:hospital_id>', methods=['GET'])
def get_hospital_details(hospital_id):
    try:
        hospital = HospitalModel.get_by_id(hospital_id)
        if not hospital:
            return jsonify({'success': False, 'message': 'Hospital not found.'}), 404
        return jsonify({'success': True, 'hospital': hospital})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching hospital: {str(e)}'}), 500

@hospital_bp.route('/api/departments', methods=['GET'])
def get_departments():
    try:
        hospital_id = request.args.get('hospital_id')
        if hospital_id:
            departments = DepartmentModel.get_by_hospital(hospital_id)
        else:
            departments = DepartmentModel.get_all_distinct()
        return jsonify({'success': True, 'departments': departments})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching departments: {str(e)}'}), 500

@hospital_bp.route('/api/doctors', methods=['GET'])
def get_doctors():
    try:
        hospital_id = request.args.get('hospital_id')
        department_id = request.args.get('department_id')
        search = request.args.get('search')

        doctors = DoctorModel.get_all(hospital_id=hospital_id, department_id=department_id, search=search)
        return jsonify({'success': True, 'doctors': doctors, 'count': len(doctors)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching doctors: {str(e)}'}), 500

@hospital_bp.route('/api/doctors/<int:doctor_id>', methods=['GET'])
def get_doctor_details(doctor_id):
    try:
        doctor = DoctorModel.get_by_id(doctor_id)
        if not doctor:
            return jsonify({'success': False, 'message': 'Doctor not found.'}), 404
        return jsonify({'success': True, 'doctor': doctor})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching doctor details: {str(e)}'}), 500

@hospital_bp.route('/api/doctors/<int:doctor_id>/availability', methods=['GET'])
def get_doctor_availability(doctor_id):
    try:
        target_date_str = request.args.get('date')
        if not target_date_str:
            target_date_str = date.today().strftime('%Y-%m-%d')
            
        # Validate date format and prevent past dates
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            if target_date < date.today():
                return jsonify({
                    'success': False,
                    'message': 'Cannot check availability or book appointments for past dates.',
                    'slots': [],
                    'available_count': 0
                }), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

        availability = DoctorModel.get_availability(doctor_id, target_date_str)
        return jsonify({'success': True, 'data': availability})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error retrieving doctor availability: {str(e)}'}), 500
