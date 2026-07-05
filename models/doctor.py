from services.doctor_service import DoctorService
from utils.helper import Helper
from utils.exceptions import BackRequested

class Doctor:
    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.service = DoctorService(db, user)

    def dashboard(self):

        while True:

            print("""
=====================================
        DOCTOR DASHBOARD
=====================================

1. Today's Appointments
2. Search Appointment
3. Consult Patient
4. View Consultation History
5. Logout
""")

            choice = input("Enter your choice : ").strip()

            match choice:

                case "1":
                    self.service.today_appointments()

                case "2":
                    self.service.search_appointment()

                case "3":
                    self.service.consult_patient()

                case "4":
                    self.service.consultation_history()

                case "5":
                    print("\nLogging out...")
                    return

                case _:
                    print("Invalid Choice.")
