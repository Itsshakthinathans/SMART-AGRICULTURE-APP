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

const proxyGet = async (path, res) => {
  try {
    const r = await axios.get(`${FLASK_URL}${path}`);
    return res.status(r.status).json(r.data);
  } catch (error) {
    return res.status(error.response?.status || 500).json(error.response?.data || { error: 'Gateway error' });
  }
};

const proxyPost = async (path, body, res) => {
  try {
    const r = await axios.post(`${FLASK_URL}${path}`, body);
    return res.status(r.status).json(r.data);
  } catch (error) {
    return res.status(error.response?.status || 500).json(error.response?.data || { error: 'Gateway error' });
  }
};

app.get('/api/health', async (_, res) => proxyGet('/health', res));
app.get('/api/model-info', async (_, res) => proxyGet('/api/model-info', res));
app.get('/api/recent-predictions', async (_, res) => proxyGet('/api/recent-predictions', res));
app.get('/api/crop-calendar', async (_, res) => proxyGet('/api/crop-calendar', res));

app.post('/api/train-models', async (_, res) => proxyPost('/api/train-models', {}, res));
app.post('/api/recommend-crop', async (req, res) => proxyPost('/api/recommend-crop', req.body, res));
app.post('/api/fertilizer-plan', async (req, res) => proxyPost('/api/fertilizer-plan', req.body, res));

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

app.listen(PORT, () => console.log(`AgriTech Pro running at http://localhost:${PORT}`));
