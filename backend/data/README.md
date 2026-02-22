# Kaggle Datasets Setup

Place datasets here before training/serving models.

## 1) Crop Recommendation Dataset
- Kaggle: `atharvaingle/crop-recommendation-dataset`
- Required file path: `backend/data/Crop_recommendation.csv`

## 2) Plant Disease Dataset (PlantVillage style)
- Kaggle: `emmarex/plantdisease`
- Extracted folder path required: `backend/data/plantvillage/`
- Structure should be class folders containing images.

Example:
```
backend/data/plantvillage/
  Tomato___Early_blight/
  Tomato___Late_blight/
  Pepper__bell___healthy/
  ...
```

## Optional: download with Kaggle CLI
```bash
pip install kaggle
export KAGGLE_USERNAME=...
export KAGGLE_KEY=...
python backend/scripts/fetch_kaggle_data.py
```
