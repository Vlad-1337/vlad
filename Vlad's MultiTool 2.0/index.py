import sys
import os
import math
import requests
from PyQt5 import QtCore, QtGui, QtWidgets

class SplashScreen(QtWidgets.QSplashScreen):
    def __init__(self):
        pixmap = QtGui.QPixmap(400, 300)
        pixmap.fill(QtGui.QColor(53, 53, 53))
        
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QColor(255, 255, 255))
        font = painter.font()
        font.setPointSize(16)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignTop | QtCore.Qt.AlignTop, "Vlad's MultiTool")

        font.setPointSize(12)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, "Loading tools...")
        
        progress_rect = QtCore.QRect(50, 250, 300, 20)
        painter.setPen(QtGui.QColor(70, 70, 70))
        painter.setBrush(QtGui.QColor(70, 70, 70))
        painter.drawRect(progress_rect)
        
        painter.end()
        
        super().__init__(pixmap)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setGeometry(50, 250, 300, 20)
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 5px;
                background: #353535;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 5px;
            }
        """)

    def update_progress(self, value):
        self.progress.setValue(value)
        QtWidgets.QApplication.processEvents()

class Downloader(QtCore.QThread):
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)

    def __init__(self, url, target_path):
        super().__init__()
        self.url = url
        self.target_path = target_path
        self._cancelled = False

    def run(self):
        try:
            with requests.get(self.url, stream=True) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(self.target_path, 'wb') as f:
                    for chunk in r.iter_content(8192):
                        if self._cancelled:
                            return
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                percent = math.floor(downloaded * 100 / total)
                                self.progress.emit(percent)
            self.finished.emit(self.target_path)
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._cancelled = True

class LearningToolApp(QtWidgets.QMainWindow):
    def __init__(self, icon_path=None, banner_path=None, icons_dir="icons"):
        super().__init__()
        self.setWindowTitle("Vlad's MultiTool")
        self.resize(900, 650)
        self.setMinimumSize(800, 550)

        self.icons_dir = icons_dir
        self.icon_path = icon_path
        self.banner_path = banner_path

        self.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(35, 35, 35))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(46, 204, 113).lighter())
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        self.setPalette(palette)

        self.set_application_icon()

        container = QtWidgets.QWidget()
        container.setObjectName("mainContainer")
        main_layout = QtWidgets.QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        self.setCentralWidget(container)

        header = QtWidgets.QWidget()
        header.setObjectName("header")
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        if self.banner_path and os.path.exists(self.banner_path):
            banner = QtWidgets.QLabel()
            banner.setPixmap(QtGui.QPixmap(self.banner_path).scaledToHeight(100, QtCore.Qt.SmoothTransformation))
            banner.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            header_layout.addWidget(banner)
        else:
            title = QtWidgets.QLabel("Vlad's MultiTool")
            title.setObjectName("appTitle")
            title.setStyleSheet("font-size: 28px; font-weight: bold;")
            header_layout.addWidget(title)

        header_layout.addStretch()

        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search tools...")
        self.search_bar.setFixedWidth(250)
        self.search_bar.setObjectName("searchBar")
        header_layout.addWidget(self.search_bar)

        main_layout.addWidget(header)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll.setObjectName("scrollArea")
        main_layout.addWidget(self.scroll)

        self.tool_area = QtWidgets.QWidget()
        self.tool_area.setObjectName("toolArea")
        self.tool_layout = QtWidgets.QGridLayout(self.tool_area)
        self.tool_layout.setContentsMargins(10, 10, 10, 10)
        self.tool_layout.setSpacing(20)
        self.tool_layout.setAlignment(QtCore.Qt.AlignTop)
        self.scroll.setWidget(self.tool_area)

        self.progress_container = QtWidgets.QFrame()
        self.progress_container.setObjectName("progressContainer")
        self.progress_container.setStyleSheet("""
            #progressContainer {
                background-color: #3a3a3a; 
                border-radius: 8px; 
                padding: 12px;
                border: 1px solid #4a4a4a;
            }
        """)
        progress_layout = QtWidgets.QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(10, 5, 10, 5)
        progress_layout.setSpacing(8)

        self.progress_label = QtWidgets.QLabel("Ready to download")
        self.progress_label.setStyleSheet("color: #cccccc; font-size: 14px;")
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: #4a4a4a; 
                border-radius: 5px; 
                height: 20px;
                text-align: center;
            } 
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 5px;
            }
        """)
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.cancel_btn = QtWidgets.QPushButton("Cancel Download")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setStyleSheet("""
            #cancelButton {
                background: #ff4757;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            #cancelButton:hover {
                background: #ff6b81;
            }
        """)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        progress_layout.addWidget(self.cancel_btn)

        main_layout.addWidget(self.progress_container)

        self.setStyleSheet("""
            QMainWindow {
                background: #353535;
            }
            QPushButton {
                background: #2ecc71;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 6px;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #27ae60;
            }
            QPushButton:pressed {
                background: #1e8449;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background: #4a4a4a;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 8px;
                color: white;
                selection-background-color: #2ecc71;
            }
            QLineEdit:focus {
                border: 1px solid #2ecc71;
            }
            QScrollArea {
                background: transparent;
            }
            #toolArea {
                background: transparent;
            }
            QToolTip {
                color: white;
                background-color: #5a5a5a;
                border: 1px solid #6a6a6a;
            }
            #toolCard {
                background: #3a3a3a;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #4a4a4a;
            }
            #toolCard:hover {
                border: 1px solid #2ecc71;
            }
        """)

        self.tools = [
            {"name": "System Informer", "url": "https://github.com/winsiderss/si-builds/releases/download/3.2.25215.2022/systeminformer-3.2.25215.2022-canary-setup.exe",
             "description": "System Informer", "icon": "🛠️"},
            {"name": "SrumECmd", "url": "https://download.ericzimmermanstools.com/net9/SrumECmd.zip",
             "description": "SrumECmd", "icon": "🛠️"},
            {"name": "MFTECmd", "url": "https://download.ericzimmermanstools.com/MFTECmd.zip",
             "description": "MFTECmd", "icon": "🛠️"},
            {"name": "Timeline Explorer", "url": "https://download.ericzimmermanstools.com/net9/TimelineExplorer.zip",
             "description": "Timeline Explorer", "icon": "🛠️"},
            {"name": "Autopsy", "url": "https://github.com/sleuthkit/autopsy/releases/download/autopsy-4.22.1/autopsy-4.22.1-64bit.msi",
             "description": "Autopsy", "icon": "🛠️"},
            {"name": "AmcacheParser", "url": "https://download.ericzimmermanstools.com/net9/AmcacheParser.zip",
             "description": "AmcacheParser", "icon": "🛠️"},
        ]

        self.populate_tools()
        self.current_downloader = None

        self.search_bar.textChanged.connect(self.filter_tools)

    def set_application_icon(self):
        """Set application icon from specified path or fallback to default"""
        if self.icon_path and os.path.exists(self.icon_path):
            self.setWindowIcon(QtGui.QIcon(self.icon_path))
        else:
            self.create_programmatic_icon()

    def create_programmatic_icon(self):
        """Create a simple icon programmatically as fallback"""
        pixmap = QtGui.QPixmap(64, 64)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        painter.setBrush(QtGui.QColor(46, 204, 113))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(2, 2, 60, 60)
        
        painter.setPen(QtGui.QColor(255, 255, 255))
        font = painter.font()
        font.setPointSize(24)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, "PC")
        
        painter.end()
        self.setWindowIcon(QtGui.QIcon(pixmap))

    def get_icon_pixmap(self, icon_name):
        """Get icon pixmap from icons directory or return default"""
        if not os.path.exists(self.icons_dir):
            return None
            
        for ext in ['.png', '.jpg', '.jpeg', '.ico', '.svg']:
            icon_path = os.path.join(self.icons_dir, icon_name.lower() + ext)
            if os.path.exists(icon_path):
                return QtGui.QPixmap(icon_path)
        
        icon_path = os.path.join(self.icons_dir, icon_name)
        if os.path.exists(icon_path):
            return QtGui.QPixmap(icon_path)
            
        return None

    def create_tool_card(self, tool):
        """Create a styled card for each tool with proper icon"""
        card = QtWidgets.QFrame()
        card.setObjectName("toolCard")
        card.setFixedWidth(250)
        card.setMinimumHeight(180)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.setSpacing(15)

        icon_pixmap = self.get_icon_pixmap(tool.get("icon", "default"))
        if icon_pixmap:
            icon_label = QtWidgets.QLabel()
            icon_pixmap = icon_pixmap.scaled(32, 32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
        else:
            icon_label = QtWidgets.QLabel(tool.get("icon", "📚"))
            icon_label.setStyleSheet("font-size: 28px;")
        
        title_layout.addWidget(icon_label)

        title = QtWidgets.QLabel(tool["name"])
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        desc = QtWidgets.QLabel(tool.get("description", "No description available"))
        desc.setStyleSheet("color: #cccccc; font-size: 13px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        btn = QtWidgets.QPushButton("Download")
        btn.setToolTip(f"Download {tool['name']}")
        btn.clicked.connect(lambda _, url=tool["url"], name=tool["name"]: self.start_download(url, name))
        layout.addWidget(btn)

        return card

    def populate_tools(self):
        """Populate the tools area with cards using grid layout"""
        row = 0
        col = 0
        max_cols = 3

        for tool in self.tools:
            card = self.create_tool_card(tool)
            self.tool_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def filter_tools(self, text):
        """Filter tools based on search text"""
        for i in range(self.tool_layout.count()):
            widget = self.tool_layout.itemAt(i).widget()
            if widget:
                title_layout = widget.layout().itemAt(0).layout()
                title_label = title_layout.itemAt(1).widget()
                tool_name = title_label.text().lower()
                widget.setVisible(text.lower() in tool_name)

    def start_download(self, url, name):
        """Start downloading a tool"""
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        filename = os.path.basename(url.split('?')[0]) or f"{name.replace(' ', '_')}.download"
        target_path = os.path.join(desktop, filename)

        self.progress_label.setText(f"Downloading {name}...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.cancel_btn.setVisible(True)

        self.current_downloader = Downloader(url, target_path)
        self.current_downloader.progress.connect(self.on_progress)
        self.current_downloader.finished.connect(self.on_finished)
        self.current_downloader.error.connect(self.on_error)
        self.current_downloader.start()

    def cancel_download(self):
        """Cancel the current download"""
        if self.current_downloader:
            self.current_downloader.cancel()
            self.progress_label.setText("Download cancelled")
            self.progress_bar.setVisible(False)
            self.cancel_btn.setVisible(False)
            QtWidgets.QMessageBox.warning(self, "Download Cancelled", "The download was cancelled.")

    def on_progress(self, percent):
        """Update progress bar"""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(f"Downloading... {percent}%")

    def on_finished(self, filepath):
        """Handle download completion"""
        self.progress_label.setText("Download complete!")
        self.progress_bar.setVisible(False)
        self.cancel_btn.setVisible(False)
        QtWidgets.QMessageBox.information(self, "Download Complete", f"File saved to:\n{filepath}")
        self.current_downloader = None

    def on_error(self, msg):
        """Handle download errors"""
        self.progress_label.setText("Error during download")
        self.progress_bar.setVisible(False)
        self.cancel_btn.setVisible(False)
        QtWidgets.QMessageBox.critical(self, "Download Error", f"An error occurred:\n{msg}")
        self.current_downloader = None

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    if sys.platform == "win32":
        import ctypes
        myappid = 'pc.check.learning.tool.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    splash = SplashScreen()
    splash.show()
    
    for i in range(0, 101, 10):
        splash.update_progress(i)
        QtCore.QThread.msleep(100)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "icon.ico")
    banner_path = os.path.join(base_dir, "banner.png")
    icons_dir = os.path.join(base_dir, "icons")
    
    window = LearningToolApp(
        icon_path=icon_path,
        banner_path=banner_path,
        icons_dir=icons_dir
    )
    
    splash.finish(window)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()