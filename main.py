import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# Fix for macOS - ensure sys.argv has at least one argument
if not sys.argv:
    sys.argv = [""]

def start_vue_frontend():
    command1 = subprocess.Popen(['npm', 'install', 'axios'], cwd='./frontend') # axios needed to send http requests to backend
    command1#.wait()
    command2 = subprocess.Popen(['npm', 'install'], cwd='./frontend')
    command2#.wait()
    command3 = subprocess.Popen(['npm', 'run', 'dev'], cwd='./frontend')
    command3#.wait()
    print('done starting frontend')

def start_backend():
    subprocess.Popen(['uvicorn', 'main:app', '--reload'], cwd='./backend')
    print('done starting backend')

app = QApplication(sys.argv)  # Pass sys.argv to QApplication
window = QWidget()
layout = QVBoxLayout()
view = QWebEngineView()
layout.addWidget(view)
start_backend()
start_vue_frontend()
view.setUrl(QUrl("http://localhost:5173/"))
window.setLayout(layout)
window.show()
app.exec()