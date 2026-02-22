import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / 'models'
MODELS_DIR.mkdir(exist_ok=True)

crop_df = pd.read_csv(ROOT / 'data' / 'crop_recommendation.csv')
X_crop = crop_df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y_crop = crop_df['label']

Xc_train, Xc_test, yc_train, yc_test = train_test_split(X_crop, y_crop, test_size=0.2, random_state=42)

crop_model = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(n_estimators=250, random_state=42))
])
crop_model.fit(Xc_train, yc_train)
crop_acc = accuracy_score(yc_test, crop_model.predict(Xc_test))

joblib.dump(crop_model, MODELS_DIR / 'crop_recommender.joblib')


disease_df = pd.read_csv(ROOT / 'data' / 'disease_symptoms.csv')
X_disease = disease_df[['temp', 'humidity', 'leaf_spots', 'leaf_yellowing', 'wilting', 'powdery_growth', 'stem_rot']]
y_disease = disease_df['disease']

Xd_train, Xd_test, yd_train, yd_test = train_test_split(X_disease, y_disease, test_size=0.2, random_state=42)

disease_model = RandomForestClassifier(n_estimators=300, random_state=42)
disease_model.fit(Xd_train, yd_train)
disease_acc = accuracy_score(yd_test, disease_model.predict(Xd_test))

joblib.dump(disease_model, MODELS_DIR / 'disease_detector.joblib')

report = {
    'crop_model_accuracy': round(float(crop_acc), 4),
    'disease_model_accuracy': round(float(disease_acc), 4)
}

with open(MODELS_DIR / 'training_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

print('Training complete:', report)
