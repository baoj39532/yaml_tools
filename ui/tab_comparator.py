"""
YAML比较器UI标签页
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFileDialog, QGroupBox, QRadioButton, QLabel,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QLineEdit, QComboBox, QCheckBox, QHeaderView)
from PyQt5.QtCore import Qt
from core.yaml_comparator import YAMLComparator
from utils.excel_exporter import ExcelExporter
import os


class ComparatorTab(QWidget):
    """YAML比较器标签页"""
    
    def __init__(self):
        super().__init__()
        self.comparator = YAMLComparator()
        self.excel_exporter = ExcelExporter()
        self.comparison_results = []
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 比较模式选择
        mode_group = QGroupBox("比较模式")
        mode_layout = QVBoxLayout()
        
        self.cluster_mode_radio = QRadioButton("集群文件夹比较")
        self.cluster_mode_radio.setChecked(True)
        self.cluster_mode_radio.toggled.connect(self.on_mode_changed)
        
        self.file_mode_radio = QRadioButton("单文件比较")
        
        mode_layout.addWidget(self.cluster_mode_radio)
        mode_layout.addWidget(self.file_mode_radio)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # 集群模式选择区域
        self.cluster_group = QGroupBox("集群文件夹选择")
        cluster_layout = QVBoxLayout()
        
        cluster1_layout = QHBoxLayout()
        self.cluster1_label = QLabel("集群1: 未选择")
        self.select_cluster1_btn = QPushButton("选择集群1")
        self.select_cluster1_btn.clicked.connect(lambda: self.select_cluster(1))
        cluster1_layout.addWidget(self.cluster1_label)
        cluster1_layout.addWidget(self.select_cluster1_btn)
        cluster1_layout.addStretch()
        
        cluster2_layout = QHBoxLayout()
        self.cluster2_label = QLabel("集群2: 未选择")
        self.select_cluster2_btn = QPushButton("选择集群2")
        self.select_cluster2_btn.clicked.connect(lambda: self.select_cluster(2))
        cluster2_layout.addWidget(self.cluster2_label)
        cluster2_layout.addWidget(self.select_cluster2_btn)
        cluster2_layout.addStretch()
        
        cluster_layout.addLayout(cluster1_layout)
        cluster_layout.addLayout(cluster2_layout)
        self.cluster_group.setLayout(cluster_layout)
        layout.addWidget(self.cluster_group)
        
        # 文件模式选择区域
        self.file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout()
        
        file1_layout = QHBoxLayout()
        self.file1_label = QLabel("文件1: 未选择")
        self.select_file1_btn = QPushButton("选择文件1")
        self.select_file1_btn.clicked.connect(lambda: self.select_file(1))
        file1_layout.addWidget(self.file1_label)
        file1_layout.addWidget(self.select_file1_btn)
        file1_layout.addStretch()
        
        file2_layout = QHBoxLayout()
        self.file2_label = QLabel("文件2: 未选择")
        self.select_file2_btn = QPushButton("选择文件2")
        self.select_file2_btn.clicked.connect(lambda: self.select_file(2))
        file2_layout.addWidget(self.file2_label)
        file2_layout.addWidget(self.select_file2_btn)
        file2_layout.addStretch()
        
        file_layout.addLayout(file1_layout)
        file_layout.addLayout(file2_layout)
        self.file_group.setLayout(file_layout)
        self.file_group.setVisible(False)
        layout.addWidget(self.file_group)
        
        # 比较Key配置区域
        key_group = QGroupBox("比较Key配置")
        key_layout = QVBoxLayout()
        
        # Key配置表格
        self.key_table = QTableWidget()
        self.key_table.setColumnCount(5)
        self.key_table.setHorizontalHeaderLabels([
            "Key路径", "ConfigMap文件", "文件Key", "文件类型", "比较Key"
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
        
        self.compare_btn = QPushButton("执行比较")
        self.compare_btn.clicked.connect(self.execute_comparison)
        button_layout.addWidget(self.compare_btn)
        
        self.export_btn = QPushButton("导出比较结果到Excel")
        self.export_btn.clicked.connect(self.export_results)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 状态标签
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 初始化路径
        self.cluster1_path = ""
        self.cluster2_path = ""
        self.file1_path = ""
        self.file2_path = ""
    
    def on_mode_changed(self):
        """比较模式改变"""
        is_cluster_mode = self.cluster_mode_radio.isChecked()
        self.cluster_group.setVisible(is_cluster_mode)
        self.file_group.setVisible(not is_cluster_mode)
    
    def select_cluster(self, cluster_num):
        """选择集群文件夹"""
        folder = QFileDialog.getExistingDirectory(self, f"选择集群{cluster_num}文件夹")
        if folder:
            cluster_name = os.path.basename(folder)
            if cluster_num == 1:
                self.cluster1_path = folder
                self.cluster1_label.setText(f"集群1: {cluster_name}")
            else:
                self.cluster2_path = folder
                self.cluster2_label.setText(f"集群2: {cluster_name}")
    
    def select_file(self, file_num):
        """选择YAML文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"选择文件{file_num}", "", "YAML文件 (*.yaml *.yml)"
        )
        if file_path:
            file_name = os.path.basename(file_path)
            if file_num == 1:
                self.file1_path = file_path
                self.file1_label.setText(f"文件1: {file_name}")
            else:
                self.file2_path = file_path
                self.file2_label.setText(f"文件2: {file_name}")
    
    def add_key_row(self):
        """添加Key配置行"""
        row = self.key_table.rowCount()
        self.key_table.insertRow(row)
        
        # Key路径输入框
        key_input = QLineEdit()
        key_input.setPlaceholderText("如: spec.replicas")
        self.key_table.setCellWidget(row, 0, key_input)
        
        # ConfigMap文件复选框
        is_configmap = QCheckBox()
        is_configmap.stateChanged.connect(lambda state, r=row: self.on_configmap_changed(r, state))
        self.key_table.setCellWidget(row, 1, is_configmap)
        
        # 文件Key输入框
        file_key_input = QLineEdit()
        file_key_input.setPlaceholderText("如: application.yaml")
        file_key_input.setEnabled(False)
        self.key_table.setCellWidget(row, 2, file_key_input)
        
        # 文件类型下拉框
        file_type_combo = QComboBox()
        file_type_combo.addItems(["text", "yaml", "properties"])
        file_type_combo.setEnabled(False)
        self.key_table.setCellWidget(row, 3, file_type_combo)
        
        # 比较Key输入框
        compare_key_input = QLineEdit()
        compare_key_input.setPlaceholderText("如: server.port")
        compare_key_input.setEnabled(False)
        self.key_table.setCellWidget(row, 4, compare_key_input)
    
    def on_configmap_changed(self, row, state):
        """ConfigMap复选框状态改变"""
        is_checked = (state == Qt.Checked)
        
        # 启用/禁用相关控件
        self.key_table.cellWidget(row, 2).setEnabled(is_checked)  # 文件Key
        self.key_table.cellWidget(row, 3).setEnabled(is_checked)  # 文件类型
        self.key_table.cellWidget(row, 4).setEnabled(is_checked)  # 比较Key
        
        # 禁用/启用普通Key路径
        self.key_table.cellWidget(row, 0).setEnabled(not is_checked)
    
    def remove_key_row(self):
        """删除选中的Key行"""
        current_row = self.key_table.currentRow()
        if current_row >= 0:
            self.key_table.removeRow(current_row)
    
    def get_compare_keys(self):
        """获取比较Key配置"""
        compare_keys = []
        
        for row in range(self.key_table.rowCount()):
            is_configmap = self.key_table.cellWidget(row, 1).isChecked()
            
            if is_configmap:
                # ConfigMap文件比较
                file_key = self.key_table.cellWidget(row, 2).text().strip()
                if not file_key:
                    continue
                
                config = {
                    'is_configmap_file': True,
                    'file_key': file_key,
                    'file_type': self.key_table.cellWidget(row, 3).currentText(),
                    'compare_key': self.key_table.cellWidget(row, 4).text().strip()
                }
            else:
                # 普通Key比较
                key_path = self.key_table.cellWidget(row, 0).text().strip()
                if not key_path:
                    continue
                
                config = {
                    'key_path': key_path,
                    'is_configmap_file': False
                }
            
            compare_keys.append(config)
        
        return compare_keys
    
    def execute_comparison(self):
        """执行比较"""
        compare_keys = self.get_compare_keys()
        
        if not compare_keys:
            QMessageBox.warning(self, "警告", "请至少配置一个比较Key")
            return
        
        if self.cluster_mode_radio.isChecked():
            # 集群模式
            if not self.cluster1_path or not self.cluster2_path:
                QMessageBox.warning(self, "警告", "请选择两个集群文件夹")
                return
            
            self.status_label.setText("正在比较集群...")
            self.comparison_results = self.comparator.compare_clusters(
                self.cluster1_path, self.cluster2_path, compare_keys
            )
        else:
            # 文件模式
            if not self.file1_path or not self.file2_path:
                QMessageBox.warning(self, "警告", "请选择两个YAML文件")
                return
            
            self.status_label.setText("正在比较文件...")
            self.comparison_results = self.comparator.compare_files(
                self.file1_path, self.file2_path, compare_keys
            )
        
        if self.comparator.get_errors():
            error_msg = "\n".join(self.comparator.get_errors())
            QMessageBox.warning(self, "比较警告", f"比较过程中出现以下错误:\n{error_msg}")
            self.comparator.clear_errors()
        
        diff_count = len(self.comparison_results)
        self.status_label.setText(f"比较完成，发现 {diff_count} 个差异项")
        
        if diff_count == 0:
            QMessageBox.information(self, "结果", "两个对象完全相同，没有发现差异")
        else:
            QMessageBox.information(self, "结果", f"发现 {diff_count} 个有差异的资源")
    
    def export_results(self):
        """导出比较结果"""
        if not self.comparison_results:
            QMessageBox.warning(self, "警告", "没有可导出的比较结果，请先执行比较")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        
        if output_dir:
            if self.cluster_mode_radio.isChecked():
                cluster1_name = os.path.basename(self.cluster1_path)
                cluster2_name = os.path.basename(self.cluster2_path)
            else:
                cluster1_name = "文件1"
                cluster2_name = "文件2"
            
            success = self.excel_exporter.export_comparison_result(
                self.comparison_results, output_dir, cluster1_name, cluster2_name
            )
            
            if success:
                QMessageBox.information(self, "成功", f"成功导出比较结果到:\n{output_dir}")
            else:
                error_msg = "\n".join(self.excel_exporter.get_errors())
                QMessageBox.critical(self, "错误", f"导出失败:\n{error_msg}")
                self.excel_exporter.clear_errors()
