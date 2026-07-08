import mysql.connector
class Database:

    def __init__(self):
        self.__connect()
        self.__cursor = self.__dbobj.cursor(dictionary=True)

    def __connect(self):
        self.__dbobj = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin123",
            database="cms_oops"
        )

    def execute_query(self, query, values=None):
        try:
            if values is None:
                self.__cursor.execute(query)
            else:
                self.__cursor.execute(query, values)

        except Exception as e:
            print("Database Error:", type(e).__name__)
            print(e)
            raise

    def fetch_one(self):
        return self.__cursor.fetchone()

    def fetch_all(self):
        return self.__cursor.fetchall()

    def commit(self):
        self.__dbobj.commit()

    def close(self):
        self.__cursor.close()
        self.__dbobj.close()

    def last_insert_id(self):
        return self.__cursor.lastrowid
    
    def rollback(self):
        self.__dbobj.rollback()