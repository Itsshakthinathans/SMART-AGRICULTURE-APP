const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const FLASK_URL = process.env.FLASK_URL || 'http://127.0.0.1:5000';
const HISTORY_PATH = path.join(__dirname, 'data', 'history.json');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

if (!fs.existsSync(HISTORY_PATH)) {
  fs.mkdirSync(path.dirname(HISTORY_PATH), { recursive: true });
  fs.writeFileSync(HISTORY_PATH, JSON.stringify({ recommendations: [], diseaseChecks: [] }, null, 2));
}

const readHistory = () => JSON.parse(fs.readFileSync(HISTORY_PATH, 'utf-8'));
const writeHistory = (history) => fs.writeFileSync(HISTORY_PATH, JSON.stringify(history, null, 2));

app.get('/api/history', (_req, res) => {
  res.json(readHistory());
});

app.post('/api/ml/crop', async (req, res) => {
  try {
    const response = await fetch(`${FLASK_URL}/predict/crop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    });

    if (!response.ok) {
      const error = await response.text();
      return res.status(response.status).json({ error });
    }

    const result = await response.json();
    const history = readHistory();
    history.recommendations.unshift({ ...req.body, ...result, createdAt: new Date().toISOString() });
    history.recommendations = history.recommendations.slice(0, 20);
    writeHistory(history);

    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Failed to connect to ML service', details: error.message });
  }
});

app.post('/api/ml/disease', async (req, res) => {
  try {
    const response = await fetch(`${FLASK_URL}/predict/disease`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    });

    if (!response.ok) {
      const error = await response.text();
      return res.status(response.status).json({ error });
    }

    const result = await response.json();
    const history = readHistory();
    history.diseaseChecks.unshift({ ...req.body, ...result, createdAt: new Date().toISOString() });
    history.diseaseChecks = history.diseaseChecks.slice(0, 20);
    writeHistory(history);

    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Failed to connect to ML service', details: error.message });
  }
});

app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Node server running on http://127.0.0.1:${PORT}`);
});
