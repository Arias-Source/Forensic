document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('toggle-summary');
    const ipInfoDiv = document.getElementById('ip-info');
    const summaryDiv = document.getElementById('summary');

    toggleButton.addEventListener('click', () => {
        // Check if the IP info is already displayed
        if (ipInfoDiv.style.display === 'none') {
            // Show loading message
            ipInfoDiv.innerText = 'Loading...';
            ipInfoDiv.style.display = 'block'; // Show the IP info div

            chrome.storage.local.get('summary', (data) => {
                if (data.summary) {
                    // Update the summary with the stored data
                    summaryDiv.innerText = data.summary;
                } else {
                    summaryDiv.innerText = 'No summary available. Please visit a website first.';
                }
            });
        } else {
            // Hide the IP info
            ipInfoDiv.style.display = 'none';
        }
    });
});

