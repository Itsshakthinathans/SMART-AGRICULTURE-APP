const cropForm = document.getElementById('cropForm');
const diseaseForm = document.getElementById('diseaseForm');
const fertForm = document.getElementById('fertForm');

const cropResult = document.getElementById('cropResult');
const diseaseResult = document.getElementById('diseaseResult');
const fertResult = document.getElementById('fertResult');

const healthBox = document.getElementById('healthBox');
const modelInfoBox = document.getElementById('modelInfoBox');
const calendarBox = document.getElementById('calendarBox');
const recentBox = document.getElementById('recentBox');

const checkHealthBtn = document.getElementById('checkHealthBtn');
const retrainBtn = document.getElementById('retrainBtn');
const loadModelInfoBtn = document.getElementById('loadModelInfoBtn');
const loadRecentBtn = document.getElementById('loadRecentBtn');
const loadCalendarBtn = document.getElementById('loadCalendarBtn');
const weatherFillBtn = document.getElementById('weatherFillBtn');

const toJson = async (resp) => {
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error || data.message || 'Request failed');
  return data;
};

const badges = (arr, key1, key2) => (arr || []).map(x => `<span class="badge">${x[key1]}: ${x[key2]}%</span>`).join('');

checkHealthBtn.addEventListener('click', async () => {
  try { healthBox.textContent = JSON.stringify(await toJson(await fetch('/api/health')), null, 2); }
  catch (e) { healthBox.textContent = e.message; }
});

retrainBtn.addEventListener('click', async () => {
  retrainBtn.disabled = true;
  try { healthBox.textContent = JSON.stringify(await toJson(await fetch('/api/train-models', { method: 'POST' })), null, 2); }
  catch (e) { healthBox.textContent = e.message; }
  retrainBtn.disabled = false;
});

loadModelInfoBtn.addEventListener('click', async () => {
  try { modelInfoBox.textContent = JSON.stringify(await toJson(await fetch('/api/model-info')), null, 2); }
  catch (e) { modelInfoBox.textContent = e.message; }
});

loadRecentBtn.addEventListener('click', async () => {
  try { recentBox.textContent = JSON.stringify(await toJson(await fetch('/api/recent-predictions')), null, 2); }
  catch (e) { recentBox.textContent = e.message; }
});

loadCalendarBtn.addEventListener('click', async () => {
  try { calendarBox.textContent = JSON.stringify(await toJson(await fetch('/api/crop-calendar')), null, 2); }
  catch (e) { calendarBox.textContent = e.message; }
});

weatherFillBtn.addEventListener('click', () => {
  if (!navigator.geolocation) return alert('Geolocation not supported');
  navigator.geolocation.getCurrentPosition(async ({ coords }) => {
    try {
      const resp = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${coords.latitude}&longitude=${coords.longitude}&current=temperature_2m,relative_humidity_2m,precipitation`);
      const data = await resp.json();
      cropForm.temperature.value = data.current?.temperature_2m ?? '';
      cropForm.humidity.value = data.current?.relative_humidity_2m ?? '';
      cropForm.rainfall.value = data.current?.precipitation ?? '';
    } catch {
      alert('Weather fetch failed');
    }
  });
});

cropForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(cropForm).entries());
  try {
    const data = await toJson(await fetch('/api/recommend-crop', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
    }));

    const stagePlan = data.fertilizer_plan.stage_plan.map(s => `<li><b>${s.stage}</b>: ${s.recommendation}</li>`).join('');
    cropResult.innerHTML = `
      <h3>Recommended Crop: ${data.recommended_crop}</h3>
      <div>${badges(data.top_choices, 'crop', 'confidence')}</div>
      <h4>Hints</h4>
      <ul>${data.fertilizer_hints.map(x => `<li>${x}</li>`).join('')}</ul>
      <h4>Fertilizer Stage Plan</h4>
      <ul>${stagePlan}</ul>
    `;
  } catch (e2) {
    cropResult.textContent = e2.message;
  }
});

diseaseForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const file = document.getElementById('leafImage').files[0];
  if (!file) return;

  const form = new FormData();
  form.append('leafImage', file);

  try {
    const data = await toJson(await fetch('/api/disease-detect', { method: 'POST', body: form }));
    diseaseResult.innerHTML = `
      <h3>${data.disease} (${data.confidence}%)</h3>
      <p><b>Diagnosis:</b> ${data.diagnosis}</p>
      <p><b>Solution:</b> ${data.solution}</p>
      <div>${badges(data.top_matches, 'label', 'confidence')}</div>
    `;
  } catch (e2) {
    diseaseResult.textContent = e2.message;
  }
});

fertForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(fertForm).entries());
  try {
    const data = await toJson(await fetch('/api/fertilizer-plan', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
    }));
    fertResult.innerHTML = `
      <h3>Plan for ${data.crop}</h3>
      <p>Target NPK: N=${data.target_npk.N}, P=${data.target_npk.P}, K=${data.target_npk.K}</p>
      <p>Gap: N=${data.estimated_gap.N}, P=${data.estimated_gap.P}, K=${data.estimated_gap.K}</p>
      <ul>${data.stage_plan.map(s => `<li><b>${s.stage}</b>: ${s.recommendation}</li>`).join('')}</ul>
    `;
  } catch (e2) {
    fertResult.textContent = e2.message;
  }
});
