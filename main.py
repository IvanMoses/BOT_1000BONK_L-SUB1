import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

load_dotenv()

app = Flask(__name__)

session = HTTP(
    api_key=os.getenv("BYBIT_API_KEY"),
    api_secret=os.getenv("BYBIT_API_SECRET"),
    testnet=True
)

@app.route("/signal", methods=["POST"])
def receive_signal():
    data = request.json

    if not data:
        return jsonify({"error": "No data received"}), 400

    try:
        symbol = data.get("symbol")
        side = data.get("side", "buy").lower()
        take_profit_pct = float(data.get("take_profit_pct", 2.0))
        stop_loss_pct = float(data.get("stop_loss_pct", 9.0))
        usdt_amount = float(data.get("usdt_amount", 40))

        price_info = session.get_latest_price(symbol=symbol)
        mark_price = float(price_info["result"]["price"])
        quantity = round(usdt_amount / mark_price, 3)

        order_price = mark_price
        take_profit_price = round(order_price * (1 + take_profit_pct / 100), 3)
        stop_loss_price = round(order_price * (1 - stop_loss_pct / 100), 3)

        order = session.place_order(
            category="linear",
            symbol=symbol,
            side="Buy" if side == "buy" else "Sell",
            order_type="Market",
            qty=quantity,
            take_profit=take_profit_price,
            stop_loss=stop_loss_price,
            time_in_force="GoodTillCancel"
        )

        return jsonify(order)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7000)))