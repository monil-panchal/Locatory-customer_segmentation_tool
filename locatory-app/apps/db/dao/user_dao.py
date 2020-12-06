from apps.db.config.mongo_connection import PyMongo


class AppUser:

    def __init__(self):
        pass

    def get_customer_data(self, username):
        pymongoObj = PyMongo()
        db = pymongoObj.get_db_connection()
        cursor = db.Users.find({"email": username})
        user = {}
        for item in cursor:
            user = item

        pymongoObj.close_db_connection()
        return user
