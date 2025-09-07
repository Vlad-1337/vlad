import sys
import os
import math
import requests
from PyQt5 import QtCore, QtGui, QtWidgets

class SplashScreen(QtWidgets.QSplashScreen):
    def __init__(self):
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QtGui.QPixmap(logo_path)
            logo_pixmap = logo_pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            
            pixmap = QtGui.QPixmap(500, 400)
            pixmap.fill(QtGui.QColor(53, 53, 53))
            
            painter = QtGui.QPainter(pixmap)
            
            logo_rect = QtCore.QRect(150, 80, 200, 200)
            painter.drawPixmap(logo_rect, logo_pixmap)
            
            painter.setPen(QtGui.QColor(255, 255, 255))
            font = painter.font()
            font.setPointSize(14)
            font.setBold(True)
            font.setWeight(QtGui.QFont.DemiBold)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter, "Loading tools...")
            
            progress_rect = QtCore.QRect(75, 320, 350, 25)
            painter.setPen(QtGui.QColor(70, 70, 70))
            painter.setBrush(QtGui.QColor(70, 70, 70))
            painter.drawRect(progress_rect)
            
            painter.end()
        else:
            pixmap = QtGui.QPixmap(400, 300)
            pixmap.fill(QtGui.QColor(53, 53, 53))
            
            painter = QtGui.QPainter(pixmap)
            painter.setPen(QtGui.QColor(255, 255, 255))
            font = painter.font()
            font.setPointSize(16)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), QtCore.Qt.AlignTop | QtCore.Qt.AlignTop, "PC Check Learning Multi Tool")

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
        self.progress.setGeometry(75, 320, 350, 25)
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 5px;
                background: #353535;
            }
            QProgressBar::chunk {
                background-color: #3498db;
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
        self.setWindowTitle("PC Check Learning Multi Tool")
        self.resize(1400, 900)
        self.setMinimumSize(1000, 700)

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
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(52, 152, 219).lighter())
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        self.setPalette(palette)

        self.set_application_icon()

        container = QtWidgets.QWidget()
        container.setObjectName("mainContainer")
        main_layout = QtWidgets.QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(25)
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
            title = QtWidgets.QLabel("PC Check Learning Multi Tool")
            title.setObjectName("appTitle")
            title.setStyleSheet("font-size: 28px; font-weight: 600;")
            header_layout.addWidget(title)

        header_layout.addStretch()

        # Search and filter controls
        search_filter_widget = QtWidgets.QWidget()
        search_filter_layout = QtWidgets.QHBoxLayout(search_filter_widget)
        search_filter_layout.setContentsMargins(0, 0, 0, 0)
        search_filter_layout.setSpacing(10)
        
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search tools...")
        self.search_bar.setFixedWidth(200)
        self.search_bar.setObjectName("searchBar")
        search_filter_layout.addWidget(self.search_bar)
        
        self.category_filter = QtWidgets.QComboBox()
        self.category_filter.setFixedWidth(150)
        self.category_filter.setObjectName("categoryFilter")
        self.category_filter.addItem("All Categories")
        search_filter_layout.addWidget(self.category_filter)
        
        header_layout.addWidget(search_filter_widget)
        self.discord_btn = QtWidgets.QPushButton("Discord")
        self.discord_btn.setObjectName("discordButton")
        self.discord_btn.setFixedWidth(80)
        self.discord_btn.setStyleSheet("""
            #discordButton {
                background: #5865F2;
                color: white;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 6px;
                border: none;
            }
            #discordButton:hover {
                background: #4752C4;
            }
        """)
        self.discord_btn.clicked.connect(self.open_discord)
        header_layout.addWidget(self.discord_btn)
        
        self.website_btn = QtWidgets.QPushButton("Website")
        self.website_btn.setObjectName("websiteButton")
        self.website_btn.setFixedWidth(80)
        self.website_btn.setStyleSheet("""
            #websiteButton {
                background: #3498db;
                color: white;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 6px;
                border: none;
            }
            #websiteButton:hover {
                background: #2980b9;
            }
        """)
        self.website_btn.clicked.connect(self.open_website)
        header_layout.addWidget(self.website_btn)

        main_layout.addWidget(header)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll.setObjectName("scrollArea")
        main_layout.addWidget(self.scroll)

        self.tool_area = QtWidgets.QWidget()
        self.tool_area.setObjectName("toolArea")
        self.tool_layout = QtWidgets.QGridLayout(self.tool_area)
        self.tool_layout.setContentsMargins(20, 20, 20, 20)
        self.tool_layout.setSpacing(30)
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
                background-color: #3498db;
                border-radius: 5px;
            }
        """)
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.cancel_btn = QtWidgets.QPushButton("Cancel Download")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setStyleSheet("""
            #cancelButton {
                background: #e74c3c;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            #cancelButton:hover {
                background: #c0392b;
            }
        """)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        progress_layout.addWidget(self.cancel_btn)

        main_layout.addWidget(self.progress_container)

        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)

        self.setStyleSheet("""
            QMainWindow {
                background: #353535;
            }
            QPushButton {
                background: #3498db;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 14px 24px;
                border-radius: 8px;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:pressed {
                background: #1f5f8b;
            }
            QLabel {
                color: white;
                font-weight: 500;
            }
            QLineEdit {
                background: #4a4a4a;
                border: 1px solid #5a5a5a;
                border-radius: 6px;
                padding: 10px 12px;
                color: white;
                font-weight: 500;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QComboBox {
                background: #4a4a4a;
                border: 1px solid #5a5a5a;
                border-radius: 6px;
                padding: 10px 12px;
                color: white;
                font-weight: 500;
                min-width: 120px;
            }
            QComboBox:focus {
                border: 1px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: #4a4a4a;
                border: 1px solid #5a5a5a;
                selection-background-color: #3498db;
                color: white;
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
            QStatusBar {
                background: #2a2a2a;
                color: white;
                border-top: 1px solid #4a4a4a;
            }
            #toolCard {
                background: #3a3a3a;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #4a4a4a;
                margin: 5px;
            }
            #toolCard:hover {
                border: 2px solid #3498db;
                background: #404040;
            }
        """)

        self.tools = [
            {"name": "System Informer", "url": "https://github.com/winsiderss/si-builds/releases/download/3.2.25093.1138/systeminformer-3.2.25093.1138-canary-setup.exe",
             "description": "Advanced system monitoring and process analysis tool", "icon": "system_informer.png", "category": "System Analysis"},
            {"name": "Bam Parser", "url": "https://github.com/spokwn/BAM-parser/releases/download/v1.2.7/BAMParser.exe",
             "description": "Background Activity Moderator parser for Windows 10/11", "icon": "bam_parser.png", "category": "System Analysis"},
            {"name": "Paths Parser", "url": "https://github.com/spokwn/PathsParser/releases/download/v1.0.11/PathsParser.exe",
             "description": "Windows Paths registry parser for forensic analysis", "icon": "paths_parser.png", "category": "System Analysis"},
            {"name": "WinPrefetchView", "url": "https://www.nirsoft.net/utils/winprefetchview-x64.zip",
             "description": "View and analyze Windows Prefetch files", "icon": "prefetch_view.png", "category": "System Analysis"},
            {"name": "WinDefLogs", "url": "https://www.nirsoft.net/utils/windeflogview.zip",
             "description": "View Windows Defender logs and quarantine information", "icon": "defender_logs.png", "category": "Security"},
            {"name": "WinDefThreads", "url": "https://www.nirsoft.net/utils/windefthreadsview.zip",
             "description": "Monitor Windows Defender threads and processes", "icon": "defender_threads.png", "category": "Security"},
            {"name": "Everything Tool", "url": "https://www.voidtools.com/Everything-1.4.1.1026.x64-Setup.exe",
             "description": "Lightning-fast file search utility", "icon": "everything_tool.png", "category": "File Tools"},
            {"name": "Previous File Recovery", "url": "https://www.majorgeeks.com/mg/get/previousfilesrecovery,2.html",
             "description": "Recover previous versions of files", "icon": "file_recovery.png", "category": "File Recovery"},
            {"name": "USBDeview", "url": "https://www.nirsoft.net/utils/usbdeview.zip",
             "description": "View all USB devices that were connected to your computer", "icon": "usb_view.png", "category": "System Analysis"},
            {"name": "Browser Downloads View", "url": "https://www.nirsoft.net/utils/browserdownloadsview.zip",
             "description": "View downloads from various web browsers", "icon": "browser_downloads.png", "category": "File Tools"},
            {"name": "Disk Drill", "url": "https://www.cleverfiles.com/disk-drill-windows.html",
             "description": "Professional data recovery software for Windows", "icon": "disk_drill.png", "category": "File Recovery"},
            {"name": "Hayabusa", "url": "https://github.com/Yamato-Security/hayabusa/releases/download/v3.1.1/hayabusa-3.1.1-win-x64.zip",
             "description": "Fast Windows event log analyzer for blue team", "icon": "hayabusa.png", "category": "Forensics"},
            {"name": "Journal Trace", "url": "https://github.com/spokwn/JournalTrace/releases/download/1.2/JournalTrace.exe",
             "description": "Windows Journal trace parser for forensic analysis", "icon": "journal_trace.png", "category": "Forensics"},
            {"name": "App Compact Cache Parser", "url": "https://download.ericzimmermanstools.com/net6/AppCompatCacheParser.zip",
             "description": "Parse Windows Application Compatibility Cache", "icon": "app_cache.png", "category": "Forensics"},
            {"name": "PECMD", "url": "https://f001.backblazeb2.com/file/EricZimmermanTools/PECmd.zip",
             "description": "Parse Windows Prefetch files", "icon": "pecmd.png", "category": "Forensics"},
            {"name": "Last Activity", "url": "https://www.nirsoft.net/utils/lastactivityview.zip",
             "description": "View last activity on your computer", "icon": "last_activity.png", "category": "Forensics"},
            {"name": "Timeline Explorer", "url": "https://download.ericzimmermanstools.com/net6/TimelineExplorer.zip",
             "description": "Timeline analysis tool for forensic investigations", "icon": "timeline_explorer.png", "category": "Forensics"},
            {"name": "Prefetch Parser", "url": "https://github.com/spokwn/prefetch-parser/releases/download/v1.5.4/PrefetchParser.exe",
             "description": "Advanced Windows Prefetch file parser", "icon": "prefetch_parser.png", "category": "Forensics"},
            {"name": "MFTECmd", "url": "https://download.ericzimmermanstools.com/MFTECmd.zip",
             "description": "Master File Table parser for NTFS analysis", "icon": "mftecmd.png", "category": "Forensics"},
            {"name": "AmcacheParser", "url": "https://download.ericzimmermanstools.com/AmcacheParser.zip",
             "description": "Parse Windows AmCache.hve registry file", "icon": "amcache_parser.png", "category": "Forensics"},
            {"name": "Disk Investigator", "url": "https://www.majorgeeks.com/mg/getmirror/disk_investigator,2.html",
             "description": "Investigate disk usage and file allocation", "icon": "disk_investigator.png", "category": "Disk Tools"},
            {"name": "FTK Imager", "url": "https://archive.org/download/access-data-ftk-imager-4.7.1/AccessData_FTK_Imager_4.7.1.exe",
             "description": "Forensic toolkit for disk imaging and analysis", "icon": "ftk_imager.png", "category": "Forensics"},
            
            # Hex & Binary Tools
            {"name": "HxD", "url": "https://mh-nexus.de/en/downloads.php?product=HxD20",
             "description": "Professional hex editor and disk editor", "icon": "hxd.png", "category": "Hex Tools"},
            {"name": "Hasher", "url": "https://download.ericzimmermanstools.com/hasher.zip",
             "description": "Calculate file hashes (MD5, SHA1, SHA256)", "icon": "hasher.png", "category": "Hex Tools"},
            {"name": "Bstrings", "url": "https://download.ericzimmermanstools.com/bstrings.zip",
             "description": "Extract strings from binary files", "icon": "bstrings.png", "category": "Hex Tools"},
            {"name": "Magnet Process Capture", "url": "https://go.magnetforensics.com/e/52162/MagnetProcessCapture/kpt99v/1596068034/h/W_fAl_pThcDb-QN7ecFXAw8szOQU2dFtF_t_N383OvM",
             "description": "Capture and analyze running processes", "icon": "magnet_process.png", "category": "Process Analysis"},
            
            # Specialized Tools
            {"name": "Minecraft Tool", "url": "https://mega.nz/file/ICVwRTIa#41vMenW5HRwSUotNSy_5VH-QRUfT_g4RBEeMwwAfW0c",
             "description": "Minecraft analysis tool", "icon": "minecraft_tool.png", "category": "Specialized"},
            {"name": "OSForensics", "url": "https://osforensics.com/downloads/OSForensics.exe",
             "description": "Comprehensive digital forensics suite", "icon": "osforensics.png", "category": "Forensics"},
            {"name": "VirusTotal", "url": "https://www.virustotal.com/gui/",
             "description": "Online malware and file analysis service", "icon": "virustotal.png", "category": "Web Tools", "is_web": True},
            
            # System Commands
            {"name": "Check Services", "url": "powershell_command",
             "description": "Check important Windows services status", "icon": "check_services.png", "category": "System Commands", "is_command": True},
        ]

        self.populate_categories()
        self.populate_tools()
        self.current_downloader = None

        self.status_bar.showMessage(f"Ready - {len(self.tools)} tools available")

        self.search_bar.textChanged.connect(self.filter_tools)
        self.category_filter.currentTextChanged.connect(self.filter_tools)

    def set_application_icon(self):
        if self.icon_path and os.path.exists(self.icon_path):
            self.setWindowIcon(QtGui.QIcon(self.icon_path))
        else:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
            if os.path.exists(logo_path):
                self.setWindowIcon(QtGui.QIcon(logo_path))
            else:
                self.create_programmatic_icon()

    def create_programmatic_icon(self):
        pixmap = QtGui.QPixmap(64, 64)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        painter.setBrush(QtGui.QColor(52, 152, 219))
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
        if not os.path.exists(self.icons_dir):
            return None
        
        if '.' in icon_name:
            icon_path = os.path.join(self.icons_dir, icon_name)
            if os.path.exists(icon_path):
                return QtGui.QPixmap(icon_path)
        else:
            for ext in ['.png', '.jpg', '.jpeg', '.ico', '.svg']:
                icon_path = os.path.join(self.icons_dir, icon_name.lower() + ext)
                if os.path.exists(icon_path):
                    return QtGui.QPixmap(icon_path)
            
            icon_path = os.path.join(self.icons_dir, icon_name)
            if os.path.exists(icon_path):
                return QtGui.QPixmap(icon_path)
            
        return None

    def populate_categories(self):
        categories = set()
        for tool in self.tools:
            if "category" in tool:
                categories.add(tool["category"])
        
        for category in sorted(categories):
            self.category_filter.addItem(category)

    def create_tool_card(self, tool):
        card = QtWidgets.QFrame()
        card.setObjectName("toolCard")
        card.setFixedWidth(300)
        card.setMinimumHeight(220)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.setSpacing(15)

        icon_pixmap = self.get_icon_pixmap(tool.get("icon", "default"))
        if icon_pixmap:
            icon_label = QtWidgets.QLabel()
            icon_pixmap = icon_pixmap.scaled(32, 32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
        else:
            fallback_icons = {
                "System Analysis": "🖥️",
                "Security": "🛡️", 
                "File Tools": "📁",
                "File Recovery": "🔄",
                "Forensics": "🔍",
                "Disk Tools": "💿",
                "Hex Tools": "🔢",
                "Process Analysis": "⚙️",
                "Specialized": "🎯",
                "Web Tools": "🌐",
                "System Commands": "⚡"
            }
            category = tool.get("category", "System Analysis")
            fallback_icon = fallback_icons.get(category, "🛠️")
            icon_label = QtWidgets.QLabel(fallback_icon)
            icon_label.setStyleSheet("font-size: 28px;")
        
        title_layout.addWidget(icon_label)

        title = QtWidgets.QLabel(tool["name"])
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        desc = QtWidgets.QLabel(tool.get("description", "No description available"))
        desc.setStyleSheet("color: #cccccc; font-size: 13px; font-weight: 500;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        if "category" in tool:
            category_label = QtWidgets.QLabel(tool["category"])
            category_label.setStyleSheet("color: #3498db; font-size: 11px; font-weight: 600;")
            layout.addWidget(category_label)

        layout.addStretch()
        if tool.get("is_web", False):
            btn = QtWidgets.QPushButton("Open in Browser")
            btn.setToolTip(f"Open {tool['name']} in web browser")
            btn.clicked.connect(lambda _, url=tool["url"]: self.open_web_tool(url))
        elif tool.get("is_command", False):
            btn = QtWidgets.QPushButton("Run Command")
            btn.setToolTip(f"Execute {tool['name']}")
            btn.clicked.connect(lambda _, name=tool["name"]: self.run_command(name))
        else:
            btn = QtWidgets.QPushButton("Download")
            btn.setToolTip(f"Download {tool['name']}")
            btn.clicked.connect(lambda _, url=tool["url"], name=tool["name"]: self.start_download(url, name))
        
        layout.addWidget(btn)

        return card

    def populate_tools(self):
        row = 0
        col = 0
        max_cols = 4

        for tool in self.tools:
            card = self.create_tool_card(tool)
            self.tool_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def open_web_tool(self, url):
        import webbrowser
        webbrowser.open(url)

    def open_discord(self):
        import webbrowser
        discord_url = "https://discord.gg/2HneyYnk"
        webbrowser.open(discord_url)

    def open_website(self):
        import webbrowser
        website_url = "https://pc-check-learning.netlify.app/"
        webbrowser.open(website_url)

    def run_command(self, command_name):
        if command_name == "Check Services":
            powershell_cmd = "get-service | findstr -i 'pcasvc'; get-service | findstr -i 'DPS'; get-service | findstr -i 'Diagtrack'; get-service | findstr -i 'sysmain'; get-service | findstr -i 'eventlog'; get-service | findstr -i 'sgrmbroker'; get-service | findstr -i 'cdpusersvc'; get-service | findstr -i 'appinfo'; get-service | findstr -i 'WSearch'; get-service | findstr -i 'VSS'; Read-Host 'Press Enter to exit...'"
            
            import subprocess
            try:
                subprocess.Popen([
                    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", 
                    "-Command", powershell_cmd
                ], shell=True)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Command Error", f"Failed to run command:\n{str(e)}")

    def filter_tools(self, text=None):
        search_text = self.search_bar.text().lower()
        selected_category = self.category_filter.currentText()
        
        for i in range(self.tool_layout.count()):
            widget = self.tool_layout.itemAt(i).widget()
            if widget:
                title_layout = widget.layout().itemAt(0).layout()
                title_label = title_layout.itemAt(1).widget()
                tool_name = title_label.text().lower()
                
                category_match = True
                if selected_category != "All Categories":
                    category_found = False
                    for j in range(widget.layout().count()):
                        item = widget.layout().itemAt(j)
                        if item and item.widget() and isinstance(item.widget(), QtWidgets.QLabel):
                            label_text = item.widget().text()
                            if label_text == selected_category:
                                category_found = True
                                break
                    category_match = category_found
                
                search_match = search_text in tool_name or search_text == ""
                widget.setVisible(search_match and category_match)
        
        visible_count = sum(1 for i in range(self.tool_layout.count()) 
                          if self.tool_layout.itemAt(i).widget().isVisible())
        self.status_bar.showMessage(f"Showing {visible_count} of {len(self.tools)} tools")

    def start_download(self, url, name):
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
        if self.current_downloader:
            self.current_downloader.cancel()
            self.progress_label.setText("Download cancelled")
            self.progress_bar.setVisible(False)
            self.cancel_btn.setVisible(False)
            QtWidgets.QMessageBox.warning(self, "Download Cancelled", "The download was cancelled.")

    def on_progress(self, percent):
        self.progress_bar.setValue(percent)
        self.progress_label.setText(f"Downloading... {percent}%")

    def on_finished(self, filepath):
        self.progress_label.setText("Download complete!")
        self.progress_bar.setVisible(False)
        self.cancel_btn.setVisible(False)
        QtWidgets.QMessageBox.information(self, "Download Complete", f"File saved to:\n{filepath}")
        self.current_downloader = None

    def on_error(self, msg):
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
    logo_path = os.path.join(base_dir, "logo.png")
    icon_path = os.path.join(base_dir, "icon.ico") if not os.path.exists(logo_path) else logo_path
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