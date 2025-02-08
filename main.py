import sys
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QPushButton, QLineEdit, QHBoxLayout, QTabWidget, QTabBar)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon, QPalette, QColor

class CustomTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: #fff;
                padding: 5px 10px;
                border-radius: 4px;
                margin: 2px 8px 2px 2px;
                min-width: 28px;
                max-width: 28px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:pressed {
                background-color: #333;
            }
        """)
        
        self.setCornerWidget(self.new_tab_button, Qt.Corner.TopRightCorner)

class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        
        nav_container = QWidget()
        nav_container.setFixedHeight(44)
        nav_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #363636, stop:1 #2b2b2b);
                border-bottom: 1px solid #222;
            }
        """)
        
        self.url_bar = QLineEdit()
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: #fff;
                padding: 6px 10px;
                border-radius: 6px;
                border: 1px solid #222;
                margin: 6px;
                font-size: 13px;
                selection-background-color: #0066cc;
            }
            QLineEdit:focus {
                border: 1px solid #0066cc;
                background-color: #333;
            }
            QLineEdit:hover {
                background-color: #333;
            }
        """)
        self.url_bar.returnPressed.connect(self.load_url)
        
        button_style = """
            QPushButton {
                background-color: transparent;
                color: #fff;
                padding: 6px 12px;
                border-radius: 4px;
                margin: 6px 2px;
                min-width: 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QPushButton:disabled {
                color: #666;
            }
        """
        
        self.back_button = QPushButton("←")
        self.back_button.setStyleSheet(button_style)
        self.back_button.clicked.connect(self.browser.back)
        
        self.forward_button = QPushButton("→")
        self.forward_button.setStyleSheet(button_style)
        self.forward_button.clicked.connect(self.browser.forward)
        
        self.reload_button = QPushButton("⟳")
        self.reload_button.setStyleSheet(button_style)
        self.reload_button.clicked.connect(self.browser.reload)
        
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(8, 0, 8, 0)
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.reload_button)
        nav_layout.addWidget(self.url_bar)
        
        self.layout.addWidget(nav_container)
        self.layout.addWidget(self.browser)
        

        self.browser.urlChanged.connect(self.update_url)
        self.browser.loadStarted.connect(lambda: self.reload_button.setText("✕"))
        self.browser.loadFinished.connect(lambda: self.reload_button.setText("⟳"))
        
        self.browser.loadFinished.connect(self.update_navigation_state)
        
    def update_navigation_state(self):
        self.back_button.setEnabled(self.browser.history().canGoBack())
        self.forward_button.setEnabled(self.browser.history().canGoForward())

    def load_url(self):
        url = self.url_bar.text().strip()
        if re.match(r"^(http://|https://|www\.)", url):
            self.browser.setUrl(QUrl(url))
        elif re.match(r"\w+\.\w+", url):
            self.browser.setUrl(QUrl(f"https://{url}"))
        else:
            search_url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
            self.browser.setUrl(QUrl(search_url))

    def update_url(self, url):
        self.url_bar.setText(url.toString())

class CloseButtonTabBar(QTabBar):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QTabBar::close-button {
                image: none;
            }
            QTabBar::close-button::after {
                content: '×';
                color: #999;
                font-size: 14px;
                font-weight: bold;
                padding: 2px;
            }
            QTabBar::close-button:hover::after {
                color: white;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
            }
        """)

class StratusBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("path/to/your/icon.png"))

        self.setStyleSheet("""
            QMainWindow { 
                background: #2b2b2b;
            }
            QWidget { 
                background: #2b2b2b;
            }
            QTabWidget::pane {
                border: none;
                background: #2b2b2b;
            }
            QTabBar::tab {
                background: #333;
                color: #bbb;
                padding: 8px 30px 8px 12px;
                margin: 2px 1px 0px 1px;
                border-radius: 4px 4px 0 0;
                min-width: 100px;
                max-width: 200px;
            }
            QTabBar::tab:selected {
                background: #444;
                color: #fff;
            }
            QTabBar::tab:hover:!selected {
                background: #3a3a3a;
                color: #ddd;
            }
        """)
        
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = CustomTabWidget()
        self.tabs.setTabBar(CloseButtonTabBar())
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.new_tab_button.clicked.connect(self.add_new_tab)
        
        main_layout.addWidget(self.tabs)
        self.setCentralWidget(main_container)
        
        self.add_new_tab()

    def add_new_tab(self):
        new_tab = BrowserTab()
        index = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        new_tab.browser.titleChanged.connect(lambda title, tab=new_tab: self.update_tab_title(tab, title))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        
    def update_tab_title(self, tab, title):
        index = self.tabs.indexOf(tab)
        if index >= 0:
            self.tabs.setTabText(index, title[:20] + "..." if len(title) > 20 else title)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(43, 43, 43))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(dark_palette)
    
    window = StratusBrowser()
    window.show()
    sys.exit(app.exec())