import os
import sqlite3
import json
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
from backend.config import Config

try:
    import pymysql
    import pymysql.cursors
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

DB_TYPE = None  # 'mysql' or 'sqlite'

def check_mysql_connection():
    """Check if MySQL is reachable with current credentials."""
    if not PYMYSQL_AVAILABLE:
        return False, "PyMySQL package not installed."
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            connect_timeout=2
        )
        conn.close()
        return True, "MySQL connection successful."
    except Exception as e:
        return False, str(e)

def get_db():
    """Get active database connection based on resolved DB_TYPE."""
    global DB_TYPE
    if DB_TYPE is None:
        init_db()

    if DB_TYPE == 'mysql':
        return pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    else:
        conn = sqlite3.connect(Config.SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def adapt_sql(query):
    """Adapt standard SQL query between MySQL (%s) and SQLite (?)."""
    if DB_TYPE == 'sqlite':
        # Replace %s with ? for SQLite placeholders
        adapted = query.replace('%s', '?')
        # Replace MySQL specific date functions
        adapted = adapted.replace('CURDATE() + INTERVAL 2 DAY', "date('now', '+2 days')")
        adapted = adapted.replace('CURDATE() - INTERVAL 10 DAY', "date('now', '-10 days')")
        adapted = adapted.replace('CURDATE()', "date('now')")
        adapted = adapted.replace('NOW()', "datetime('now')")
        return adapted
    return query

def query_db(query, args=(), one=False, commit=False):
    """
    Execute query against active database with automatic dictionary result conversion
    and error resilience.
    """
    conn = get_db()
    cursor = conn.cursor()
    adapted_query = adapt_sql(query)
    
    try:
        cursor.execute(adapted_query, args)
        
        if commit:
            if DB_TYPE == 'sqlite':
                conn.commit()
                last_id = cursor.lastrowid
            else:
                conn.commit()
                last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id
            
        if DB_TYPE == 'sqlite':
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            # Convert sqlite3.Row to standard dict
            result = [dict(row) for row in rows]
            return (result[0] if result else None) if one else result
        else:
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return (result[0] if result else None) if one else result
    except Exception as e:
        if DB_TYPE == 'sqlite':
            conn.rollback()
        conn.close()
        raise e

def init_db():
    """Initialize schema and seed demo data in MySQL or fallback to SQLite."""
    global DB_TYPE
    mysql_ok, msg = check_mysql_connection()
    
    if mysql_ok:
        try:
            print("[DATABASE] Connecting to MySQL Server...")
            admin_conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                autocommit=True
            )
            with admin_conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME};")
            admin_conn.close()
            
            DB_TYPE = 'mysql'
            print(f"[DATABASE] MySQL Database '{Config.DB_NAME}' ready.")
            _init_mysql_tables()
            return
        except Exception as e:
            print(f"[DATABASE WARNING] MySQL setup encountered error: {e}")
            print("[DATABASE] Switching to SQLite fallback...")
            
    DB_TYPE = 'sqlite'
    print(f"[DATABASE] Using SQLite Mode ({Config.SQLITE_PATH})")
    print(f"[DATABASE] Reason: {msg}")
    print("[DATABASE] Tip: Set DB_PASSWORD or start MySQL with matching credentials to switch seamlessly.")
    _init_sqlite_tables()

