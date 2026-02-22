# AgriTech Pro (Enhanced) - Full Stack Smart Agriculture Platform

This is an enhanced AgriTech-style full-stack app with a distinct implementation and expanded modules.

## What’s Included
- Crop recommendation using a Kaggle-trained ML model.
- Plant disease detection from leaf images (Kaggle PlantVillage-style training).
- Fertilizer planner endpoint + UI module.
- Crop calendar API for seasonal planning.
- Model observability (health, model-info, retrain).
- Recent prediction logs endpoint.
- Node.js gateway + responsive dashboard frontend.

## Stack
- Frontend: HTML/CSS/JavaScript
- Gateway: Node.js + Express
- ML API: Python + Flask + scikit-learn

## Kaggle Datasets
- Crop: `atharvaingle/crop-recommendation-dataset`
- Disease: `emmarex/plantdisease`

Put datasets according to: `backend/data/README.md`.

## Run
1. Backend:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```
2. Gateway + frontend:
   ```bash
   npm install
   npm start
   ```
3. Open: `http://localhost:3000`

## Endpoints
- `GET /health`
- `GET /api/model-info`
- `GET /api/recent-predictions`
- `GET /api/crop-calendar`
- `POST /api/train-models`
- `POST /api/recommend-crop`
- `POST /api/fertilizer-plan`
- `POST /api/disease-detect`

## Notes
- If datasets are missing, the health endpoint reports precise boot errors.
- A Kaggle download helper exists in `backend/scripts/fetch_kaggle_data.py`.
