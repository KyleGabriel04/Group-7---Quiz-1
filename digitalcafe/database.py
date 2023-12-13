import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

products_db = myclient["products"]


def get_product(code):
    products_coll = products_db["products"]

    product = products_coll.find_one({"code":code},{"_id":0})

    return product

def get_products():
    product_list = []

    products_coll = products_db["products"]

    for p in products_coll.find({},{"_id":0}):
        product_list.append(p)

    return product_list



def get_branch(code):
    branches_coll = products_db["branches"]
    branch = branches_coll.find_one({"code": code})
    return branch

def get_branches():
    branches_coll = products_db["branches"]
    branches_list = list(branches_coll.find({}))
    return branches_list


def get_user(username):
    order_management_db = myclient["order_management"]
    customers_coll = order_management_db['customers']
    user = customers_coll.find_one({"username": username})
    return user


def create_order(order):
    order_management_db = myclient["order_management"]
    orders_coll = order_management_db['orders']
    orders_coll.insert(order)



