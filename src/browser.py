from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile, QWebEngineSettings  
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sys
import os
from PyQt5.QtGui import QKeySequence, QShortcutEvent, QIcon
import os
from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from pathlib import Path
os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
from PyQt5.QtGui import QPalette, QColor

dark_palette = QPalette()
dark_palette.setColor(QPalette.Window, QColor(0, 0, 0))
dark_palette.setColor(QPalette.Base, QColor(0, 0, 0))
dark_palette.setColor(QPalette.Button, QColor(0, 0, 0))
dark_palette.setColor(QPalette.Highlight, QColor(40, 0, 114))
dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))


class NavPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
    def acceptNavigationRequest(self, url, nav_type, isMainFrame):
        if url.scheme() == "mybrowser" and url.host() == "search":
            query = QUrlQuery(url).queryItemValue("q")
            search_url = f"https://www.google.com/search?q={query}"
            self.view().setUrl(QUrl(search_url))
            return False
        return super().acceptNavigationRequest(url, nav_type, isMainFrame)
        

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FuturePlot Browser")
        self.showMaximized() 
        self.minimumSizeHint = QSize(800, 600)  # Set minimum size for the window
        # this is where the SHIT HAPPENS, delete this and youre fucked!
        self.tabs = QTabWidget()
        self.tabs.isMovable= True
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        tab_bar = self.tabs.tabBar()
        tab_bar.setExpanding(True)  # prevents tabs from stretching equally
        tab_bar.setTabsClosable(True)
        tab_bar.setMovable(True)
        self.tabs.setUsesScrollButtons(True)  # enables scroll arrows if tabs overflow
        self.setCentralWidget(self.tabs)
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.profile.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.profile.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

        old_resize_event = self.tabs.resizeEvent

        def new_resize_event(event):
            adjust_tab_widths()
            old_resize_event(event)

        self.tabs.resizeEvent = new_resize_event

        

        BASE_DIR = Path(__file__).resolve().parent  # points to 'src/'
        print(BASE_DIR)
        homepage_path = (BASE_DIR / "assets" / "homepage.html").resolve()


        homepage_url = QUrl.fromLocalFile(str(homepage_path))
        self.homepage_url = homepage_url  

        # Create first tab using local homepage
        self.new_tab(url=homepage_url, label="Home")

        # Add nav bar here later if needed, thank you gpt
        self.create_navbar()


        '''KEY BINDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'''

        newtab_shortcut = QKeySequence(Qt.CTRL + Qt.Key_T)
        self.new_tab_shortcut = QShortcut(newtab_shortcut, self)
        self.new_tab_shortcut.activated.connect(self.new_tab)


        closetab_shortcut = QKeySequence(Qt.CTRL + Qt.Key_W)
        self.close_tab_shortcut = QShortcut(closetab_shortcut, self)
        self.close_tab_shortcut.activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        def adjust_tab_widths():
            tab_count = self.tabs.count()
            if tab_count == 0:
                return
            available_width = self.tabs.width()
            tab_width = max(80, min(150, available_width // tab_count))
            self.tabs.tabBar().setStyleSheet(f"""
                QTabBar::tab {{
                    min-width: {tab_width}px;
                    max-width: {tab_width}px;
                    padding: 5px;
                }}
            """)



        '''STYLING  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'''
        closebutton_path = BASE_DIR / "assets" / "icons" / "closebutton.png"
        #closebuttonico_path = QUrl.fromLocalFile(str(closebutton_path)).toString()
        closebuttonico_path = str(closebutton_path).replace("\\", "/")  # No 'file://'
        print("close ico path:", closebuttonico_path)
        print("Exists:", closebutton_path.exists())      
        self.tabs.setTabsClosable(True)  # Just to be sure

        self.tabs.setStyleSheet(f"""
            QTabBar::close-button {{
                image: url("{closebuttonico_path}");
                width: 16px;
                height: 16px;
                
            }}
            QTabBar::close-button:hover {{
                image: url("{closebuttonico_path}");
                background: #00FF15FF;
                width: 16px;
                height: 16px;
                
            }}

            QTabWidget::pane {{
        background: #313131FF;
        border: none;
        }}

            QTabBar {{
                background: #363636FF;
            }}

            QTabBar::tab {{
                background: #000000;
                color: #FFFFFF;
                padding: 10px;
                border: 1px solid #444;
                
            }}

            QTabBar::tab:selected {{
                background: #280072;
            }}

                """)

    def on_icon_changed(self, icon):
        index = self.tabs.indexOf(self.sender())
        if index != -1:
            self.tabs.setTabIcon(index, icon)

    def new_tab(self, url=None, label="New Tab"):
        

        view = QWebEngineView() #the view of the web    
        page = NavPage(self.profile, view)
        page.profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )

        view.setPage(page)
        view.iconChanged.connect(self.on_icon_changed)  # Set the window icon when it changes
        if url is None:
            url = self.homepage_url #no url = go to homepage

        print("Loading URL in new tab:", url.toString())
        view.setUrl(url)

        index = self.tabs.addTab(view, label) #now you are a tab!
        self.tabs.setCurrentIndex(index)

        view.urlChanged.connect(self.update_url)
        view.titleChanged.connect(lambda title, vw=view: self.tabs.setTabText(self.tabs.indexOf(vw), title))
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            widget = self.tabs.widget(index)
            self.tabs.removeTab(index)
            widget.deleteLater()  # kill it.
        else:
            widget = self.tabs.widget(index)
            widget.setUrl(QUrl(self.homepage_url))



    def create_navbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        toolbar.setMovable(False)  
        # BACK BUTTON
        back_btn = QAction("←", self)
        
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())

        toolbar.addAction(back_btn)

        # FORWARD BUTTON
        fwd_btn = QAction("→", self)
        fwd_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        toolbar.addAction(fwd_btn)

        # RELOAD
        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        toolbar.addAction(reload_btn)

        # ADDRESS BAR
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.url_bar)

        # Sync bar when page loads
        self.tabs.currentChanged.connect(self.sync_url_bar)
    def sync_url_bar(self, index):
        browser = self.tabs.widget(index)
        if browser:
            browser.urlChanged.connect(lambda q: self.update_url(q))


    def load_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "https://" + url
        self.tabs.currentWidget().setUrl(QUrl(url))



    def update_url(self, q):
        self.url_bar.setText(q.toString())

app = QApplication(sys.argv)
app.setPalette(dark_palette)

window = Browser()
window.show()

sys.exit(app.exec_())
