from PIL import Image
import numpy as np


class DiseaseDetector:
    def __init__(self):
        self.knowledge_base = {
            "Healthy": {
                "confidence_tip": "Leaf color and texture look balanced.",
                "solution": "Maintain regular irrigation, balanced fertilization, and weekly scouting.",
                "prevention": "Use certified seeds and avoid overwatering.",
            },
            "Leaf Blight": {
                "confidence_tip": "Detected dominant brown/yellow dry patches.",
                "solution": "Remove infected leaves and apply copper-based fungicide every 7-10 days.",
                "prevention": "Improve air circulation and avoid wetting foliage during irrigation.",
            },
            "Rust": {
                "confidence_tip": "Detected orange/reddish speckle-like areas.",
                "solution": "Spray sulfur or triazole fungicide according to label instructions.",
                "prevention": "Use resistant varieties and keep canopy dry.",
            },
            "Nutrient Deficiency": {
                "confidence_tip": "Detected pale/yellow dominant coloration.",
                "solution": "Apply foliar micronutrient spray and soil test-guided NPK correction.",
                "prevention": "Follow stage-wise fertilization schedule and monitor pH.",
            },
        }

    def predict(self, image_path):
        image = Image.open(image_path).convert("RGB").resize((224, 224))
        arr = np.array(image).astype(np.float32)

        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        mean_r, mean_g, mean_b = r.mean(), g.mean(), b.mean()
        yellow_mask = (r > 120) & (g > 110) & (b < 100)
        brown_mask = (r > 90) & (g > 60) & (g < 120) & (b < 80)
        rust_mask = (r > 120) & (g > 60) & (g < 120) & (b < 90)

        yellow_ratio = yellow_mask.mean()
        brown_ratio = brown_mask.mean()
        rust_ratio = rust_mask.mean()

        if rust_ratio > 0.14:
            label = "Rust"
            confidence = min(0.99, 0.60 + rust_ratio)
        elif brown_ratio > 0.18:
            label = "Leaf Blight"
            confidence = min(0.98, 0.58 + brown_ratio)
        elif yellow_ratio > 0.22 and mean_g < 150:
            label = "Nutrient Deficiency"
            confidence = min(0.96, 0.55 + yellow_ratio)
        else:
            label = "Healthy"
            confidence = 0.88

        info = self.knowledge_base[label]
        return {
            "disease": label,
            "confidence": round(confidence * 100, 2),
            "solution": info["solution"],
            "prevention": info["prevention"],
            "note": info["confidence_tip"],
            "color_stats": {
                "mean_r": round(float(mean_r), 2),
                "mean_g": round(float(mean_g), 2),
                "mean_b": round(float(mean_b), 2),
            },
        }
