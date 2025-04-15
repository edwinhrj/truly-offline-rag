import sys
import threading
import time
import socket
from PyQt6 import QtWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

def run_server():
    from backend.server import app
    app.run(host="127.0.0.1", port=8080, threaded=True, use_reloader=False)

def wait_for_port(host, port, timeout=30):
    """Wait until a TCP port is open or the timeout is reached."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(1)
    return False

def main():
    # Start the Flask server in a daemon thread.
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give the server an initial head start.
    time.sleep(2)
    
    # Retry mechanism to ensure the server is running.
    max_attempts = 3
    attempt = 0
    while attempt < max_attempts:
        if wait_for_port("127.0.0.1", 8080, timeout=30):
            print("Flask server is up.")
            break
        else:
            attempt += 1
            print(f"Attempt {attempt} failed; retrying...")
            time.sleep(2)  # Optional: Delay between retry attempts.
    if attempt == max_attempts:
        print("Error: Flask server did not start within the allowed attempts.")
        sys.exit(1)
    
    # Create the PyQt6 application.
    qt_app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    mainWindow.setWindowTitle("爱漫调企业私有大模型")
    mainWindow.resize(800, 800)

    # Create a QWebEngineView and point it to the Flask server.
    web_view = QWebEngineView()
    web_view.load(QUrl("http://127.0.0.1:8080"))
    mainWindow.setCentralWidget(web_view)
    mainWindow.show()
    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()
