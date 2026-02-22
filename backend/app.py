import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from ml.crop_recommendation import CropRecommendationModel
from ml.disease_detector import DiseaseDetector

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
CORS(app)

crop_model = CropRecommendationModel()
disease_model = DiseaseDetector()


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/recommend-crop")
def recommend_crop():
    data = request.get_json(force=True)
    required_fields = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        numeric_data = {k: float(data[k]) for k in required_fields}
    except ValueError:
        return jsonify({"error": "All fields must be numeric"}), 400

    result = crop_model.predict(numeric_data)
    return jsonify(result)


@app.post("/api/disease-detect")
def detect_disease():
    if "leafImage" not in request.files:
        return jsonify({"error": "No file uploaded. Use form-data key: leafImage"}), 400

    file = request.files["leafImage"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    result = disease_model.predict(save_path)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
