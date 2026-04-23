from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

import os
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

users = {}
cart = {}
orders = []

products = [
    {"id":1,"name":"Black Hoodie","category":"hoodie","gender":"men","price":40},
    {"id":2,"name":"White T-Shirt","category":"tshirt","gender":"women","price":20},
    {"id":3,"name":"Blue Jeans","category":"jeans","gender":"men","price":45},
    {"id":4,"name":"Grey Sweatpants","category":"pants","gender":"women","price":35},
    {"id":5,"name":"Leather Jacket","category":"jacket","gender":"men","price":90},
    {"id":6,"name":"Red Hoodie","category":"hoodie","gender":"women","price":42},
    {"id":7,"name":"Black Shorts","category":"shorts","gender":"men","price":25},
    {"id":8,"name":"Sneakers","category":"shoes","gender":"unisex","price":60},
    {"id":9,"name":"Cap","category":"accessories","gender":"unisex","price":15},
    {"id":10,"name":"Denim Jacket","category":"jacket","gender":"women","price":75}
]

@app.route("/")
def home():
    return {"message": "API running"}

@app.route("/products")
def get_products():
    return jsonify(products)

@app.route("/products/<int:product_id>")
def get_product(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        return jsonify(product)
    return {"error": "Not found"}, 404

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = data["password"]

    if username in users:
        return {"error": "User exists"}

    users[username] = password
    return {"message": "Registered"}

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    if username not in users or users[username] != password:
        return {"error": "Invalid"}

    return {"message": "Success"}

@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    data = request.json
    product_id = data["product_id"]

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        return {"error": "Not found"}, 404

    if product_id in cart:
        cart[product_id]["quantity"] += 1
    else:
        cart[product_id] = {
            "name": product["name"],
            "price": product["price"],
            "quantity": 1
        }

    return {"message": "Added", "cart": cart}

@app.route("/cart")
def view_cart():
    total = sum(item["price"] * item["quantity"] for item in cart.values())
    return {"items": cart, "total": total}

@app.route("/cart/remove", methods=["POST"])
def remove():
    data = request.json
    product_id = data["product_id"]

    if product_id in cart:
        del cart[product_id]
        return {"message": "Removed"}

    return {"error": "Not found"}, 404

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    items = data.get("items", [])

    if not items:
        return {"error": "Cart empty"}, 400

    line_items = []

    for item in items:
        line_items.append({
            "price_data": {
                "currency": "gbp",
                "product_data": {
                    "name": item["name"]
                },
                "unit_amount": int(item["price"] * 100)
            },
            "quantity": item["quantity"]
        })

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url="http://127.0.0.1:5501/index.html",
        cancel_url="http://127.0.0.1:5500/checkout.html"
    )

    print(session.url)

    return jsonify({"url": session.url})

@app.route("/orders")
def get_orders():
    return jsonify(orders)

if __name__ == "__main__":
    app.run(debug=True)




import os
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
