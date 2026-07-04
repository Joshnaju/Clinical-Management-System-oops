import datetime
from enums import Role
from models.patient import Patient
from utils.exceptions import BackRequested
from utils.helper import Helper

class Appointment:
    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.patient = Patient(db, user)
        self.create_table()

    def create_table(self):
        query="""
        CREATE TABLE IF NOT EXISTS appointments(
            appointment_id INT AUTO_INCREMENT PRIMARY KEY,
            appointment_code VARCHAR(10) UNIQUE NOT NULL,
            patient_id INT NOT NULL,
            doctor_id INT NOT NULL,
            appointment_date DATE NOT NULL,
            consultation_start_time TIME NOT NULL,
            consultation_end_time TIME NOT NULL,
            token_number INT NOT NULL,
            status ENUM('Scheduled','Completed','Cancelled') DEFAULT 'Scheduled',
            created_by INT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY(doctor_id) REFERENCES users(user_id),
            FOREIGN KEY(created_by) REFERENCES users(user_id)
        );
        """

        self.db.execute_query(query)
        self.db.commit()


    def view_appointments(self):
        pass

    def search_appointment(self):
        pass

    def cancel_appointment(self):
        pass

    def generate_appointment_code(self):
        query = "SELECT COUNT(*) AS total FROM appointments"
        self.db.execute_query(query)
        count = self.db.fetch_one()["total"]
        return f"APT{count+1:03d}"
    
    def book_appointment(self):
        while True:

            print("""
====================================
    BOOK APPOINTMENT
====================================

1. New Patient
2. Existing Patient
3. Back
    """)

            Helper.show_back_option()
            try:
                choice = Helper.get_input("Enter choice : ").strip()

                match choice:

                    case "1":

                        patient_code = self.patient.register_patient()

                        if patient_code:
                            self.schedule_appointment(patient_code, False)

                    case "2":

                        self.schedule_appointment()

                    case "3":
                        return

                    case _:
                        print("Invalid Choice.")
            except BackRequested:
                return

    def walkin_consultation(self):
            while True:

                print("""
====================================
    WALK-IN CONSULTATION
====================================

1. New Patient
2. Existing Patient
3. Back
        """)
                try:
                    Helper.show_back_option()
                    choice = Helper.get_input("Enter choice : ")

                    match choice:
                        case "1":

                            patient_code = self.patient.register_patient()

                            if patient_code:
                                self.schedule_appointment(patient_code, True)

                        case "2":
                            self.schedule_appointment(is_walkin=True)

                        case "3":
                            return

                        case _:
                            print("Invalid Choice.")
                except BackRequested:
                    print("Returning to the previous menu...")
                    return
                
