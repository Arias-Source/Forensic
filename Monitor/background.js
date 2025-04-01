// Fetch the user's public IP address using ipify API
async function fetchUserIP() {
    try {
        const response = await fetch('https://api.ipify.org?format=json');
        if (!response.ok) throw new Error('Failed to fetch user IP');
        const data = await response.json();
        return data.ip;
    } catch (error) {
        console.error('Error fetching user IP:', error);
        return 'Unable to fetch user IP';
    }
}

// Ping the website to measure response time (no IP address retrieval here)
async function pingWebsite(url) {
    const start = performance.now();
    try {
        const response = await fetch(url, { method: 'HEAD', mode: 'no-cors' });
        const end = performance.now();
        return (end - start).toFixed(2); // Return ping in milliseconds
    } catch (error) {
        console.error('Error pinging website:', error);
        return 'Ping failed';
    }
}

// Listen for webRequest completion
chrome.webRequest.onCompleted.addListener(async (details) => {
    try {
        // Fetch the user's IP address
        const userIP = await fetchUserIP();
        // Ping the website and measure the response time
        const ping = await pingWebsite(details.url);

        // Send a message to content.js to extract meta data
        chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
            const tabId = tabs[0].id;
            chrome.scripting.executeScript({
                target: { tabId: tabId },
                func: extractMetaData
            }, (result) => {
                const metaData = result[0].result;
                
                // Construct the summary of results (user IP, ping, and meta data)
                const summary = `User IP: ${userIP}\nPing: ${ping} ms\nMeta Data:\n${metaData}`;
                
                console.log('Summary:', summary); // Debugging line to log the summary

                // Store the results in local storage for use in the popup
                chrome.storage.local.set({ summary: summary }, () => {
                    console.log('Summary stored in local storage'); // Debugging line
                });
            });
        });
    } catch (error) {
        console.error('Error during webRequest listener:', error);
    }
}, { urls: ["<all_urls>"] });

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

