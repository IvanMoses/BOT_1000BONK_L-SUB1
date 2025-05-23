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
    testnet=False  # False — ты торгуешь на реальном аккаунте
)

@app.route("/signal", methods=["POST"])
def receive_signal():
    data = request.json

    if not data:
        return jsonify({"error": "No data received"}), 400

    try:
        symbol = data.get("symbol")
        side = data.get("side", "buy").capitalize()
        take_profit_pct = float(data.get("take_profit_pct", 2.0))
        stop_loss_pct = float(data.get("stop_loss_pct", 9.0))
        usdt_amount = float(data.get("usdt_amount", 40))

        # Market ордер без запроса цены
        order = session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=None,  # Можно заменить на конкретное значение при расчёте
            time_in_force="GoodTillCancel",
            take_profit=take_profit_pct,
            stop_loss=stop_loss_pct
        )

        return jsonify(order)

    except Exception as e:
        print("Exception occurred:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))