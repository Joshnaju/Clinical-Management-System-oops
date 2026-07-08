# import datetime
from datetime import datetime, timedelta, date
from enums import Role
from enums import AppointmentStatus
from models.patient import Patient
from utils.exceptions import BackRequested
from utils.helper import Helper
from models.billing import Billing
from utils.constants import CLINIC_START_TIME, CLINIC_END_TIME, SLOT_DURATION
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

            UNIQUE (doctor_id, appointment_date, token_number),
            FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY(doctor_id) REFERENCES users(user_id),
            FOREIGN KEY(created_by) REFERENCES users(user_id)
        );
        """

        self.db.execute_query(query)
        self.db.commit()

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
                        patient_code,patient_id,patient_name = self.patient.register_patient()
                        if patient_code:
                            self.schedule_appointment(patient_code,patient_id,patient_name, False,is_new_patient=True)

                    case "2":
                        self.schedule_appointment(patient_code=None,patient_id=None,patient_name=None,is_new_patient=False)

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
                            patient_code,patient_id,patient_name = self.patient.register_patient()
                            if patient_code:
                                self.schedule_appointment(patient_code,patient_id,patient_name,True,is_new_patient=True)

                        case "2":
                            if not Helper.is_walkin_available():
                                print("\nToday's walk-in consultation time is over.")
                                print("Walk-in appointments are not available.\n")
                                return
                            self.schedule_appointment(patient_code=None,patient_id=None,patient_name=None,is_walkin=True,is_new_patient=False)

                        case "3":
                            return

                        case _:
                            print("Invalid Choice.")

                except BackRequested:
                    print("Returning to the previous menu...")
                    return
                
    def schedule_appointment(self, patient_code=None, patient_id=None, patient_name=None, is_walkin=False,is_new_patient=False):
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
                if patient_code is not None and patient_id is not None and patient_name is not None:
                    patient = {}
                    print(f"\nPatient : {patient_name}")
                    patient["patient_id"]=patient_id
                    patient["name"]=patient_name
                    patient["patient_code"]=patient_code

                else:
                    if patient_code is None:
                        patient_code = Helper.get_input("Enter Patient Code : ").upper()

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

                    values = (patient_code,)
                    self.db.execute_query(query, values)
                    patient = self.db.fetch_one()

                    if not patient:
                        print("\nPatient not found.\n")
                        patient_code = None
                        continue

                    print(f"\nPatient : {patient['name']}")


                  # ==================================================
                # -----------------------------
                # WALK-IN CHECK
                # -----------------------------
                if is_walkin:
                    if not Helper.is_walkin_available():
                        print("\nToday's walk-in consultation time is over.")
                        print("Walk-in appointments are not available.\n")
                        return

                    appointment_date = date.today()
                    print(f"\nAppointment Date : {appointment_date}")
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
                    name,
                    consultation_fee
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
                        doctor_consultation_fee=selected["consultation_fee"]
                        break

                    print("Invalid Doctor Code.")

                # -----------------------------
                # Appointment Date
                # -----------------------------

                if not is_walkin:
                    while True:

                        date_input = Helper.get_input("Appointment Date (YYYY-MM-DD): ")

                        try:

                            appointment_date = datetime.strptime(date_input,"%Y-%m-%d").date()
                            today = date.today()

                            if appointment_date < today:
                                print("Past date not allowed.")
                                continue

                            if appointment_date > today + timedelta(days=2):
                                print("Booking allowed only for today and next 2 days.")
                                continue

                            break
                        except ValueError as e:
                            print(e)
            except BackRequested:
                print("Returning to the previous menu...")
                return

            # -----------------------------
            # Duplicate Appointment Check
            # -----------------------------
            query = """
            SELECT COUNT(*) AS total
            FROM appointments
            WHERE patient_id=%s
            AND doctor_id=%s
            AND appointment_date=%s
            AND status=%s
            """

            values = (
                patient["patient_id"],
                doctor_id,
                appointment_date,
                AppointmentStatus.SCHEDULED
            )

            self.db.execute_query(query, values)

            count = self.db.fetch_one()["total"]

            current_time = datetime.now().time()
            clinic_end = datetime.strptime("18:00", "%H:%M").time()

            if appointment_date == date.today() and current_time >= clinic_end:
                print("\nToday's consultation time is over.")
                print("Please book for tomorrow or the next available day.\n")
                continue

            if count > 0:
                print("\nPatient already has an appointment with this doctor on this date.\n")
                continue

            #BILLING
            bill = Billing(self.user)

            payment_success,bill_id = bill.generate_bill(patient,doctor_name,doctor_consultation_fee)

            if not payment_success:
                return
            # -----------------------------
            # Token
            # -----------------------------
            query = """
            SELECT COALESCE(MAX(token_number), 0) AS last_token
            FROM appointments
            WHERE doctor_id=%s
            AND appointment_date=%s
            AND status=%s
            """
            values = (
                doctor_id,
                appointment_date,
                AppointmentStatus.SCHEDULED
            )

            self.db.execute_query(query, values)
            last_token = self.db.fetch_one()["last_token"]
            token_number = last_token + 1

            # -----------------------------
            # Consultation Time
            # -----------------------------

            clinic_start = datetime.strptime(CLINIC_START_TIME, "%H:%M")
            clinic_end = datetime.strptime(CLINIC_END_TIME, "%H:%M")

            slot_duration = SLOT_DURATION

            max_slots = int((clinic_end - clinic_start).total_seconds() // (slot_duration * 60))

            if token_number > max_slots:
                print("\nNo appointment slots available for this doctor.")
                return

            consultation_start = clinic_start + timedelta(minutes=(token_number - 1) * slot_duration)
            consultation_end = consultation_start + timedelta(minutes=slot_duration)

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
            appointment_id = self.db.last_insert_id()

            print("""
