# Smart Agriculture App (Full Stack)

This project provides:
- **Crop Recommendation** using an ML classifier (Python + scikit-learn).
- **Plant Disease Detection + Solution** using an image-analysis ML heuristic (Python + Flask).
- **Modern Web UI** with HTML/CSS/JavaScript.
- **Node.js API Gateway** that serves frontend and proxies requests to Flask ML backend.

## Tech Stack
- Frontend: HTML, CSS, JavaScript
- Gateway/API + static hosting: Node.js, Express, Multer
- ML backend: Python, Flask, scikit-learn, NumPy, Pillow

## Project Structure

```
.
├── backend
│   ├── app.py
│   ├── requirements.txt
│   └── ml
│       ├── crop_recommendation.py
│       └── disease_detector.py
├── public
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── package.json
└── server.js
```

## Run Locally

### 1) Start Flask backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Flask runs on `http://localhost:5000`.

### 2) Start Node frontend + proxy server
Open another terminal:
```bash
npm install
npm start
```
Node runs on `http://localhost:3000`.

## API Endpoints

### Crop recommendation
`POST /api/recommend-crop`

Body:
```json
{
  "nitrogen": 90,
  "phosphorus": 42,
  "potassium": 43,
  "temperature": 20,
  "humidity": 82,
  "ph": 6.5,
  "rainfall": 220
}
```

### Disease detection
`POST /api/disease-detect` with `multipart/form-data`
- key: `leafImage`
- value: image file

## Notes
- Crop model is trained on compact agronomy-oriented sample data for demonstration.
- Disease detection uses color-pattern ML-style heuristics and returns treatment + prevention guidance.
