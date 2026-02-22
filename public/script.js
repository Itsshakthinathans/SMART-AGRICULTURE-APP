const cropForm = document.getElementById('cropForm');
const diseaseForm = document.getElementById('diseaseForm');
const cropResult = document.getElementById('cropResult');
const diseaseResult = document.getElementById('diseaseResult');
const healthBox = document.getElementById('healthBox');
const modelInfoBox = document.getElementById('modelInfoBox');

const checkHealthBtn = document.getElementById('checkHealthBtn');
const retrainBtn = document.getElementById('retrainBtn');
const loadModelInfoBtn = document.getElementById('loadModelInfoBtn');
const weatherFillBtn = document.getElementById('weatherFillBtn');

const toJson = async (resp) => {
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error || data.message || 'Request failed');
  return data;
};

checkHealthBtn.addEventListener('click', async () => {
  try {
    const data = await toJson(await fetch('/api/health'));
    healthBox.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    healthBox.textContent = e.message;
  }
});

retrainBtn.addEventListener('click', async () => {
  retrainBtn.disabled = true;
  retrainBtn.textContent = 'Retraining...';
  try {
    const data = await toJson(await fetch('/api/train-models', { method: 'POST' }));
    healthBox.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    healthBox.textContent = e.message;
  } finally {
    retrainBtn.disabled = false;
    retrainBtn.textContent = 'Retrain Models';
  }
});

loadModelInfoBtn.addEventListener('click', async () => {
  try {
    const data = await toJson(await fetch('/api/model-info'));
    modelInfoBox.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    modelInfoBox.textContent = e.message;
  }
});

weatherFillBtn.addEventListener('click', () => {
  if (!navigator.geolocation) {
    alert('Geolocation is not supported in your browser.');
    return;
  }

  weatherFillBtn.disabled = true;
  weatherFillBtn.textContent = 'Fetching weather...';

  navigator.geolocation.getCurrentPosition(async (position) => {
    try {
      const { latitude, longitude } = position.coords;
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,precipitation`;
      const resp = await fetch(url);
      const data = await resp.json();
      const current = data.current;

      cropForm.temperature.value = current.temperature_2m ?? cropForm.temperature.value;
      cropForm.humidity.value = current.relative_humidity_2m ?? cropForm.humidity.value;
      cropForm.rainfall.value = current.precipitation ?? cropForm.rainfall.value;
    } catch (error) {
      alert('Unable to auto-fill weather right now.');
    } finally {
      weatherFillBtn.disabled = false;
      weatherFillBtn.textContent = 'Auto-fill Weather (Location)';
    }
  }, () => {
    weatherFillBtn.disabled = false;
    weatherFillBtn.textContent = 'Auto-fill Weather (Location)';
  });
});

cropForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(cropForm).entries());

  try {
    const data = await toJson(await fetch('/api/recommend-crop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }));

    const choices = data.top_choices
      .map(item => `<span class="badge">${item.crop}: ${item.confidence}%</span>`)
      .join('');
    const fert = data.fertilizer_hints.map(x => `<li>${x}</li>`).join('');

    cropResult.innerHTML = `
      <h3>Recommended: ${data.recommended_crop}</h3>
      <div>${choices}</div>
      <h4>Fertilizer Hints</h4>
      <ul>${fert}</ul>
    `;
  } catch (error) {
    cropResult.textContent = error.message;
  }
});

diseaseForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const input = document.getElementById('leafImage');
  if (!input.files.length) {
    diseaseResult.textContent = 'Please upload a leaf image.';
    return;
  }

  const formData = new FormData();
  formData.append('leafImage', input.files[0]);

  try {
    const data = await toJson(await fetch('/api/disease-detect', {
      method: 'POST',
      body: formData,
    }));

    const top = data.top_matches.map(t => `<span class="badge">${t.label}: ${t.confidence}%</span>`).join('');
    diseaseResult.innerHTML = `
      <h3>${data.disease} (${data.confidence}%)</h3>
      <p><strong>Diagnosis:</strong> ${data.diagnosis}</p>
      <p><strong>Solution:</strong> ${data.solution}</p>
      <div>${top}</div>
    `;
  } catch (error) {
    diseaseResult.textContent = error.message;
  }
});
