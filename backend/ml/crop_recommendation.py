import numpy as np
from sklearn.ensemble import RandomForestClassifier


class CropRecommendationModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=200, random_state=42)
        self.labels = np.array([
            "rice",
            "maize",
            "cotton",
            "wheat",
            "jute",
            "chickpea",
            "mango",
            "apple",
            "banana",
        ])
        self._train()

    def _train(self):
        # Synthetic-but-realistic agronomy ranges: N, P, K, temperature, humidity, pH, rainfall
        X = np.array([
            [90, 42, 43, 20, 82, 6.5, 220],
            [85, 58, 41, 23, 80, 6.2, 200],
            [60, 55, 45, 27, 62, 6.8, 120],
            [62, 50, 44, 26, 60, 6.7, 115],
            [120, 40, 20, 30, 55, 6.4, 95],
            [118, 38, 22, 31, 52, 6.6, 90],
            [80, 40, 40, 18, 65, 6.1, 80],
            [75, 45, 35, 17, 68, 6.3, 75],
            [70, 38, 42, 26, 88, 6.9, 180],
            [72, 35, 40, 28, 85, 6.8, 170],
            [35, 60, 80, 22, 45, 7.1, 60],
            [38, 65, 75, 21, 48, 7.0, 55],
            [20, 30, 30, 27, 70, 5.8, 130],
            [25, 35, 28, 28, 68, 5.9, 140],
            [22, 28, 32, 16, 72, 6.0, 150],
            [24, 26, 35, 15, 74, 5.7, 145],
            [100, 35, 80, 29, 75, 6.0, 160],
            [95, 32, 78, 30, 78, 6.1, 165],
        ])
        y = np.array([
            "rice", "rice",
            "maize", "maize",
            "cotton", "cotton",
            "wheat", "wheat",
            "jute", "jute",
            "chickpea", "chickpea",
            "mango", "mango",
            "apple", "apple",
            "banana", "banana",
        ])
        self.model.fit(X, y)

    def predict(self, input_features):
        features = np.array([
            input_features["nitrogen"],
            input_features["phosphorus"],
            input_features["potassium"],
            input_features["temperature"],
            input_features["humidity"],
            input_features["ph"],
            input_features["rainfall"],
        ]).reshape(1, -1)

        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        class_scores = dict(zip(self.model.classes_, probabilities))
        sorted_scores = sorted(class_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "recommended_crop": prediction,
            "top_choices": [{"crop": c, "confidence": round(s * 100, 2)} for c, s in sorted_scores[:3]],
        }
