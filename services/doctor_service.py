from datetime import date

from models.consultation import Consultation
from utils.constants import LAB_TESTS, MEDICINES
from enums import AppointmentStatus, PrescriptionTypes
from utils.exceptions import BackRequested
from utils.helper import Helper

class DoctorService:
    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.consultation = Consultation(db)

    #LIST TODAY APPOINTMENTS 
    def today_appointments(self):
        print("""
=====================================
    TODAY'S APPOINTMENTS
=====================================
    """)

        query = """
        SELECT
            a.appointment_code,
            p.patient_code,
            p.name,
            a.token_number,
            a.consultation_start_time,
            a.consultation_end_time,
            a.status
        FROM appointments a
        INNER JOIN patients p
            ON a.patient_id = p.patient_id
        WHERE a.doctor_id = %s
        AND a.appointment_date = %s
        AND a.status IN (%s, %s)
        ORDER BY a.token_number
        """

        values = (self.user["user_id"],date.today(),AppointmentStatus.SCHEDULED,AppointmentStatus.COMPLETED)

        self.db.execute_query(query, values)
        appointments = self.db.fetch_all()

        if not appointments:
            print("\nNo appointments for today.\n")
            return

        print("-" * 133)
        print(
            f"{'Token':<6}"
            f"{'Appt Code':<12}"
            f"{'Patient':<12}"
            f"{'Name':<20}"
            f"{'Time':<22}"
            f"{'Status':<12}"
        )
        print("-" * 133)

        for appointment in appointments:

            # time_slot = (
            #     f"{appointment['consultation_start_time'].strftime('%I:%M %p')} - "
            #     f"{appointment['consultation_end_time'].strftime('%I:%M %p')}"
            # )
            time_slot = (
                f"{Helper.format_mysql_time(appointment['consultation_start_time'])} - "
                f"{Helper.format_mysql_time(appointment['consultation_end_time'])}"
            )
            print(
                f"{appointment['token_number']:<6}"
                f"{appointment['appointment_code']:<12}"
                f"{appointment['patient_code']:<12}"
                f"{appointment['name']:<20}"
                f"{time_slot:<22}"
                f"{appointment['status']:<12}"
            )

        print("-" * 133)
        print(f"Total Appointments : {len(appointments)}")

    #SEARCH APPOINTMENTS
    def search_appointment(self):
        while True:

            print("""
=====================================
        SEARCH APPOINTMENT
=====================================

1. Appointment Code
2. Patient Code
3. Patient Name
4. Back
    """)

            Helper.show_back_option()

            try:
                choice = Helper.get_input("Enter your choice : ")

                match choice:
                    case "1":

                        value = Helper.get_input("Enter Appointment Code : ").upper()

                        query = """
                        SELECT
                            a.appointment_code,
                            p.patient_code,
                            p.name,
                            a.appointment_date,
                            a.consultation_start_time,
                            a.consultation_end_time,
                            a.token_number,
                            a.status
                        FROM appointments a
                        INNER JOIN patients p
                            ON a.patient_id = p.patient_id
                        WHERE a.appointment_code=%s
                        AND a.doctor_id=%s
                        """

                        values = (value,self.user["user_id"])

                    case "2":

                        value = Helper.get_input("Enter Patient Code : ").upper()

                        query = """
                        SELECT
                            a.appointment_code,
                            p.patient_code,
                            p.name,
                            a.appointment_date,
                            a.consultation_start_time,
                            a.consultation_end_time,
                            a.token_number,
                            a.status
                        FROM appointments a
                        INNER JOIN patients p
                            ON a.patient_id = p.patient_id
                        WHERE p.patient_code=%s
                        AND a.doctor_id=%s
                        ORDER BY a.appointment_date DESC
                        """

                        values = (value,self.user["user_id"])

                    case "3":

                        value = Helper.get_input("Enter Patient Name : ")

                        query = """
                        SELECT
                            a.appointment_code,
                            p.patient_code,
                            p.name,
                            a.appointment_date,
                            a.consultation_start_time,
                            a.consultation_end_time,
                            a.token_number,
                            a.status
                        FROM appointments a
                        INNER JOIN patients p
                            ON a.patient_id = p.patient_id
                        WHERE p.name LIKE %s
                        AND a.doctor_id=%s
                        ORDER BY a.appointment_date DESC
                        """

                        values = (f"%{value}%",self.user["user_id"])

                    case "4":
                        return

                    case _:
                        print("Invalid Choice.")
                        continue

            except BackRequested:
                print("\nReturning to previous menu.")
                return

            self.db.execute_query(query, values)

            appointments = self.db.fetch_all()

            if not appointments:
                print("\nNo appointments found.\n")
                continue

            print("-" * 133)

            print(
                f"{'Appt Code':<12}"
                f"{'Patient':<12}"
                f"{'Name':<20}"
                f"{'Date':<12}"
                f"{'Time':<22}"
                f"{'Token':<8}"
                f"{'Status':<12}")

            print("-" * 133)

            for appointment in appointments:
                time_slot = (
                f"{Helper.format_mysql_time(appointment['consultation_start_time'])} - "
                f"{Helper.format_mysql_time(appointment['consultation_end_time'])}")

                print(
                f"{appointment['appointment_code']:<12}"
                f"{appointment['patient_code']:<12}"
                f"{appointment['name']:<20}"
                f"{str(appointment['appointment_date']):<12}"
                f"{time_slot:<22}"
                f"{appointment['token_number']:<8}"
                f"{appointment['status']:<12}")

            print("-" * 133)
            print(f"Total Appointments : {len(appointments)}")

    #CONSULT PATIENT
    def consult_patient(self):
        query = """
        SELECT

        a.appointment_id,
        a.appointment_code,
        a.patient_id,
        a.appointment_date,

        p.patient_code,
        p.name,
        p.dob,
        p.gender,

        a.token_number,
        a.consultation_start_time,
        a.consultation_end_time

        FROM appointments a

        INNER JOIN patients p
        ON a.patient_id=p.patient_id

        WHERE
        a.doctor_id=%s
        AND a.appointment_date=CURDATE()
        AND a.status=%s

        ORDER BY a.token_number
        """

        values = (self.user["user_id"],AppointmentStatus.SCHEDULED)
        self.db.execute_query(query, values)
        appointments = self.db.fetch_all()

        if not appointments:
            print("\nNo scheduled appointments for today.\n")
            return
    
        print("""
=====================================
    TODAY'S PATIENT CONSULTATION
=====================================
""")
        Helper.show_back_option()

        print("-"*95)

        print(
            f"{'Token':<8}"
            f"{'Appt Code':<12}"
            f"{'Patient':<12}"
            f"{'Name':<25}"
            f"{'Time':<20}"
        )

        print("-"*95)

        for appointment in appointments:
            start = Helper.format_mysql_time(appointment["consultation_start_time"])
            end = Helper.format_mysql_time(appointment["consultation_end_time"])

            print(

                f"{appointment['token_number']:<8}"
                f"{appointment['appointment_code']:<12}"
                f"{appointment['patient_code']:<12}"
                f"{appointment['name']:<25}"
                f"{start} - {end}"

            )

        print()

        try:
            while True:
                appointment_code = Helper.get_input("Enter Appointment Code : ").upper()

                selected = None

                for appointment in appointments:
                    if appointment["appointment_code"] == appointment_code:
                        selected = appointment
                        break

                if selected:
                    break

                print("Invalid Appointment Code.")
            
            age = Helper.calculate_age(selected["dob"])

            print(f"""
=====================================
    CONSULTATION DETAILS
=====================================

Appointment Code : {selected['appointment_code']}
Patient Code     : {selected['patient_code']}
Patient Name     : {selected['name']}
Age              : {age}
Gender           : {selected['gender']}
Token Number     : {selected['token_number']}
Consultation Date: {selected['appointment_date'].strftime("%d-%m-%Y")}

=====================================
            """)

            while True:
                symptoms = Helper.get_input("Symptoms : ")
                if symptoms:
                    break

                print("Symptoms are required.")

            while True:
                diagnosis = Helper.get_input("Diagnosis : ")
                if diagnosis:
                    break

                print("Diagnosis is required.")


            notes = Helper.get_input("Clinical Notes (Optional) : ")

            print("""
Prescription

1. Medicine
2. Lab Test
3. Medicine + Lab Test
            """)

            while True:
                choice = Helper.get_input("Choose Prescription Type : ")

                match choice:
                    case "1":
                        prescription_type = PrescriptionTypes.MEDICINE
                        break

                    case "2":
                        prescription_type = PrescriptionTypes.LAB
                        break

                    case "3":
                        prescription_type = PrescriptionTypes.BOTH
                        break

                    case _:
                        print("Invalid Choice.")

