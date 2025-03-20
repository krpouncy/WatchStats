// core.js
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
    loadScreenshots();  // Load existing screenshots
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
    console.log('Received show_loading_overlay event');
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'block';
});

socket.on('hide_loading_overlay', () => {
    console.log('Received hide_loading_overlay event');
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
});

/* ==========================
   Input Type Handling
========================== */
function setInput(inputType) {
    fetch('/set-input', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({input_type: inputType}),
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
    // move to the div location
    window.scrollTo(0, 0);
});

/* ==========================
   End Game Handling
========================== */
document.getElementById('end-game-btn')?.addEventListener('click', () => {
    const outcomeDiv = document.getElementById('game-outcome-options');
    if (outcomeDiv) outcomeDiv.style.display = 'block';
});

function setGameOutcome(outcome) {
    fetch('/set-game-outcome', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({outcome: outcome}),
    })
        .then((resp) => resp.json())
        .then((data) => {
            console.log(`Game ended with outcome: ${outcome}`);
            alert(`Game outcome set: ${outcome}. Screenshots moved to folder: ${data.folder}`);

            // Hide the outcome options
            const outcomeDiv = document.getElementById('game-outcome-options');
            if (outcomeDiv) outcomeDiv.style.display = 'none';
        })
        .catch((error) => console.error('Error setting game outcome:', error));
}

function saveOrder(location, order) {
    fetch('/save_order', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({location, order}),
    });
}

window.addEventListener('DOMContentLoaded', function () {
    /* Load initial data */
    fetch('/load');
    initCore();
});

// Function to update the displayed delay value
function updateDelayValue(val) {
    document.getElementById('capture-delay-value').innerText = val + ' seconds';
    // Send the new value to the server
    fetch('/set-screenshot-delay', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ screenshot_delay: val })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Screenshot delay updated:', data.screenshot_delay);
    })
    .catch(error => console.error('Error updating screenshot delay:', error));
}

// Add event listener to update the value when the slider is moved
var slider = document.getElementById('capture-delay-slider');
slider.addEventListener('input', function() {
    updateDelayValue(this.value);
});

// Toggle the display of the capture delay section
function toggleCaptureDelay() {
    var captureDelaySection = document.getElementById("capture-delay-settings");
    var arrow = document.getElementById("toggle-capture-delay");
    if (captureDelaySection.style.display === "none") {
        captureDelaySection.style.display = "block";
        arrow.innerHTML = "&#x25BC;"; // downward arrow
    } else {
        captureDelaySection.style.display = "none";
        arrow.innerHTML = "&#x25B2;"; // upward arrow
    }
}

// Set the initial value when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Fetch the current screenshot delay from the server and update the slider
    fetch('/get-screenshot-delay')
        .then(response => response.json())
        .then(data => {
            const slider = document.getElementById('capture-delay-slider');
            if (slider) {
                // Assuming the delay is in milliseconds, you might want to
                // convert it if your slider is in seconds. Here, we assume they match.
                slider.value = data.screenshot_delay;
                updateDelayValue(slider.value);
            }
        })
        .catch(error => console.error('Error fetching screenshot delay:', error));
});