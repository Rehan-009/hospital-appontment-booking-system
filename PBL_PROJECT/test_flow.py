import sys
import os
import io

# Add root directory to path
sys.path.insert(0, r'c:\Users\Vamshi\OneDrive\Desktop\PBL_PROJECT')

from backend.app import app
from datetime import date, timedelta

def run_tests():
    client = app.test_client()
    print("=" * 60)
    print("STARTING END-TO-END VERIFICATION TEST SUITE")
    print("=" * 60)

    # 1. Test Home Page
    res = client.get('/')
    assert res.status_code == 200, f"Home page failed: {res.status_code}"
    print("[PASS] GET / -> 200 OK")

    # 2. Test Hospitals Page
    res = client.get('/hospitals')
    assert res.status_code == 200, f"Hospitals page failed: {res.status_code}"
    print("[PASS] GET /hospitals -> 200 OK")

    # 3. Test Doctors Page
    res = client.get('/doctors')
    assert res.status_code == 200, f"Doctors page failed: {res.status_code}"
    print("[PASS] GET /doctors -> 200 OK")

    # 4. Test API Hospitals
    res = client.get('/api/hospitals')
    data = res.get_json()
    assert res.status_code == 200 and data['count'] >= 3, f"API hospitals failed: {data}"
    print(f"[PASS] GET /api/hospitals -> {data['count']} hospitals loaded")

    # 5. Test API Doctors
    res = client.get('/api/doctors')
    data = res.get_json()
    assert res.status_code == 200 and data['count'] >= 8, f"API doctors failed: {data}"
    print(f"[PASS] GET /api/doctors -> {data['count']} doctors loaded")

    # 6. Test Doctor Availability for future date
    future_date = (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')
    res = client.get(f'/api/doctors/1/availability?date={future_date}')
    data = res.get_json()
    assert res.status_code == 200 and len(data['data']['slots']) > 0, f"Availability check failed: {data}"
    print(f"[PASS] GET /api/doctors/1/availability -> {data['data']['available_count']} slots available")

    # 7. Test Past Date Error Handling
    past_date = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
    res = client.get(f'/api/doctors/1/availability?date={past_date}')
    assert res.status_code == 400, f"Past date check failed: {res.status_code}"
    print("[PASS] Past date check correctly returned 400 Bad Request")

    # 8. Test Invalid Login
    res = client.post('/api/login', json={'email': 'wrong@test.com', 'password': 'wrong'})
    assert res.status_code == 401, f"Invalid login check failed: {res.status_code}"
    print("[PASS] Invalid login correctly rejected with 401 Unauthorized")

    # 9. Test Patient Login
    res = client.post('/api/login', json={'email': 'patient@gmail.com', 'password': '1234'})
    assert res.status_code == 200, f"Patient login failed: {res.get_json()}"
    print("[PASS] POST /api/login -> Patient login successful")

    # 10. Test Patient Dashboard API
    res = client.get('/api/patient/dashboard')
    data = res.get_json()
    assert res.status_code == 200 and 'stats' in data, f"Patient dashboard failed: {data}"
    print(f"[PASS] GET /api/patient/dashboard -> Stats: {data['stats']}")

    # 11. Test Book Appointment Flow
    booking_date = (date.today() + timedelta(days=4)).strftime('%Y-%m-%d')
    booking_time = "11:00 AM"

    res = client.post('/api/appointments', json={
        'doctorId': 1,
        'hospitalId': 1,
        'departmentId': 1,
        'date': booking_date,
        'time': booking_time,
        'reason': 'Automated Test Cardiology Screening'
    })
    data = res.get_json()
    assert res.status_code == 201 and data['success'], f"Booking failed: {data}"
    apt_id = data['appointmentId']
    apt_number = data['appointmentNumber']
    print(f"[PASS] POST /api/appointments -> Created Appointment ID {apt_id} ({apt_number})")

    # 12. Test Double Booking Prevention
    res_dup = client.post('/api/appointments', json={
        'doctorId': 1,
        'hospitalId': 1,
        'departmentId': 1,
        'date': booking_date,
        'time': booking_time,
        'reason': 'Attempt duplicate slot'
    })
    assert res_dup.status_code == 409, f"Double booking should fail with 409: {res_dup.get_json()}"
    print("[PASS] Double booking prevention verified (Returned 409 Conflict)")

    # 13. Test Simulated Payment
    res = client.post('/api/payment', json={
        'appointmentId': apt_id,
        'paymentMethod': 'UPI',
        'totalAmount': 800.00
    })
    data = res.get_json()
    assert res.status_code == 200 and data['success'], f"Payment failed: {data}"
    print(f"[PASS] POST /api/payment -> Success! Generated Payment ID: {data['paymentNumber']}")

    # 14. Test Confirmation Receipt Page
    res = client.get(f'/book/confirmation/{apt_id}')
    assert res.status_code == 200 and b'APPOINTMENT CONFIRMED' in res.data, f"Confirmation failed: {res.status_code}"
    print(f"[PASS] GET /book/confirmation/{apt_id} -> Official Receipt Rendered")

    # 15. Test Reschedule Appointment
    reschedule_date = (date.today() + timedelta(days=6)).strftime('%Y-%m-%d')
    reschedule_time = "03:00 PM"
    res = client.put(f'/api/appointments/{apt_id}/reschedule', json={
        'newDate': reschedule_date,
        'newTime': reschedule_time
    })
    data = res.get_json()
    assert res.status_code == 200 and data['success'], f"Reschedule failed: {data}"
    print(f"[PASS] PUT /api/appointments/{apt_id}/reschedule -> Updated to {reschedule_date} at {reschedule_time}")

    # 16. Test Cancel Appointment with Simulated Refund
    res = client.put(f'/api/appointments/{apt_id}/cancel')
    data = res.get_json()
    assert res.status_code == 200 and data['success'], f"Cancel failed: {data}"
    print(f"[PASS] PUT /api/appointments/{apt_id}/cancel -> Cancelled with Demo Refund: {data.get('refundStatus')}")

    # 17. Verify Doctor Login and Doctor Dashboard
    client.get('/logout')
    res = client.post('/api/login', json={'email': 'doctor@gmail.com', 'password': '1234'})
    assert res.status_code == 200, f"Doctor login failed: {res.get_json()}"
    print("[PASS] POST /api/login -> Doctor login successful")

    res = client.get('/api/doctor/dashboard')
    data = res.get_json()
    assert res.status_code == 200 and 'doctor' in data, f"Doctor dashboard failed: {data}"
    print(f"[PASS] GET /api/doctor/dashboard -> Doctor: {data['doctor']['full_name']}")

    # 18. Test Role Access Protection: Doctor trying to access Patient dashboard
    res = client.get('/patient')
    assert res.status_code in [302, 403], f"Role protection failed: {res.status_code}"
    print("[PASS] Role Access Protection verified: Doctor redirected away from patient dashboard")

    # 19. Test Navigation Bar and Page Access for Doctor Role
    res_dash = client.get('/doctor/dashboard')
    html_content = res_dash.data.decode('utf-8')
    nav_links_start = html_content.find('<ul class="nav-links">')
    nav_links_end = html_content.find('</ul>', nav_links_start)
    doctor_nav_html = html_content[nav_links_start:nav_links_end]
    
    assert '>Home<' not in doctor_nav_html, "Home option must not appear in doctor navbar"
    assert '>Hospitals<' not in doctor_nav_html, "Hospitals option must not appear in doctor navbar"
    assert '>Doctors<' not in doctor_nav_html, "Doctors option must not appear in doctor navbar"
    assert '>Appointments<' not in doctor_nav_html, "Appointments option must not appear in doctor navbar"
    print("[PASS] Doctor navigation bar verified: Home, Hospitals, Doctors, and Appointments removed")

    # Verify doctor cannot access hospitals or appointment pages directly
    res_hosp = client.get('/hospitals')
    assert res_hosp.status_code == 302 and '/doctor/dashboard' in res_hosp.headers['Location']
    print("[PASS] Doctor accessing /hospitals correctly redirected to /doctor/dashboard")

    res_apt = client.get('/appointment')
    assert res_apt.status_code == 302 and '/doctor/dashboard' in res_apt.headers['Location']
    print("[PASS] Doctor accessing /appointment correctly redirected to /doctor/dashboard")

    res_docs = client.get('/doctors')
    assert res_docs.status_code == 302 and '/doctor/dashboard' in res_docs.headers['Location']
    print("[PASS] Doctor accessing /doctors correctly redirected to /doctor/dashboard")

    # Verify that public / patient navbar still contains Home, Hospitals, Doctors, Appointments
    client.get('/logout')
    res_public = client.get('/')
    public_html = res_public.data.decode('utf-8')
    pub_nav_start = public_html.find('<ul class="nav-links">')
    pub_nav_end = public_html.find('</ul>', pub_nav_start)
    pub_nav_html = public_html[pub_nav_start:pub_nav_end]
    assert '>Home<' in pub_nav_html and '>Hospitals<' in pub_nav_html and '>Doctors<' in pub_nav_html and '>Appointments<' in pub_nav_html
    print("[PASS] Public navigation bar verified: Contains Home, Hospitals, Doctors, Appointments")

    # 20. Test New Doctor Account Registration & Own Name Replacement
    import random
    rand_suffix = random.randint(1000, 9999)
    new_doc_email = f"dr_ananya_{rand_suffix}@hospital.com"
    new_doc_phone = f"98765{rand_suffix}"

    res = client.post('/api/register', json={
        'fullName': 'Ananya Sen',
        'email': new_doc_email,
        'phone': new_doc_phone,
        'password': 'docPassword123',
        'confirmPassword': 'docPassword123',
        'role': 'doctor'
    })
    data = res.get_json()
    assert res.status_code == 201 and data['success'], f"New doctor registration failed: {data}"
    assert data['user']['name'] == 'Dr. Ananya Sen', f"Expected Dr. Ananya Sen, got: {data['user']['name']}"
    print(f"[PASS] POST /api/register (Doctor) -> Registered successfully as '{data['user']['name']}'")

    # Verify doctor dashboard returns their own name and not hardcoded Doctor 1
    res = client.get('/api/doctor/dashboard')
    data = res.get_json()
    assert res.status_code == 200 and data['success'], f"Doctor dashboard failed: {data}"
    assert data['doctor']['full_name'] == 'Dr. Ananya Sen', f"Expected Dr. Ananya Sen, got {data['doctor']['full_name']}"
    assert data['doctor']['id'] != 1, f"Doctor ID should be unique, got {data['doctor']['id']}"
    print(f"[PASS] GET /api/doctor/dashboard -> Displays new doctor's own name '{data['doctor']['full_name']}' (ID: {data['doctor']['id']})")

    # 21. Verify Rendered Doctor Dashboard HTML contains new doctor name and profile editing form
    res = client.get('/doctor/dashboard')
    doc_html = res.data.decode('utf-8')
    assert 'Dr. Ananya Sen' in doc_html, "Rendered HTML does not include doctor's own name"
    assert 'id="doctorProfileForm"' in doc_html, "Doctor profile modification form missing from dashboard"
    print("[PASS] GET /doctor/dashboard HTML -> Doctor name rendered with editable profile form")

    # 22. Test Modifying Doctor Details (PUT /api/doctor/profile)
    res = client.put('/api/doctor/profile', json={
        'fullName': 'Dr. Ananya Sen Sharma',
        'qualification': 'MBBS, MS, MCh (AIIMS)',
        'specialization': 'Chief Pediatric Cardiac Surgeon',
        'hospitalId': 1,
        'departmentId': 1,
        'experienceYears': 14,
        'consultationFee': 950.0,
        'availableDays': 'Mon, Wed, Fri, Sat',
        'cabinNumber': 'OPD Suite 502, Tower B',
        'bio': 'Internationally recognized specialist in pediatric cardiology and complex congenital cardiac care.'
    })
    data = res.get_json()
    assert res.status_code == 200 and data['success'], f"Profile update failed: {data}"
    assert data['doctor']['full_name'] == 'Dr. Ananya Sen Sharma', f"Updated name mismatch: {data['doctor']}"
    assert data['doctor']['specialization'] == 'Chief Pediatric Cardiac Surgeon'
    assert float(data['doctor']['consultation_fee']) == 950.0
    assert data['doctor']['cabin_number'] == 'OPD Suite 502, Tower B'
    print("[PASS] PUT /api/doctor/profile -> Modified credentials, fee (Rs 950), specialization, and cabin successfully")

    # 23. Test Doctor Logout, Re-login, and Persistence of Modified Details
    client.get('/logout')
    res = client.post('/api/login', json={
        'email': new_doc_email,
        'password': 'docPassword123'
    })
    data = res.get_json()
    assert res.status_code == 200 and data['success'], f"Re-login failed: {data}"
    assert data['user']['name'] == 'Dr. Ananya Sen Sharma'
    print("[PASS] POST /api/login -> Logged in with modified name 'Dr. Ananya Sen Sharma'")

    res = client.get('/api/doctor/dashboard')
    data = res.get_json()
    assert data['doctor']['specialization'] == 'Chief Pediatric Cardiac Surgeon'
    assert float(data['doctor']['consultation_fee']) == 950.0
    print("[PASS] Persistence verified: Doctor dashboard retained all modified details")

    # 24. Test Doctor Photo Upload
    test_img_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    res = client.post(
        '/api/doctor/upload-photo',
        data={'photo': (io.BytesIO(test_img_data), 'ananya_portrait.png')},
        content_type='multipart/form-data'
    )
    data = res.get_json()
    assert res.status_code == 200 and data['success'], f"Photo upload failed: {data}"
    assert data['imageUrl'].startswith('/static/images/uploads/doctor_'), f"Invalid image URL: {data['imageUrl']}"
    print(f"[PASS] POST /api/doctor/upload-photo -> Uploaded successfully to {data['imageUrl']}")

    # Verify photo is reflected in doctor dashboard API
    res = client.get('/api/doctor/dashboard')
    data = res.get_json()
    assert data['doctor']['image_url'].startswith('/static/images/uploads/doctor_'), f"Doctor profile image not updated: {data}"
    print(f"[PASS] GET /api/doctor/dashboard -> Returned updated image_url: {data['doctor']['image_url']}")

    # 25. Test Rejection of Invalid File Type
    res_bad = client.post(
        '/api/doctor/upload-photo',
        data={'photo': (io.BytesIO(b'malicious script content'), 'script.exe')},
        content_type='multipart/form-data'
    )
    assert res_bad.status_code == 400, f"Expected 400 for invalid file type, got: {res_bad.status_code}"
    print("[PASS] Security check: Invalid file upload correctly rejected with 400 Bad Request")

    print("\n" + "=" * 60)
    print("ALL 25 END-TO-END AUTOMATED TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
