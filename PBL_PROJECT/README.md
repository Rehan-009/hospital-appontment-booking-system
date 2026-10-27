# MediCare Connect - Hospital Appointment Booking System (HABS)

A modern, full-featured desktop-oriented **Hospital Appointment Booking System** built with **Python Flask**, **MySQL**, and modern **HTML5/CSS3/JavaScript**.

---

## 🏥 Project Overview & Features

MediCare Connect is designed as an enterprise-grade hospital network portal. It enables patients to discover accredited hospitals, consult verified specialists, book confirmed time slots with double-booking prevention, complete simulated payments, download/print official clinical receipts, and manage appointments with instant rescheduling and cancellation.

### 🌟 Key Highlights
* **Desktop-First Healthcare Design**: Clean medical aesthetics with light backgrounds, calming blue/teal accents, rounded cards, subtle elevated shadows, and no template bloat.
* **Authentication Modal with Role-Based Routing**:
  * Unified Modal for Sign In and Account Registration.
  * Role-based access control protecting `/patient` and `/doctor/dashboard`.
  * One-click demo credential autofill for easy evaluation.
* **Complete End-to-End Booking Funnel**:
  $$\text{Home} \rightarrow \text{Select Hospital} \rightarrow \text{Select Doctor} \rightarrow \text{Pick Date \& Slot} \rightarrow \text{Summary} \rightarrow \text{Payment} \rightarrow \text{Confirmation Receipt}$$
* **Real-Time Slot Engine**:
  * Dynamic AJAX slot loading based on doctor schedules.
  * Real-time booked slot detection disabling duplicate bookings.
  * Past date protection preventing invalid reservations.
* **Simulated Multi-Gateway Payment Engine**:
  * UPI (with simulated QR code & VPA validation).
  * Credit Card (live card preview, chip animation, formatting).
  * Debit Card & Net Banking (popular bank grid).
  * Simulated gateway authorization with security status updates.
* **Official Hospital Receipt & Print Engine**:
  * Clean printable receipt layout with barcode, transaction reference, cabin number, and hospital accreditation details (`@media print` supported).
* **Interactive Patient Dashboard (`/patient`)**:
  * Stats: Upcoming, Completed, Cancelled, and Total visits.
  * Reschedule modal: Live slot availability check, date selection, appointment history logging.
  * Cancel modal: Warning prompt, time slot release, and simulated demo refund status.
  * Personal medical records and profile editor.
* **Interactive Doctor Dashboard (`/doctor/dashboard`)**:
  * Today's consultation roster with patient demographics and reason for visit.
  * "Mark as Completed" status toggle.
  * Doctor schedule viewer and patient registry.

---

## 🛠️ Technology Stack

* **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6+), Font Awesome 6.7.2, Google Fonts (Plus Jakarta Sans & Inter)
* **Backend**: Python 3 (Flask, Werkzeug)
* **Database**: MySQL 8.0+ (with automatic zero-config fallback to SQLite if MySQL service is not authenticated)
* **API Architecture**: RESTful JSON APIs between frontend and backend
* **Template Engine**: Flask Jinja2 with template inheritance (`base.html`)

---

## 📁 Project Directory Structure

```
PBL_PROJECT/
│
├── app.py                      # Root Application Runner (python app.py)
├── requirements.txt            # Python Dependencies
├── test_flow.py                # 18-Step Automated Verification Test Suite
├── README.md                   # Documentation & Setup Guide
│
├── backend/
│   ├── app.py                  # Flask Application Factory & URL Routes
│   ├── config.py               # Environment & Database Configuration
│   ├── database.py             # Dual Engine DB Connector (MySQL + SQLite fallback)
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py           # Data Access Layer & Business Logic
│   └── routes/
│       ├── __init__.py
│       ├── auth_routes.py      # Register, Login, Session status, Logout
│       ├── hospital_routes.py  # Hospitals, Departments, Doctors, Availability API
│       ├── appointment_routes.py # Booking, Simulated Payment, Reschedule, Cancel
│       └── dashboard_routes.py # Patient & Doctor Dashboard Data
│
├── frontend/
│   ├── templates/
│   │   ├── base.html           # Master Layout + Navigation + Auth Modal
│   │   ├── index.html          # Professional Hospital Landing Page
│   │   ├── hospitals.html      # Hospital Selection & Location Filters
│   │   ├── doctors.html        # Doctor Selection & Specialty Cards
│   │   ├── appointment.html    # Interactive Date & Dynamic Time Slot Picker
│   │   ├── summary.html        # Pre-Payment Review & Itemized Charges
│   │   ├── payment.html        # Multi-option Simulated Payment Page
│   │   ├── confirmation.html   # Official Printable Hospital Receipt
│   │   ├── patient.html        # Patient Dashboard (Stats, Reschedule, Cancel)
│   │   └── doctor_dashboard.html # Doctor Dashboard (Roster, Status updates)
│   │
│   └── static/
│       ├── css/
│       │   ├── style.css       # Core Healthcare Theme, Navbar, Cards, Modal
│       │   ├── booking.css     # Stepper, Slot Grid, Payment & Receipt Styles
│       │   └── dashboard.css   # Sidebar, Stat Counters, Appointment Rows
│       ├── js/
│       │   ├── script.js       # Auth Modal, Form Submissions, Toast Alerts
│       │   ├── booking.js      # Dynamic Availability & Payment Engine
│       │   ├── patient.js      # Reschedule & Cancel Modal Operations
│       │   └── doctor.js       # Status Toggle & Roster Updates
│       └── images/             # Hospital Photos, Doctor Profiles, Logo
│
└── database/
    ├── schema.sql              # MySQL DDL Schema
    ├── seed.sql                # MySQL Sample Data Insert Script
    ├── setup_db.py             # Automated DB Initializer & Seeder
    └── hospital.db             # Auto-generated SQLite Database (Fallback)
```

