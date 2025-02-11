import sys
import re
import urllib.parse
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QPushButton, QLineEdit, QHBoxLayout, QTabWidget, QTabBar)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineUrlRequestInterceptor
from PyQt6.QtCore import QUrl, Qt, QTimer, QSize
from PyQt6.QtGui import QIcon, QPalette, QColor, QKeySequence, QShortcut, QImage, QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

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
            domain = re.sub(r'^www\.', '', domain)
            return f"Visited {domain}"

        return title

def get_styles():
    return """
    QMainWindow, QWidget {
        background: #1a1a1a;
        color: #fff;
    }
    QTabWidget::pane {
        border: none;
        background: #1a1a1a;
        margin-top: -1px;
    }
    QTabWidget {
        padding-top: 0px;
        background: #1a1a1a;
    }
    QTabBar::tab {
        background: rgba(255, 255, 255, 0.05);
        color: #bbb;
        padding: 8px 30px 8px 12px;
        margin: 2px 1px 0px 1px;
        border-radius: 4px 4px 0 0;
        min-width: 100px;
        max-width: 200px;
    }
    QTabBar::tab:selected {
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
        font-weight: bold;
    }
    QTabBar::tab:hover:!selected {
        background: rgba(255, 255, 255, 0.07);
        color: #ddd;
    }
    QPushButton {
        background-color: transparent;
        color: #fff;
        padding: 0;
        border-radius: 16px;
        margin: 8px 4px;
        min-width: 32px;
        max-width: 32px;
        min-height: 32px;
        max-height: 32px;
        font-size: 14px;
        font-weight: 400;
        line-height: 32px;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    QPushButton:pressed {
        background-color: rgba(255, 255, 255, 0.05);
    }
    QPushButton:disabled {
        color: rgba(255, 255, 255, 0.3);
    }
    QLineEdit {
        background-color: #2b2b2b;
        color: #fff;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #222;
        margin: 4px;
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
    """

class TrackerBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self, tracker_list):
        super().__init__()
        self.tracker_list = tracker_list

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if any(tracker in url for tracker in self.tracker_list):
            info.block(True)

class CustomTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()

class BrowserTab(QWidget):
    def __init__(self, history_manager, cache, browser_window, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.cache = cache
        self.browser_window = browser_window
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))

        nav_container = QWidget()
        nav_container.setFixedHeight(48)
        nav_container.setStyleSheet("""
            QWidget {
                background: #1a1a1a;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: #fff;
                padding: 4px 10px;
                border-radius: 6px;
                border: 1px solid #222;
                margin: 4px;
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
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        self.url_bar.returnPressed.connect(self.load_url)
        self.url_bar.clear()

        button_style = """
            QPushButton {
                background-color: transparent;
                color: #fff;
                padding: 0;
                border-radius: 16px;
                margin: 8px 4px;
                min-width: 32px;
                max-width: 32px;
                min-height: 32px;
                max-height: 32px;
                font-size: 14px;
                font-weight: 400;
                line-height: 32px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QPushButton:disabled {
                color: rgba(255, 255, 255, 0.3);
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

        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #fff;
                padding: 5px;
                border-radius: 15px;
                margin: 0px 8px 0px 2px;
                min-width: 30px;
                max-width: 30px;
                min-height: 28px;
                max-height: 28px;
                font-size: 18px;
                font-weight: 400;
                line-height: 1;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)

        self.new_tab_button.clicked.connect(self.browser_window.add_new_tab)

        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(8, 0, 8, 0)
        nav_layout.setSpacing(2)
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.reload_button)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.new_tab_button)

        self.layout.addWidget(nav_container)
        self.layout.addWidget(self.browser)

        self.browser.urlChanged.connect(self.update_url)
        self.browser.urlChanged.connect(self.record_history)
        self.browser.loadStarted.connect(lambda: self.reload_button.setText("✕"))
        self.browser.loadFinished.connect(lambda: self.reload_button.setText("⟳"))
        self.browser.loadFinished.connect(self.handle_load_finished)
        self.browser.loadFinished.connect(self.update_navigation_state)
        self.browser.iconChanged.connect(self.update_tab_icon)

        self.setup_shortcuts()

    def setup_shortcuts(self):
        reload_shortcut = QShortcut(QKeySequence("F5"), self)
        reload_shortcut.activated.connect(self.browser.reload)

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
            self.cache_page(url.toString())

    def cache_page(self, url):
        self.browser.page().toHtml(lambda html: self.cache.update({url: (html, datetime.now())}))

    def handle_load_finished(self, success):
        if not success:
            self.browser.setHtml("<h1>Failed to load page</h1>")

    def update_tab_icon(self, icon):
        index = self.browser_window.tabs.indexOf(self)
        if index >= 0:
            self.browser_window.tabs.setTabIcon(index, icon)

