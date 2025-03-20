function removeModule(closeButton) {
    let gridItem = closeButton.closest(".grid-stack-item"); // Find the GridStack container

    if (!gridItem) {
        console.error("Grid item not found.");
        return;
    }

    let grid = GridStack.init(); // Get the GridStack instance

    if (!grid) {
        console.error("GridStack instance not found.");
        return;
    }

    grid.removeWidget(gridItem); // Remove the module completely
}
