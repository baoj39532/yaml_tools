"""
Key提取器UI标签页
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFileDialog, QGroupBox, QLabel, QTreeWidget, 
                             QTreeWidgetItem, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from core.key_extractor import KeyExtractor
from utils.excel_exporter import ExcelExporter
from typing import List, Dict
import os


class KeyExtractorTab(QWidget):
    """Key提取器标签页"""
    
    def __init__(self):
        super().__init__()
        self.extractor = KeyExtractor()
        self.excel_exporter = ExcelExporter()
        self.extracted_keys = []
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
        
        # 资源类型区域
        resource_group = QGroupBox("资源类型")
        resource_layout = QHBoxLayout()
        resource_info = QLabel("当前支持: ConfigMap")
        resource_layout.addWidget(resource_info)
        resource_layout.addStretch()
        resource_group.setLayout(resource_layout)
        layout.addWidget(resource_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.extract_btn = QPushButton("提取Key")
        self.extract_btn.clicked.connect(self.execute_extraction)
        button_layout.addWidget(self.extract_btn)
        
        self.export_btn = QPushButton("导出到Excel")
        self.export_btn.clicked.connect(self.export_keys)
        self.export_btn.setEnabled(False)  # 初始禁用
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 结果展示树形控件
        result_group = QGroupBox("提取结果")
        result_layout = QVBoxLayout()
        
        # 统计信息
        self.stats_label = QLabel("尚未提取")
        result_layout.addWidget(self.stats_label)
        
        # Key树形结构
        self.result_tree = QTreeWidget()
        self.result_tree.setHeaderLabels(["Key层级结构"])
        self.result_tree.header().setSectionResizeMode(QHeaderView.Stretch)
        self.result_tree.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.result_tree.setSelectionBehavior(QTreeWidget.SelectRows)
        self.result_tree.setAnimated(True)  # 启用动画
        result_layout.addWidget(self.result_tree)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
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
            self.status_label.setText(f"已选择路径: {folder}")
    
    def select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择YAML文件", "", "YAML文件 (*.yaml *.yml)"
        )
        if file_path:
            self.selected_path = file_path
            file_name = os.path.basename(file_path)
            self.path_label.setText(f"已选择文件: {file_name}")
            self.status_label.setText(f"已选择路径: {file_path}")
    
    def execute_extraction(self):
        """执行Key提取"""
        if not self.selected_path:
            QMessageBox.warning(self, "警告", "请先选择文件夹或文件")
            return
        
        self.status_label.setText("正在提取Key...")
        self.extract_btn.setEnabled(False)
        
        try:
            # 执行提取
            keys_set = self.extractor.extract_from_path(self.selected_path)
            
            # 排序
            self.extracted_keys = self.extractor.get_sorted_keys(keys_set)
            
            # 显示结果
            self.display_keys()
            
            # 检查错误
            errors = self.extractor.get_errors()
            if errors:
                error_msg = "\n".join(errors[:5])  # 只显示前5个错误
                if len(errors) > 5:
                    error_msg += f"\n... 还有 {len(errors) - 5} 个错误"
                QMessageBox.warning(self, "提取完成（有错误）", 
                                   f"提取完成，但遇到以下错误：\n\n{error_msg}")
            else:
                self.status_label.setText(f"提取完成，共 {len(self.extracted_keys)} 个去重后的Key")
            
            # 启用导出按钮
            self.export_btn.setEnabled(len(self.extracted_keys) > 0)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"提取失败：{str(e)}")
            self.status_label.setText("提取失败")
        finally:
            self.extract_btn.setEnabled(True)
    
    def display_keys(self):
        """在树形控件中显示提取的Key"""
        self.result_tree.clear()
        
        if not self.extracted_keys:
            self.stats_label.setText("未提取到任何Key")
            return
        
        # 构建树形结构
        tree_dict = self._build_tree_structure(self.extracted_keys)
        
        # 递归添加到QTreeWidget
        self._add_tree_items(self.result_tree.invisibleRootItem(), tree_dict)
        
        # 展开所有节点
        self.result_tree.expandAll()
        
        # 更新统计信息
        self.stats_label.setText(f"共提取 {len(self.extracted_keys)} 个叶子节点Key（树形结构展示）")
    
    def _build_tree_structure(self, keys: List[str]) -> Dict:
        """
        将平铺的key列表转换为树形字典结构
        
        Args:
            keys: 如 ["database.host", "database.port", "server.host"]
            
        Returns:
            嵌套字典：{
                "database": {
                    "host": {},
                    "port": {}
                },
                "server": {
                    "host": {}
                }
            }
        """
        tree = {}
        for key in keys:
            parts = key.split('.')
            current = tree
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
        return tree
    
    def _add_tree_items(self, parent_item, tree_dict: Dict):
        """
        递归添加树节点到QTreeWidget
        
        Args:
            parent_item: 父节点项
            tree_dict: 树形字典
        """
        for key, subtree in sorted(tree_dict.items()):
            item = QTreeWidgetItem(parent_item)
            item.setText(0, key)
            
            if subtree:  # 有子节点
                self._add_tree_items(item, subtree)
    
    def export_keys(self):
        """导出Key列表到Excel（树形结构）"""
        if not self.extracted_keys:
            QMessageBox.warning(self, "警告", "没有可导出的Key")
            return
        
        # 选择保存路径
        default_name = "configmap_keys_tree.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存Excel文件", default_name, "Excel文件 (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            self.status_label.setText("正在导出到Excel...")
            
            # 使用树形导出方法
            self.excel_exporter.export_key_tree(self.extracted_keys, file_path)
            
            QMessageBox.information(self, "成功", f"Key树形结构已导出到：\n{file_path}")
            self.status_label.setText(f"导出成功: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{str(e)}")
            self.status_label.setText("导出失败")
    
    def clear_results(self):
        """清除结果"""
        self.extracted_keys = []
        self.result_tree.clear()
        self.stats_label.setText("尚未提取")
        self.export_btn.setEnabled(False)
        self.status_label.setText("")
