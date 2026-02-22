const express = require('express');
const cors = require('cors');
const multer = require('multer');
const axios = require('axios');
const FormData = require('form-data');

const app = express();
const upload = multer({ storage: multer.memoryStorage() });
const PORT = process.env.PORT || 3000;
const FLASK_URL = process.env.FLASK_URL || 'http://127.0.0.1:5000';

app.use(cors());
app.use(express.json({ limit: '4mb' }));
app.use(express.static('public'));

const proxyJsonPost = async (path, body, res) => {
  try {
    const r = await axios.post(`${FLASK_URL}${path}`, body);
    return res.status(r.status).json(r.data);
  } catch (error) {
    return res.status(error.response?.status || 500).json(error.response?.data || { error: 'Gateway error' });
  }
};

app.get('/api/health', async (_, res) => {
  try {
    const r = await axios.get(`${FLASK_URL}/health`);
    res.json(r.data);
  } catch {
    res.status(503).json({ error: 'Flask backend unreachable' });
  }
});

app.get('/api/model-info', async (_, res) => {
  try {
    const r = await axios.get(`${FLASK_URL}/api/model-info`);
    res.json(r.data);
  } catch (error) {
    res.status(error.response?.status || 500).json(error.response?.data || { error: 'Gateway error' });
  }
});

app.post('/api/train-models', async (_, res) => {
  try {
    const r = await axios.post(`${FLASK_URL}/api/train-models`);
    res.status(r.status).json(r.data);
  } catch (error) {
    res.status(error.response?.status || 500).json(error.response?.data || { error: 'Gateway error' });
  }
});

app.post('/api/recommend-crop', async (req, res) => proxyJsonPost('/api/recommend-crop', req.body, res));

app.post('/api/disease-detect', upload.single('leafImage'), async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: 'Upload image as leafImage' });

    const form = new FormData();
    form.append('leafImage', req.file.buffer, req.file.originalname);

    const r = await axios.post(`${FLASK_URL}/api/disease-detect`, form, {
      headers: form.getHeaders(),
      maxBodyLength: Infinity,
    });

    return res.status(r.status).json(r.data);
  } catch (error) {
    return res.status(error.response?.status || 500).json(error.response?.data || { error: 'Gateway error' });
  }
});

app.listen(PORT, () => console.log(`Smart Agriculture app running: http://localhost:${PORT}`));