---

## 🚀 Quick Start (Running Locally)

### 1. Install Dependencies
Open PowerShell or Terminal in the project directory:
```bash
pip install -r requirements.txt
```

### 2. Start the Application
Run the root launcher:
```bash
python app.py
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Demo Test Accounts

You can log in immediately using the pre-seeded demo accounts or use the **Quick Demo Fill** buttons inside the Sign In modal:

| Role | Email Address | Password | Name | Access Level |
|---|---|---|---|---|
| **Patient** | `patient@gmail.com` | `1234` | Vamshi Kumar | `/patient` (Booking, Rescheduling, Receipts) |
| **Doctor** | `doctor@gmail.com` | `1234` | Dr. Rajesh Sharma | `/doctor/dashboard` (Roster, Mark Completed) |
| **Patient 2** | `patient2@gmail.com` | `1234` | Sarah Jenkins | `/patient` (Pre-seeded test records) |

*(Note: You can also register any new patient or doctor account directly via the registration form).*

---

## 🗄️ MySQL Database Setup & Dual-Engine Architecture

This project includes a **Dual-Engine Database Connector** in `backend/database.py`:
* **MySQL 8.0 Native Support**: Designed for MySQL 8.0+.
* **Automatic Fallback Guarantee**: If MySQL root credentials differ or MySQL is not running on port 3306, the system **automatically** switches to a local SQLite database (`database/hospital.db`) populated with the exact same tables and seed data. This guarantees that `python app.py` **runs immediately with zero setup errors**.

### Connecting to your MySQL Server
To use your local MySQL server:
1. Open `backend/config.py` (or set environment variables):
   ```python
   DB_HOST = '127.0.0.1'
   DB_PORT = 3306
   DB_USER = 'root'
   DB_PASSWORD = 'your_mysql_password'  # Enter your MySQL root password here
   DB_NAME = 'hospital_db'
   ```
2. Run the database setup script:
   ```bash
   python database/setup_db.py
   ```
   Or import the SQL files directly in MySQL Workbench / CLI:
   ```bash
   mysql -u root -p < database/schema.sql
   mysql -u root -p < database/seed.sql
   ```

---

## 🧪 Automated Testing

An automated verification test script covering all 18 key scenarios is included:
```bash
python test_flow.py
```
**Test Coverage:**
1. Home page rendering
2. Hospital discovery page
3. Doctor selection page
4. REST API `/api/hospitals` (3 hospitals verified)
5. REST API `/api/doctors` (8 doctors verified)
6. Dynamic availability check (`/api/doctors/<id>/availability`)
7. Past date validation error handling (400 Bad Request)
8. Invalid credentials rejection (401 Unauthorized)
9. Patient authentication & session establishment
10. Patient dashboard metrics retrieval
11. Slot reservation & appointment creation
12. Double booking prevention (409 Conflict)
13. Payment simulation & transaction generation
14. Confirmation receipt rendering
15. Rescheduling appointment to new date & time
16. Cancellation with simulated demo refund
17. Doctor login & doctor dashboard data
18. Role access protection (redirecting doctor from patient portal)

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/register` | Register new user as patient or doctor |
| `POST` | `/api/login` | Authenticate user & establish session |
| `GET` | `/api/auth/status` | Current logged-in user state |
| `POST` | `/api/logout` | Terminate session |
| `GET` | `/api/hospitals` | List hospitals with optional location/dept filters |
| `GET` | `/api/hospitals/<id>` | Single hospital details, depts, doctors |
| `GET` | `/api/departments` | Distinct hospital departments |
| `GET` | `/api/doctors` | List doctors with filter by hospital/dept |
| `GET` | `/api/doctors/<id>/availability?date=YYYY-MM-DD` | Dynamic slot availability |
| `POST` | `/api/appointments` | Reserve consultation slot |
| `GET` | `/api/appointments` | Retrieve patient/doctor appointments |
| `GET` | `/api/appointments/<id>` | Full appointment & receipt details |
| `POST` | `/api/payment` | Process simulated payment & confirm booking |
| `PUT` | `/api/appointments/<id>/reschedule` | Change appointment date and slot |
| `PUT` | `/api/appointments/<id>/cancel` | Cancel booking & trigger demo refund |
| `GET` | `/api/patient/dashboard` | Patient statistics, visits, and profile |
| `GET` | `/api/doctor/dashboard` | Doctor today's roster, schedule, patient count |
| `PUT` | `/api/doctor/appointments/<id>/status` | Update visit status (Mark Completed) |
| `PUT` | `/api/patient/profile` | Update patient medical and contact info |

---

## 📜 Academic Integrity / PBL Notes
* Built for desktop and laptop displays with modern responsive layouts.
* Payment processing is strictly simulated in demo mode for safety and compliance.
* All data entered into appointments dynamically updates the patient dashboard and doctor roster.
