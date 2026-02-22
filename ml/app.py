from pathlib import Path

import joblib
from flask import Flask, jsonify, request
from flask_cors import CORS

ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / 'models'

app = Flask(__name__)
CORS(app)

crop_model = joblib.load(MODELS_DIR / 'crop_recommender.joblib')
disease_model = joblib.load(MODELS_DIR / 'disease_detector.joblib')

DISEASE_SOLUTIONS = {
    'Healthy': 'No major disease symptoms detected. Maintain balanced irrigation and periodic nutrient checks.',
    'Bacterial Spot': 'Use copper-based bactericides and avoid overhead irrigation. Remove infected leaves promptly.',
    'Powdery Mildew': 'Apply sulfur/fungicide spray and increase field air circulation.',
    'Leaf Blight': 'Use resistant varieties, reduce leaf wetness duration, and apply recommended fungicide schedule.',
    'Root Rot': 'Improve drainage, reduce overwatering, and treat with biological fungicides where appropriate.'
}

@app.get('/health')
def health():
    return jsonify({'status': 'ok'})

@app.post('/predict/crop')
def predict_crop():
    payload = request.get_json(force=True)
    features = [[
        float(payload['N']), float(payload['P']), float(payload['K']),
        float(payload['temperature']), float(payload['humidity']),
        float(payload['ph']), float(payload['rainfall'])
    ]]

    prediction = crop_model.predict(features)[0]
    return jsonify({'recommended_crop': prediction})

@app.post('/predict/disease')
def predict_disease():
    payload = request.get_json(force=True)
    features = [[
        float(payload['temp']), float(payload['humidity']), int(payload['leaf_spots']),
        int(payload['leaf_yellowing']), int(payload['wilting']), int(payload['powdery_growth']),
        int(payload['stem_rot'])
    ]]

    disease = disease_model.predict(features)[0]
    solution = DISEASE_SOLUTIONS.get(disease, 'Consult local agronomist for tailored treatment.')

    return jsonify({'disease': disease, 'solution': solution})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
