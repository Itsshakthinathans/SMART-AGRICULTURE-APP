import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

from ml.crop_recommendation import CropRecommendationModel
from ml.disease_detector import DiseaseDetector
from ml.fertilizer_advisor import FertilizerAdvisor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS = os.path.join(BASE_DIR, "uploads")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

CROP_DATASET = os.path.join(DATA_DIR, "Crop_recommendation.csv")
DISEASE_DATASET = os.path.join(DATA_DIR, "plantvillage")
CROP_MODEL_PATH = os.path.join(MODELS_DIR, "crop_model.joblib")
DISEASE_MODEL_PATH = os.path.join(MODELS_DIR, "disease_model.joblib")

os.makedirs(UPLOADS, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOADS
CORS(app)

crop_model = None
disease_model = None
fertilizer_advisor = FertilizerAdvisor()
boot_errors = []
recent_predictions = []


def _add_history(entry):
    recent_predictions.append(entry)
    if len(recent_predictions) > 25:
        recent_predictions.pop(0)


def init_models():
    global crop_model, disease_model
    boot_errors.clear()

    try:
        crop_model = CropRecommendationModel(CROP_DATASET, CROP_MODEL_PATH)
    except Exception as e:
        crop_model = None
        boot_errors.append(f"Crop model unavailable: {e}")

    try:
        disease_model = DiseaseDetector(DISEASE_DATASET, DISEASE_MODEL_PATH)
    except Exception as e:
        disease_model = None
        boot_errors.append(f"Disease model unavailable: {e}")


init_models()


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "time": datetime.utcnow().isoformat() + "Z",
            "crop_model_ready": crop_model is not None,
            "disease_model_ready": disease_model is not None,
            "boot_errors": boot_errors,
            "recent_predictions_count": len(recent_predictions),
        }
    )


@app.get("/api/model-info")
def model_info():
    return jsonify(
        {
            "crop_dataset": CROP_DATASET,
            "disease_dataset_root": DISEASE_DATASET,
            "crop_model_path": CROP_MODEL_PATH,
            "disease_model_path": DISEASE_MODEL_PATH,
            "crop_classes": getattr(crop_model, "classes_", []),
            "disease_classes": getattr(disease_model, "classes_", []),
            "boot_errors": boot_errors,
        }
    )


@app.get("/api/recent-predictions")
def get_recent_predictions():
    return jsonify({"items": recent_predictions})


@app.get("/api/crop-calendar")
def crop_calendar():
    return jsonify(
        {
            "rice": "Kharif (June-Nov), irrigated: year-round in some regions",
            "wheat": "Rabi (Nov-Apr)",
            "maize": "Kharif and Rabi (region dependent)",
            "cotton": "Kharif (Apr-Oct sowing windows vary)",
            "banana": "Year-round with irrigation",
        }
    )


@app.post("/api/train-models")
def train_models():
    init_models()
    if boot_errors:
        return jsonify({"message": "Training finished with errors", "errors": boot_errors}), 400
    return jsonify({"message": "Models trained/reloaded successfully"})


@app.post("/api/recommend-crop")
def recommend_crop():
    if crop_model is None:
        return jsonify({"error": "Crop model unavailable", "details": boot_errors}), 503

    data = request.get_json(force=True)
    fields = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"]

    try:
        payload = {k: float(data[k]) for k in fields}
    except Exception:
        return jsonify({"error": f"Invalid payload. Required numeric fields: {fields}"}), 400

    rec = crop_model.predict(payload)
    fertilizer_hints = crop_model.fertilizer_hint(payload)
    fertilizer_plan = fertilizer_advisor.plan(rec["recommended_crop"], payload)

    result = {**rec, "fertilizer_hints": fertilizer_hints, "fertilizer_plan": fertilizer_plan}
    _add_history(
        {
            "type": "crop",
            "time": datetime.utcnow().isoformat() + "Z",
            "input": payload,
            "output": {"recommended_crop": rec["recommended_crop"]},
        }
    )
    return jsonify(result)


@app.post("/api/fertilizer-plan")
def fertilizer_plan():
    data = request.get_json(force=True)
    required = ["crop", "nitrogen", "phosphorus", "potassium"]
    try:
        for k in required:
            _ = data[k]
        values = {
            "nitrogen": float(data["nitrogen"]),
            "phosphorus": float(data["phosphorus"]),
            "potassium": float(data["potassium"]),
        }
    except Exception:
        return jsonify({"error": f"Invalid payload. Required fields: {required}"}), 400

    return jsonify(fertilizer_advisor.plan(data["crop"], values))


@app.post("/api/disease-detect")
def detect_disease():
    if disease_model is None:
        return jsonify({"error": "Disease model unavailable", "details": boot_errors}), 503

    if "leafImage" not in request.files:
        return jsonify({"error": "Upload image with form-data key: leafImage"}), 400

    f = request.files["leafImage"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(f.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    f.save(save_path)

    result = disease_model.predict(save_path)
    _add_history(
        {
            "type": "disease",
            "time": datetime.utcnow().isoformat() + "Z",
            "input": {"filename": filename},
            "output": {"disease": result["disease"], "confidence": result["confidence"]},
        }
    )
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
