import data from './data/crops.js';

const rowContainer = document.getElementById('cropRows');
const summaryCards = document.getElementById('summaryCards');
const alerts = document.getElementById('alerts');
const irrigationTips = document.getElementById('irrigationTips');
const searchInput = document.getElementById('search');
const themeToggle = document.getElementById('themeToggle');

const summarize = (rows) => {
  const totalArea = rows.reduce((sum, item) => sum + item.area, 0);
  const avgYield = rows.reduce((sum, item) => sum + item.yield, 0) / rows.length;
  const avgMoisture = rows.reduce((sum, item) => sum + item.moisture, 0) / rows.length;
  return [
    { label: 'Active Fields', value: rows.length },
    { label: 'Total Area', value: `${totalArea.toFixed(0)} ha` },
    { label: 'Avg Yield', value: `${avgYield.toFixed(2)} t/ha` },
    { label: 'Avg Moisture', value: `${avgMoisture.toFixed(0)}%` }
  ];
};

const statusClass = { Healthy: 'good', Watch: 'warn', Risk: 'bad' };

function renderRows(rows) {
  rowContainer.innerHTML = rows
    .map(
      (crop) => `<tr>
        <td>${crop.name}</td>
        <td>${crop.region}</td>
        <td>${crop.area}</td>
        <td>${crop.yield}</td>
        <td>${crop.moisture}%</td>
        <td><span class="tag ${statusClass[crop.status]}">${crop.status}</span></td>
      </tr>`
    )
    .join('');

  summaryCards.innerHTML = summarize(rows)
    .map((m) => `<div class="metric"><small>${m.label}</small><strong>${m.value}</strong></div>`)
    .join('');

  alerts.innerHTML = rows
    .filter((item) => item.status !== 'Healthy')
    .map((item) => `<li>${item.name} in ${item.region}: ${item.note}</li>`)
    .join('') || '<li>No active alerts. Conditions are stable.</li>';

  irrigationTips.innerHTML = rows
    .map((item) => `<li>${item.region} • ${item.name}: ${item.moisture < 35 ? 'Increase irrigation cycle' : 'Maintain current cycle'}</li>`)
    .join('');
}

searchInput.addEventListener('input', (event) => {
  const query = event.target.value.toLowerCase();
  const filtered = data.filter(
    (item) => item.name.toLowerCase().includes(query) || item.region.toLowerCase().includes(query)
  );
  renderRows(filtered.length ? filtered : data);
});

themeToggle.addEventListener('click', () => {
  document.documentElement.classList.toggle('dark');
  themeToggle.textContent = document.documentElement.classList.contains('dark') ? '☀️' : '🌙';
});

renderRows(data);
