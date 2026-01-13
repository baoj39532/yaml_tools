"""
YAML解析核心模块
负责解析Kubernetes YAML文件和提取信息
"""

import os
import yaml
from typing import List, Any, Dict, Optional
from models.resource import Resource
from utils.file_utils import scan_yaml_files, get_relative_path, is_yaml_file
from utils.validators import validate_yaml_resource


class YAMLParser:
    """YAML解析器"""
    
    def __init__(self):
        self.errors = []
    
    def parse_cluster_folder(self, cluster_path: str) -> List[Resource]:
        """
        解析集群文件夹
        结构：集群名/命名空间/资源类型/yaml文件
        
        Args:
            cluster_path: 集群文件夹路径
            
        Returns:
            Resource对象列表
        """
        resources = []
        self.errors = []
        
        if not os.path.exists(cluster_path):
            self.errors.append(f"路径不存在: {cluster_path}")
            return resources
        
        if not os.path.isdir(cluster_path):
            self.errors.append(f"不是有效的目录: {cluster_path}")
            return resources
        
        cluster_name = os.path.basename(cluster_path)
        
        # 扫描所有YAML文件
        yaml_files = scan_yaml_files(cluster_path)
        
        for yaml_file in yaml_files:
            try:
                file_resources = self.parse_yaml_file(
                    yaml_file, 
                    cluster_name, 
                    cluster_path
                )
                resources.extend(file_resources)
            except Exception as e:
                self.errors.append(f"解析文件失败 {yaml_file}: {str(e)}")
        
        return resources
    
    def parse_yaml_file(self, file_path: str, cluster_name: str = "", 
                       cluster_base_path: str = "") -> List[Resource]:
        """
        解析单个YAML文件，支持多文档（---分隔）
        
        Args:
            file_path: YAML文件路径
            cluster_name: 集群名称
            cluster_base_path: 集群根路径
            
        Returns:
            Resource对象列表
        """
        resources = []
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 如果没有提供集群信息，从文件路径推断
        if not cluster_name:
            cluster_name = self._extract_cluster_name_from_path(file_path)
        
        if not cluster_base_path:
            cluster_base_path = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                # 使用safe_load_all支持多文档YAML
                yaml_documents = yaml.safe_load_all(f)
                
                for doc in yaml_documents:
                    if doc is None:
                        continue
                    
                    # 验证YAML资源
                    is_valid, kind, name, namespace, error_msg = validate_yaml_resource(doc)
                    
                    if not is_valid:
                        self.errors.append(f"文件 {file_path} 中的资源验证失败: {error_msg}")
                        continue
                    
                    # 提取资源类型文件夹名
                    resource_type_folder = self._extract_resource_type_folder(file_path, cluster_base_path)
                    
                    # 创建Resource对象
                    resource = Resource(
                        kind=kind,
                        name=name,
                        namespace=namespace,
                        cluster=cluster_name,
                        file_path=get_relative_path(file_path, cluster_base_path),
                        yaml_content=doc,
                        abs_file_path=file_path,
                        resource_type_folder=resource_type_folder
                    )
                    
                    resources.append(resource)
                    
            except yaml.YAMLError as e:
                raise ValueError(f"YAML格式错误: {str(e)}")
        
        return resources
    
    def _extract_cluster_name_from_path(self, file_path: str) -> str:
        """从文件路径提取集群名称"""
        # 假设结构：.../集群名/命名空间/资源类型/文件
        parts = file_path.split(os.sep)
        if len(parts) >= 4:
            return parts[-4]
        return "unknown"
    
    def _extract_resource_type_folder(self, file_path: str, cluster_base_path: str) -> str:
        """提取资源类型文件夹名"""
        rel_path = get_relative_path(file_path, cluster_base_path)
        parts = rel_path.split(os.sep)
        # 结构：命名空间/资源类型/文件
        if len(parts) >= 3:
            return parts[1]
        elif len(parts) >= 2:
            return parts[0]
        return ""
    
    def extract_value_by_path(self, yaml_obj: Dict[str, Any], key_path: str) -> Any:
        """
        根据路径提取YAML中的值
        支持格式: a.b.c 或 a.b[0].c
        
        Args:
            yaml_obj: YAML对象
            key_path: 键路径
            
        Returns:
            提取的值，如果路径不存在返回None
        """
        if not key_path:
            return None
        
        try:
            current = yaml_obj
            
            # 分割路径
            parts = self._parse_key_path(key_path)
            
            for part in parts:
                if isinstance(part, int):
                    # 数组索引
                    if isinstance(current, list) and 0 <= part < len(current):
                        current = current[part]
                    else:
                        return None
                else:
                    # 字典键
                    if isinstance(current, dict):
                        current = current.get(part)
                        if current is None:
                            return None
                    else:
                        return None
            
            return current
            
        except Exception:
            return None
    
    def _parse_key_path(self, key_path: str) -> List:
        """
        解析键路径为部件列表
        例如: "a.b[0].c" -> ["a", "b", 0, "c"]
        """
        parts = []
        current = ""
        i = 0
        
        while i < len(key_path):
            char = key_path[i]
            
            if char == '.':
                if current:
                    parts.append(current)
                    current = ""
            elif char == '[':
                # 处理数组索引
                if current:
                    parts.append(current)
                    current = ""
                
                # 查找右括号
                j = i + 1
                while j < len(key_path) and key_path[j] != ']':
                    j += 1
                
                if j < len(key_path):
                    try:
                        index = int(key_path[i+1:j])
                        parts.append(index)
                    except ValueError:
                        pass
                    i = j
            else:
                current += char
            
            i += 1
        
        if current:
            parts.append(current)
        
        return parts
    
    def get_errors(self) -> List[str]:
        """获取解析过程中的错误"""
        return self.errors
    
    def clear_errors(self):
        """清除错误列表"""
        self.errors = []


def parse_properties_content(content: str) -> Dict[str, str]:
    """
    解析properties格式的内容
    
    Args:
        content: properties格式的字符串
        
    Returns:
        键值对字典
    """
    result = {}
    
    if not content:
        return result
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行和注释
        if not line or line.startswith('#') or line.startswith('!'):
            continue
        
        # 查找等号或冒号
        separator_idx = -1
        for i, char in enumerate(line):
            if char in ('=', ':'):
                separator_idx = i
                break
        
        if separator_idx > 0:
            key = line[:separator_idx].strip()
            value = line[separator_idx+1:].strip()
            result[key] = value
    
    return result
