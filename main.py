import sys
import re
import urllib.parse
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QPushButton, QLineEdit, QHBoxLayout, QTabWidget, QTabBar)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineHistory
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon, QPalette, QColor, QKeySequence, QShortcut

class HistoryManager:
    def __init__(self):
        self.history_items = []

    def add_item(self, url, title):
        if not title:
            title = url
        self.history_items.append({
            'url': url,
            'title': title,
            'timestamp': datetime.now()
        })

    def get_items(self):
        return sorted(self.history_items, key=lambda x: x['timestamp'], reverse=True)

    def get_display_text(self, url, title):
        if "google.com/search" in url:
            query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('q', [''])[0]
            return f"Searched for: {query}" if query else "Google Search"
        
        if any(engine in url for engine in ["bing.com/search", "yahoo.com/search", "duckduckgo.com"]):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('q', [''])[0]
            return f"Searched for: {query}" if query else "Web Search"
        
        if "youtube.com/watch" in url:
            return f"Watched: {title}"
        
        if title == url:
            domain = urllib.parse.urlparse(url).netloc
            domain = re.sub(r'^www\.', '', domain)  # Remove www.
            return f"Visited {domain}"
        
        return title
    
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
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
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
        self.url_bar.clear()
        
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
        self.browser.urlChanged.connect(self.record_history)
        self.browser.loadStarted.connect(lambda: self.reload_button.setText("✕"))
        self.browser.loadFinished.connect(lambda: self.reload_button.setText("⟳"))
        self.browser.loadFinished.connect(self.update_navigation_state)
        
        # Add tab-specific shortcuts
        self.setup_shortcuts()
        
    def setup_shortcuts(self):
        # Reload page
        reload_shortcut = QShortcut(QKeySequence("F5"), self)
        reload_shortcut.activated.connect(self.browser.reload)
        
        # Focus URL bar
        focus_url_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        focus_url_shortcut.activated.connect(self.url_bar.selectAll)
        focus_url_shortcut.activated.connect(self.url_bar.setFocus)
        
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
        if url.toString() == "https://www.google.com/":
            self.url_bar.clear()
        else:
            self.url_bar.setText(url.toString())

    def record_history(self, url):
        if url.isValid() and not url.toString().startswith("data:"):
            self.history_manager.add_item(url.toString(), self.browser.title())

class HistoryTab(BrowserTab):
    def __init__(self, browser_window, history_manager, parent=None):
        super().__init__(history_manager, parent)
        self.browser_window = browser_window
        self.display_history()

    def get_day_header(self, date):
        today = datetime.now().date()
        diff = (today - date.date()).days

        if diff == 0:
            return "Today"
        elif diff == 1:
            return "Yesterday"
        elif diff < 7:
            return date.strftime('%A')
        elif diff < 30:
            return "Last Month"
        else:
            return date.strftime('%B %Y')

    def display_history(self):
        history_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    background-color: #2b2b2b;
                    color: #ffffff;
                    margin: 0;
                    padding: 20px;
                }
                h1, h2 {
                    color: #ffffff;
                }
                h1 {
                    border-bottom: 1px solid #444;
                    padding-bottom: 10px;
                }
                h2 {
                    font-size: 1.2em;
                    margin-top: 20px;
                    color: #aaa;
                    padding-bottom: 5px;
                    border-bottom: 1px solid #444;
                }
                .history-item {
                    padding: 12px;
                    margin: 5px 0;
                    border-radius: 4px;
                    background-color: #333;
                    transition: background-color 0.2s;
                    display: flex;
                    align-items: center;
                }
                .history-item:hover {
                    background-color: #444;
                }
                .history-item a {
                    color: #4a9eff;
                    text-decoration: none;
                    flex-grow: 1;
                }
                .history-item a:hover {
                    text-decoration: underline;
                }
                .history-item .icon {
                    margin-right: 12px;
                    color: #888;
                    font-size: 1.1em;
                }
                .search-query {
                    color: #4a9eff;
                }
            </style>
        </head>
        <body>
            <h1>Browsing History</h1>
        """
        
        current_day = None
        for item in self.history_manager.get_items():
            day = self.get_day_header(item['timestamp'])
            
            if day != current_day:
                if current_day is not None:
                    history_html += "</div>"
                current_day = day
                history_html += f"<h2>{day}</h2><div class='day-group'>"
            
            display_text = self.history_manager.get_display_text(item['url'], item['title'])
            icon = "🔍" if "Searched for:" in display_text else "🌐"
            
            history_html += f"""
            <div class="history-item">
                <span class="icon">{icon}</span>
                <a href="{item['url']}">{display_text}</a>
            </div>
            """
        
        if current_day is not None:
            history_html += "</div>"
        
        history_html += """
        </body>
        </html>
        """
        
        self.browser.setHtml(history_html)

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
        self.history_manager = HistoryManager()

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
        self.setup_shortcuts()

    def setup_shortcuts(self):
        # New tab
        new_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        new_tab_shortcut.activated.connect(self.add_new_tab)
        
        # Close tab
        close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_tab_shortcut.activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        
        # Next tab
        if sys.platform == 'darwin':
            next_tab_shortcut = QShortcut(QKeySequence("Meta+Shift+]"), self)
        else:
            next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+]"), self)
        next_tab_shortcut.activated.connect(self.next_tab)
        
        # Previous tab
        if sys.platform == 'darwin':
            prev_tab_shortcut = QShortcut(QKeySequence("Meta+Shift+["), self)
        else:
            prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+["), self)
        prev_tab_shortcut.activated.connect(self.prev_tab)
        
        # Reload page (global)
        reload_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        reload_shortcut.activated.connect(self.reload_current_tab)

                # Add history shortcut
        if sys.platform == 'darwin':
            history_shortcut = QShortcut(QKeySequence("Meta+Shift+H"), self)
        else:
            history_shortcut = QShortcut(QKeySequence("Ctrl+Shift+H"), self)
        history_shortcut.activated.connect(self.show_history)

    def show_history(self):
        history_tab = HistoryTab(self, self.history_manager)
        index = self.tabs.addTab(history_tab, "History")
        self.tabs.setCurrentIndex(index)

    def next_tab(self):
        current = self.tabs.currentIndex()
        if current < self.tabs.count() - 1:
            self.tabs.setCurrentIndex(current + 1)
        else:
            self.tabs.setCurrentIndex(0)

    def prev_tab(self):
        current = self.tabs.currentIndex()
        if current > 0:
            self.tabs.setCurrentIndex(current - 1)
        else:
            self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def reload_current_tab(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, BrowserTab):
            current_tab.browser.reload()

    def add_new_tab(self):
        new_tab = BrowserTab(self.history_manager)
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