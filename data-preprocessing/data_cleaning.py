from preprocessing_creating_dataset import read_dataset
import pandas as pd
from pathlib import Path
from random import shuffle, seed
from faker.providers.person.en import Provider
import random
import pymongo
import dateutil.parser as parser
import datetime
import json
from collections import defaultdict
import dateutil.parser


def format_store_data():
    # ------FORMAT STORE DATA-------

    df = pd.read_csv("olist_dataset.csv")

    # Grouping different payments and performing sum
    gby_cols = list(df.columns.values)
    gby_cols.remove('payment_value')
    final_df = df.groupby(gby_cols).agg({'payment_value': ['sum']})
    final_df.columns = final_df.columns.droplevel(1)
    # final_df.head()
    final_df = final_df.reset_index()

    # Consider required columns
    req_columns = ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"]

    req_store_df = final_df[req_columns]
    req_store_df = req_store_df.drop_duplicates()

    # Append country column
    req_store_df["country"] = "Brazil"

    req_store_df = req_store_df.rename(columns={'seller_id': 'store_id',
                                                'seller_city': 'city',
                                                'seller_state': 'state',
                                                'seller_zip_code_prefix': 'zip_code'})

    # Read geography and drop duplicates
    geography_df = read_dataset(Path('olist_geolocation_dataset.csv'))
    geography_df = geography_df.drop_duplicates(subset=['geolocation_zip_code_prefix'], keep='first')

    # Removing unnecessary columns
    geography_df = geography_df.iloc[:, ~geography_df.columns.isin(['geolocation_city', 'geolocation_state'])]
    req_store_df = pd.merge(req_store_df, geography_df, left_on="zip_code",
                            right_on="geolocation_zip_code_prefix",
                            how="left")

    # Delete columns that are unnecessary
    del req_store_df["geolocation_zip_code_prefix"]

    req_store_df = req_store_df.rename(columns={'geolocation_lat': 'lat', 'geolocation_lng': 'lng'})

    # Append store name based on store id
    req_store_df['name'] = 'Store-' + req_store_df["store_id"]

    # Change type of zipcode to int
    req_store_df['zip_code'] = req_store_df['zip_code'].astype(int)

    # Creating geoJson point format
    val = []
    for index, row in req_store_df.iterrows():
        point = {
            'type': 'Point',
            'coordinates': [row["lng"], row["lat"]]
        }
        val.append(point)

    # Assign geoJson value
    req_store_df["co_ordinate"] = val

    new_df = req_store_df[["store_id", "name"]]
    new_df['address'] = req_store_df.loc[:,
                        ["country", "state", "city", "zip_code", "co_ordinate"]].to_dict(
        orient='records')

    # return the final dataframe
    return new_df


