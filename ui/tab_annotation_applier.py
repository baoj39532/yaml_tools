"""
标注回写导出UI标签页
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QGroupBox, QLabel, QMessageBox)
from core.annotation_applier import AnnotationApplier
import os


class AnnotationApplierTab(QWidget):
    """标注回写导出标签页"""

    def __init__(self):
        super().__init__()
        self.applier = AnnotationApplier()
        self.annotated_excel_path = ""
        self.cluster_path = ""
        self.output_dir = ""
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 标注Excel选择
        excel_group = QGroupBox("标注Excel文件")
        excel_layout = QHBoxLayout()
        self.excel_label = QLabel("未选择文件")
        self.select_excel_btn = QPushButton("选择文件")
        self.select_excel_btn.clicked.connect(self.select_annotated_excel)
        excel_layout.addWidget(self.excel_label)
        excel_layout.addWidget(self.select_excel_btn)
        excel_layout.addStretch()
        excel_group.setLayout(excel_layout)
        layout.addWidget(excel_group)

        # 集群文件夹选择
        cluster_group = QGroupBox("集群文件夹（含ConfigMap）")
        cluster_layout = QHBoxLayout()
        self.cluster_label = QLabel("未选择文件夹")
        self.select_cluster_btn = QPushButton("选择文件夹")
        self.select_cluster_btn.clicked.connect(self.select_cluster_path)
        cluster_layout.addWidget(self.cluster_label)
        cluster_layout.addWidget(self.select_cluster_btn)
        cluster_layout.addStretch()
        cluster_group.setLayout(cluster_layout)
        layout.addWidget(cluster_group)

        # 输出目录选择
        output_group = QGroupBox("输出目录")
        output_layout = QHBoxLayout()
        self.output_label = QLabel("未选择目录")
        self.select_output_btn = QPushButton("选择目录")
        self.select_output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.select_output_btn)
        output_layout.addStretch()
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # 说明提示
        hint_label = QLabel(
            "说明：标注Excel须为Key提取器导出的树形Excel，并在前两列插入「所属领域」和「所属组件」。\n"
            "程序将按 输出目录/命名空间/ConfigMap/资源名/数据文件名.xlsx 结构导出标注结果。"
        )
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)

        # 执行按钮
        btn_layout = QHBoxLayout()
        self.execute_btn = QPushButton("执行标注导出")
        self.execute_btn.clicked.connect(self.execute)
        btn_layout.addWidget(self.execute_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 状态标签
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        layout.addStretch()
        self.setLayout(layout)

    def select_annotated_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择标注Excel文件", "", "Excel文件 (*.xlsx *.xls);;所有文件 (*)"
        )
        if file_path:
            self.annotated_excel_path = file_path
            self.excel_label.setText(f"已选择: {os.path.basename(file_path)}")

    def select_cluster_path(self):
        folder = QFileDialog.getExistingDirectory(self, "选择集群文件夹")
        if folder:
            self.cluster_path = folder
            self.cluster_label.setText(f"已选择: {os.path.basename(folder)}")

    def select_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            self.output_dir = folder
            self.output_label.setText(f"已选择: {os.path.basename(folder)}")

    def execute(self):
        """执行标注回写导出"""
        if not self.annotated_excel_path:
            QMessageBox.warning(self, "警告", "请先选择标注Excel文件")
            return
        if not self.cluster_path:
            QMessageBox.warning(self, "警告", "请先选择集群文件夹")
            return
        if not self.output_dir:
            QMessageBox.warning(self, "警告", "请先选择输出目录")
            return

        self.status_label.setText("正在读取标注Excel...")
        annotation_map = self.applier.load_annotated_excel(self.annotated_excel_path)

        if self.applier.get_errors():
            error_msg = "\n".join(self.applier.get_errors())
            QMessageBox.warning(self, "读取失败", error_msg)
            self.applier.clear_errors()
            self.status_label.setText("读取标注Excel失败")
            return

        self.status_label.setText(f"已读取 {len(annotation_map)} 条标注，正在导出...")

        success = self.applier.apply_annotations(
            self.cluster_path, annotation_map, self.output_dir
        )

        if not success or self.applier.get_errors():
            error_msg = "\n".join(self.applier.get_errors())
            QMessageBox.warning(self, "导出警告", f"部分文件导出失败:\n{error_msg}")
            self.applier.clear_errors()
            self.status_label.setText("导出完成（部分失败，请查看警告）")
        else:
            self.status_label.setText("导出完成")
            QMessageBox.information(
                self, "成功",
                f"标注回写导出完成\n输出目录: {self.output_dir}"
            )
