import database as db
from flask import session
from datetime import datetime
from app import order_management_db

def create_order_from_cart():
    order = {}
    order.setdefault("username",session["user"]["username"])
    order.setdefault("orderdate",datetime.utcnow())
    order_details = []
    cart = session["cart"]
    for key, value in cart.items():
        order_details.append({"code":key,
                            "name":value["name"],
                            "qty":value["qty"],
                            "subtotal":value["subtotal"]})
    order.setdefault("details",order_details)
    db.create_order(order)

def get_past_orders(username):
    orders_coll = order_management_db['orders']
    orders = list(orders_coll.find({"username": username}))
    return orders
