from apps.db.mongo_connection import PyMongo
import pandas as pd


class SingletonDecorator:
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        print("Call once-----------------")
        if self.instance == None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


@SingletonDecorator
class Customer:
    def __init__(self):
        self.customers = []

    def get_customer_data(self):
        if (len(self.customers) > 0):
            print("Returning customers")
            return self.customers
        print("fetching customer data from mongodb")
        pymongoObj = PyMongo()
        db = pymongoObj.get_db_connection()
        customer_list = []
        cursor = db.Customer.find({},
                                  {'name': 1, 'email': 1, 'age': 1, 'gender': 1, 'income': 1, 'address': 1, '_id': 0},
                                  batch_size=500)
        for item in cursor:
            customer = {}
            address = item.pop('address', {})
            coordinates = address.pop('co_ordinate', {})
            customer.update(item)
            customer.update(address)
            customer['long'] = coordinates['coordinates'][0]
            customer['lat'] = coordinates['coordinates'][1]
            customer_list.append(customer)
        pymongoObj.close_db_connection()
        self.customers = customer_list
        return self.customers
