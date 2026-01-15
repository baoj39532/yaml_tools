"""
信息提取器UI标签页
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFileDialog, QGroupBox, QLabel, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QLineEdit, 
                             QComboBox, QCheckBox, QHeaderView)
from PyQt5.QtCore import Qt
from core.info_extractor import InfoExtractor
from utils.excel_exporter import ExcelExporter
import os


class ExtractorTab(QWidget):
    """信息提取器标签页"""
    
    def __init__(self):
        super().__init__()
        self.extractor = InfoExtractor()
        self.excel_exporter = ExcelExporter()
        self.extraction_results = []
        self.selected_path = ""
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 路径选择区域
        path_group = QGroupBox("选择路径")
        path_layout = QVBoxLayout()
        
        folder_layout = QHBoxLayout()
        self.path_label = QLabel("未选择路径")
        self.select_folder_btn = QPushButton("选择文件夹")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.select_file_btn = QPushButton("选择文件")
        self.select_file_btn.clicked.connect(self.select_file)
        
        folder_layout.addWidget(self.path_label)
        folder_layout.addWidget(self.select_folder_btn)
        folder_layout.addWidget(self.select_file_btn)
        folder_layout.addStretch()
        
        path_layout.addLayout(folder_layout)
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        # Key配置区域
        key_group = QGroupBox("提取Key配置")
        key_layout = QVBoxLayout()
        
        # Key配置表格
        self.key_table = QTableWidget()
        self.key_table.setColumnCount(6)
        self.key_table.setHorizontalHeaderLabels([
            "Key路径", "别名", "ConfigMap文件", "文件Key", "文件类型", "提取Key"
        ])
        self.key_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        key_layout.addWidget(self.key_table)
        
        # 添加/删除按钮
        key_btn_layout = QHBoxLayout()
        self.add_key_btn = QPushButton("添加Key")
        self.add_key_btn.clicked.connect(self.add_key_row)
        self.remove_key_btn = QPushButton("删除选中")
        self.remove_key_btn.clicked.connect(self.remove_key_row)
        key_btn_layout.addWidget(self.add_key_btn)
        key_btn_layout.addWidget(self.remove_key_btn)
        key_btn_layout.addStretch()
        
        key_layout.addLayout(key_btn_layout)
        key_group.setLayout(key_layout)
        layout.addWidget(key_group)
        
        # 添加初始行
        self.add_key_row()
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.extract_btn = QPushButton("提取信息")
        self.extract_btn.clicked.connect(self.execute_extraction)
        button_layout.addWidget(self.extract_btn)
        
        self.export_btn = QPushButton("导出提取结果到Excel")
        self.export_btn.clicked.connect(self.export_results)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 状态标签
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def select_folder(self):
        """选择文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.selected_path = folder
            folder_name = os.path.basename(folder)
            self.path_label.setText(f"已选择文件夹: {folder_name}")
    
    def select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择YAML文件", "", "YAML文件 (*.yaml *.yml)"
        )
        if file_path:
            self.selected_path = file_path
            file_name = os.path.basename(file_path)
            self.path_label.setText(f"已选择文件: {file_name}")
    
    def add_key_row(self):
        """添加Key配置行"""
        row = self.key_table.rowCount()
        self.key_table.insertRow(row)
        
        # Key路径输入框
        key_input = QLineEdit()
        key_input.setPlaceholderText("如: spec.replicas")
        self.key_table.setCellWidget(row, 0, key_input)
        
        # 别名输入框
        alias_input = QLineEdit()
        alias_input.setPlaceholderText("如: 副本数")
        self.key_table.setCellWidget(row, 1, alias_input)
        
        # ConfigMap文件复选框
        is_configmap = QCheckBox()
        is_configmap.stateChanged.connect(lambda state, r=row: self.on_configmap_changed(r, state))
        self.key_table.setCellWidget(row, 2, is_configmap)
        
        # 文件Key输入框
        file_key_input = QLineEdit()
        file_key_input.setPlaceholderText("如: application.yaml")
        file_key_input.setEnabled(False)
        self.key_table.setCellWidget(row, 3, file_key_input)
        
        # 文件类型下拉框
        file_type_combo = QComboBox()
        file_type_combo.addItems(["text", "yaml", "properties"])
        file_type_combo.setEnabled(False)
        self.key_table.setCellWidget(row, 4, file_type_combo)
        
        # 提取Key输入框
        extract_key_input = QLineEdit()
        extract_key_input.setPlaceholderText("如: server.port")
        extract_key_input.setEnabled(False)
        self.key_table.setCellWidget(row, 5, extract_key_input)
    
    def on_configmap_changed(self, row, state):
        """ConfigMap复选框状态改变"""
        is_checked = (state == Qt.Checked)
        
        # 启用/禁用相关控件
        self.key_table.cellWidget(row, 3).setEnabled(is_checked)  # 文件Key
        self.key_table.cellWidget(row, 4).setEnabled(is_checked)  # 文件类型
        self.key_table.cellWidget(row, 5).setEnabled(is_checked)  # 提取Key
        
        # 禁用/启用普通Key路径
        self.key_table.cellWidget(row, 0).setEnabled(not is_checked)
    
    def remove_key_row(self):
        """删除选中的Key行"""
        current_row = self.key_table.currentRow()
        if current_row >= 0:
            self.key_table.removeRow(current_row)
    
    def get_extract_configs(self):
        """获取提取配置"""
        extract_configs = []
        
        for row in range(self.key_table.rowCount()):
            alias = self.key_table.cellWidget(row, 1).text().strip()
            is_configmap = self.key_table.cellWidget(row, 2).isChecked()
            
            if is_configmap:
                # ConfigMap文件提取
                file_key = self.key_table.cellWidget(row, 3).text().strip()
                if not file_key:
                    continue
                
                config = {
                    'is_configmap_file': True,
                    'file_key': file_key,
                    'file_type': self.key_table.cellWidget(row, 4).currentText(),
                    'extract_key': self.key_table.cellWidget(row, 5).text().strip(),
                    'alias': alias
                }
            else:
                # 普通Key提取
                key_path = self.key_table.cellWidget(row, 0).text().strip()
                if not key_path:
                    continue
                
                config = {
                    'key_path': key_path,
                    'alias': alias,
                    'is_configmap_file': False
                }
            
            extract_configs.append(config)
        
        return extract_configs

    def get_key_configs(self):
        """获取可持久化的Key配置"""
        configs = []
        for row in range(self.key_table.rowCount()):
            alias = self.key_table.cellWidget(row, 1).text().strip()
            is_configmap = self.key_table.cellWidget(row, 2).isChecked()
            if is_configmap:
                file_key = self.key_table.cellWidget(row, 3).text().strip()
                if not file_key:
                    continue
                configs.append({
                    "key_path": "",
                    "alias": alias,
                    "is_configmap_file": True,
                    "file_key": file_key,
                    "file_type": self.key_table.cellWidget(row, 4).currentText(),
                    "compare_key": "",
                    "extract_key": self.key_table.cellWidget(row, 5).text().strip(),
                })
            else:
                key_path = self.key_table.cellWidget(row, 0).text().strip()
                if not key_path:
                    continue
                configs.append({
                    "key_path": key_path,
                    "alias": alias,
                    "is_configmap_file": False,
                    "file_key": "",
                    "file_type": "text",
                    "compare_key": "",
                    "extract_key": "",
                })
        return configs

    def set_key_configs(self, configs):
        """从配置加载Key配置"""
        self.key_table.setRowCount(0)
        if not configs:
            self.add_key_row()
            return
        for config in configs:
            self.add_key_row()
            row = self.key_table.rowCount() - 1
            is_configmap = bool(config.get("is_configmap_file", False))
            self.key_table.cellWidget(row, 1).setText(config.get("alias", ""))
            if is_configmap:
                self.key_table.cellWidget(row, 3).setText(config.get("file_key", ""))
                file_type = config.get("file_type", "text")
                combo = self.key_table.cellWidget(row, 4)
                idx = combo.findText(file_type)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                self.key_table.cellWidget(row, 5).setText(config.get("extract_key", ""))
            else:
                self.key_table.cellWidget(row, 0).setText(config.get("key_path", ""))
            checkbox = self.key_table.cellWidget(row, 2)
            checkbox.setChecked(is_configmap)
            self.on_configmap_changed(row, Qt.Checked if is_configmap else Qt.Unchecked)
    
    def execute_extraction(self):
        """执行提取"""
        if not self.selected_path:
            QMessageBox.warning(self, "警告", "请先选择文件或文件夹")
            return
        
        extract_configs = self.get_extract_configs()
        
        if not extract_configs:
            QMessageBox.warning(self, "警告", "请至少配置一个提取Key")
            return
        
        self.status_label.setText("正在提取信息...")
        self.extraction_results = self.extractor.extract_from_path(
            self.selected_path, extract_configs
        )
        
        if self.extractor.get_errors():
            error_msg = "\n".join(self.extractor.get_errors())
            QMessageBox.warning(self, "提取警告", f"提取过程中出现以下错误:\n{error_msg}")
            self.extractor.clear_errors()
        
        result_count = len(self.extraction_results)
        self.status_label.setText(f"提取完成，共提取 {result_count} 个资源的信息")
        
        if result_count == 0:
            QMessageBox.information(self, "结果", "未找到可提取的资源")
        else:
            QMessageBox.information(self, "结果", f"成功提取 {result_count} 个资源的信息")
    
    def export_results(self):
        """导出提取结果"""
        if not self.extraction_results:
            QMessageBox.warning(self, "警告", "没有可导出的提取结果，请先执行提取")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        
        if output_dir:
            success = self.excel_exporter.export_extraction_result(
                self.extraction_results, output_dir
            )
            
            if success:
                QMessageBox.information(self, "成功", f"成功导出提取结果到:\n{output_dir}")
            else:
                error_msg = "\n".join(self.excel_exporter.get_errors())
                QMessageBox.critical(self, "错误", f"导出失败:\n{error_msg}")
                self.excel_exporter.clear_errors()
