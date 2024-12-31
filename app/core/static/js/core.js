// core.js

// Global reference to chart
let winChart = null;

// Initialize Socket.IO
const socket = io();

socket.on('connect', () => {
  console.log("Connected to server!");
});
socket.on('connect_error', (error) => {
  console.error("Socket connection error:", error);
});


// Called on DOMContentLoaded or window.onload
function initCore() {
  checkInputType();   // Hide/Show input selection if already set
  initChart();        // Initialize chart
  loadScreenshots();  // Load existing screenshots
}

/* ==========================
   Chart Initialization
========================== */
function initChart() {
  const ctx = document.getElementById('win-chart');
  if (!ctx) {
    console.warn("No #win-chart element found. Skipping chart init.");
    return;
  }
  winChart = new Chart(ctx.getContext('2d'), {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Win Probability',
          data: [],
          backgroundColor: 'rgba(255, 140, 0, 0.4)',
          borderColor: 'rgba(255, 215, 0, 1)',
          borderWidth: 4,
        },
      ],
    },
    options: {
      plugins: {
        legend: {
          labels: { color: 'white' },
        },
        annotation: {
          annotations: {
            thresholdLine: {
              type: 'line',
              mode: 'horizontal',
              scaleID: 'y',
              value: 55, // If you have a threshold
              borderColor: 'red',
              borderWidth: 2,
              borderDash: [5, 5],
              label: {
                enabled: true,
                content: 'Threshold',
                position: 'start',
                backgroundColor: 'rgba(0,0,0,0.7)',
                color: 'white',
              },
            },
          },
        },
      },
      scales: {
        x: {
          ticks: { color: 'white' },
          title: { display: true, text: 'Events', color: 'white' },
        },
        y: {
          ticks: { color: 'white' },
          title: { display: true, text: 'Win Probability (%)', color: 'white' },
          min: 0,
          max: 100,
        },
      },
    },
  });
}

/* ==========================
   Socket.IO Events (Core)
========================== */
socket.on('update_chart', (data) => {
  console.log('Received update_chart event:', data);
  if (winChart && data && typeof data.win_probability !== 'undefined') {
    const probability = (data.win_probability * 100).toFixed(1);
    winChart.data.labels.push(`Event ${winChart.data.labels.length + 1}`);
    winChart.data.datasets[0].data.push(probability);
    winChart.update();
  }
});

socket.on('reset_chart', () => {
  console.log('Chart reset event received');
  if (winChart) {
    winChart.data.labels = [];
    winChart.data.datasets[0].data = [];
    winChart.update();
  }
});

socket.on('performance_update', (data) => {
  console.log('Received performance_update:', data);

  // Update the performance rows
  const { tank, damage, support } = data;
  updatePerformanceRow('tank-row', tank);
  updatePerformanceRow('damage-row', damage);
  updatePerformanceRow('support-row', support);

});

/**
 * Updates the background color and text for a role row
 * (Tank, Damage, Support).
 */
function updatePerformanceRow(rowId, performance) {
  const row = document.getElementById(rowId);
  if (!row) return;

  row.textContent = performance.text;
  switch (performance.status) {
    case 'good':
      row.className = 'p-2 my-2 text-center bg-success';
      break;
    case 'average':
      row.className = 'p-2 my-2 text-center bg-warning';
      break;
    case 'poor':
      row.className = 'p-2 my-2 text-center bg-danger';
      break;
    default:
      row.className = 'p-2 my-2 text-center bg-secondary';
      break;
  }
}

/* ==========================
   Screenshot Handling
========================== */
socket.on('screenshot_taken', () => {
  console.log('Screenshot taken, refreshing screenshots...');
  loadScreenshots();
});

function loadScreenshots() {
  fetch('/api/screenshots')
    .then((response) => response.json())
    .then((data) => {
      const screenshotRow = document.getElementById('screenshot-row');
      if (!screenshotRow) return;

      screenshotRow.innerHTML = ''; // Clear previous images
      let screenshots = data.screenshots || [];
      const MAX_IMAGES = 5;

      if (screenshots.length > MAX_IMAGES) {
        screenshots = screenshots.slice(-MAX_IMAGES);
      }

      if (screenshots.length === 0) {
        screenshotRow.innerHTML = '<div class="text-center text-light d-inline-block">No screenshots available</div>';
      } else {
        screenshots.forEach((screenshot) => {
          const img = document.createElement('img');
          img.src = `/screenshots/${screenshot}`;
          img.alt = 'Screenshot';
          img.style.height = '100px';
          img.style.width = 'auto';
          img.style.display = 'inline-block';
          img.style.margin = '0 5px';
          screenshotRow.appendChild(img);
        });
      }
    })
    .catch((error) => console.error('Error fetching screenshots:', error));
}

/* ==========================
   Overlay Show/Hide
========================== */
socket.on('show_loading_overlay', () => {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.style.display = 'block';
});

socket.on('hide_loading_overlay', () => {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.style.display = 'none';
});

/* ==========================
   Input Type Handling
========================== */
function setInput(inputType) {
  fetch('/set-input', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input_type: inputType }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(`Input type set to: ${data.input_type}`);
      const inputSection = document.getElementById('input-section');
      if (inputSection) inputSection.style.display = 'none';
    });
}

function checkInputType() {
  fetch('/get-input')
    .then((response) => response.json())
    .then((data) => {
      if (data.input_type) {
        console.log(`Using saved input type: ${data.input_type}`);
        const inputSection = document.getElementById('input-section');
        if (inputSection) inputSection.style.display = 'none';
      } else {
        const inputSection = document.getElementById('input-section');
        if (inputSection) inputSection.style.display = 'block';
      }
    });
}

document.getElementById('reset-input-btn')?.addEventListener('click', () => {
    const inputSection = document.getElementById('input-section');
    if (inputSection) inputSection.style.display = 'block';
});

/* ==========================
   End Game Handling
========================== */
document.getElementById('end-game-btn')?.addEventListener('click', () => {
  const outcomeDiv = document.getElementById('game-outcome-options');
  if (outcomeDiv) outcomeDiv.style.display = 'block';
});

function setGameOutcome(outcome) {
  // send alert that this is called

  fetch('/set-game-outcome', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ outcome: outcome }),
  })
    .then((resp) => resp.json())
    .then((data) => {
      console.log(`Game ended with outcome: ${outcome}`);
      alert(`Game outcome set: ${outcome}. Screenshots moved to folder: ${data.folder}`);
      // Reset the chart if needed
      return fetch('/reset-chart', { method: 'POST' });
    })
    .then((resp) => resp.json())
    .then(() => {
      console.log('Chart has been reset.');
      const outcomeDiv = document.getElementById('game-outcome-options');
      if (outcomeDiv) outcomeDiv.style.display = 'none';
      window.location.reload();
    })
    .catch((error) => console.error('Error setting game outcome:', error));
}

/*
  Ensure that "core.js" runs initCore() on page load,
  either by hooking into window.onload or DOMContentLoaded.
*/
window.addEventListener('DOMContentLoaded', initCore);
