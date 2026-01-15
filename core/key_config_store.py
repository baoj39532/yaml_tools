"""
配置读写模块
负责保存/加载比较器与提取器的Key配置
"""

import os
from typing import List, Dict, Any
import yaml


class KeyConfigStore:
    """YAML配置读写器"""

    def __init__(self):
        self.errors = []

    def load(self, file_path: str) -> List[Dict[str, Any]]:
        """从YAML文件加载配置"""
        self.errors = []
        if not file_path or not os.path.exists(file_path):
            self.errors.append(f"配置文件不存在: {file_path}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            self.errors.append(f"读取配置失败: {str(e)}")
            return []

        items = data.get("key_configs", [])
        if not isinstance(items, list):
            self.errors.append("配置格式错误: key_configs必须是列表")
            return []

        normalized = []
        for item in items:
            if not isinstance(item, dict):
                continue
            normalized.append(self._normalize_item(item))

        return normalized

    def save(self, file_path: str, items: List[Dict[str, Any]]) -> bool:
        """保存配置到YAML文件"""
        self.errors = []
        if not file_path:
            self.errors.append("配置文件路径为空")
            return False

        data = {
            "version": 1,
            "key_configs": items or [],
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    data,
                    f,
                    allow_unicode=False,
                    default_flow_style=False,
                    sort_keys=False,
                )
            return True
        except Exception as e:
            self.errors.append(f"保存配置失败: {str(e)}")
            return False

    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """标准化配置项字段"""
        return {
            "key_path": item.get("key_path", ""),
            "alias": item.get("alias", ""),
            "is_configmap_file": bool(item.get("is_configmap_file", False)),
            "file_key": item.get("file_key", ""),
            "file_type": item.get("file_type", "text"),
            "compare_key": item.get("compare_key", ""),
            "extract_key": item.get("extract_key", ""),
        }

    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors

    def clear_errors(self):
        """清理错误列表"""
        self.errors = []