====================================
Appointment Scheduled Successfully
====================================
    """)
            query = """
                UPDATE bills
                SET appointment_id=%s
                WHERE bill_id=%s
            """

            values = (appointment_id,bill_id)

            self.db.execute_query(query, values)
            self.db.commit()

            # print("Appointment Code :", appointment_code)
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
        
    def view_appointments(self):
        query = """
            SELECT
                a.appointment_code,
                p.patient_code,
                p.name AS patient_name,
                u.name AS doctor_name,
                u.department,
                a.appointment_date,
                a.consultation_start_time,
                a.consultation_end_time,
                a.token_number,
                a.status
            FROM appointments a
            JOIN patients p
                ON a.patient_id = p.patient_id
            JOIN users u
                ON a.doctor_id = u.user_id
            WHERE p.is_active = TRUE
            ORDER BY
                a.appointment_date Desc,
                u.name,
                a.token_number
            """
        
        self.db.execute_query(query)
        appointments = self.db.fetch_all()

        if not appointments:
            print("\nNo appointments found.\n")
            return
        
        print("\n" + "=" * 133)

        print(
            f"{'App.Code':<10} | "
            f"{'Patient':<15} | "
            f"{'Doctor':<20} | "
            f"{'Department':<15} | "
            f"{'Date':<12} | "
            f"{'Time':<20} | "
            f"{'Token':<6} | "
            f"{'Status':<10}"
        )

        print("-" * 133)

        for appointment in appointments:
            start = appointment["consultation_start_time"]
            end = appointment["consultation_end_time"]

            start_hours = start.seconds // 3600
            start_minutes = (start.seconds % 3600) // 60

            end_hours = end.seconds // 3600
            end_minutes = (end.seconds % 3600) // 60

            consultation_time = (
                f"{start_hours:02}:{start_minutes:02} - "
                f"{end_hours:02}:{end_minutes:02}"
            )

            print(
                f"{appointment['appointment_code']:<10} | "
                f"{appointment['patient_name']:<15} | "
                f"{appointment['doctor_name']:<20} | "
                f"{appointment['department']:<15} | "
                f"{appointment['appointment_date'].strftime('%d-%m-%Y'):<12} | "
                f"{consultation_time:<20} | "
                f"{appointment['token_number']:<6} | "
                f"{appointment['status']:<10}"
            )

        print("-" * 133)
        print(f"Total Appointments : {len(appointments)}")

    def search_appointment(self):
        while True:
            print("""
