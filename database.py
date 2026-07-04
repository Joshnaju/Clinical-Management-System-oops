import mysql.connector

class Database:

    def __init__(self):
        self.connect()
        self.cursor = self.dbobj.cursor(dictionary=True)

    def connect(self):
        self.dbobj = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin123",     
            database="cms_oops"       
        )

    def execute_query(self, query, values=None):
        try:
            self.cursor.execute(query, values)

        except Exception as e:
            print("Database Error:", type(e).__name__)
            print(e)
            raise

    def fetch_one(self):
        return self.cursor.fetchone()

    def fetch_all(self):
        return self.cursor.fetchall()

    def commit(self):
        self.dbobj.commit()

    def close(self):
        self.cursor.close()
        self.dbobj.close()