class HistoryTab(QWidget):
    def __init__(self, browser_window, history_manager, cache, parent=None):
        super().__init__(parent)
        self.browser_window = browser_window
        self.history_manager = history_manager
        self.cache = cache
        self.layout = QVBoxLayout(self)

        self.browser = QWebEngineView()
        self.layout.addWidget(self.browser)

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
            QTabBar {
                background: #1a1a1a;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.05);
                color: #bbb;
                padding: 8px 32px 8px 16px;
                margin: 4px 2px 0px 2px;
                border-radius: 8px 8px 0 0;
                min-width: 120px;
                max-width: 200px;
                min-height: 20px;
                font-size: 13px;
                line-height: 20px;
            }
            QTabBar::tab:selected {
                background: rgba(255, 255, 255, 0.1);
                color: #fff;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(255, 255, 255, 0.07);
                color: #fff;
            }
            QTabBar::close-button {
                image: none;
                subcontrol-position: right;
                subcontrol-origin: padding;
                margin-right: 4px;
            }
            QTabBar::close-button::after {
                content: "✕";
                color: rgba(255, 255, 255, 0.5);
                font-size: 16px;
                font-weight: 400;
                background: transparent;
                border-radius: 10px;
                padding: 2px 6px;
            }
            QTabBar::close-button:hover::after {
                color: white;
                background: rgba(255, 255, 255, 0.1);
            }
        """)

class StratusBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stratus Browser")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("path/to/your/icon.png"))
        self.history_manager = HistoryManager()
        self.cache = {}

        self.setStyleSheet(get_styles())

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

        main_layout.addWidget(self.tabs)
        self.setCentralWidget(main_container)

        self.add_new_tab()
        self.setup_shortcuts()

# Block known trackers
        self.tracker_list = [
    "google-analytics.com",
    "analytics.google.com",
    "googletagmanager.com",
    "doubleclick.net",
    "googleadservices.com",
    "googlesyndication.com",
    "facebook.com",
    "facebook.net",
    "fbcdn.net",
    "fbevents.com",
    "omtrdc.net",
    "demdex.net",
    "twitter.com",
    "twimg.com",
    "t.co",
    "linkedin.com",
    "licdn.com",
    "snap.licdn.com",
    "clarity.ms",
    "hotjar.com",
    "hotjar.io",
    "mixpanel.com",
    "segment.com",
    "segment.io",
    "crazyegg.com",
    "hubspot.com",
    "hs-analytics.net",
    "hs-scripts.com",
    "newrelic.com",
    "pinterest.com",
    "pinimg.com",
    "yandex.ru",
    "mc.yandex.ru",
    "bat.bing.com",
    "scorecardresearch.com",
    "quantserve.com",
    "chartbeat.com",
    "chartbeat.net",
    "outbrain.com",
    "taboola.com",
    "addthis.com",
    "addthisedge.com",
    "disqus.com",
    "disquscdn.com",
    "optimizely.com",
    "criteo.com",
    "criteo.net",
    "appnexus.com",
    "adnxs.com",
    "bluekai.com",
    "sharethis.com",
    "matomo.cloud",
    "matomo.org",
    "amplitude.com",
    "api.amplitude.com",
    "cdn.amplitude.com",
    "analytics.tiktok.com",
    "analytics-sg.tiktok.com",
    "business-api.tiktok.com",
    "ads-api.tiktok.com",
    "pixel.facebook.com",
    "an.facebook.com",
    "pixel-a.basis.net",
    "pixel-sync.sitescout.com",
    "pixel.tapad.com",
    "pixel.advertising.com",
    "pixel.mathtag.com",
    "id5-sync.com",
    "match.adsrvr.org",
    "secure.adnxs.com",
    "pixel.rubiconproject.com",
    "analytics.yahoo.com",
    "sp.analytics.yahoo.com",
    "udc.yahoo.com",
    "log.outbrain.com",
    "amplify.outbrain.com",
    "widgets.outbrain.com",
    "snowplow.io",
    "collector.snowplow.io",
    "plausible.io",
    "collector.plausible.io",
    "analytics.heap.io",
    "tracking.monsido.com",
    "cdn.mouseflow.com",
    "tools.mouseflow.com",
    "stats.wp.com",
    "pixel.wp.com",
    "s.pinimg.com",
    "trk.pinterest.com",
    "analytics.pinterest.com",
    "log.pinterest.com",
    "adservice.google.com",
    "adservice.google.com.au",
    "googlesurvey.com",
    "moatads.com",
    "tapad.com",
    "everesttech.net",
    "quantcast.com",
    "adsrvr.org",
    "advertising.com",
    "adobedtm.com",
    "demdex.net",
    "adform.net",
    "openx.net",
    "adroll.com",
    "exelator.com",
    "zqtk.net",
    "revcontent.com",
    "3lift.com",
    "bidswitch.net",
    "adnuntius.com",
    "adscale.de",
    "mediamath.com",
    "admedo.com",
    "connexity.net",
    "smartadserver.com",
    "spotxchange.com",
    "rubiconproject.com",
    "gumgum.com",
    "yieldlab.net",
    "pubmatic.com",
    "simpli.fi",
    "adacado.com"
        ]

        profile = QWebEngineProfile.defaultProfile()
        interceptor = TrackerBlocker(self.tracker_list)
        QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(interceptor)

        self.cache_cleanup_timer = QTimer()
        self.cache_cleanup_timer.timeout.connect(self.cleanup_cache)
        self.cache_cleanup_timer.start(3600000)  # 1 hour

    def setup_shortcuts(self):
        new_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        new_tab_shortcut.activated.connect(self.add_new_tab)

        close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_tab_shortcut.activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))

        next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+]"), self)
        next_tab_shortcut.activated.connect(self.next_tab)

        next_tab_shortcut_alt = QShortcut(QKeySequence("Ctrl+Tab"), self)
        next_tab_shortcut_alt.activated.connect(self.next_tab)

        prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+["), self)
        prev_tab_shortcut.activated.connect(self.prev_tab)

        prev_tab_shortcut_alt = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        prev_tab_shortcut_alt.activated.connect(self.prev_tab)

        reload_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        reload_shortcut.activated.connect(self.reload_current_tab)

        history_shortcut = QShortcut(QKeySequence("Ctrl+Shift+H"), self)
        history_shortcut.activated.connect(self.show_history)

        focus_url_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        focus_url_shortcut.activated.connect(self.focus_url_bar)

        focus_url_shortcut_alt = QShortcut(QKeySequence("Alt+D"), self)
        focus_url_shortcut_alt.activated.connect(self.focus_url_bar)

    def focus_url_bar(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, BrowserTab):
            current_tab.url_bar.setFocus()
            current_tab.url_bar.selectAll()

    def show_history(self):
        history_tab = HistoryTab(self, self.history_manager, self.cache)
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

    def add_new_tab(self, url=None):
        new_tab = BrowserTab(self.history_manager, self.cache, self)
        if url:
            new_tab.browser.setUrl(QUrl(url))
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

    def cleanup_cache(self):
        current_time = datetime.now()
        keys_to_remove = []

        for key, (timestamp, _) in self.cache.items():
            try:
                if isinstance(timestamp, str):
                    timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                elif not isinstance(timestamp, datetime):
                    continue

                if current_time - timestamp > timedelta(hours=1):
                    keys_to_remove.append(key)
            except ValueError:

                continue

        for key in keys_to_remove:
            del self.cache[key]

    def load_tab_content(self, index):
        tab = self.tabs.widget(index)
        if isinstance(tab, BrowserTab) and not tab.browser.url().isValid():
            tab.browser.setUrl(QUrl("https://www.google.com"))

    def tab_changed(self, index):
        self.load_tab_content(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(26, 26, 26))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(26, 26, 26))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(66, 133, 244))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(66, 133, 244))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    app.setPalette(dark_palette)

    window = StratusBrowser()
    window.tabs.currentChanged.connect(window.tab_changed)
    window.show()
    sys.exit(app.exec())