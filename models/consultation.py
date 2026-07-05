class Consultation:

    def __init__(self, db):
        self.db = db
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS consultations(
            consultation_id INT AUTO_INCREMENT PRIMARY KEY,
            appointment_id INT NOT NULL,
            doctor_id INT NOT NULL,
            symptoms TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            notes TEXT,
            prescription_type ENUM('Medicine','Lab','Both') NOT NULL,
            medicine TEXT,
            lab_test TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(appointment_id)
            REFERENCES appointments(appointment_id),

            FOREIGN KEY(doctor_id)
            REFERENCES users(user_id)

        )
        """

        self.db.execute_query(query)
        self.db.commit()

    def save_consultation(self,appointment_id,doctor_id,symptoms,diagnosis,notes,prescription_type,medicine,lab_test):
            query="""
            SELECT consultation_id
            FROM consultations
            WHERE appointment_id=%s
            """
            values=(appointment_id,)
            self.db.execute_query(query, values)
            consultation = self.db.fetch_one()

            if consultation:
                return False
    
            query = """
            INSERT INTO consultations
            (
                appointment_id,
                doctor_id,
                symptoms,
                diagnosis,
                notes,
                prescription_type,
                medicine,
                lab_test
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
            """

            values = (
                appointment_id,
                doctor_id,
                symptoms,
                diagnosis,
                notes,
                prescription_type,
                medicine,
                lab_test
            )

            self.db.execute_query(query, values)
            return True