#MEDICINE
            medicines_selected = []

            if prescription_type in (PrescriptionTypes.MEDICINE, PrescriptionTypes.BOTH):

                print("\nMedicines\n")

                for i, medicine in enumerate(MEDICINES, start=1):
                    print(f"{i}. {medicine}")

                while True:

                    choice = Helper.get_input(
                        "\nChoose Medicines (Ex: 1,3,5): "
                    )

                    try:
                        indexes = [int(x.strip()) for x in choice.split(",")]

                        if any(index < 1 or index > len(MEDICINES) for index in indexes):
                            print("Invalid Choice.")
                            continue

                        medicines_selected = []

                        for index in indexes:

                            medicine = MEDICINES[index - 1]

                            if medicine == "Other":

                                while True:
                                    medicine = Helper.get_input(
                                        "Enter Medicine Name : "
                                    )

                                    if medicine:
                                        break

                                    print("Medicine name is required.")

                            medicines_selected.append(medicine)

                        break

                    except ValueError:
                        print("Invalid Choice.")

#LAB
            lab_tests_selected = []

            if prescription_type in (PrescriptionTypes.LAB, PrescriptionTypes.BOTH):

                print("\nLab Tests\n")

                for i, test in enumerate(LAB_TESTS, start=1):
                    print(f"{i}. {test}")

                while True:

                    choice = Helper.get_input(
                        "\nChoose Lab Tests (Ex: 1,2,5): "
                    )

                    try:
                        indexes = [int(x.strip()) for x in choice.split(",")

                        ]

                        if any(index < 1 or index > len(LAB_TESTS) for index in indexes):
                            print("Invalid Choice.")
                            continue

                        lab_tests_selected = []

                        for index in indexes:

                            test = LAB_TESTS[index - 1]

                            if test == "Other":

                                while True:
                                    test = Helper.get_input(
                                        "Enter Lab Test : "
                                    )

                                    if test:
                                        break

                                    print("Lab Test name is required.")

                            lab_tests_selected.append(test)

                        break

                    except ValueError:
                        print("Invalid Choice.")

            medicine = ", ".join(medicines_selected) if medicines_selected else None
            lab_test = ", ".join(lab_tests_selected) if lab_tests_selected else None