====================================
    SEARCH APPOINTMENT
====================================

1. Appointment Code
2. Patient Code
3. Doctor Code
4. Appointment Date
5. Back

====================================
    """)

            Helper.show_back_option()

            try:
                choice = Helper.get_input("Enter your choice : ")
                match choice:
                    case "1":
                        self.search_by_appointment_code()

                    case "2":
                        self.search_by_patient_code()

                    case "3":
                        self.search_by_doctor_code()

                    case "4":
                        self.search_by_date()

                    case "5":
                        return

                    case _:
                        print("Invalid choice.\n")

            except BackRequested:
                return

    #SEARCH BY APPOINTMENT   
    def search_by_appointment_code(self):
        try:
            appointment_code = Helper.get_input(
                "Enter Appointment Code : "
            ).upper()
        except BackRequested:
            print("\nReturning to previous menu.")
            return

        query = """
        SELECT
            a.appointment_code,
            p.patient_code,
            p.name AS patient_name,
            u.user_code,
            u.name AS doctor_name,
            u.department,
            a.appointment_date,
            a.token_number,
            a.status
        FROM appointments a
        JOIN patients p
            ON a.patient_id=p.patient_id
        JOIN users u
            ON a.doctor_id=u.user_id
        WHERE a.appointment_code=%s
        """

        self.db.execute_query(query, (appointment_code,))
        appointment = self.db.fetch_one()

        if not appointment:
            print("\nAppointment not found.\n")
            return

        self.display_appointments([appointment])

    #SEARCH BY PATIENT CODE
    def search_by_patient_code(self):
        try:
            patient_code = Helper.get_input("Enter Patient Code : ").upper()
        except BackRequested:
            print("\nReturning to previous menu.")
            return

        query = """
        SELECT
            a.appointment_code,
            p.patient_code,
            p.name AS patient_name,
            u.user_code,
            u.name AS doctor_name,
            u.department,
            a.appointment_date,
            a.token_number,
            a.status
        FROM appointments a
        JOIN patients p
            ON a.patient_id=p.patient_id
        JOIN users u
            ON a.doctor_id=u.user_id
        WHERE p.patient_code=%s
        ORDER BY a.appointment_date DESC
        """

        self.db.execute_query(query, (patient_code,))
        appointments = self.db.fetch_all()

        if not appointments:
            print("\nNo appointments found.\n")
            return

        self.display_appointments(appointments)

    #SEARCH BY DOCTOR CODE
    def search_by_doctor_code(self):
        try:
            doctor_code = Helper.get_input("Enter Doctor Code : ").upper()
        except BackRequested:
            print("\nReturning to previous menu.")
            return
        query = """
        SELECT
            a.appointment_code,
            p.patient_code,
            p.name AS patient_name,
            u.user_code,
            u.name AS doctor_name,
            u.department,
            a.appointment_date,
            a.token_number,
            a.status
        FROM appointments a
        JOIN patients p
            ON a.patient_id=p.patient_id
        JOIN users u
            ON a.doctor_id=u.user_id
        WHERE u.user_code=%s
        ORDER BY a.appointment_date,a.token_number
        """

        self.db.execute_query(query, (doctor_code,))

        appointments = self.db.fetch_all()

        if not appointments:
            print("\nNo appointments found.\n")
            return

        self.display_appointments(appointments)

    #SEARCH BY APPOINTMENT DATE
    def search_by_date(self):
        try:
            date_input = Helper.get_input("Enter Appointment Date (YYYY-MM-DD): ")
        except BackRequested:
            print("\nReturning to previous menu.")
            return
        try:
            appointment_date = datetime.strptime(date_input,"%Y-%m-%d").date()

        except ValueError:
            print("Invalid date.")
            return

        query = """
        SELECT
            a.appointment_code,
            p.patient_code,
            p.name AS patient_name,
            u.user_code,
            u.name AS doctor_name,
            u.department,
            a.appointment_date,
            a.token_number,
            a.status
        FROM appointments a
        JOIN patients p
            ON a.patient_id=p.patient_id
        JOIN users u
            ON a.doctor_id=u.user_id
        WHERE a.appointment_date=%s
        ORDER BY
            u.name,
            a.token_number
        """

        self.db.execute_query(query, (appointment_date,))
        appointments = self.db.fetch_all()

        if not appointments:
            print("\nNo appointments found.\n")
            return

        self.display_appointments(appointments)

    def display_appointments(self, appointments):

        print("\n" + "=" * 133)
        print(
            f"{'App.Code':<10} | "
            f"{'Patient':<20} | "
            f"{'Doctor':<20} | "
            f"{'Department':<18} | "
            f"{'Date':<12} | "
            f"{'Token':<6} | "
            f"{'Status':<10}"
        )
        print("-" * 133)

        for appointment in appointments:
            print(
                f"{appointment['appointment_code']:<10} | "
                f"{appointment['patient_name']:<20} | "
                f"{appointment['doctor_name']:<20} | "
                f"{appointment['department']:<18} | "
                f"{appointment['appointment_date'].strftime('%d-%m-%Y'):<12} | "
                f"{appointment['token_number']:<6} | "
                f"{appointment['status']:<10}"
            )

        print("-" * 133)
        print(f"Total Appointments : {len(appointments)}")

    def cancel_appointment(self):
        print("""
