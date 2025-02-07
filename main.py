import sys
import re
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon

class StratusBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Use the default window flags so that the native title bar (and its controls) appear.
        # (Do not set FramelessWindowHint.)
        self.setWindowTitle("")  # Remove text title if desired
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("path/to/your/icon.png"))

        # Optional: set a stylesheet for a dark background.
        self.setStyleSheet("""
            QMainWindow { 
                background: #2b2b2b;
            }
            QWidget { 
                background: #2b2b2b;
            }
        """)

        # Create the browser
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))

        # Create the URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setStyleSheet("background-color: #444; color: white; padding: 5px; border-radius: 5px;")
        self.url_bar.returnPressed.connect(self.load_url)

        # Create navigation buttons
        self.back_button = QPushButton("←")
        self.back_button.setStyleSheet("background-color: #444; color: white; padding: 5px; border-radius: 5px;")
        self.back_button.clicked.connect(self.browser.back)

        self.forward_button = QPushButton("→")
        self.forward_button.setStyleSheet("background-color: #444; color: white; padding: 5px; border-radius: 5px;")
        self.forward_button.clicked.connect(self.browser.forward)

        self.reload_button = QPushButton("⟳")
        self.reload_button.setStyleSheet("background-color: #444; color: white; padding: 5px; border-radius: 5px;")
        self.reload_button.clicked.connect(self.browser.reload)

        # Create the top navigation bar layout (this will be placed directly below the native title bar)
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.reload_button)
        nav_layout.addWidget(self.url_bar)

        # Create the main layout for the window
        central_layout = QVBoxLayout()
        central_layout.addLayout(nav_layout)
        central_layout.addWidget(self.browser)
        central_layout.setStretch(1, 1)  # Make the browser fill available space

        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def load_url(self):
        url = self.url_bar.text().strip()
        if re.match(r"^(http://|https://|www\.)", url):
            self.browser.setUrl(QUrl(url))
        elif re.match(r"\w+\.\w+", url):  # If it looks like a domain
            self.browser.setUrl(QUrl(f"https://{url}"))
        else:  # Otherwise, treat it as a search query
            search_url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
            self.browser.setUrl(QUrl(search_url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StratusBrowser()
    window.show()
    sys.exit(app.exec())