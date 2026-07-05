from enum import StrEnum
class Role(StrEnum):
    DOCTOR = "Doctor"
    RECEPTIONIST = "Receptionist"
class Gender(StrEnum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
class BloodGroup(StrEnum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"
class AppointmentStatus(StrEnum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
class BillingStatus(StrEnum):
    PAID= "paid",
    PENDING="pending"
class PrescriptionTypes(StrEnum):
    MEDICINE= 'medicine',
    LAB= 'lab',
    BOTH= 'both'