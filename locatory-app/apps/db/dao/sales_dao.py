from apps.db.config.mongo_connection import PyMongo
from datetime import datetime
import calendar


class Sales:

    def __init__(self):
        pass

    def fetch_timeline(self):
        pymongoObj = PyMongo()
        db = pymongoObj.get_db_connection()
        cursor = db.Orders.aggregate([
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

        pymongoObj.close_db_connection()
        return data

    def fetch_geo_info(self):
        pymongoObj = PyMongo()
        db = pymongoObj.get_db_connection()
        cursor = db.Orders.aggregate([
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
        pymongoObj.close_db_connection()
        return list(cursor)

    def get_orders_for_dashboard(self, data: dict):

        print(f'data received in db call: {data}')

        if data:

            pymongoObj = PyMongo()
            db = pymongoObj.get_db_connection()

            year = data.get('year', None)
            prev_year = data.get('prev_year', None)
            month = data.get('month', None)
            prev_month = data.get('prev_month', None)
            country = data.get('country', None)
            state = data.get('state', None)
            city = data.get('city', None)

            queries = []

            if prev_year is not None:
                if prev_month is not None and month is not None:
                    start = datetime(prev_year, prev_month, 1)
                    end = datetime(year, month, calendar.monthrange(year, month)[1])
                    year_month_range_query = {'order_date': {'$gte': start, '$lte': end}}
                else:
                    start = datetime(prev_year, 1, 1)
                    end = datetime(year, 12, calendar.monthrange(year, 12)[1])
                    year_month_range_query = {'order_date': {'$gte': start, '$lte': end}}
                queries.append(year_month_range_query)

            elif year is not None:
                if prev_month is not None and month is not None:
                    start = datetime(year, prev_month, 1)
                    end = datetime(year, month, calendar.monthrange(year, month)[1])
                    year_month_range_query = {'order_date': {'$gte': start, '$lte': end}}
                    queries.append(year_month_range_query)
                elif month is not None:
                    year_query = {'$expr': {'$eq': [{'$year': '$order_date'}, year]}}
                    queries.append(year_query)

                    month_query = {'$expr': {'$eq': [{'$month': '$order_date'}, month]}}
                    queries.append(month_query)
                else:
                    year_query = {'$expr': {'$eq': [{'$year': '$order_date'}, year]}}
                    queries.append(year_query)

            country_query = {'customer.address.customer_country': country}
            queries.append(country_query)

            if state:
                state_query = {'customer.address.customer_state': state}
                queries.append(state_query)

            if city:
                city_query = {'customer.address.customer_city': city}
                queries.append(city_query)

            dashboard_data_query = {
                '$and': queries
            }
            print(f'dashboard_data_query: {dashboard_data_query}')

            orders = []
            cursor = db.Orders.find(dashboard_data_query)
            for order in cursor:
                orders.append(order)

            print(f'number of orders retrieved are: {len(orders)}')
            pymongoObj.close_db_connection()
            return orders

        return []
