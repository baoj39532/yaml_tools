"""
命令生成器UI标签页
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QFileDialog, 
                             QGroupBox, QCheckBox, QMessageBox, QLabel,
                             QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt
from core.yaml_parser import YAMLParser
from core.command_generator import CommandGenerator
from utils.excel_exporter import ExcelExporter
from config import SUPPORTED_RESOURCE_TYPES


class CommandGeneratorTab(QWidget):
    """命令生成器标签页"""
    
    def __init__(self):
        super().__init__()
        self.parser = YAMLParser()
        self.cmd_gen = CommandGenerator()
        self.excel_exporter = ExcelExporter()
        self.resources = []
        self.cluster_path = ""
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 文件夹选择区域
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("未选择集群文件夹")
        self.select_folder_btn = QPushButton("选择集群文件夹")
        self.select_folder_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.select_folder_btn)
        folder_layout.addStretch()
        layout.addLayout(folder_layout)
        
        # 资源类型选择区域
        type_group = QGroupBox("资源类型选择")
        type_layout = QHBoxLayout()
        self.type_checkboxes = {}
        for resource_type in SUPPORTED_RESOURCE_TYPES:
            checkbox = QCheckBox(resource_type)
            checkbox.setChecked(True)
            self.type_checkboxes[resource_type] = checkbox
            type_layout.addWidget(checkbox)
        type_layout.addStretch()
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # 资源表格
        self.resource_table = QTableWidget()
        self.resource_table.setColumnCount(5)
        self.resource_table.setHorizontalHeaderLabels(["集群名", "命名空间", "资源类型", "资源名", "文件路径"])
        self.resource_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.resource_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resource_table.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.resource_table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.parse_btn = QPushButton("解析并显示资源")
        self.parse_btn.clicked.connect(self.parse_and_display)
        button_layout.addWidget(self.parse_btn)
        
        self.export_excel_btn = QPushButton("导出资源表到Excel")
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        button_layout.addWidget(self.export_excel_btn)
        
        self.gen_delete_btn = QPushButton("生成删除命令")
        self.gen_delete_btn.clicked.connect(self.generate_delete_commands)
        button_layout.addWidget(self.gen_delete_btn)
        
        self.gen_deploy_btn = QPushButton("生成部署命令")
        self.gen_deploy_btn.clicked.connect(self.generate_deploy_commands)
        button_layout.addWidget(self.gen_deploy_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def select_folder(self):
        """选择集群文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择集群文件夹")
        if folder:
            self.cluster_path = folder
            self.folder_label.setText(f"已选择: {folder}")
    
    def parse_and_display(self):
        """解析并显示资源"""
        if not self.cluster_path:
            QMessageBox.warning(self, "警告", "请先选择集群文件夹")
            return
        
        # 解析集群
        self.resources = self.parser.parse_cluster_folder(self.cluster_path)
        
        if self.parser.get_errors():
            error_msg = "\n".join(self.parser.get_errors())
            QMessageBox.warning(self, "解析警告", f"解析过程中出现以下错误:\n{error_msg}")
            self.parser.clear_errors()
        
        if not self.resources:
            QMessageBox.information(self, "提示", "未找到有效的YAML资源")
            return
        
        # 显示资源
        self.display_resources(self.resources)
        QMessageBox.information(self, "成功", f"成功解析 {len(self.resources)} 个资源")
    
    def display_resources(self, resources):
        """在表格中显示资源"""
        self.resource_table.setRowCount(0)
        
        for resource in resources:
            row = self.resource_table.rowCount()
            self.resource_table.insertRow(row)
            
            self.resource_table.setItem(row, 0, QTableWidgetItem(resource.cluster))
            self.resource_table.setItem(row, 1, QTableWidgetItem(resource.namespace))
            self.resource_table.setItem(row, 2, QTableWidgetItem(resource.kind))
            self.resource_table.setItem(row, 3, QTableWidgetItem(resource.name))
            self.resource_table.setItem(row, 4, QTableWidgetItem(resource.file_path))
    
    def get_selected_resources(self):
        """获取选中的资源"""
        selected_rows = set()
        for item in self.resource_table.selectedItems():
            selected_rows.add(item.row())
        
        if selected_rows:
            # 返回选中的资源
            return [self.resources[row] for row in sorted(selected_rows)]
        else:
            # 没有选中，返回按资源类型过滤的资源
            selected_types = [t for t, cb in self.type_checkboxes.items() if cb.isChecked()]
            return self.cmd_gen.filter_resources_by_types(self.resources, selected_types)
    
    def export_to_excel(self):
        """导出资源表到Excel"""
        if not self.resources:
            QMessageBox.warning(self, "警告", "没有可导出的资源，请先解析集群")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存Excel文件", "", "Excel文件 (*.xlsx)"
        )
        
        if file_path:
            resources_to_export = self.get_selected_resources()
            success = self.excel_exporter.export_resource_table(resources_to_export, file_path)
            
            if success:
                QMessageBox.information(self, "成功", f"成功导出 {len(resources_to_export)} 个资源到Excel")
            else:
                error_msg = "\n".join(self.excel_exporter.get_errors())
                QMessageBox.critical(self, "错误", f"导出失败:\n{error_msg}")
                self.excel_exporter.clear_errors()
    
    def generate_delete_commands(self):
        """生成删除命令"""
        if not self.resources:
            QMessageBox.warning(self, "警告", "没有可用的资源，请先解析集群")
            return
        
        resources_to_delete = self.get_selected_resources()
        
        if not resources_to_delete:
            QMessageBox.warning(self, "警告", "没有选中任何资源")
            return
        
        commands = self.cmd_gen.generate_delete_commands(resources_to_delete)
        
        if not commands:
            QMessageBox.information(self, "提示", "没有生成任何删除命令")
            return
        
        # 保存到文件
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存删除命令文件", "delete_commands.sh", "Shell脚本 (*.sh)"
        )
        
        if file_path:
            success = self.cmd_gen.save_commands_to_file(commands, file_path)
            
            if success:
                QMessageBox.information(self, "成功", f"成功生成 {len(commands)} 条删除命令")
            else:
                error_msg = "\n".join(self.cmd_gen.get_errors())
                QMessageBox.critical(self, "错误", f"保存失败:\n{error_msg}")
                self.cmd_gen.clear_errors()
    
    def generate_deploy_commands(self):
        """生成部署命令"""
        if not self.resources:
            QMessageBox.warning(self, "警告", "没有可用的资源，请先解析集群")
            return
        
        resources_to_deploy = self.get_selected_resources()
        
        if not resources_to_deploy:
            QMessageBox.warning(self, "警告", "没有选中任何资源")
            return
        
        commands = self.cmd_gen.generate_deploy_commands(resources_to_deploy)
        
        if not commands:
            QMessageBox.information(self, "提示", "没有生成任何部署命令")
            return
        
        # 保存到文件
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存部署命令文件", "deploy_commands.sh", "Shell脚本 (*.sh)"
        )
        
        if file_path:
            success = self.cmd_gen.save_commands_to_file(commands, file_path)
            
            if success:
                QMessageBox.information(self, "成功", f"成功生成 {len(commands)} 条部署命令")
            else:
                error_msg = "\n".join(self.cmd_gen.get_errors())
                QMessageBox.critical(self, "错误", f"保存失败:\n{error_msg}")
                self.cmd_gen.clear_errors()
