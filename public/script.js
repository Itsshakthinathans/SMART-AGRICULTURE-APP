const cropForm = document.getElementById('cropForm');
const cropResult = document.getElementById('cropResult');
const diseaseForm = document.getElementById('diseaseForm');
const diseaseResult = document.getElementById('diseaseResult');

cropForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(cropForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch('/api/recommend-crop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Failed to fetch recommendation');

    cropResult.innerHTML = `
      <h3>Recommended Crop: ${data.recommended_crop}</h3>
      <ul>${data.top_choices.map((item) => `<li>${item.crop}: ${item.confidence}%</li>`).join('')}</ul>
    `;
  } catch (error) {
    cropResult.textContent = error.message;
  }
});

diseaseForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById('leafImage');
  if (!fileInput.files.length) {
    diseaseResult.textContent = 'Please choose an image first.';
    return;
  }

  const formData = new FormData();
  formData.append('leafImage', fileInput.files[0]);

  try {
    const response = await fetch('/api/disease-detect', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Failed to detect disease');

    diseaseResult.innerHTML = `
      <h3>Disease: ${data.disease} (${data.confidence}%)</h3>
      <p><strong>Solution:</strong> ${data.solution}</p>
      <p><strong>Prevention:</strong> ${data.prevention}</p>
      <p><em>${data.note}</em></p>
    `;
  } catch (error) {
    diseaseResult.textContent = error.message;
  }
});
