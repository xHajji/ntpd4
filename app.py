from flask import Flask, request, jsonify
import numpy as np
import redis
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# Połączenie z Redis (host "redis" zamiast "localhost", bo Docker używa nazw kontenerów)
redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

# Przykładowe dane do trenowania modelu ML
X = np.array([[1], [2], [3], [4], [5]])
y = np.array([2, 4, 6, 8, 10])
model = LinearRegression().fit(X, y)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "hello world"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if "input" not in data:
        return jsonify({"error": "Brak wymaganej wartosci"}), 400
    try:
        input_value = np.array([[data["input"]]])
        prediction = model.predict(input_value).tolist()

        # Zapis wyniku do Redis
        redis_client.set("last_prediction", prediction[0])

        return jsonify({"prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/last", methods=["GET"])
def last_prediction():
    """ Pobiera ostatnią predykcję z Redis """
    last_pred = redis_client.get("last_prediction")
    if last_pred is None:
        return jsonify({"error": "Brak zapisanej predykcji"}), 404
    return jsonify({"last_prediction": float(last_pred)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
