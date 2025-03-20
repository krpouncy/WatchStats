document.addEventListener("DOMContentLoaded", function () {
    function fetchLatestScreenshot() {
        fetch("/api/screenshots")
            .then((response) => response.json())
            .then((data) => {
                const screenshots = data.screenshots || [];
                const imgElement = document.getElementById("latest-screenshot");
                const messageElement = document.getElementById("no-screenshot-message");

                if (screenshots.length > 0) {
                    const latestScreenshot = screenshots[screenshots.length - 1]; // Get latest screenshot
                    imgElement.src = `/screenshots/${latestScreenshot}`;
                    imgElement.style.display = "block";
                    messageElement.style.display = "none"; // Hide message
                } else {
                    imgElement.style.display = "none";
                    messageElement.style.display = "block"; // Show message
                }
            })
            .catch((error) => console.error("Error fetching latest screenshot:", error));
    }

    // Initial fetch
    fetchLatestScreenshot();

    // Listen for new screenshot events
    socket.on("screenshot_taken", () => {
        console.log("New screenshot detected, updating...");
        fetchLatestScreenshot();
    });
});
