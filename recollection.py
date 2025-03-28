import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# Adapt for PyInstaller runtime environment
if getattr(sys, 'frozen', False):  # If running as a PyInstaller-packaged executable
    base_path = sys._MEIPASS     # PyInstaller extraction directory
else:
    base_path = os.path.abspath(os.path.dirname(__file__))  # Project root directory

# Use index.html from the compiled frontend in the dist folder
html_path = os.path.join(base_path, "index.html")

print("Extraction directory:", base_path)
print("Expected path for index.html:", html_path)
print("Directory contents:", os.listdir(base_path))

# Create the PyQt application
app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout()
view = QWebEngineView()

# Set a custom User-Agent (browser version)
def set_custom_user_agent():
    # Example of a more recent User-Agent (for example, Chrome 100 on Windows)
    new_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
    
    # Get the current profile and set the new User-Agent
    profile = view.page().profile()
    profile.setHttpUserAgent(new_user_agent)

# Apply the custom User-Agent
set_custom_user_agent()

# Load the HTML file into the web view
view.setUrl(QUrl.fromLocalFile(html_path))

layout.addWidget(view)
window.setLayout(layout)
window.show()
app.exec()