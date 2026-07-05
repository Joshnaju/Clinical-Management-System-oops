from database import Database
from enums import BillingStatus
from utils.exceptions import BackRequested
from utils.helper import Helper
from utils.constants import REGISTRATION_FEE

class Billing:

    def __init__(self, user):
        self.user = user
        self.db=Database()

    def generate_bill(self,patient,doctor_name,consultation_fee):
        # Check whether registration fee has already been paid
        query = """
        SELECT registration_fee_paid
        FROM patients
        WHERE patient_id=%s
        """

        self.db.execute_query(query, (patient["patient_id"],))
        result = self.db.fetch_one()

        registration_fee = 0

        if not result["registration_fee_paid"]:
            registration_fee = REGISTRATION_FEE

        total_amount = registration_fee + consultation_fee

        # Generate Bill Code
        query = "SELECT COUNT(*) AS total FROM bills"
        self.db.execute_query(query)

        count = self.db.fetch_one()["total"] + 1
        bill_code = f"BILL{count:03d}"

        print("""
====================================
        CONSULTATION BILL
====================================
""")

        print(f"Bill Code         : {bill_code}")
        print(f"Patient           : {patient['name']}")
        print(f"Doctor            : {doctor_name}")

        if registration_fee > 0:
            print(f"Registration Fee  : ₹{registration_fee}")

        print(f"Consultation Fee  : ₹{consultation_fee}")
        print("------------------------------------")
        print(f"Total Amount      : ₹{total_amount}")

        print("""
Payment Mode

1. Cash
2. Card
3. UPI
""")

        payment_modes = {
            "1": "Cash",
            "2": "Card",
            "3": "UPI"
        }

        while True:

            try:
                choice = Helper.get_input("Choose Payment Mode : ")
            except BackRequested:
                print("\nReturning to previous menu.")
                return
            
            if choice in payment_modes:
                payment_mode = payment_modes[choice]
                break

            print("Invalid Payment Mode.")

        try:
            paid = Helper.get_input("Payment Received (Y/N): ").upper()
        except BackRequested:
            print("\nReturning to previous menu.")
            return
        
        payment_status = BillingStatus.PAID if paid == "Y" else BillingStatus.PENDING

        # Save bill
        query = """
        INSERT INTO bills
        (
            bill_code,
            patient_id,
            appointment_id,
            registration_fee,
            consultation_fee,
            total_amount,
            payment_status,
            payment_mode,
            created_by
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            bill_code,
            patient["patient_id"],
            None,                   # appointment not created yet
            registration_fee,
            consultation_fee,
            total_amount,
            payment_status,
            payment_mode,
            self.user["user_id"]
        )

        self.db.execute_query(query, values)
        self.db.commit()

        if payment_status == BillingStatus.PENDING:
            print("\nPayment Pending.")
            return False, None

        print("\nPayment Successful.")

        if registration_fee > 0:
            query = """
            UPDATE patients
            SET registration_fee_paid = TRUE
            WHERE patient_id = %s
            """

            self.db.execute_query(query, (patient["patient_id"],))
            self.db.commit()

        bill_id = self.db.cursor.lastrowid
        return True, bill_id