def _init_mysql_tables():
    """Ensure MySQL tables and seed data exist."""
    users = query_db("SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = %s AND table_name = 'users';", (Config.DB_NAME,), one=True)
    if not users or users['count'] == 0:
        schema_path = os.path.join(Config.BASE_DIR, 'database', 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            conn = get_db()
            with conn.cursor() as cur:
                for stmt in statements:
                    if stmt.upper().startswith(('CREATE DATABASE', 'USE')):
                        continue
                    cur.execute(stmt)
                conn.commit()
            conn.close()
            print("[DATABASE] MySQL tables created successfully.")
            _seed_data()
    else:
        _ensure_test_users()

def _init_sqlite_tables():
    """Create SQLite tables and seed data if not present."""
    os.makedirs(os.path.dirname(Config.SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.SQLITE_PATH)
    cur = conn.cursor()
    
    # 1. Users
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'patient',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    
    # 2. Patients
    cur.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        blood_group TEXT DEFAULT 'O+',
        address TEXT,
        emergency_contact TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')
    
    # 3. Hospitals
    cur.execute('''
    CREATE TABLE IF NOT EXISTS hospitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tagline TEXT,
        location TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        rating REAL DEFAULT 4.8,
        total_reviews INTEGER DEFAULT 120,
        image_url TEXT,
        description TEXT,
        emergency_hours TEXT DEFAULT '24/7 Emergency Services',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    
    # 4. Departments
    cur.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        icon TEXT DEFAULT 'fa-stethoscope',
        description TEXT,
        FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
    );
    ''')
    
    # 5. Doctors
    cur.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NULL,
        hospital_id INTEGER NOT NULL,
        department_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        qualification TEXT NOT NULL,
        specialization TEXT NOT NULL,
        experience_years INTEGER NOT NULL DEFAULT 5,
        consultation_fee REAL NOT NULL DEFAULT 500.00,
        available_days TEXT DEFAULT 'Mon, Tue, Wed, Thu, Fri',
        bio TEXT,
        image_url TEXT,
        cabin_number TEXT DEFAULT 'Cabin 102',
        rating REAL DEFAULT 4.9,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
        FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
    );
    ''')
    
    # 6. Doctor Schedules
    cur.execute('''
    CREATE TABLE IF NOT EXISTS doctor_schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        day_of_week TEXT NOT NULL DEFAULT 'ALL',
        start_time TEXT NOT NULL DEFAULT '09:00 AM',
        end_time TEXT NOT NULL DEFAULT '05:00 PM',
        slot_duration_minutes INTEGER DEFAULT 30,
        slots_json TEXT NOT NULL,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
    );
    ''')
    
    # 7. Appointments
    cur.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_number TEXT NOT NULL UNIQUE,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        hospital_id INTEGER NOT NULL,
        department_id INTEGER NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        reason_for_visit TEXT,
        status TEXT NOT NULL DEFAULT 'Confirmed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
        FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
        FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
    );
    ''')
    
    # 8. Payments
    cur.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_number TEXT NOT NULL UNIQUE,
        appointment_id INTEGER NOT NULL,
        patient_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        additional_charges REAL DEFAULT 50.00,
        total_amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT NOT NULL DEFAULT 'Success',
        transaction_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
    );
    ''')
    
    # 9. Appointment History
    cur.execute('''
    CREATE TABLE IF NOT EXISTS appointment_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        old_date TEXT,
        old_time TEXT,
        new_date TEXT,
        new_time TEXT,
        remarks TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE
    );
    ''')
    
    # 10. Notifications
    cur.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')
    
    conn.commit()
    conn.close()
    
    _seed_data()

def _ensure_test_users():
    """Ensure standard test passwords work with hashing."""
    try:
        users = query_db("SELECT id, email, password_hash FROM users WHERE email IN ('patient@gmail.com', 'doctor@gmail.com')")
        for u in users:
            # If hash is demo placeholder or needs refresh
            if not u['password_hash'].startswith('pbkdf2:sha256:') and not u['password_hash'].startswith('scrypt:'):
                new_hash = generate_password_hash('1234')
                query_db("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, u['id']), commit=True)
    except Exception as e:
        pass

def _seed_data():
    """Seed sample data if tables are empty."""
    user_count = query_db("SELECT COUNT(*) as count FROM users", one=True)
    if user_count and user_count['count'] > 0:
        return

    print("[DATABASE] Seeding comprehensive demo data...")
    pwd_hash = generate_password_hash('1234')
    
    # 1. Users
    u1 = query_db("INSERT INTO users (email, phone, password_hash, role) VALUES (%s, %s, %s, %s)",
                  ('patient@gmail.com', '9876543210', pwd_hash, 'patient'), commit=True)
    u2 = query_db("INSERT INTO users (email, phone, password_hash, role) VALUES (%s, %s, %s, %s)",
                  ('doctor@gmail.com', '9876543211', pwd_hash, 'doctor'), commit=True)
    u3 = query_db("INSERT INTO users (email, phone, password_hash, role) VALUES (%s, %s, %s, %s)",
                  ('patient2@gmail.com', '9876543212', pwd_hash, 'patient'), commit=True)

    # 2. Patients
    p1 = query_db("INSERT INTO patients (user_id, full_name, age, gender, blood_group, address, emergency_contact) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                  (u1, 'Vamshi Kumar', 28, 'Male', 'O+', '45 Metro Avenue, Tech City', '9876543299'), commit=True)
    p2 = query_db("INSERT INTO patients (user_id, full_name, age, gender, blood_group, address, emergency_contact) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                  (u3, 'Sarah Jenkins', 34, 'Female', 'A+', '12 Lake View Road, Green Park', '9876543288'), commit=True)

    # 3. Hospitals
    h1 = query_db("""INSERT INTO hospitals (name, tagline, location, address, phone, email, rating, total_reviews, image_url, description, emergency_hours)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                  ('ApexCare Multi-Speciality Hospital', 'Excellence in Tertiary Healthcare & Research',
                   'Downtown Medical District', '108 Healthcare Blvd, Central District',
                   '+91 (040) 4567-8901', 'contact@apexcare.org', 4.9, 342,
                   '/static/images/hospital-1.png',
                   'ApexCare is a premier JCI-accredited tertiary care medical center known for robotic cardiology, neurosurgery, and world-class inpatient care.',
                   '24/7 Level 1 Trauma & Emergency'), commit=True)

    h2 = query_db("""INSERT INTO hospitals (name, tagline, location, address, phone, email, rating, total_reviews, image_url, description, emergency_hours)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                  ('St. Jude Memorial Healthcare', 'Compassionate Care, Advanced Medical Technology',
                   'Westside Health Corridor', '74 West Park Ave, Westside Suburb',
                   '+91 (040) 7890-1234', 'info@stjudememorial.org', 4.8, 285,
                   '/static/images/hospital-2.png',
                   'St. Jude Memorial provides holistic, patient-centered clinical services featuring leading oncology, dermatology, and comprehensive wellness programs.',
                   '24/7 Emergency & Critical Care'), commit=True)

    h3 = query_db("""INSERT INTO hospitals (name, tagline, location, address, phone, email, rating, total_reviews, image_url, description, emergency_hours)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                  ('Horizon Children & Family Hospital', 'Dedicated to Next-Generation Family Wellness',
                   'North City Campus', '22 North Ring Road, North Campus',
                   '+91 (040) 2345-6789', 'care@horizonhealth.org', 4.9, 198,
                   '/static/images/hospital-3.png',
                   'Horizon Hospital is specialized in pediatric critical care, radiology diagnostics, and comprehensive maternal-family medicine with specialized child facilities.',
                   '24/7 Pediatric Emergency Care'), commit=True)

    # 4. Departments
    # ApexCare
    d1 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                  (h1, 'Cardiology', 'fa-heart-pulse', 'Comprehensive heart care, catheterization lab, bypass surgery, and non-invasive cardiac imaging.'), commit=True)
    d2 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                  (h1, 'Neurology & Neurosurgery', 'fa-brain', 'Advanced diagnostics and microscopic surgical interventions for brain and spine disorders.'), commit=True)
    d3 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                  (h1, 'Orthopedics & Joint Care', 'fa-bone', 'Total joint replacements, sports injuries, arthroscopic surgeries, and musculoskeletal rehab.'), commit=True)
    d4 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                  (h1, 'General Medicine', 'fa-stethoscope', 'Primary care, preventive health check-ups, chronic lifestyle disease management, and internal medicine.'), commit=True)

    # St. Jude
    d5 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                  (h2, 'Oncology & Cancer Care', 'fa-ribbon', 'Precision chemotherapy, surgical oncology, immunotherapy, and dedicated patient support.'), commit=True)
    d6 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                  (h2, 'Dermatology & Cosmetology', 'fa-hand-dots', 'Specialized skin, hair, and nail treatments, cosmetic lasers, and allergy diagnostics.'), commit=True)
    d7 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                  (h2, 'Cardiology', 'fa-heart-pulse', 'Preventive cardiac checkups, ECG/Echo, hypertension management, and heart failure clinics.'), commit=True)
    d8 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                  (h2, 'General Medicine', 'fa-stethoscope', 'General physician consultation, infectious diseases, fever clinics, and elderly healthcare.'), commit=True)

    # Horizon
    d9 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                  (h3, 'Pediatrics & Neonatology', 'fa-baby', 'Specialized neonatal ICU, child vaccination, growth monitoring, and pediatric surgery.'), commit=True)
    d10 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                   (h3, 'Radiology & Imaging', 'fa-x-ray', 'High-field MRI 3.0T, 128-slice CT scans, ultrasound 4D, and digital mammography.'), commit=True)
    d11 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                   (h3, 'General Medicine', 'fa-stethoscope', 'Family healthcare, seasonal flu treatments, diagnostic screenings, and outpatient checkups.'), commit=True)
    d12 = query_db("INSERT INTO departments (hospital_id, name, icon, description) VALUES (%s, %s, %s, %s)",
                   (h3, 'Dermatology', 'fa-hand-dots', 'Pediatric eczema, general dermatology, and rash treatment center.'), commit=True)

    # 5. Doctors
    default_slots = json.dumps([
        "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", 
        "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM", 
        "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"
    ])

    doctors_data = [
        (u2, h1, d1, 'Dr. Rajesh Sharma', 'MD, DM (Cardiology), FACC', 'Senior Consultant Interventional Cardiologist', 16, 750.00, 'Mon, Tue, Wed, Thu, Fri, Sat', 'Dr. Rajesh Sharma has performed over 4,500 coronary interventions and specializes in complex angioplasties and preventative cardiology.', '/static/images/doctor-1.png', 'Cabin 204, 2nd Floor', 4.9),
        (None, h1, d2, 'Dr. Priya Patel', 'MD, DNB (Neurology), DM', 'Chief Neurologist & Spine Specialist', 13, 800.00, 'Mon, Tue, Wed, Thu, Fri', 'Dr. Priya Patel is an internationally recognized expert in stroke rehabilitation, epilepsy management, and neuromuscular disorders.', '/static/images/doctor-2.png', 'Cabin 308, 3rd Floor', 4.9),
        (None, h1, d3, 'Dr. Vikram Reddy', 'MS (Ortho), M.Ch (UK), Fellowship in Joint Replacement', 'Senior Orthopedic & Joint Replacement Surgeon', 15, 700.00, 'Mon, Wed, Fri, Sat', 'Specialist in robotic knee and hip arthroplasty, complex trauma, and sports medicine with over 15 years of surgical excellence.', '/static/images/doctor-3.png', 'Cabin 112, 1st Floor', 4.8),
        (None, h1, d4, 'Dr. Arjun Mehta', 'MBBS, MD (Internal Medicine)', 'Consultant Physician & Diabetologist', 9, 500.00, 'Mon, Tue, Wed, Thu, Fri, Sat', 'Expert in comprehensive adult medicine, metabolic disorders, hypertension, and preventive health screenings.', '/static/images/doctor-4.png', 'Cabin 105, 1st Floor', 4.7),
        (None, h2, d5, 'Dr. David Miller', 'MD, DM (Medical Oncology), ESMO', 'Director of Clinical Oncology', 18, 900.00, 'Tue, Wed, Thu, Fri, Sat', 'Pioneer in targeted therapies and immunotherapy with fellowship training from Memorial Sloan Kettering.', '/static/images/doctor-5.png', 'Cabin 401, 4th Floor', 4.9),
        (None, h2, d6, 'Dr. Sneha Kulkarni', 'MD (Dermatology, Venereology & Leprosy)', 'Consultant Dermatologist & Dermato-Surgeon', 8, 600.00, 'Mon, Tue, Thu, Fri, Sat', 'Specialized in clinical dermatology, acne scarring, laser procedures, and pediatric skin conditions.', '/static/images/doctor-1.png', 'Cabin 210, 2nd Floor', 4.8),
        (None, h3, d9, 'Dr. Ananya Sen', 'MD (Pediatrics), DCH, FAAP', 'Senior Pediatrician & Neonatologist', 12, 650.00, 'Mon, Tue, Wed, Thu, Fri, Sat', 'Compassionate pediatric specialist caring for child developmental milestones, immunizations, and newborn critical care.', '/static/images/doctor-2.png', 'Cabin 108, Pediatric Wing', 5.0),
        (None, h3, d10, 'Dr. Kavita Nair', 'MD (Radiodiagnosis), FICR', 'Senior Consultant Radiologist', 11, 550.00, 'Mon, Tue, Wed, Thu, Fri', 'Extensive expertise in advanced neuro-imaging, musculoskeletal MRI, fetal ultrasound, and image-guided procedures.', '/static/images/doctor-3.png', 'Cabin B-04, Radiology Center', 4.8)
    ]

    for doc in doctors_data:
        doc_id = query_db("""INSERT INTO doctors (user_id, hospital_id, department_id, full_name, qualification, specialization, experience_years, consultation_fee, available_days, bio, image_url, cabin_number, rating)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                          doc, commit=True)
        # Schedule
        query_db("""INSERT INTO doctor_schedules (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes, slots_json)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                 (doc_id, 'ALL', '09:00 AM', '05:00 PM', 30, default_slots), commit=True)

    # 6. Sample Initial Appointments for Demo Patient 1
    today = date.today()
    future_date = (today + timedelta(days=2)).strftime('%Y-%m-%d')
    past_date = (today - timedelta(days=10)).strftime('%Y-%m-%d')

    apt1 = query_db("""INSERT INTO appointments (appointment_number, patient_id, doctor_id, hospital_id, department_id, appointment_date, appointment_time, reason_for_visit, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    ('APT-2026-10492', p1, 1, h1, d1, future_date, '10:30 AM', 'Routine cardiac health screening and blood pressure consultation', 'Confirmed'), commit=True)

    apt2 = query_db("""INSERT INTO appointments (appointment_number, patient_id, doctor_id, hospital_id, department_id, appointment_date, appointment_time, reason_for_visit, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    ('APT-2026-09281', p1, 4, h1, d4, past_date, '02:30 PM', 'Annual executive physical examination and fasting lipid profile', 'Completed'), commit=True)

    # 7. Payments
    query_db("""INSERT INTO payments (payment_number, appointment_id, patient_id, amount, additional_charges, total_amount, payment_method, payment_status, transaction_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
             ('PAY-MED-77102', apt1, p1, 750.00, 50.00, 800.00, 'UPI', 'Success', 'TXN_UPI_882940172'), commit=True)

    query_db("""INSERT INTO payments (payment_number, appointment_id, patient_id, amount, additional_charges, total_amount, payment_method, payment_status, transaction_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
             ('PAY-MED-66104', apt2, p1, 500.00, 50.00, 550.00, 'Credit Card', 'Success', 'TXN_CC_449201938'), commit=True)

    # 8. Appointment History
    query_db("""INSERT INTO appointment_history (appointment_id, action, old_date, old_time, new_date, new_time, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
             (apt1, 'Created', None, None, future_date, '10:30 AM', 'Initial appointment booked via online portal'), commit=True)

    query_db("""INSERT INTO appointment_history (appointment_id, action, old_date, old_time, new_date, new_time, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
             (apt2, 'Created', None, None, past_date, '02:30 PM', 'Appointment booked and completed successfully'), commit=True)

    # 9. Notifications
    query_db("INSERT INTO notifications (user_id, title, message, is_read) VALUES (%s, %s, %s, %s)",
             (u1, 'Appointment Confirmed', 'Your appointment with Dr. Rajesh Sharma for Cardiology has been confirmed for 10:30 AM.', 0), commit=True)
    query_db("INSERT INTO notifications (user_id, title, message, is_read) VALUES (%s, %s, %s, %s)",
             (u1, 'Welcome to MediCare', 'Thank you for registering with MediCare Hospital Connect. Access your medical records anytime.', 1), commit=True)
    query_db("INSERT INTO notifications (user_id, title, message, is_read) VALUES (%s, %s, %s, %s)",
             (u2, 'New Patient Appointment', 'Patient Vamshi Kumar has booked a consultation slot on your schedule.', 0), commit=True)

    print("[DATABASE] Demo data successfully seeded!")
