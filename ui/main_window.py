"""
主窗口
"""

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QAction, QMessageBox,
                             QDesktopWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ui.tab_command_gen import CommandGeneratorTab
from ui.tab_comparator import ComparatorTab
from ui.tab_extractor import ExtractorTab
from config import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # 居中显示
        self.center()
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # 添加三个功能标签页
        self.command_gen_tab = CommandGeneratorTab()
        self.comparator_tab = ComparatorTab()
        self.extractor_tab = ExtractorTab()
        
        self.tabs.addTab(self.command_gen_tab, "命令生成器")
        self.tabs.addTab(self.comparator_tab, "YAML比较器")
        self.tabs.addTab(self.extractor_tab, "信息提取器")
        
        # 设置样式
        self.set_style()
    
    def center(self):
        """窗口居中"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出应用程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.setStatusTip("关于本程序")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        usage_action = QAction("使用说明(&U)", self)
        usage_action.setStatusTip("查看使用说明")
        usage_action.triggered.connect(self.show_usage)
        help_menu.addAction(usage_action)
    
    def show_about(self):
        """显示关于对话框"""
        about_text = f"""
        <h2>{APP_NAME}</h2>
        <p>版本: {APP_VERSION}</p>
        <p>这是一个Kubernetes YAML管理工具，提供以下功能：</p>
        <ul>
            <li>YAML命令生成器：生成部署和删除命令</li>
            <li>YAML比较器：比较两个集群或文件的差异</li>
            <li>信息提取器：提取YAML中的指定信息</li>
        </ul>
        <p>© 2024 YAML Tools. All rights reserved.</p>
        """
        QMessageBox.about(self, "关于", about_text)
    
    def show_usage(self):
        """显示使用说明"""
        usage_text = """
        <h3>使用说明</h3>
        
        <h4>1. 命令生成器</h4>
        <ol>
            <li>选择集群文件夹</li>
            <li>点击"解析并显示资源"查看所有资源</li>
            <li>选择资源类型或表格中的特定资源</li>
            <li>点击"生成删除命令"或"生成部署命令"</li>
            <li>可导出资源表到Excel</li>
        </ol>
        
        <h4>2. YAML比较器</h4>
        <ol>
            <li>选择比较模式（集群文件夹或单文件）</li>
            <li>选择要比较的两个对象</li>
            <li>配置比较Key（支持普通Key和ConfigMap文件）</li>
            <li>点击"执行比较"</li>
            <li>点击"导出比较结果到Excel"</li>
        </ol>
        
        <h4>3. 信息提取器</h4>
        <ol>
            <li>选择文件或文件夹</li>
            <li>配置提取Key和别名</li>
            <li>点击"提取信息"</li>
            <li>点击"导出提取结果到Excel"</li>
        </ol>
        
        <h4>文件夹结构要求</h4>
        <p>集群名/命名空间/资源类型/YAML文件</p>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("使用说明")
        msg.setTextFormat(Qt.RichText)
        msg.setText(usage_text)
        msg.exec_()
    
    def set_style(self):
        """设置样式"""
        style = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 20px;
            margin-right: 2px;
            border: 1px solid #cccccc;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 1px solid white;
        }
        
        QPushButton {
            background-color: #4472C4;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 3px;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #5584D4;
        }
        
        QPushButton:pressed {
            background-color: #3362B4;
        }
        
        QGroupBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        QTableWidget {
            border: 1px solid #cccccc;
            gridline-color: #e0e0e0;
        }
        
        QTableWidget::item:selected {
            background-color: #4472C4;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #e0e0e0;
            padding: 5px;
            border: 1px solid #cccccc;
            font-weight: bold;
        }
        
        QLineEdit {
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 4px;
        }
        
        QLineEdit:focus {
            border: 1px solid #4472C4;
        }
        
        QComboBox {
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 4px;
        }
        """
        self.setStyleSheet(style)
