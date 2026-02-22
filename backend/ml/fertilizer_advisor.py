from typing import Dict


class FertilizerAdvisor:
    """Rule + profile based agronomy advisor."""

    CROP_PROFILES = {
        "rice": {"N": 100, "P": 40, "K": 40},
        "maize": {"N": 120, "P": 60, "K": 40},
        "wheat": {"N": 90, "P": 45, "K": 35},
        "cotton": {"N": 110, "P": 50, "K": 45},
        "banana": {"N": 200, "P": 60, "K": 200},
    }

    def plan(self, crop: str, values: Dict[str, float]):
        crop_l = crop.lower()
        target = self.CROP_PROFILES.get(crop_l, {"N": 100, "P": 50, "K": 50})

        n_gap = max(0.0, target["N"] - float(values["nitrogen"]))
        p_gap = max(0.0, target["P"] - float(values["phosphorus"]))
        k_gap = max(0.0, target["K"] - float(values["potassium"]))

        stage_plan = [
            {
                "stage": "Basal (before sowing/transplanting)",
                "recommendation": f"Apply ~{round(p_gap * 0.5, 1)} kg/ha P2O5 and ~{round(k_gap * 0.4, 1)} kg/ha K2O.",
            },
            {
                "stage": "Vegetative",
                "recommendation": f"Apply ~{round(n_gap * 0.5, 1)} kg/ha N in split doses.",
            },
            {
                "stage": "Flowering/fruit set",
                "recommendation": f"Top-dress ~{round(n_gap * 0.5, 1)} kg/ha N and ~{round(k_gap * 0.6, 1)} kg/ha K2O.",
            },
        ]

        notes = [
            "Always confirm with local soil test recommendations.",
            "Use drip/fertigation for higher nutrient-use efficiency where possible.",
            "Add organic matter/compost to improve soil structure and micronutrient availability.",
        ]

        return {
            "crop": crop,
            "target_npk": target,
            "estimated_gap": {"N": round(n_gap, 2), "P": round(p_gap, 2), "K": round(k_gap, 2)},
            "stage_plan": stage_plan,
            "notes": notes,
        }
