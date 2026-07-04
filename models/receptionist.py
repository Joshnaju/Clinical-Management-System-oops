from models.appointment import Appointment
from models.patient import Patient

class Receptionist:
    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.patient = Patient(self.db, user)
        self.appointment = Appointment(self.db, user)

    def dashboard(self):
        while True:
            print("""
=====================================
    RECEPTIONIST DASHBOARD
=====================================

1. Patient Management
2. Scheduling
3. Logout

=====================================
""")

            choice = input("Enter your choice: ")

            match choice:
                case "1":
                    self.patient_management()

                case "2":
                    self.scheduling()

                case "3":
                    print("Logging out...")
                    break

                case _:
                    print("Invalid choice.")


    def patient_management(self):
        while True:
            print("""
===========================
    Patient Management
===========================

1. Register Patient
2. View Patient
3. Search Patient
4. Update Patient
5. Disable Patient
6. Back

===========================
""")

            choice = input("Enter choice : ")
            match choice:
                case "1":
                    self.patient.register_patient()

                case "2":
                    self.patient.view_patients()

                case "3":
                    self.patient.search_patient()

                case "4":
                    self.patient.update_patient()

                case "5":
                    self.patient.disable_patient()

                case "6":
                    break

                case _:
                    print("Invalid choice.")


    def scheduling(self):
        while True:

            print("""
====================================
    APPOINTMENT SCHEDULING
====================================

1. Book Appointment
2. Walk-in Consultation
3. Back
    """)

            choice = input("Enter your choice : ").strip()

            match choice:

                case "1":
                    self.appointment.book_appointment()

                case "2":
                    self.appointment.walkin_consultation()

                case "3":
                    return

                case _:
                    print("Invalid Choice.")

  