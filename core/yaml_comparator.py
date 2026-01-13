"""
YAML比较核心模块
负责比较两个YAML资源的差异
"""

import yaml
from typing import List, Dict, Any, Optional
from models.resource import Resource, ComparisonResult
from core.yaml_parser import YAMLParser, parse_properties_content


class YAMLComparator:
    """YAML比较器"""
    
    def __init__(self):
        self.parser = YAMLParser()
        self.errors = []
    
    def compare_clusters(self, cluster1_path: str, cluster2_path: str, 
                        compare_keys: List[Dict[str, Any]]) -> List[ComparisonResult]:
        """
        比较两个集群文件夹
        
        Args:
            cluster1_path: 集群1路径
            cluster2_path: 集群2路径
            compare_keys: 比较key配置列表，每个配置包含:
                        {
                            'key_path': str,  # key路径
                            'is_configmap_file': bool,  # 是否为ConfigMap/Secret文件内容
                            'file_key': str,  # 文件名key（仅当is_configmap_file=True时）
                            'file_type': str,  # 文件类型: 'yaml', 'properties', 'text'
                        }
            
        Returns:
            比较结果列表
        """
        # 解析两个集群
        resources1 = self.parser.parse_cluster_folder(cluster1_path)
        resources2 = self.parser.parse_cluster_folder(cluster2_path)
        
        # 创建资源映射 (namespace, kind, name) -> Resource
        resources2_map = {}
        for r in resources2:
            key = (r.namespace, r.kind, r.name)
            resources2_map[key] = r
        
        # 比较资源
        comparison_results = []
        
        for r1 in resources1:
            key = (r1.namespace, r1.kind, r1.name)
            r2 = resources2_map.get(key)
            
            result = ComparisonResult(resource_left=r1, resource_right=r2)
            
            if r2 is None:
                # 右侧资源不存在
                comparison_results.append(result)
            else:
                # 比较两个资源
                self._compare_resources(r1, r2, compare_keys, result)
                if result.has_differences():
                    comparison_results.append(result)
        
        return comparison_results
    
    def compare_files(self, file1_path: str, file2_path: str, 
                     compare_keys: List[Dict[str, Any]]) -> List[ComparisonResult]:
        """
        比较两个YAML文件
        
        Args:
            file1_path: 文件1路径
            file2_path: 文件2路径
            compare_keys: 比较key配置列表
            
        Returns:
            比较结果列表
        """
        # 解析两个文件
        resources1 = self.parser.parse_yaml_file(file1_path)
        resources2 = self.parser.parse_yaml_file(file2_path)
        
        # 创建资源映射
        resources2_map = {}
        for r in resources2:
            key = (r.kind, r.name)
            resources2_map[key] = r
        
        # 比较资源
        comparison_results = []
        
        for r1 in resources1:
            key = (r1.kind, r1.name)
            r2 = resources2_map.get(key)
            
            result = ComparisonResult(resource_left=r1, resource_right=r2)
            
            if r2 is None:
                # 右侧资源不存在
                comparison_results.append(result)
            else:
                # 比较两个资源
                self._compare_resources(r1, r2, compare_keys, result)
                if result.has_differences():
                    comparison_results.append(result)
        
        return comparison_results
    
    def _compare_resources(self, r1: Resource, r2: Resource, 
                          compare_keys: List[Dict[str, Any]], 
                          result: ComparisonResult):
        """比较两个资源"""
        for key_config in compare_keys:
            key_path = key_config.get('key_path', '')
            is_configmap_file = key_config.get('is_configmap_file', False)
            
            if is_configmap_file:
                # ConfigMap/Secret特殊处理
                self._compare_configmap_file(r1, r2, key_config, result)
            else:
                # 普通key比较
                value1 = self.parser.extract_value_by_path(r1.yaml_content, key_path)
                value2 = self.parser.extract_value_by_path(r2.yaml_content, key_path)
                
                if value1 != value2:
                    result.add_difference(key_path, value1, value2)
    
    def _compare_configmap_file(self, r1: Resource, r2: Resource, 
                               key_config: Dict[str, Any], 
                               result: ComparisonResult):
        """
        比较ConfigMap/Secret中的文件内容
        
        Args:
            r1: 资源1
            r2: 资源2
            key_config: key配置
            result: 比较结果
        """
        file_key = key_config.get('file_key', '')
        file_type = key_config.get('file_type', 'text')
        compare_key = key_config.get('compare_key', '')  # 文件内容中要比较的key
        
        # 提取data字段
        data1 = r1.yaml_content.get('data', {})
        data2 = r2.yaml_content.get('data', {})
        
        # 获取文件内容
        file_content1 = data1.get(file_key, '')
        file_content2 = data2.get(file_key, '')
        
        if file_type == 'text':
            # 直接文本比较
            if file_content1 != file_content2:
                full_path = f"data.{file_key}"
                result.add_difference(full_path, file_content1, file_content2)
        
        elif file_type == 'yaml':
            # 解析YAML内容
            try:
                yaml_obj1 = yaml.safe_load(file_content1) if file_content1 else {}
                yaml_obj2 = yaml.safe_load(file_content2) if file_content2 else {}
                
                # 提取比较key
                if compare_key:
                    value1 = self.parser.extract_value_by_path(yaml_obj1, compare_key)
                    value2 = self.parser.extract_value_by_path(yaml_obj2, compare_key)
                    
                    if value1 != value2:
                        full_path = f"data.{file_key}.{compare_key}"
                        result.add_difference(full_path, value1, value2)
                else:
                    # 比较整个YAML对象
                    if yaml_obj1 != yaml_obj2:
                        full_path = f"data.{file_key}"
                        result.add_difference(full_path, yaml_obj1, yaml_obj2)
            
            except Exception as e:
                self.errors.append(f"解析YAML文件内容失败: {str(e)}")
        
        elif file_type == 'properties':
            # 解析properties内容
            props1 = parse_properties_content(file_content1)
            props2 = parse_properties_content(file_content2)
            
            if compare_key:
                # 提取指定key
                value1 = self.parser.extract_value_by_path(props1, compare_key)
                value2 = self.parser.extract_value_by_path(props2, compare_key)
                
                if value1 != value2:
                    full_path = f"data.{file_key}.{compare_key}"
                    result.add_difference(full_path, value1, value2)
            else:
                # 比较所有属性
                all_keys = set(props1.keys()) | set(props2.keys())
                for key in all_keys:
                    value1 = props1.get(key, '')
                    value2 = props2.get(key, '')
                    
                    if value1 != value2:
                        full_path = f"data.{file_key}.{key}"
                        result.add_difference(full_path, value1, value2)
    
    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors + self.parser.get_errors()
    
    def clear_errors(self):
        """清除错误列表"""
        self.errors = []
        self.parser.clear_errors()
