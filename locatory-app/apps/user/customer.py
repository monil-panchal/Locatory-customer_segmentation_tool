from apps.db.config.mongo_connection import PyMongo
import pandas as pd

class Customer:
    def __init__(self):
        self.db = PyMongo().get_db_connection()
        self.customers = []

    def get_customer_data(self):
        if(len(self.customers)>0):
            return self.customers
        cursor = self.db.Customer.find({}, {'name': 1, 'email': 1, 'age': 1, 'gender': 1, 'income': 1, 'address': 1, '_id':0})
        for item in cursor:
            customer = {}
            address = item.pop('address', {})
            coordinates = address.pop('co_ordinate', {})
            customer.update(item)
            customer.update(address)
            customer['long'] = coordinates['coordinates'][0]
            customer['lat'] = coordinates['coordinates'][1]
            self.customers.append(customer)
        return self.customers

