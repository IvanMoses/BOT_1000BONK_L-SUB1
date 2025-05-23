import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Введите адрес вашего локального или внешнего main.py сервера
MAIN_BOT_URL = "http://localhost:5000/webhook"

@app.route('/signal', methods=['POST'])
def receive_signal():
    try:
        data = request.json

        # Простая валидация входного сигнала
        symbol = data.get("symbol")
        direction = data.get("side")
        if symbol is None or direction is None:
            return jsonify({"error": "Missing symbol or side"}), 400

        # Опциональные параметры
        usdt_amount = data.get("usdt_amount", 40)
        tp_pct = data.get("take_profit_pct", 1.5)
        sl_pct = data.get("stop_loss_pct", 0.7)

        payload = {
            "symbol": symbol,
            "side": direction.lower(),
            "usdt_amount": usdt_amount,
            "take_profit_pct": tp_pct,
            "stop_loss_pct": sl_pct
        }

        # Отправка данных в боевого бота
        response = requests.post(MAIN_BOT_URL, json=payload)

        return jsonify({"status": "Signal forwarded", "response": response.json()}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=7000)