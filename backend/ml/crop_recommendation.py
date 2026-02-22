import os
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd
from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


@dataclass
class CropTrainingResult:
    accuracy: float
    samples: int
    classes: List[str]


class CropRecommendationModel:
    """
    Trains on Kaggle Crop Recommendation dataset:
    https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
    Expected CSV columns: N, P, K, temperature, humidity, ph, rainfall, label
    """

    def __init__(self, dataset_path: str, model_path: str):
        self.dataset_path = dataset_path
        self.model_path = model_path
        self.model = None
        self.classes_ = []

        if os.path.exists(self.model_path):
            self._load()
        else:
            self.train_and_save()

    def _load_dataset(self):
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(
                f"Crop dataset not found at {self.dataset_path}. "
                "Download from Kaggle and place CSV at this location."
            )

        df = pd.read_csv(self.dataset_path)
        required = set(FEATURES + ["label"])
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Dataset missing required columns: {sorted(missing)}")
        return df

    def train_and_save(self) -> CropTrainingResult:
        df = self._load_dataset()
        X = df[FEATURES].astype(float)
        y = df["label"].astype(str)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.model = RandomForestClassifier(
            n_estimators=400,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced_subsample",
        )
        self.model.fit(X_train, y_train)
        accuracy = float(self.model.score(X_test, y_test))
        self.classes_ = list(self.model.classes_)

        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        dump({"model": self.model, "classes": self.classes_}, self.model_path)

        _ = classification_report(y_test, self.model.predict(X_test), output_dict=True)
        return CropTrainingResult(accuracy=accuracy, samples=len(df), classes=self.classes_)

    def _load(self):
        payload = load(self.model_path)
        self.model = payload["model"]
        self.classes_ = payload["classes"]

    def predict(self, input_features: Dict[str, float]):
        values = [
            input_features["nitrogen"],
            input_features["phosphorus"],
            input_features["potassium"],
            input_features["temperature"],
            input_features["humidity"],
            input_features["ph"],
            input_features["rainfall"],
        ]
        X = np.array(values, dtype=float).reshape(1, -1)

        pred = self.model.predict(X)[0]
        proba = self.model.predict_proba(X)[0]
        ranked = sorted(zip(self.model.classes_, proba), key=lambda t: t[1], reverse=True)

        return {
            "recommended_crop": pred,
            "top_choices": [
                {"crop": crop, "confidence": round(float(score) * 100, 2)}
                for crop, score in ranked[:5]
            ],
        }

    def fertilizer_hint(self, input_features: Dict[str, float]):
        n, p, k = (
            float(input_features["nitrogen"]),
            float(input_features["phosphorus"]),
            float(input_features["potassium"]),
        )
        hints = []
        if n < 40:
            hints.append("Low Nitrogen: add urea/compost in split doses.")
        if p < 30:
            hints.append("Low Phosphorus: apply single super phosphate near root zone.")
        if k < 30:
            hints.append("Low Potassium: apply muriate of potash for stress tolerance.")
        if not hints:
            hints.append("NPK profile appears balanced for many field crops.")
        return hints
