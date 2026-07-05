from utils.helper import Helper
from utils.exceptions import BackRequested
from utils.validator import Validator
from datetime import date

class Patient:
    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS patients(
            patient_id INT AUTO_INCREMENT PRIMARY KEY,
            patient_code VARCHAR(10) UNIQUE NOT NULL,
            name VARCHAR(40) NOT NULL,
            dob DATE NOT NULL,
            address VARCHAR(200) NOT NULL,
            phone VARCHAR(10) NOT NULL,
            email VARCHAR(100) NOT NULL,
            blood_group ENUM('A+','A-','B+','B-','AB+','AB-','O+','O-') NOT NULL,
            gender ENUM('M','F','O') NOT NULL,
            created_by INT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            registration_fee_paid BOOLEAN DEFAULT FALSE,

            FOREIGN KEY (created_by) REFERENCES users(user_id)
        )"""

        self.db.execute_query(query)
        self.db.commit()

    def register_patient(self):
        print("""
=====================================
        PATIENT REGISTRATION
=====================================
""")
        
        Helper.show_back_option()
        try:
            # Name
            while True:
                name = Helper.get_input("Enter Name : ")

                if not name:
                    print("Name is required.")
                elif not Validator.validate_name(name):
                    print("Name should contain only letters and be 3-40 characters.")
                else:
                    break


            # DOB
            while True:
                dob = Helper.get_input("Enter DOB (YYYY-MM-DD) : ")

                if not dob:
                    print("DOB is required.")
                    continue

                valid, message = Validator.validate_dob(dob)

                if valid:
                    break

                print(message)

            # Address
            while True:
                address = Helper.get_input("Enter Address : ")

                if not address:
                    print("Address is required.")
                elif not Validator.validate_address(address):
                    print("Enter a valid address.")
                else:
                    break


            # Phone
            while True:
                phone = Helper.get_input("Enter Phone Number : ")

                if not phone:
                    print("Phone number is required.")
                elif not Validator.validate_phone(phone):
                    print("Phone must contain 10 digits and start with 6,7,8 or 9.")
                else:
                    break


            # Email
            while True:
                email = Helper.get_input("Enter Email : ")

                if not email:
                    print("Email is required.")
                elif not Validator.validate_email(email):
                    print("Enter a valid email.")
                else:
                    break
            
            print("""
    Blood Group

    1. A+
    2. A-
    3. B+
    4. B-
    5. AB+
    6. AB-
    7. O+
    8. O-
    """)
            #Blood Group
            while True:
                choice = Helper.get_input("Choose Blood Group : ")

                if not choice:
                    print("Blood Group is required.")
                    continue

                valid, blood_group = Validator.validate_blood_group(choice)

                if valid:
                    break

                print(blood_group)
            
            #Gender
            while True:
                gender = Helper.get_input("Enter Gender (M/F/O): ")

                if not gender:
                    print("Gender is required.")
                    continue

                valid, result = Validator.validate_gender(gender)

                if valid:
                    gender = result      
                    break

                print(result)
        except BackRequested:
            print("\nReturning to previous menu.")
            return

        query = """
            SELECT patient_code
            FROM patients
            WHERE name=%s
            AND dob=%s
            AND phone=%s
            AND is_active=TRUE
        """

        values = (name, dob, phone)
        self.db.execute_query(query, values)
        patient = self.db.fetch_one()
        if patient:
            print(f"Patient already exists. Patient ID: {patient['patient_code']}")
            return
        
        patient_code = self.generate_patient_code()

        query = """
        INSERT INTO patients
        (patient_code,name,dob,address,phone,email,blood_group,gender,created_by)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            patient_code,
            name,
            dob,
            address,
            phone,
            email,
            blood_group,
            gender,
            self.user["user_id"]
        )

        self.db.execute_query(query, values)
        self.db.commit()

        print("\nPatient Registered Successfully.")
        print("Patient Code :", patient_code)
        patient_id = self.db.last_insert_id()

        return patient_code,patient_id,name

    def generate_patient_code(self):
        query = "SELECT COUNT(*) FROM patients"
        self.db.execute_query(query)
        count = self.db.fetch_one()["COUNT(*)"]
        return f"PAT{count+1:03d}" #integer min 3,pad with 0

    def view_patients(self):

            query = """
            SELECT
                p.patient_code,
                p.name,
                p.dob,
                p.address,
                p.phone,
                p.email,
                p.blood_group,
                p.gender,
                u.name AS registered_by,
                p.created_at
            FROM patients p
            INNER JOIN users u
                ON p.created_by = u.user_id
            WHERE p.is_active = TRUE
            ORDER BY p.patient_code;
            """

            self.db.execute_query(query)
            patients = self.db.fetch_all()

            if not patients:
                print("\nNo patients found.")
                return

            print("\n" + "=" * 133)

            print(
                f"{'Patient Code':^6} | "
                f"{'Name':^12} | "
                f"{'Age':^6} | "
                f"{'Gender':^3} | "
                f"{'Blood':^5} | "
                f"{'Phone':^10} | "
                f"{'Email':^10} | "
                f"{'Registered By':^15} | "
                f"{'Registered On':^15} | "
                f"{'Address':^20}"
            )

            print("-" * 133)

            today = date.today()

            for patient in patients:

                age_display = Helper.calculate_age(patient["dob"])
                print(
                f"{patient['patient_code']:^6} | "
                f"{patient['name']:^12} | "
                f"{age_display:^6} | "
                f"{patient['gender']:^3} | "
                f"{patient['blood_group']:^5} | "
                f"{patient['phone']:^10} | "
                f"{patient['email']:^10} | "
                f"{patient['registered_by']:^15} | "
                f"{patient['created_at'].strftime('%d-%m-%Y %H:%M'):^15} | "
                f"{patient['address']:^20}"
                )
                
            print("-" * 133)
            print(f"Total Patients : {len(patients)}")

    def search_patient(self):
        while True:
            print("""
=====================================
        SEARCH PATIENT
=====================================
1. Patient ID
2. Name
3. Phone Number
4. Email
5. Back
    """)
            Helper.show_back_option()
            try:
                choice = Helper.get_input("Enter your choice : ")

                match choice:
                    case "1":
                        value = Helper.get_input("Enter Patient ID : ").strip().upper()

                        query = """
                        SELECT patient_code,name,dob,address,phone,email,blood_group,gender
                        FROM patients
                        WHERE patient_code=%s AND is_active=TRUE
                        """

                        values = (value,)

                    case "2":
                        value = Helper.get_input("Enter Name : ")

                        query = """
                        SELECT patient_code,name,dob,address,phone,email,blood_group,gender
                        FROM patients
                        WHERE name LIKE %s AND is_active=TRUE
                        """

                        values = (f"%{value}%",)

                    case "3":

                        while True:
                            value = Helper.get_input("Enter Phone Number : ")

                            if not value:
                                print("Phone number is required.")
                                continue

                            if not Validator.validate_phone(value):
                                print("Phone number must contain 10 digits and start with 6, 7, 8, or 9.")
                                continue

                            query = """
                            SELECT patient_code,name,dob,address,phone,email,blood_group,gender
                            FROM patients
                            WHERE phone=%s AND is_active=TRUE
                            """

                            values = (value,)
                            break

                    case "4":
                        value = Helper.get_input("Enter Email : ")

                        query = """
                        SELECT patient_code,name,dob,address,phone,email,blood_group,gender
                        FROM patients
                        WHERE email=%s AND is_active=TRUE
                        """

                        values = (value,)

                    case "5":
                        return

                    case _:
                        print("Invalid Choice")
                        continue

            except BackRequested:
                print("\nReturning to previous menu.")
                return
                
            self.db.execute_query(query, values)
            patients = self.db.fetch_all()

            if not patients:
                print("\nPatient not found.")
                continue
            
            print("\n" + "=" * 133)

            print(
                f"{'Patient Code':<12} | "
                f"{'Name':<20} | "
                f"{'Age':<12} | "
                f"{'Gender':<6} | "
                f"{'Blood':<5} | "
                f"{'Phone':<10} | "
                f"{'Email':<30} | "
                f"{'Address':<25}"
            )

            print("-" * 133)

            for patient in patients:
                age_display = Helper.calculate_age(patient["dob"])

                print(
                    f"{patient['patient_code']:<12} | "
                    f"{patient['name']:<20} | "
                    f"{age_display:<12} | "
                    f"{patient['gender']:<6} | "
                    f"{patient['blood_group']:<5} | "
                    f"{patient['phone']:<10} | "
                    f"{patient['email']:<30} | "
                    f"{patient['address']:<25}"
                )

            print("=" * 133)
            print(f"Total Patients Found : {len(patients)}")

    def update_patient(self):
        while True:
            print("""
=====================================
        UPDATE PATIENT
=====================================
        """)
            Helper.show_back_option()
            try:

                patient_code = Helper.get_input("Enter Patient Code : ").upper()

                query = """
                SELECT *
                FROM patients
                WHERE patient_code=%s
                AND is_active=TRUE
                """

                self.db.execute_query(query, (patient_code,))
                patient = self.db.fetch_one()

                if not patient:
                    print("\nPatient not found.")
                    continue

                print("\nLeave blank to keep existing value.\n")

                #NAME
                while True:
                    name = Helper.get_input(f"Name [{patient['name']}] : ").strip()

                    if name == "":
                        name = patient["name"]
                        break

                    if Validator.validate_name(name):
                        break

                    print("Name should contain only letters and be 3-40 characters.")

                #DOB
                while True:
                    dob = Helper.get_input(f"DOB [{patient['dob']}] : ").strip()

                    if dob == "":
                        dob = patient["dob"]
                        break

                    valid, message = Validator.validate_dob(dob)

                    if valid:
                        break

                    print(message)

                #ADDRESS
                while True:
                    address = Helper.get_input(f"Address [{patient['address']}] : ").strip()

                    if address == "":
                        address = patient["address"]
                        break

                    if Validator.validate_address(address):
                        break

                    print("Invalid address.")

                #PHONE
                while True:
                    phone = Helper.get_input(f"Phone [{patient['phone']}] : ").strip()

                    if phone == "":
                        phone = patient["phone"]
                        break

                    if Validator.validate_phone(phone):
                        break

                    print("Invalid phone number.")

                #EMAIL
                while True:
                    email = Helper.get_input(f"Email [{patient['email']}] : ").strip()

                    if email == "":
                        email = patient["email"]
                        break

                    if Validator.validate_email(email):
                        break

                    print("Invalid email.")

                #Blood Group
                print("""
        Blood Group

        1. A+
        2. A-
        3. B+
        4. B-
        5. AB+
        6. AB-
        7. O+
        8. O-
        """)

                while True:

                    choice = Helper.get_input(f"Blood Group [{patient['blood_group']}] : ").strip()

                    if choice == "":
                        blood_group = patient["blood_group"]
                        break

                    valid, result = Validator.validate_blood_group(choice)

                    if valid:
                        blood_group = result
                        break

                    print(result)

                #Gender
                while True:
                    gender = Helper.get_input(f"Gender [{patient['gender']}] (M/F/O): ").strip()

                    if gender == "":
                        gender = patient["gender"]
                        break

                    valid, result = Validator.validate_gender(gender)

                    if valid:
                        gender = result
                        break

                    print(result)
            except BackRequested:
                print("\nReturning to previous menu.")
                return

            #update query
            query = """
            UPDATE patients
            SET
                name=%s,
                dob=%s,
                address=%s,
                phone=%s,
                email=%s,
                blood_group=%s,
                gender=%s
            WHERE patient_code=%s
            """

            values = (
                name,
                dob,
                address,
                phone,
                email,
                blood_group,
                gender,
                patient_code
            )

            self.db.execute_query(query, values)
            self.db.commit()

            print("\nPatient updated successfully.")
            return

    def disable_patient(self):
        print("""
=====================================
        DISABLE PATIENT
=====================================
    """)

        while True:
            Helper.show_back_option()
            try:
                patient_code = Helper.get_input("Enter Patient Code : ").strip().upper()

                if not patient_code:
                    print("Patient Code is required.")
                    continue

                break
            except BackRequested:
                print("\nReturning to previous menu.")
                return

        query = """
        SELECT patient_code, name, phone, email
        FROM patients
        WHERE patient_code = %s
        AND is_active = TRUE
        """

        self.db.execute_query(query, (patient_code,))
        patient = self.db.fetch_one()

        if not patient:
            print("\nActive patient not found.")
            return

        print("\nPatient Details")
        print("-" * 35)
        print(f"Patient Code : {patient['patient_code']}")
        print(f"Name         : {patient['name']}")
        print(f"Phone        : {patient['phone']}")
        print(f"Email        : {patient['email']}")

        while True:
            try:
                confirm = Helper.get_input("\nDisable this patient? (Y/N): ").strip().upper()

            except BackRequested:
                print("\nReturning to previous menu.")
                return

            if confirm == "Y":
                query = """
                UPDATE patients
                SET is_active = FALSE
                WHERE patient_code = %s
                """

                self.db.execute_query(query, (patient_code,))
                self.db.commit()

                print("\nPatient disabled successfully.")
                break

            elif confirm == "N":
                print("\nOperation cancelled.")
                break

            else:
                print("Please enter Y or N.")