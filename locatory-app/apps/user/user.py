from apps.db.mongo_connection import PyMongo


class AppUser:

    def __init__(self):
        self.db = PyMongo().get_db_connection()

    def get_customer_data(self, username):
        cursor = self.db.Users.find({"email": username})
        user = {}
        for item in cursor:
            user = item

        return user
