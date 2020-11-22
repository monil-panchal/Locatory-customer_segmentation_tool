from apps.db.mongo_connection import PyMongo


class Sales:

    def __init__(self):
        self.db = PyMongo().get_db_connection()

    def fetch_timeline(self):
        cursor = self.db.Orders.aggregate([
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
        cursor = self.db.Orders.aggregate([
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

    def get_orders_for_dashboard(self, data: dict):

        print(f'data received in db call: {data}')

        if data:
            year = data['year']
            month = data['month']
            country = data['country']
            state = data['state']
            city = data['city']

            queries = []
            year_query = { '$expr': {'$eq': [{'$year': '$order_date'}, year]} }
            queries.append(year_query)

            if month:
                month_query = { '$expr': {'$eq': [{'$month': '$order_date'}, month]} }
                queries.append(month_query)

            country_query= {'customer.address.customer_country': country}
            queries.append(country_query)

            if state:
                state_query= {'customer.address.customer_state': state}
                queries.append(state_query)

            if city:
                city_query= {'customer.address.customer_city': city}
                queries.append(city_query)

            dashboard_data_query = {
                '$and': queries
            }
            print(f'dashboard_data_query: {dashboard_data_query}')


            orders = []
            cursor = self.db.Orders.find(dashboard_data_query)
            for order in cursor:
                orders.append(order)

            print(f'number of orders retrieved are: {len(orders)}')
            return orders

        return []
