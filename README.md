# FarmIntel Pro (AgriTech-Style Full Stack)

A complete full-stack agriculture platform with:
- **Crop recommendation** (ML model trained on nutrient/weather data)
- **Plant disease detection** (ML model trained on symptom features)
- **Treatment solution suggestions**
- **Node.js API gateway + history persistence**
- **Flask ML microservice**
- **Responsive HTML/CSS/JS front-end dashboard**

## Tech stack
- Frontend: HTML, CSS, JavaScript
- Backend: Node.js (Express)
- ML service: Python Flask + scikit-learn

## Project structure
- `public/` UI files
- `server.js` Node backend + static serving + proxy to Flask
- `ml/app.py` Flask ML API
- `ml/train_models.py` model trainer
- `data/` training datasets and history store
- `models/` trained `.joblib` models

## Run locally
### 1) Install dependencies
```bash
npm install
python3 -m pip install -r ml/requirements.txt
```

### 2) Train models
```bash
python3 ml/train_models.py
```

### 3) Start ML service
```bash
python3 ml/app.py
```

### 4) Start Node app (new terminal)
```bash
npm start
```

Open `http://127.0.0.1:3000`.
