from database import Database
from enums import Role
from models.doctor import Doctor
from models.patient import Patient
from models.receptionist import Receptionist

class Login:

    def __init__(self):
        self.db = Database()

    def login(self):
        while True:
            print("""
+--------------------------------+
|  Clinical Management System    |
+--------------------------------+
              Login
""")

            username = input("Enter Username : ").strip()
            password = input("Enter Password : ").strip()
            query = """
            SELECT *
            FROM users
            WHERE user_code=%s
            AND BINARY password=%s
            AND is_active=True
            """
            values = (username, password)
            self.db.execute_query(query, values)
            user = self.db.fetch_one()
            if user:

                print("\nLogin Successfully")

                role = user["role"]

                if role == Role.DOCTOR:
                    print(f"Welcome Doctor, {user['name']}")
                    doctor = Doctor(self.db,user)
                    doctor.dashboard()

                elif role == Role.RECEPTIONIST:
                    print(f"Welcome Receptionist, {user['name']}")
                    receptionist = Receptionist(self.db,user)
                    receptionist.dashboard()
            else:
                print("\nInvalid Username or Password. Please try again.\n")

       