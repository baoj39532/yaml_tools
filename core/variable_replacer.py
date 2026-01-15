"""
变量替换模块
负责将YAML中的{{VAR}}替换为指定值并导出副本
"""

import os
import re
from typing import List, Dict, Any
from utils.file_utils import scan_yaml_files, is_yaml_file, get_relative_path, ensure_dir


class VariableReplacer:
    """变量替换器"""

    def __init__(self):
        self.errors = []

    def replace_to_output(self, input_path: str, output_dir: str,
                          variables: List[Dict[str, Any]]) -> bool:
        """替换变量并导出副本"""
        self.errors = []
        if not input_path or not os.path.exists(input_path):
            self.errors.append("输入路径不存在")
            return False
        if not output_dir:
            self.errors.append("输出目录为空")
            return False

        var_map = self._build_var_map(variables)
        if not var_map:
            self.errors.append("未配置任何变量")
            return False

        try:
            ensure_dir(output_dir)
        except Exception as e:
            self.errors.append(f"创建输出目录失败: {str(e)}")
            return False

        if os.path.isfile(input_path):
            if not is_yaml_file(input_path):
                self.errors.append("输入文件不是YAML文件")
                return False
            files = [input_path]
            base_path = os.path.dirname(input_path)
        else:
            files = scan_yaml_files(input_path)
            base_path = input_path

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                replaced = self._replace_content(content, var_map)

                rel_path = get_relative_path(file_path, base_path)
                target_path = os.path.join(output_dir, rel_path)
                ensure_dir(os.path.dirname(target_path))
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(replaced)
            except Exception as e:
                self.errors.append(f"替换失败 {file_path}: {str(e)}")

        return len(self.errors) == 0

    def _build_var_map(self, variables: List[Dict[str, Any]]) -> Dict[str, str]:
        var_map = {}
        for item in variables or []:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            value = item.get("value", "")
            var_map[name] = "" if value is None else str(value)
        return var_map

    def _replace_content(self, content: str, var_map: Dict[str, str]) -> str:
        result = content
        for name, value in var_map.items():
            pattern = r"{{\s*" + re.escape(name) + r"\s*}}"
            result = re.sub(pattern, value, result)
        return result

    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors

    def clear_errors(self):
        """清除错误列表"""
        self.errors = []
