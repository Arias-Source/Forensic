from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys


class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Leaflet Map in PyQt6")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        # Create the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        layout = QVBoxLayout()

        # WebView to display the Leaflet map
        self.browser = QWebEngineView()
        self.load_map()

        layout.addWidget(self.browser)
        self.central_widget.setLayout(layout)

    def load_map(self):
        # Leaflet HTML map
        map_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Leaflet Map</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                #map { width: 100%; height: 100vh; }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([34.0548883,-118.2428237], 10); // Coordinates for San Francisco
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; OpenStreetMap contributors'
                }).addTo(map);

                L.marker([34.0548883,-118.2428237]).addTo(map)
                    .bindPopup('Hello from Los Angeles!')
                    .openPopup();
            </script>
        </body>
        </html>
        """

        # Load HTML directly into the WebEngineView
        self.browser.setHtml(map_html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapApp()
    window.show()
    sys.exit(app.exec())