def schedule_appointment(self, patient_code=None, is_walkin=False):

    while True:
        print("""
====================================
    SCHEDULE APPOINTMENT
====================================
""")

    
        Helper.show_back_option()
        try:
            # -----------------------------
            # Patient
            # -----------------------------
            if patient_code is None:
                patient_code = Helper.get_input("Enter Patient Code : ").strip().upper()

            if not patient_code:
                print("Patient Code is required.")
                patient_code = None
                continue

            query = """
            SELECT patient_id, patient_code, name
            FROM patients
            WHERE patient_code=%s
            AND is_active=TRUE
            """

            self.db.execute_query(query, (patient_code,))
            patient = self.db.fetch_one()

            if not patient:
                print("\nPatient not found.\n")
                patient_code = None
                continue

            print(f"\nPatient : {patient['name']}")

            # -----------------------------
            # Department
            # -----------------------------
            print("""
    Departments

    1. General Medicine
    2. Cardiology
    3. Orthopedics
    4. Pediatrics
    5. ENT
    6. Dermatology
    7. Neurology
    8. Gynecology
    """)

            departments = {
                "1": "General Medicine",
                "2": "Cardiology",
                "3": "Orthopedics",
                "4": "Pediatrics",
                "5": "ENT",
                "6": "Dermatology",
                "7": "Neurology",
                "8": "Gynecology"
            }

            while True:

                choice = Helper.get_input("Choose Department : ")

                if choice in departments:
                    department = departments[choice]
                    break

                print("Invalid Department.")

            # -----------------------------
            # Doctors
            # -----------------------------
            query = """
            SELECT user_id,
                user_code,
                name
            FROM users
            WHERE role=%s
            AND department=%s
            AND is_active=TRUE
            """

            values = (Role.DOCTOR, department)

            self.db.execute_query(query, values)

            doctors = self.db.fetch_all()

            if not doctors:
                print("\nNo doctors available.\n")
                continue

            print("\nAvailable Doctors\n")

            for doctor in doctors:
                print(f"{doctor['user_code']} - {doctor['name']}")

            while True:

                doctor_code = Helper.get_input("\nEnter Doctor Code : ").upper()

                selected = None

                for doctor in doctors:

                    if doctor["user_code"] == doctor_code:
                        selected = doctor
                        break

                if selected:
                    doctor_id = selected["user_id"]
                    doctor_name = selected["name"]
                    break

                print("Invalid Doctor Code.")

            # -----------------------------
            # Appointment Date
            # -----------------------------
            if is_walkin:

                appointment_date = datetime.today().date()

                print(f"\nAppointment Date : {appointment_date}")

            else:

                while True:

                    date_input = Helper.get_input(
                        "Appointment Date (YYYY-MM-DD): "
                    )

                    try:

                        appointment_date = datetime.strptime(
                            date_input,
                            "%Y-%m-%d"
                        ).date()

                        today = datetime.today().date()

                        if appointment_date < today:
                            print("Past date not allowed.")
                            continue

                        if appointment_date > today + datetime.timedelta(days=2):
                            print(
                                "Booking allowed only for today and next 2 days."
                            )
                            continue

                        break

                    except:
                        print("Invalid Date.")
        except BackRequested:
            print("Returning to the previous menu...")
            return

        # -----------------------------
        # Token
        # -----------------------------
        query = """
        SELECT COUNT(*) AS total
        FROM appointments
        WHERE doctor_id=%s
        AND appointment_date=%s
        """

        values = (
            doctor_id,
            appointment_date
        )

        self.db.execute_query(query, values)

        count = self.db.fetch_one()["total"]

        token_number = count + 1

        # -----------------------------
        # Consultation Time
        # -----------------------------
        clinic_start = datetime.strptime(
            "09:00",
            "%H:%M"
        )

        slot_duration = 15

        consultation_start = clinic_start + datetime.timedelta(
            minutes=(token_number - 1) * slot_duration
        )

        consultation_end = consultation_start + datetime.timedelta(
            minutes=slot_duration
        )

        consultation_start = consultation_start.time()
        consultation_end = consultation_end.time()

        # -----------------------------
        # Appointment Code
        # -----------------------------
        appointment_code = self.generate_appointment_code()

        # -----------------------------
        # Save
        # -----------------------------
        query = """
        INSERT INTO appointments(
            appointment_code,
            patient_id,
            doctor_id,
            appointment_date,
            consultation_start_time,
            consultation_end_time,
            token_number,
            created_by
        )
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            appointment_code,
            patient["patient_id"],
            doctor_id,
            appointment_date,
            consultation_start,
            consultation_end,
            token_number,
            self.user["user_id"]
        )

        self.db.execute_query(query, values)
        self.db.commit()

        print("""
====================================
Appointment Scheduled Successfully
====================================
""")

        print("Appointment Code :", appointment_code)
        print("Patient          :", patient["name"])
        print("Doctor           :", doctor_name)
        print("Token Number     :", token_number)
        print("Appointment Date :", appointment_date)
        print(
            "Consultation     :",
            consultation_start.strftime("%I:%M %p"),
            "-",
            consultation_end.strftime("%I:%M %p")
        )

        return