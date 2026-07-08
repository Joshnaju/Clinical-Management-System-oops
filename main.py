from login import Login

obj = Login()
try:
    obj.login()

finally:
    obj.db.close()