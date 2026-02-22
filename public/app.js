const cropForm = document.getElementById('cropForm');
const diseaseForm = document.getElementById('diseaseForm');
const cropResult = document.getElementById('cropResult');
const diseaseResult = document.getElementById('diseaseResult');
const cropHistory = document.getElementById('cropHistory');
const diseaseHistory = document.getElementById('diseaseHistory');

const toPayload = (form, numeric = true) => Object.fromEntries(new FormData(form).entries());

function renderHistory(history) {
  cropHistory.innerHTML = history.recommendations
    .map((r) => `<li><strong>${r.recommended_crop}</strong> · NPK(${r.N}/${r.P}/${r.K})</li>`)
    .join('') || '<li>No crop predictions yet.</li>';

  diseaseHistory.innerHTML = history.diseaseChecks
    .map((d) => `<li><strong>${d.disease}</strong> · ${new Date(d.createdAt).toLocaleString()}</li>`)
    .join('') || '<li>No disease checks yet.</li>';
}

async function loadHistory() {
  const res = await fetch('/api/history');
  renderHistory(await res.json());
}

cropForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = toPayload(cropForm);
  Object.keys(payload).forEach((k) => payload[k] = Number(payload[k]));

  const res = await fetch('/api/ml/crop', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  cropResult.textContent = data.recommended_crop
    ? `Recommended Crop: ${data.recommended_crop}`
    : `Error: ${data.error || 'Unable to predict crop.'}`;

  loadHistory();
});

diseaseForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = toPayload(diseaseForm);
  Object.keys(payload).forEach((k) => payload[k] = Number(payload[k]));

  const res = await fetch('/api/ml/disease', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  diseaseResult.innerHTML = data.disease
    ? `<strong>Disease:</strong> ${data.disease}<br><strong>Suggested Solution:</strong> ${data.solution}`
    : `Error: ${data.error || 'Unable to detect disease.'}`;

  loadHistory();
});

loadHistory();
