from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo import IndexModel, ASCENDING, DESCENDING

def get_connection(db_conn, client_name):
    client_cur = db_conn[client_name]
    return client_cur

def insert_one_document(doc_data, client_cur): 
    doc_id = client_cur.insert_one(doc_data).inserted_id
    return

def insert_many_document(list_of_customer_data, client_cur):
    customer_ids = client_cur.insert_many(list_of_customer_data).inserted_id
    return

def find_one_document(query_dict, client_cur):
    return client_cur.find_one(query_dict)

def find_many_document(query, projection, client_cur):
    return client_cur.find(query, projection)

def insert_brand_dict(customer_dict, current_doc, brand_dict, client_cur):
    client_cur.update_one({
      '_id': current_doc['_id']
    },{
      '$set': {
        'company.'+customer_dict['company']+'.'+customer_dict['brand']: brand_dict
      }
    }, upsert=False)

    return