def format_customers_data():
    # -----FORMAT CUSTOMER DATA------

    df = pd.read_csv("olist_dataset.csv")

    # Grouping different payments and performing sum
    gby_cols = list(df.columns.values)
    gby_cols.remove('payment_value')
    final_df = df.groupby(gby_cols).agg({'payment_value': ['sum']})
    final_df.columns = final_df.columns.droplevel(1)
    # final_df.head()
    final_df = final_df.reset_index()

    req_columns = ["customer_id", "customer_state", "customer_city", "customer_zip_code_prefix", "geolocation_lat",
                   "geolocation_lng"]

    req_customer_df = final_df[req_columns]
    req_customer_df = req_customer_df.drop_duplicates()

    # Set the default organization id field
    req_customer_df["organization_id"] = 1

    # Set customer country
    req_customer_df["customer_country"] = "Brazil"

    # Retrieve random names
    first_names = list(set(Provider.first_names))
    last_names = list(set(Provider.last_names))

    # Shuffle to prevent collisions
    seed(4321)
    shuffle(first_names)
    shuffle(last_names)

    names = set()
    email = set()
    mobile = set()

    f_name = []
    l_name = []

    # Add first name and email
    while len(names) < len(req_customer_df):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        names.add(first_name + " " + last_name)
        email.add(first_name + "." + last_name + ".com")

    # Add mobile number
    while len(mobile) < len(req_customer_df):
        mobile.add(random.randint(9000000000, 9999999999))

    names = list(names)
    email = list(email)
    mobile = list(mobile)

    # Assign name, email, and mobile
    req_customer_df["name"] = names
    req_customer_df["email"] = email
    req_customer_df["mobile"] = mobile

    # Generate random age
    age = []
    while len(age) < len(req_customer_df):
        age.append(random.randint(30, 90))

    # Assign age
    req_customer_df["age"] = age

    # Generate random gender
    gender = []
    gender_values = ["Male", "Female", "Other"]

    while len(gender) < len(req_customer_df):
        gender.append(random.choice(gender_values))
        # gender.append(random.randint(0, 1))

    # Assign gender
    req_customer_df["gender"] = gender

    # Generate random income
    income = []
    while len(income) < len(req_customer_df):
        # Minimum income - 1000 Maximum income - 600000
        income.append(random.randint(1000, 50000))

    # Assign income
    req_customer_df["income"] = income

    req_customer_df = req_customer_df.rename(columns={'geolocation_lat': 'lat',
                                                      'geolocation_lng': 'lng',
                                                      'customer_zip_code_prefix': 'zip_code'})

    new_df = req_customer_df[["customer_id", "organization_id", "name", "email", "mobile", "age", "gender", "income"]]

    # Creating geoJson point format
    val = []
    for index, row in req_customer_df.iterrows():
        point = {
            'type': 'Point',
            'coordinates': [row["lng"], row["lat"]]
        }
        val.append(point)

    req_customer_df["co_ordinate"] = val
    new_df['address'] = req_customer_df.loc[:,
                        ["customer_country", "customer_state", "customer_city", "zip_code",
                         "co_ordinate"]].to_dict(orient='records')

    # return the final dataframe
    return new_df


def format_organization_data():
    df = pd.read_csv("olist_dataset.csv")

    # Grouping different payments and performing sum
    gby_cols = list(df.columns.values)
    gby_cols.remove('payment_value')
    final_df = df.groupby(gby_cols).agg({'payment_value': ['sum']})
    final_df.columns = final_df.columns.droplevel(1)
    # final_df.head()
    final_df = final_df.reset_index()

    req_columns = ["seller_id"]

    req_organization_df = final_df[req_columns]

    req_organization_df = req_organization_df.drop_duplicates()

    # Rename seller_id to store_id
    req_organization_df = req_organization_df.rename(columns={'seller_id': 'store_id'})

    list_of_values = req_organization_df["store_id"].to_list()
    # print(list_of_values)

    # Creating required dataframe
    col1 = "organization_id"
    col1_values = 1
    col2 = "store"
    col2_values = pd.Series([list_of_values])

    final_organization_df = pd.DataFrame({col1: col1_values, col2: col2_values})

    # return the final dataframe
    return final_organization_df


