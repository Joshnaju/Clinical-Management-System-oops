import re
from datetime import datetime
from enums import BloodGroup, Gender


class Validator:

    @staticmethod
    def validate_name(name):
        if not (3 <= len(name) <= 40):
            return False

        return bool(re.fullmatch(r"[A-Za-z ]+", name))


    @staticmethod
    def validate_dob(dob):
        try:
            dob = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD."

        today = datetime.today().date()

        if dob > today:
            return False, "Future date is not allowed."

        try:
            min_date = today.replace(year=today.year - 100)
        except ValueError:
            # Handles Feb 29 in leap years
            min_date = today.replace(month=2, day=28, year=today.year - 100)

        if dob < min_date:
            return False, "Age cannot be more than 100 years."

        return True, ""

    @staticmethod
    def validate_address(address):

        if re.fullmatch(r"[A-Za-z0-9\s,./-]{3,200}", address):
            return True

        return False
     
    @staticmethod
    def validate_phone(phone):
        return bool(re.fullmatch(r"[6-9][0-9]{9}", phone))

    @staticmethod
    def validate_email(email):
        return bool(re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|in)$", email))
    
    #Blood Group
    @staticmethod
    def validate_gender(gender):
        gender = gender.upper()

        if gender in [g.value for g in Gender]:
            return True, gender

        return False, "Gender must be M, F or O."

    @staticmethod
    def validate_blood_group(choice):

        blood_groups = {
            "1": BloodGroup.A_POS,
            "2": BloodGroup.A_NEG,
            "3": BloodGroup.B_POS,
            "4": BloodGroup.B_NEG,
            "5": BloodGroup.AB_POS,
            "6": BloodGroup.AB_NEG,
            "7": BloodGroup.O_POS,
            "8": BloodGroup.O_NEG
        }

        if choice in blood_groups:
            return True, blood_groups[choice]

        return False, "Invalid Blood Group." 
