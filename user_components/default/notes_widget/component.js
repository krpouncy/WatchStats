// Function to remove the notes module
function removeNotesModule(closeButton) {
    let gridItem = closeButton.closest(".grid-stack-item");

    if (!gridItem) {
        console.error("Grid item not found.");
        return;
    }

    let grid = GridStack.init();

    if (!grid) {
        console.error("GridStack instance not found.");
        return;
    }

    grid.removeWidget(gridItem);
}

// Function to save notes to local storage
function saveNotes() {
    const notesText = document.getElementById("notes-text").value;
    localStorage.setItem("savedNotes", notesText);
}

// Function to load saved notes from local storage
function loadNotes() {
    const savedNotes = localStorage.getItem("savedNotes");
    if (savedNotes) {
        document.getElementById("notes-text").value = savedNotes;
    }
}

// Attach event listeners after DOM loads
document.addEventListener("DOMContentLoaded", () => {
    loadNotes();
    document.getElementById("save-notes-btn").addEventListener("click", saveNotes);
});
