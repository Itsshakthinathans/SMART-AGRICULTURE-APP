import os
from dataclasses import dataclass
from typing import List

import numpy as np
from joblib import dump, load
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass
class DiseaseTrainingResult:
    accuracy: float
    samples: int
    classes: List[str]


class DiseaseDetector:
    """
    Trains on Kaggle PlantVillage style folder dataset:
    dataset_root/
      Tomato___Early_blight/
      Tomato___Late_blight/
      Pepper__bell___healthy/
      ...
    """

    def __init__(self, dataset_root: str, model_path: str):
        self.dataset_root = dataset_root
        self.model_path = model_path
        self.model = None
        self.classes_ = []

        if os.path.exists(self.model_path):
            self._load()
        else:
            self.train_and_save()

    @staticmethod
    def _extract_features(image_path: str):
        image = Image.open(image_path).convert("RGB").resize((128, 128))
        arr = np.asarray(image, dtype=np.float32) / 255.0

        # color statistics + histogram feature vector
        means = arr.mean(axis=(0, 1))
        stds = arr.std(axis=(0, 1))
        hist = []
        for ch in range(3):
            h, _ = np.histogram(arr[:, :, ch], bins=16, range=(0, 1), density=True)
            hist.extend(h.tolist())
        feat = np.concatenate([means, stds, np.array(hist, dtype=np.float32)])
        return feat

    def _load_dataset(self):
        if not os.path.exists(self.dataset_root):
            raise FileNotFoundError(
                f"Disease dataset root not found: {self.dataset_root}. "
                "Download Kaggle PlantVillage-style dataset and extract here."
            )

        X, y = [], []
        class_dirs = [d for d in os.listdir(self.dataset_root) if os.path.isdir(os.path.join(self.dataset_root, d))]
        if not class_dirs:
            raise ValueError("No class directories found in disease dataset root.")

        for class_name in sorted(class_dirs):
            full_dir = os.path.join(self.dataset_root, class_name)
            for filename in os.listdir(full_dir):
                ext = os.path.splitext(filename)[1].lower()
                if ext not in ALLOWED_EXT:
                    continue
                img_path = os.path.join(full_dir, filename)
                try:
                    X.append(self._extract_features(img_path))
                    y.append(class_name)
                except Exception:
                    continue

        if not X:
            raise ValueError("No valid images found for disease training.")

        return np.array(X, dtype=np.float32), np.array(y, dtype=str)

    def train_and_save(self) -> DiseaseTrainingResult:
        X, y = self._load_dataset()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.model = RandomForestClassifier(
            n_estimators=500,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced_subsample",
        )
        self.model.fit(X_train, y_train)

        accuracy = float(self.model.score(X_test, y_test))
        self.classes_ = list(self.model.classes_)

        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        dump({"model": self.model, "classes": self.classes_}, self.model_path)
        return DiseaseTrainingResult(accuracy=accuracy, samples=len(y), classes=self.classes_)

    def _load(self):
        payload = load(self.model_path)
        self.model = payload["model"]
        self.classes_ = payload["classes"]

    def _solution_map(self, label: str):
        l = label.lower()
        if "healthy" in l:
            return "Plant appears healthy.", "Continue balanced irrigation, sanitation, and monitoring."
        if "blight" in l:
            return "Likely blight infection.", "Remove affected leaves and use recommended fungicide rotation."
        if "rust" in l:
            return "Likely rust disease.", "Use rust-resistant cultivar and sulfur/triazole spray as advised."
        if "mildew" in l:
            return "Possible mildew symptoms.", "Improve airflow and use preventive fungicide schedule."
        if "spot" in l:
            return "Leaf spot symptoms detected.", "Avoid overhead irrigation and apply copper-based sprays."
        return "Disease class detected.", "Consult local agronomist for crop-specific treatment protocol."

    def predict(self, image_path: str):
        feat = self._extract_features(image_path).reshape(1, -1)
        pred = self.model.predict(feat)[0]
        proba = self.model.predict_proba(feat)[0]
        ranked = sorted(zip(self.model.classes_, proba), key=lambda t: t[1], reverse=True)
        diagnosis, treatment = self._solution_map(pred)

        return {
            "disease": pred,
            "confidence": round(float(ranked[0][1]) * 100, 2),
            "diagnosis": diagnosis,
            "solution": treatment,
            "top_matches": [
                {"label": c, "confidence": round(float(p) * 100, 2)}
                for c, p in ranked[:5]
            ],
        }
