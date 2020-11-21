from apps.db.mongo_connection import PyMongo


class Sales:

    def __init__(self):
        self.db = PyMongo().get_db_connection()

    def fetch_timeline(self):
        cursor = self.db.Orders_v2.aggregate([
            {
                '$project': {
                    'year': {
                        '$year': '$order_date'
                    },
                    'month': {
                        '$month': '$order_date'
                    }
                }
            }, {
                '$group': {
                    '_id': '$year',
                    'months': {
                        '$addToSet': '$month'
                    }
                }
            }
        ])
        data = {}
        for item in cursor:
            data[item['_id']] = item['months']

        return data

    def fetch_geo_info(self):
        cursor = self.db.Orders_v2.aggregate([
            {
                '$group': {
                    '_id': {
                        'Country': '$customer.address.customer_country',
                        'state': '$customer.address.customer_state'
                    },
                    'City': {
                        '$addToSet': {
                            'City': '$customer.address.customer_city'
                        }
                    }
                }
            }, {
                '$group': {
                    '_id': '$_id.Country',
                    'States': {
                        '$addToSet': {
                            'state': '$_id.state',
                            'City': '$City'
                        }
                    }
                }
            }
        ])
        return list(cursor)
