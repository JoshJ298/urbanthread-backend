from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe
import os

app = Flask(__name__)
CORS(app)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

@app.route("/")
def home():
    return {"message": "API running"}

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        data = request.get_json()
        items = data.get("items", [])

        if not items:
            return jsonify({"error": "Cart empty"}), 400

        line_items = []

        for item in items:
            line_items.append({
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": item["name"]
                    },
                    "unit_amount": int(item["price"] * 100),
                },
                "quantity": item["quantity"],
            })

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url="https://urbanthread-backend.onrender.com/",
            cancel_url="https://urbanthread-backend.onrender.com/",
        )

        return jsonify({"url": session.url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)