#SAVE CONSULTATION
            saved=self.consultation.save_consultation(
            selected["appointment_id"],
            self.user["user_id"],
            symptoms,
            diagnosis,
            notes,
            prescription_type,
            medicine,
            lab_test)

            if not saved:
                print("Consultation already completed.")
                return

            query = """
            UPDATE appointments
            SET status=%s
            WHERE appointment_id=%s
            """

            values = (AppointmentStatus.COMPLETED,selected["appointment_id"])

            self.db.execute_query(query, values)
            self.db.commit()

            print("""
=====================================
Consultation Completed Successfully
=====================================
            """)

            print(f"Patient      : {selected['name']}")
            print(f"Doctor       : {self.user['name']}")
            print(f"Diagnosis    : {diagnosis}")

            if medicine:
                print(f"Medicine     : {medicine}")

            if lab_test:
                print(f"Lab Test     : {lab_test}")

            print("\nConsultation is completed.")
        except BackRequested:
            print("\nReturning to previous menu.")
            return
        
        except Exception as e:
            self.db.rollback()
            print("Database Error:", e)

    def consultation_history(self):
        query = """
        SELECT
            c.consultation_id,
            a.appointment_code,
            p.patient_code,
            p.name,
            a.appointment_date,
            c.diagnosis,
            c.prescription_type,
            c.medicine,
            c.lab_test
        FROM consultations c

        INNER JOIN appointments a
            ON c.appointment_id = a.appointment_id

        INNER JOIN patients p
            ON a.patient_id = p.patient_id

        WHERE c.doctor_id=%s

        ORDER BY a.appointment_date DESC,
                a.token_number DESC
        """

        values = (self.user["user_id"],)

        self.db.execute_query(query, values)

        consultations = self.db.fetch_all()

        if not consultations:
            print("\nNo consultation history found.\n")
            return

        print("""
=====================================
      CONSULTATION HISTORY
=====================================
    """)

        print("-" * 133)

        print(
            f"{'Appt Code':<12}"
            f"{'Patient':<12}"
            f"{'Name':<20}"
            f"{'Date':<12}"
            f"{'Diagnosis':<25}"
            f"{'Prescription':<15}"
            f"{'Medicine':<35}"
            f"{'Lab Test':<35}"
        )

        print("-" * 133)

        for consultation in consultations:

            print(
                f"{consultation['appointment_code']:<12}"
                f"{consultation['patient_code']:<12}"
                f"{consultation['name']:<20}"
                f"{consultation['appointment_date'].strftime('%d-%m-%Y'):<12}"
                f"{consultation['diagnosis'][:24]:<25}"
                f"{consultation['prescription_type']:<15}"
                f"{(consultation['medicine'] or '-')[:34]:<35}"
                f"{(consultation['lab_test'] or '-')[:34]:<35}"
            )

        print("-" * 133)
        print(f"Total Consultations : {len(consultations)}")