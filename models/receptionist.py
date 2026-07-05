from models.appointment import Appointment
from models.patient import Patient
from utils.exceptions import BackRequested
from utils.helper import Helper

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
3. Appointment Management
4. Logout

=====================================
""")
            try:
                choice = Helper.get_input("Enter your choice: ")

                match choice:
                    case "1":
                        self.patient_management()

                    case "2":
                        self.scheduling()

                    case "3":
                        self.appointment_management()

                    case "4":
                        print("Logging out...")
                        return

                    case _:
                        print("Invalid choice.")
            except BackRequested:
                print("Returning to the previous menu...")
                break


    def patient_management(self):
        while True:
            print("""
=====================================
    Patient Management
=====================================

1. Register Patient
2. View Patient
3. Search Patient
4. Update Patient
5. Disable Patient
6. Back

=====================================
""")
            Helper.show_back_option()
            try:
                choice = Helper.get_input("Enter choice : ")
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
            except BackRequested:
                print("Returning to the previous menu...")
                break

    def scheduling(self):
        while True:

            print("""
=====================================
    APPOINTMENT SCHEDULING
=====================================

1. Book Appointment
2. Walk-in Consultation
3. Back
    """)
            Helper.show_back_option()
            try:
                choice = Helper.get_input("Enter your choice : ")

                match choice:

                    case "1":
                        self.appointment.book_appointment()

                    case "2":
                        self.appointment.walkin_consultation()

                    case "3":
                        break

                    case _:
                        print("Invalid Choice.")
            except BackRequested:
                print("Returning to the previous menu...")
                break
                    
    def appointment_management(self):
        while True:
            print("""
====================================
      APPOINTMENT MENU
====================================

1. View Appointments
2. Search Appointment
3. Cancel Appointment
4. Back

====================================
""")
            Helper.show_back_option()
            try:
                choice = Helper.get_input("Enter your choice : ")

                match choice:
                    case "1":
                        self.appointment.view_appointments()

                    case "2":
                        self.appointment.search_appointment()

                    case"3":
                        self.appointment.cancel_appointment()

                    case "4":
                        return

                    case _:
                        print("Invalid choice.")
            except BackRequested:
                print("Returning to the previous menu...")
                break