====================================
    CANCEL APPOINTMENT
====================================
        """)

        Helper.show_back_option()

        try:
            appointment_code = Helper.get_input("Enter Appointment Code : ").upper()

            query = """
                SELECT
                    a.appointment_id,
                    a.appointment_code,
                    p.patient_code,
                    p.name AS patient_name,
                    u.name AS doctor_name,
                    u.department,
                    a.appointment_date,
                    a.consultation_start_time,
                    a.consultation_end_time,
                    a.token_number,
                    a.status
                FROM appointments a
                JOIN patients p
                    ON a.patient_id = p.patient_id
                JOIN users u
                    ON a.doctor_id = u.user_id
                WHERE a.appointment_code = %s
            """

            self.db.execute_query(query, (appointment_code,))
            appointment = self.db.fetch_one()

            if not appointment:
                print("\nAppointment not found.\n")
                return

            if appointment["status"] != AppointmentStatus.SCHEDULED:
                print(
                    f"\nOnly scheduled appointments can be cancelled. "
                    f"Current status: {appointment['status']}.\n"
                )
                return
            
            # Display appointment details
            start = datetime.min + appointment["consultation_start_time"]
            end = datetime.min + appointment["consultation_end_time"]

            print("\n====================================")
            print(f"Appointment Code : {appointment['appointment_code']}")
            print(f"Patient Code     : {appointment['patient_code']}")
            print(f"Patient Name     : {appointment['patient_name']}")
            print(f"Doctor           : {appointment['doctor_name']}")
            print(f"Department       : {appointment['department']}")
            print(f"Date             : {appointment['appointment_date'].strftime('%d-%m-%Y')}")
            print(f"Time             : {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}")
            print(f"Token Number     : {appointment['token_number']}")
            print(f"Status           : {appointment['status']}")
            print("====================================")

            confirm = Helper.get_input("Are you sure you want to cancel this appointment? (Y/N): ").upper()

            if confirm != "Y":
                print("\nCancellation aborted.\n")
                return

            query = """
            UPDATE appointments
            SET status=%s
            WHERE appointment_id=%s
            """

            values = (AppointmentStatus.CANCELLED,appointment["appointment_id"])
            self.db.execute_query(query, values)
            self.db.commit()

            print("\nAppointment cancelled successfully.\n")

        except BackRequested:
            print("Returning to previous menu...")
            return