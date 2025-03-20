let wins = 0;
let losses = 0;
let draws = 0;

/**
 * Loads stored values from localStorage.
 */
function loadSessionStats() {
    wins = parseInt(localStorage.getItem('wins')) || 0;
    losses = parseInt(localStorage.getItem('losses')) || 0;
    draws = parseInt(localStorage.getItem('draws')) || 0;
    updateSessionTracker();
}

/**
 * Saves session stats to localStorage.
 */
function saveSessionStats() {
    localStorage.setItem('wins', wins);
    localStorage.setItem('losses', losses);
    localStorage.setItem('draws', draws);
}

/**
 * Resets session stats and updates the display.
 */
function resetSessionStats() {
    wins = 0;
    losses = 0;
    draws = 0;
    localStorage.removeItem('wins');
    localStorage.removeItem('losses');
    localStorage.removeItem('draws');
    updateSessionTracker();
}

/**
 * Updates the session tracker display.
 */
function updateSessionTracker() {
    const winsElem = document.getElementById('wins-count');
    const lossesElem = document.getElementById('losses-count');
    const drawsElem = document.getElementById('draws-count');
    const winRateElem = document.getElementById('win-rate');

    if (!winsElem || !lossesElem || !drawsElem || !winRateElem) {
        console.error('Session tracker elements not found.');
        return;
    }

    // Update stats
    winsElem.textContent = wins;
    lossesElem.textContent = losses;
    drawsElem.textContent = draws;

    // Calculate Win %
    const totalGames = wins + losses + draws;
    const winPercentage = totalGames > 0 ? Math.round((wins / totalGames) * 100) : 0;
    winRateElem.textContent = winPercentage + '%';

    // Save stats
    saveSessionStats();
}

// Load stored values when the page loads
document.addEventListener('DOMContentLoaded', loadSessionStats);

// Listen for game outcome event
socket.on('game_end', (outcome) => {
    if (outcome === "win") {
        wins += 1;
    } else if (outcome === "loss") {
        losses += 1;
    } else if (outcome === "draw") {
        draws += 1;
    }
    updateSessionTracker();
});
