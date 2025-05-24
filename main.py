import os
import traceback
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

load_dotenv()

app = Flask(__name__)

session = HTTP(
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    testnet=False  # True — только для песочницы
)

@app.route("/signal", methods=["POST"])
def receive_signal():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        symbol = data.get("symbol")
        side = data.get("side", "buy").lower()
        usdt_amount = float(data.get("usdt_amount", 40))
        tp_pct = float(data.get("take_profit_pct", 2.0))
        sl_pct = float(data.get("stop_loss_pct", 9.0))

        # Открытие маркет-ордера
        order = session.place_order(
            category="linear",
            symbol=symbol,
            side="Buy" if side == "buy" else "Sell",
            order_type="Market",
            qty=usdt_amount,  # можно округлить при необходимости
            take_profit=round(usdt_amount * (tp_pct / 100), 2),
            stop_loss=round(usdt_amount * (sl_pct / 100), 2),
            time_in_force="GoodTillCancel"
        )

        return jsonify(order)

    except Exception as e:
        traceback_str = traceback.format_exc()
        return jsonify({"error": str(e), "trace": traceback_str}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))