Clinical management System
Admin will insert doctor and receptionist in mysql

login ->username,password
login as receptionist or doctor

if login as receptionist go to receptionist dashboard

1.patient management
2.scheduling

patient management:
1.register
2.view
3.search
4.update
5.disable
6.back

registeration
Receptionist: collects patients details
1.name - duplicates name allowed
2.dob - format,no future dates,dates above before 100yrs of now, 1909 not allowed - when view show age
3.address
4.phone_number - duplicate phone number is allowed
5.email
6.blood_group (choose from dropdown list)
7.gender (M/F/O)
8.patientid (auto generated)

save ->goes to scheduling

Scheduling:

department - choose from drop down
doctor - show doctors from a particular department
save->generate a bill(consultation fee get from the doctors user table) for first time user have consultation fees + registeration fees-->paid--->send bill to patient-->generate token
status - pending(becoz doctor is not consulted yet)

Receptionist->can book appointment
prior to 2 days ahead(patient must be registered)
same time token not allowed
15 mints between each token gap is needed

exit

when doctor login:
After token generation goes to ->doctors dashboard
Dont delete patient->just disable them
======================================================
Doctor ->login->can see his appointments
-->list patient for today (can give previous histroy too if u can)
-->view todays appointment
-->consult

name,age,gender - cannot delete by doctor

sl.no patientid patientname tokenno consult(button)
1 Neema

click --> consult(button)
take to neemas file

patient details
name age gender symptoms diagonsis notes,prescription

doctor can edit only symptoms,diagonsis,notes,prescription
status - completed

prescription-->1.Medicines - dropdown - also text if the medicine is not present in dropdown
2.lab - dropdown

save and print prescription

save--->After save cannot edit the consultation

======================================================================

Clinical Management System
│
├── main.py
├── database.py
├── login.py
├──enums.py
│
├── models
│ patient.py
│ doctor.py
│ receptionist.py
│ appointment.py
│ consultation.py
│ bill.py
│
└── utils
validator.py
token_generator.py

implement encapsulation

created_by = Rec01 (unchanged)
created_at = 2026-07-01 (unchanged)

updated_by = Rec02 (changes)
updated_at = 2026-07-04 (changes)

show patient,age,gender in doctor view appointments
