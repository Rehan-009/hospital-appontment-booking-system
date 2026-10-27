"""
Hospital Appointment Booking System (HABS)
Root Application Runner

To launch:
    python app.py
"""
import sys
import os

# Ensure current directory is in Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import app

if __name__ == '__main__':
    print("\n" + "=" * 65)
    print("  MediCare Hospital Appointment Booking System (HABS)  ")
    print("  Local Server: http://127.0.0.1:5000                   ")
    print("  Demo Patient: patient@gmail.com  | Password: 1234      ")
    print("  Demo Doctor:  doctor@gmail.com   | Password: 1234      ")
    print("=" * 65 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
