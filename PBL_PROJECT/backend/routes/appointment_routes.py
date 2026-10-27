from flask import Blueprint, request, jsonify, session
from datetime import datetime, date
import random
import string
from backend.models import (
    AppointmentModel, PaymentModel, DoctorModel, 
    PatientModel, HospitalModel, NotificationModel
)

appointment_bp = Blueprint('appointment_bp', __name__)

@appointment_bp.route('/api/appointments', methods=['POST'])
def create_appointment():
    try:
        data = request.get_json() or {}
        
        doctor_id = data.get('doctorId')
        hospital_id = data.get('hospitalId')
        department_id = data.get('departmentId')
        apt_date = data.get('date')
        apt_time = data.get('time')
        reason = data.get('reason', 'General Medical Consultation')

        # Check user session or resolve patient
        patient_id = session.get('patient_id')
        if not patient_id:
            # Check if user_id in session
            user_id = session.get('user_id')
            if user_id:
                patient = PatientModel.find_by_user_id(user_id)
                if patient:
                    patient_id = patient['id']
                    session['patient_id'] = patient_id

        if not patient_id:
            return jsonify({'success': False, 'message': 'You must be logged in as a patient to book an appointment.'}), 401

        # Validate inputs
        if not doctor_id or not hospital_id or not department_id or not apt_date or not apt_time:
            return jsonify({'success': False, 'message': 'Missing required booking details (doctor, date, time, etc.).'}), 400

        # Validate date is not past
        try:
            booking_date = datetime.strptime(apt_date, '%Y-%m-%d').date()
            if booking_date < date.today():
                return jsonify({'success': False, 'message': 'Appointments cannot be scheduled in the past.'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format. Expected YYYY-MM-DD.'}), 400

        # Check if slot already booked
        if AppointmentModel.is_slot_booked(doctor_id, apt_date, apt_time):
            return jsonify({'success': False, 'message': 'Selected time slot is already booked for this doctor. Please choose an available slot.'}), 409

        # Create appointment record
        apt_id, apt_number = AppointmentModel.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            department_id=department_id,
            appointment_date=apt_date,
            appointment_time=apt_time,
            reason=reason
        )

        return jsonify({
            'success': True,
            'message': 'Appointment initialized successfully. Proceed to payment.',
            'appointmentId': apt_id,
            'appointmentNumber': apt_number
        }), 201

    except ValueError as ve:
        return jsonify({'success': False, 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to create appointment: {str(e)}'}), 500

@appointment_bp.route('/api/payment', methods=['POST'])
def process_payment():
    """
    Simulated Payment Processing Endpoint.
    Validates payment details, generates confirmation, and links payment to appointment.
    """
    try:
        data = request.get_json() or {}
        
        appointment_id = data.get('appointmentId')
        payment_method = data.get('paymentMethod', 'UPI')
        amount = data.get('amount')
        additional_charges = data.get('additionalCharges', 50.00)
        total_amount = data.get('totalAmount')

        if not appointment_id:
            return jsonify({'success': False, 'message': 'Appointment ID is required for payment.'}), 400

        appointment = AppointmentModel.get_by_id(appointment_id)
        if not appointment:
            return jsonify({'success': False, 'message': 'Appointment not found.'}), 404

        patient_id = appointment['patient_id']
        fee = float(appointment['consultation_fee'])
        charges = float(additional_charges)
        calculated_total = fee + charges

        # Simulated transaction ID
        txn_prefix = {
            'UPI': 'TXN_UPI_',
            'Credit Card': 'TXN_CC_',
            'Debit Card': 'TXN_DC_',
            'Net Banking': 'TXN_NB_'
        }.get(payment_method, 'TXN_GEN_')
        
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
        transaction_id = f"{txn_prefix}{random_suffix}"

        # Create payment record
        pay_id, pay_number = PaymentModel.create(
            appointment_id=appointment_id,
            patient_id=patient_id,
            amount=fee,
            additional_charges=charges,
            total_amount=calculated_total,
            payment_method=payment_method,
            transaction_id=transaction_id
        )

        # Create notification for patient
        user_id = session.get('user_id')
        if user_id:
            NotificationModel.create(
                user_id=user_id,
                title="Appointment Confirmed & Paid",
                message=f"Appointment {appointment['appointment_number']} with {appointment['doctor_name']} has been confirmed. Payment ID: {pay_number}."
            )

        return jsonify({
            'success': True,
            'message': 'Payment processed successfully! Appointment confirmed.',
            'paymentId': pay_id,
            'paymentNumber': pay_number,
            'transactionId': transaction_id,
            'appointmentNumber': appointment['appointment_number'],
            'redirect': f"/book/confirmation/{appointment_id}"
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Payment processing error: {str(e)}'}), 500

@appointment_bp.route('/api/appointments', methods=['GET'])
def get_appointments():
    try:
        user_id = session.get('user_id')
        role = session.get('role')
        status_filter = request.args.get('status')

        if not user_id:
            return jsonify({'success': False, 'message': 'Authentication required.'}), 401

        if role == 'patient':
            patient = PatientModel.find_by_user_id(user_id)
            if not patient:
                return jsonify({'success': False, 'message': 'Patient profile not found.'}), 404
            appointments = AppointmentModel.get_patient_appointments(patient['id'], status_filter=status_filter)
        elif role == 'doctor':
            doctor = DoctorModel.find_by_user_id(user_id)
            if not doctor:
                return jsonify({'success': False, 'message': 'Doctor profile not found.'}), 404
            appointments = AppointmentModel.get_doctor_appointments(doctor['id'])
        else:
            appointments = []

        return jsonify({'success': True, 'appointments': appointments, 'count': len(appointments)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching appointments: {str(e)}'}), 500

@appointment_bp.route('/api/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment_details(appointment_id):
    try:
        appointment = AppointmentModel.get_by_id(appointment_id)
        if not appointment:
            return jsonify({'success': False, 'message': 'Appointment record not found.'}), 404
        return jsonify({'success': True, 'appointment': appointment})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching appointment details: {str(e)}'}), 500

@appointment_bp.route('/api/appointments/<int:appointment_id>/reschedule', methods=['PUT'])
def reschedule_appointment(appointment_id):
    try:
        data = request.get_json() or {}
        new_date = data.get('newDate')
        new_time = data.get('newTime')

        if not new_date or not new_time:
            return jsonify({'success': False, 'message': 'Please select both new date and new time slot.'}), 400

        # Validate date is future
        try:
            target_date = datetime.strptime(new_date, '%Y-%m-%d').date()
            if target_date < date.today():
                return jsonify({'success': False, 'message': 'Cannot reschedule to a past date.'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format. Expected YYYY-MM-DD.'}), 400

        # Verify ownership / permissions
        apt = AppointmentModel.get_by_id(appointment_id)
        if not apt:
            return jsonify({'success': False, 'message': 'Appointment not found.'}), 404

        AppointmentModel.reschedule(appointment_id, new_date, new_time)

        # Notify
        user_id = session.get('user_id')
        if user_id:
            NotificationModel.create(
                user_id=user_id,
                title="Appointment Rescheduled",
                message=f"Appointment {apt['appointment_number']} with {apt['doctor_name']} has been rescheduled to {new_date} at {new_time}."
            )

        return jsonify({
            'success': True,
            'message': f"Appointment successfully rescheduled to {new_date} at {new_time}."
        })

    except ValueError as ve:
        return jsonify({'success': False, 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Rescheduling failed: {str(e)}'}), 500

@appointment_bp.route('/api/appointments/<int:appointment_id>/cancel', methods=['PUT'])
def cancel_appointment(appointment_id):
    try:
        apt = AppointmentModel.get_by_id(appointment_id)
        if not apt:
            return jsonify({'success': False, 'message': 'Appointment not found.'}), 404

        AppointmentModel.cancel(appointment_id, reason="Cancelled by patient via dashboard")

        # Notify
        user_id = session.get('user_id')
        if user_id:
            NotificationModel.create(
                user_id=user_id,
                title="Appointment Cancelled",
                message=f"Your appointment {apt['appointment_number']} with {apt['doctor_name']} has been cancelled. Simulated refund initiated."
            )

        return jsonify({
            'success': True,
            'message': 'Appointment cancelled successfully. A demo simulated refund has been credited to your payment source.',
            'refundStatus': 'Refund Initiated (Demo Mode)'
        })

    except ValueError as ve:
        return jsonify({'success': False, 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Cancellation failed: {str(e)}'}), 500
