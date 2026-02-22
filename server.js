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
app.use(express.json());
app.use(express.static('public'));

app.get('/api/health', async (req, res) => {
  try {
    const { data } = await axios.get(`${FLASK_URL}/health`);
    res.json(data);
  } catch (error) {
    res.status(503).json({ error: 'Flask API is unreachable' });
  }
});

app.post('/api/recommend-crop', async (req, res) => {
  try {
    const response = await axios.post(`${FLASK_URL}/api/recommend-crop`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json(error.response?.data || { error: 'Internal server error' });
  }
});

app.post('/api/disease-detect', upload.single('leafImage'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'Please upload an image as leafImage' });
    }

    const form = new FormData();
    form.append('leafImage', req.file.buffer, req.file.originalname);

    const response = await axios.post(`${FLASK_URL}/api/disease-detect`, form, {
      headers: form.getHeaders(),
      maxBodyLength: Infinity,
    });

    return res.json(response.data);
  } catch (error) {
    return res.status(error.response?.status || 500).json(error.response?.data || { error: 'Internal server error' });
  }
});

app.listen(PORT, () => {
  console.log(`Node server running on http://localhost:${PORT}`);
});
