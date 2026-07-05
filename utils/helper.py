from datetime import date, datetime
from utils.exceptions import BackRequested

class Helper:
    
    @staticmethod
    def calculate_age(dob):

        today = date.today()
        age = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            age -= 1

        if age >= 1:
            return f"{age} year(s)"

        months = (today.year - dob.year) * 12 + (today.month - dob.month)
        if today.day < dob.day:
            months -= 1

        if months >= 1:
            return f"{months} month(s)"

        days = (today - dob).days

        return f"{days} day(s)"

    @staticmethod
    def show_back_option():
        print('\nType "back" to return to the previous menu.\n')

    @staticmethod
    def get_input(prompt):
        value = input(prompt).strip()

        if value.lower() == "back":
            raise BackRequested()

        return value
    
    @staticmethod
    def is_walkin_available():
        current_time = datetime.now().time()
        clinic_end = datetime.strptime("13:00", "%H:%M").time()

        return current_time < clinic_end