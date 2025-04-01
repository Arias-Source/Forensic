// Create a container for the summary
const container = document.createElement('div');
container.id = 'summary-container';
container.style.position = 'fixed';
container.style.top = '10px';
container.style.right = '10px';
container.style.zIndex = '10000';
container.style.backgroundColor = 'rgba(255, 255, 255, 0.7)'; // Semi-transparent white
container.style.border = '1px solid rgba(255, 255, 255, 0.5)'; // Semi-transparent border
container.style.borderRadius = '8px';
container.style.padding = '10px';
container.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.2)';
container.style.fontFamily = 'Arial, sans-serif';
container.style.width = '300px';
container.style.maxHeight = '400px';
container.style.overflowY = 'auto';

// Create a div for the summary
const summary = document.createElement('div');
summary.id = 'summary';
container.appendChild(summary);

// Append the container to the body
document.body.appendChild(container);

// Function to update the summary
function updateSummary(data) {
    summary.innerText = data;
}

// Function to extract meta data from the webpage
function extractMetaData() {
    const metaData = [];
    // Get the title of the page
    const title = document.querySelector('title') ? document.querySelector('title').innerText : 'No title';
    metaData.push(`Title: ${title}`);
    
    // Get the description of the page
    const description = document.querySelector('meta[name="description"]') ? 
                        document.querySelector('meta[name="description"]').getAttribute('content') : 'No description';
    metaData.push(`Description: ${description}`);
    
    // Get the keywords
    const keywords = document.querySelector('meta[name="keywords"]') ? 
                     document.querySelector('meta[name="keywords"]').getAttribute('content') : 'No keywords';
    metaData.push(`Keywords: ${keywords}`);
    
    // Extract Open Graph meta data if present (for social media previews)
    const ogTitle = document.querySelector('meta[property="og:title"]') ? 
                    document.querySelector('meta[property="og:title"]').getAttribute('content') : 'No Open Graph title';
    metaData.push(`OG Title: ${ogTitle}`);
    
    const ogDescription = document.querySelector('meta[property="og:description"]') ? 
                          document.querySelector('meta[property="og:description"]').getAttribute('content') : 'No Open Graph description';
    metaData.push(`OG Description: ${ogDescription}`);
    
    const ogImage = document.querySelector('meta[property="og:image"]') ? 
                    document.querySelector('meta[property="og:image"]').getAttribute('content') : 'No Open Graph image';
    metaData.push(`OG Image: ${ogImage}`);

    return metaData.join('\n');
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'updateSummary') {
        // Update summary with meta data
        updateSummary(extractMetaData());
    }
});

