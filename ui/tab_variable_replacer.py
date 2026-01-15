"""
变量替换器UI标签页
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QGroupBox, QLabel, QTableWidget,
                             QMessageBox, QLineEdit, QHeaderView)
from core.variable_replacer import VariableReplacer
import os


class VariableReplacerTab(QWidget):
    """变量替换器标签页"""

    def __init__(self):
        super().__init__()
        self.replacer = VariableReplacer()
        self.selected_path = ""
        self.output_dir = ""
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 路径选择区域
        path_group = QGroupBox("选择路径")
        path_layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.path_label = QLabel("未选择路径")
        self.select_folder_btn = QPushButton("选择文件夹")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.select_file_btn = QPushButton("选择文件")
        self.select_file_btn.clicked.connect(self.select_file)
        input_layout.addWidget(self.path_label)
        input_layout.addWidget(self.select_folder_btn)
        input_layout.addWidget(self.select_file_btn)
        input_layout.addStretch()
        path_layout.addLayout(input_layout)

        output_layout = QHBoxLayout()
        self.output_label = QLabel("未选择输出目录")
        self.select_output_btn = QPushButton("选择输出目录")
        self.select_output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.select_output_btn)
        output_layout.addStretch()
        path_layout.addLayout(output_layout)

        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        # 变量配置区域
        var_group = QGroupBox("变量配置")
        var_layout = QVBoxLayout()

        self.var_table = QTableWidget()
        self.var_table.setColumnCount(2)
        self.var_table.setHorizontalHeaderLabels(["变量名", "变量值"])
        self.var_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        var_layout.addWidget(self.var_table)

        var_btn_layout = QHBoxLayout()
        self.add_var_btn = QPushButton("添加变量")
        self.add_var_btn.clicked.connect(self.add_var_row)
        self.remove_var_btn = QPushButton("删除选中")
        self.remove_var_btn.clicked.connect(self.remove_var_row)
        var_btn_layout.addWidget(self.add_var_btn)
        var_btn_layout.addWidget(self.remove_var_btn)
        var_btn_layout.addStretch()
        var_layout.addLayout(var_btn_layout)

        var_group.setLayout(var_layout)
        layout.addWidget(var_group)

        # 添加初始行
        self.add_var_row()

        # 操作按钮
        button_layout = QHBoxLayout()
        self.replace_btn = QPushButton("执行替换并导出")
        self.replace_btn.clicked.connect(self.execute_replace)
        button_layout.addWidget(self.replace_btn)
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
            self.path_label.setText(f"已选择文件夹: {os.path.basename(folder)}")

    def select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择YAML文件", "", "YAML文件 (*.yaml *.yml)"
        )
        if file_path:
            self.selected_path = file_path
            self.path_label.setText(f"已选择文件: {os.path.basename(file_path)}")

    def select_output_dir(self):
        """选择输出目录"""
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            self.output_dir = folder
            self.output_label.setText(f"输出目录: {os.path.basename(folder)}")

    def add_var_row(self):
        """添加变量行"""
        row = self.var_table.rowCount()
        self.var_table.insertRow(row)

        name_input = QLineEdit()
        name_input.setPlaceholderText("如: SOME_KEY")
        self.var_table.setCellWidget(row, 0, name_input)

        value_input = QLineEdit()
        value_input.setPlaceholderText("如: 123 或 ''")
        self.var_table.setCellWidget(row, 1, value_input)

    def remove_var_row(self):
        """删除选中的变量行"""
        current_row = self.var_table.currentRow()
        if current_row >= 0:
            self.var_table.removeRow(current_row)

    def get_variables(self):
        """获取变量配置"""
        variables = []
        for row in range(self.var_table.rowCount()):
            name = self.var_table.cellWidget(row, 0).text().strip()
            if not name:
                continue
            value = self.var_table.cellWidget(row, 1).text()
            variables.append({"name": name, "value": value})
        return variables

    def set_variables(self, variables):
        """加载变量配置"""
        self.var_table.setRowCount(0)
        if not variables:
            self.add_var_row()
            return
        for item in variables:
            self.add_var_row()
            row = self.var_table.rowCount() - 1
            self.var_table.cellWidget(row, 0).setText(item.get("name", ""))
            self.var_table.cellWidget(row, 1).setText(item.get("value", ""))

    def execute_replace(self):
        """执行替换并导出"""
        if not self.selected_path:
            QMessageBox.warning(self, "警告", "请先选择文件或文件夹")
            return
        if not self.output_dir:
            QMessageBox.warning(self, "警告", "请先选择输出目录")
            return

        variables = self.get_variables()
        if not variables:
            QMessageBox.warning(self, "警告", "请至少配置一个变量")
            return

        self.status_label.setText("正在执行替换...")
        success = self.replacer.replace_to_output(self.selected_path, self.output_dir, variables)

        if not success:
            error_msg = "\n".join(self.replacer.get_errors())
            QMessageBox.warning(self, "替换失败", error_msg)
            self.replacer.clear_errors()
            self.status_label.setText("替换失败")
            return

        self.status_label.setText("替换完成")
        QMessageBox.information(self, "成功", f"替换完成，输出目录:\n{self.output_dir}")
