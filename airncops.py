#webpage that shows live air traffic data from ADSB Exchange. 
#You got this slick overlay that says "listen to emergencies around the area and ATC live..." 
#and when you click it, a dropdown pops up with links to live air traffic control and emergency feeds. 
#It’s all styled nice and smooth, 
#so it looks good while you’re vibing. Just run it, hit up http://localhost:8000,

import http.server
import socketserver

# Define the port you want to use
PORT = 8000

# HTML content (obfuscated)
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADSB Exchange Globe</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden; /* Prevent scrolling */
            position: relative; /* For positioning the overlay */
            font-family: Arial, sans-serif; /* Font style */
        }
        iframe {
            width: 100vw; /* Full width */
            height: 100vh; /* Full height */
            border: none; /* Remove border */
        }
        .overlay {
            position: absolute;
            top: 20px; /* Position from the top */
            left: 20px; /* Position from the left */
            background-color: #000000; /* Blue background */
            color: white; /* Text color */
            padding: 15px 20px; /* Padding for the overlay */
            border-radius: 5px;
            cursor: pointer;
            z-index: 10; /* Ensure it is above the iframe */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3); /* Shadow effect */
            transition: background-color 0.3s; /* Transition effect */
        }
        .overlay:hover {
            background-color: #808080; /* Darker blue on hover */
        }
        .dropdown {
            display: none; /* Hidden by default */
            position: absolute;
            top: 70px; /* Position below the overlay */
            left: 20px; /* Align with the overlay */
            background-color: #343a40; /* Dark background */
            border-radius: 5px;
            padding: 10px;
            z-index: 10; /* Ensure it is above the iframe */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3); /* Shadow effect */
            animation: slideDown 0.3s ease; /* Animation for dropdown */
        }
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .dropdown a {
            color: #ffffff; /* Link color */
            text-decoration: none; /* Remove underline */
            display: block; /* Make links block elements */
            padding: 10px; /* Padding for links */
            transition: background-color 0.3s; /* Transition effect */
        }
        .dropdown a:hover {
            background-color: #495057; /* Darker background on hover */
            border-radius: 3px; /* Rounded corners on hover */
        }
    </style>
</head>
<body>
    <iframe src="https://globe.adsbexchange.com/"></iframe>

    <div class="overlay" onclick="toggleDropdown()">
        listen to emergencys around the area and ATC live ...
    </div>

    <div class="dropdown" id="dropdown">
        <a href="https://www.liveatc.net" target="">Live Air traffic control</a>
        <a href="https://www.broadcastify.com/listen/" target="">Emergency response</a>

    </div>

    <script>
        function toggleDropdown() {
            const dropdown = document.getElementById('dropdown');
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        }
    </script>
</body>
</html>
"""

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve the obfuscated HTML content
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

# Create the server
with socketserver.TCPServer(("0.0.0.0", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
