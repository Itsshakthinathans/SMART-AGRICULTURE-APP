# AgriTech Pro - Full Stack Smart Agriculture Platform

A complete full-stack project for:
1. **Crop recommendation** using ML trained from a Kaggle crop dataset.
2. **Plant disease detection** from leaf images using ML trained from Kaggle PlantVillage-style data.
3. **Actionable advisory** with fertilizer hints and disease treatment guidance.

Built with **Flask (Python ML API)** + **Node.js (gateway)** + **HTML/CSS/JS frontend**.

## Key Functionalities
- Kaggle-dataset-based model training (not just synthetic demo data).
- Model health + status API.
- Manual model retraining endpoint.
- Crop recommendation with top-5 confidence predictions.
- NPK-based fertilizer hint generation.
- Leaf-image disease classification with top matches.
- Clean modern UI with model status panel.
- Optional weather auto-fill by geolocation (Open-Meteo API in browser).

## Architecture

```
Browser (public/) -> Node.js Express (server.js) -> Flask ML API (backend/app.py)
```

## Kaggle Datasets Used
- Crop recommendation: `atharvaingle/crop-recommendation-dataset`
- Plant disease: `emmarex/plantdisease`

See setup instructions in `backend/data/README.md`.

## Project Structure

```
.
├── backend
│   ├── app.py
│   ├── requirements.txt
│   ├── data
│   │   └── README.md
│   ├── scripts
│   │   └── fetch_kaggle_data.py
│   └── ml
│       ├── crop_recommendation.py
│       ├── disease_detector.py
│       └── models/
├── public
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── package.json
└── server.js
```

## Setup

### 1) Python backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Put Kaggle datasets in place
Follow `backend/data/README.md`.

### 3) Run Flask
```bash
python app.py
```

### 4) Run Node server (new terminal)
```bash
npm install
npm start
```

Open: `http://localhost:3000`

## API Endpoints

- `GET /health`
- `GET /api/model-info`
- `POST /api/train-models`
- `POST /api/recommend-crop`
- `POST /api/disease-detect` (`multipart/form-data`, key `leafImage`)

## Notes
- If datasets are missing, `/health` and `/api/model-info` show boot errors with exact paths.
- Retraining can be triggered after placing new data.
