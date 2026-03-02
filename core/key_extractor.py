"""
Key提取核心模块
负责从ConfigMap资源中提取所有去重的key
"""

import yaml
import os
from typing import Set, List
from models.resource import Resource
from core.yaml_parser import YAMLParser, parse_properties_content


class KeyExtractor:
    """Key提取器"""
    
    def __init__(self):
        self.parser = YAMLParser()
        self.errors = []
    
    def extract_from_path(self, path: str) -> Set[str]:
        """
        从指定路径提取所有ConfigMap的key
        支持: 集群文件夹、命名空间文件夹、资源类型文件夹、单个YAML文件
        
        Args:
            path: 文件或文件夹路径
            
        Returns:
            去重后的key集合
        """
        all_keys = set()
        self.errors = []
        
        if not os.path.exists(path):
            self.errors.append(f"路径不存在: {path}")
            return all_keys
        
        if os.path.isfile(path):
            # 单个文件
            resources = self.parser.parse_yaml_file(path)
        else:
            # 文件夹
            resources = self.parser.parse_cluster_folder(path)
        
        # 只处理ConfigMap类型的资源
        configmap_resources = [r for r in resources if r.kind == "ConfigMap"]
        
        # 从每个ConfigMap提取key
        for resource in configmap_resources:
            keys = self.extract_from_configmap(resource)
            all_keys.update(keys)
        
        return all_keys
    
    def extract_from_configmap(self, resource: Resource) -> Set[str]:
        """
        从单个ConfigMap资源提取key
        
        Args:
            resource: ConfigMap资源对象
            
        Returns:
            该资源中的所有key集合
        """
        keys = set()
        
        if resource.kind != "ConfigMap":
            return keys
        
        # 提取data字段
        data = resource.yaml_content.get('data', {})
        
        if not data:
            return keys
        
        # 处理data字段中的每个key-value对
        keys.update(self._extract_from_data_field(data))
        
        return keys
    
    def _extract_from_data_field(self, data: dict) -> Set[str]:
        """
        从ConfigMap的data字段提取key
        
        Args:
            data: ConfigMap的data字段字典
            
        Returns:
            提取的key集合
        """
        all_keys = set()
        
        for key, value in data.items():
            if not isinstance(value, str):
                continue
            
            # 判断key类型并提取
            if key.endswith('.yaml') or key.endswith('.yml'):
                # YAML格式：递归提取内部key
                keys = self._extract_keys_from_yaml(value)
                all_keys.update(keys)
            elif key.endswith('.properties'):
                # Properties格式：提取properties的key
                keys = self._extract_keys_from_properties(value)
                all_keys.update(keys)
            else:
                # 普通字符串：直接添加key本身
                all_keys.add(key)
        
        return all_keys
    
    def _extract_keys_from_yaml(self, content: str) -> Set[str]:
        """
        从YAML内容中递归提取所有key
        支持多文档（---分隔）
        
        Args:
            content: YAML格式的字符串
            
        Returns:
            提取的key集合
        """
        all_keys = set()
        
        if not content:
            return all_keys
        
        try:
            # 使用safe_load_all支持多文档
            for doc in yaml.safe_load_all(content):
                if doc is None:
                    continue
                # 递归提取该文档中的所有key
                keys = self._extract_keys_recursively(doc)
                all_keys.update(keys)
        except Exception as e:
            self.errors.append(f"解析YAML内容失败: {str(e)}")
        
        return all_keys
    
    def _extract_keys_from_properties(self, content: str) -> Set[str]:
        """
        从properties内容中提取所有key
        
        Args:
            content: properties格式的字符串
            
        Returns:
            提取的key集合
        """
        all_keys = set()
        
        if not content:
            return all_keys
        
        try:
            # 复用现有的properties解析函数
            props = parse_properties_content(content)
            # properties的key本身就是点分隔的格式
            all_keys.update(props.keys())
        except Exception as e:
            self.errors.append(f"解析Properties内容失败: {str(e)}")
        
        return all_keys
    
    def _extract_keys_recursively(self, obj, prefix: str = "") -> Set[str]:
        """
        递归提取YAML对象中的所有key（仅叶子节点）
        
        Args:
            obj: YAML对象（dict、list或其他类型）
            prefix: 当前key的前缀
            
        Returns:
            提取的key集合（仅包含叶子节点）
        """
        keys = set()
        
        if isinstance(obj, dict):
            # 字典类型：遍历所有键值对
            for k, v in obj.items():
                # 构建完整的key路径
                current_key = f"{prefix}.{k}" if prefix else k
                
                # 只有当值不是dict且不是list时，才添加key（即叶子节点）
                if not isinstance(v, dict) and not isinstance(v, list):
                    keys.add(current_key)
                
                # 继续递归处理（处理嵌套的dict和list）
                keys.update(self._extract_keys_recursively(v, current_key))
        elif isinstance(obj, list):
            # 列表类型：递归处理每个元素，但不添加索引
            for item in obj:
                keys.update(self._extract_keys_recursively(item, prefix))
        # 其他类型（str、int等）：不做处理
        
        return keys
    
    def get_sorted_keys(self, keys: Set[str]) -> List[str]:
        """
        将key集合转换为按字母序排列的列表
        
        Args:
            keys: key集合
            
        Returns:
            排序后的key列表
        """
        return sorted(list(keys))
    
    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors + self.parser.get_errors()
    
    def clear_errors(self):
        """清除错误列表"""
        self.errors = []
        self.parser.clear_errors()