def format_products_data():
    df = pd.read_csv("olist_dataset.csv")

    # Grouping different payments and performing sum
    gby_cols = list(df.columns.values)
    gby_cols.remove('payment_value')
    final_df = df.groupby(gby_cols).agg({'payment_value': ['sum']})
    final_df.columns = final_df.columns.droplevel(1)
    final_df = final_df.reset_index()

    # Retrieve required columns
    req_columns = ["product_id", "seller_id", "product_category_name"]
    req_prod_df = final_df[req_columns]
    req_prod_df = req_prod_df.drop_duplicates()

    # Read products df
    product_df = pd.read_csv("olist_products_dataset.csv")

    # Merge dimensions and product_info
    dim_cols = ['product_id', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
    req_prod_df = req_prod_df.merge(product_df[dim_cols], on="product_id")

    # Organization ID
    req_prod_df["organization_id"] = 1

    # Rename columns
    req_prod_df.rename({"seller_id": "store_id"}, axis=1, inplace=True)

    new_df = req_prod_df

    new_df = new_df.rename(
        columns={'product_height_cm': 'height', 'product_length_cm': 'length', 'product_width_cm': 'width',
                 'product_weight_g': 'weight', 'product_category_name': 'category'})

    new_df["title"] = new_df["product_id"]

    new_df["dimension"] = new_df.loc[:, ["height", "width", "length", "weight"]].to_dict(orient='records')

    # Delete unnecessary columns
    del new_df["height"]
    del new_df["width"]
    del new_df["length"]
    del new_df["weight"]

    # Return the final dataframe
    return new_df


def format_orders_data():
    df = pd.read_csv("olist_dataset.csv")

    # Grouping different payments and performing sum
    gby_cols = list(df.columns.values)
    gby_cols.remove('payment_value')
    final_df = df.groupby(gby_cols).agg({'payment_value': ['sum']})
    final_df.columns = final_df.columns.droplevel(1)
    final_df = final_df.reset_index()

    # Retrieve required columns
    req_columns = ["order_id", "order_purchase_timestamp", "customer_id", "product_id", "payment_value"]

    req_orders_df = final_df[req_columns]

    req_orders_df = req_orders_df.drop_duplicates()

    # Retrieve customer final dataframe
    customer_df = format_customers_data()

    # Merge customers df with orders df
    req_orders_df = pd.merge(req_orders_df, customer_df, on="customer_id", how="left")

    req_orders_df["customer"] = req_orders_df.loc[:,
                                ["customer_id", "organization_id", "name", "email", "mobile",
                                 "address", "age", "gender", "income"]].to_dict(orient='records')

    # Remove unecessary columns
    del req_orders_df["customer_id"]
    del req_orders_df["name"]
    del req_orders_df["email"]
    del req_orders_df["mobile"]
    del req_orders_df["address"]
    del req_orders_df["age"]
    del req_orders_df["gender"]
    del req_orders_df["income"]
    del req_orders_df["organization_id"]

    # Retrieve products final dataframe
    products_df = format_products_data()

    # Merge products df with orders df
    req_orders_df = pd.merge(req_orders_df, products_df, on="product_id", how="left")

    req_orders_df["product"] = req_orders_df.loc[:,
                               ["product_id", "organization_id", "store_id", "title", "dimension", "category"]].to_dict(
        orient='records')

    # Remove unecessary columns
    del req_orders_df["product_id"]
    del req_orders_df["store_id"]
    del req_orders_df["title"]
    del req_orders_df["dimension"]
    del req_orders_df["category"]

    # Convert to datetime format
    req_orders_df = req_orders_df.astype({'order_purchase_timestamp': 'datetime64[ns]'})

    req_orders_df["order_purchase_timestamp"] = req_orders_df["order_purchase_timestamp"].apply(lambda x: x.isoformat())

    print(dateutil.parser.parse(req_orders_df.iloc[0]["order_purchase_timestamp"]))
    req_orders_df = req_orders_df.rename(
        columns={'order_purchase_timestamp': 'order_date'})

    # Return the final df
    return req_orders_df


def create_json(df, file_name):
    # Write to a json file
    df.to_json(file_name, orient='records')


if __name__ == "__main__":
    # Create Store collection
    # Get final dataframe
    store_df = format_store_data()
    # Write to a json file
    create_json(store_df, "store.json")

    # Create Customer collection
    # Get final dataframe
    customer_df = format_customers_data()
    # Write to a json file
    create_json(customer_df, "customer.json")

    # Create Organization collection
    # Get final dataframe
    organization_df = format_organization_data()
    # Write to a json file
    create_json(organization_df, "organization.json")

    # Create Products collection
    # Get final dataframe
    products_df = format_products_data()
    # Write to a json file
    create_json(products_df, "products.json")

    # Create Orders collection
    # Get final dataframe
    orders_df = format_orders_data()
    # Write to a json file
    create_json(orders_df, "orders_dateiso.json")
