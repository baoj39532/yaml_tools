"""
信息提取核心模块
负责从YAML资源中提取指定的信息
"""

import yaml
import os
from typing import List, Dict, Any
from models.resource import Resource, ExtractionResult
from core.yaml_parser import YAMLParser, parse_properties_content


class InfoExtractor:
    """信息提取器"""
    
    def __init__(self):
        self.parser = YAMLParser()
        self.errors = []
    
    def extract_from_path(self, path: str, 
                         extract_configs: List[Dict[str, Any]]) -> List[ExtractionResult]:
        """
        从指定路径提取信息
        支持: 集群文件夹、命名空间文件夹、资源类型文件夹、单个YAML文件
        
        Args:
            path: 文件或文件夹路径
            extract_configs: 提取配置列表，每个配置包含:
                           {
                               'key_path': str,  # key路径
                               'alias': str,  # 别名
                               'is_configmap_file': bool,  # 是否为ConfigMap/Secret文件内容
                               'file_key': str,  # 文件名key
                               'file_type': str,  # 文件类型
                           }
            
        Returns:
            提取结果列表
        """
        extraction_results = []
        
        if not os.path.exists(path):
            self.errors.append(f"路径不存在: {path}")
            return extraction_results
        
        if os.path.isfile(path):
            # 单个文件
            resources = self.parser.parse_yaml_file(path)
        else:
            # 文件夹
            resources = self.parser.parse_cluster_folder(path)
        
        # 提取每个资源的信息
        for resource in resources:
            result = self._extract_from_resource(resource, extract_configs)
            extraction_results.append(result)
        
        return extraction_results
    
    def _extract_from_resource(self, resource: Resource, 
                               extract_configs: List[Dict[str, Any]]) -> ExtractionResult:
        """从单个资源提取信息"""
        result = ExtractionResult(resource=resource)
        
        for config in extract_configs:
            key_path = config.get('key_path', '')
            alias = config.get('alias', '')
            is_configmap_file = config.get('is_configmap_file', False)
            
            if is_configmap_file:
                # ConfigMap/Secret特殊处理
                self._extract_configmap_file(resource, config, result)
            else:
                # 普通key提取
                value = self.parser.extract_value_by_path(resource.yaml_content, key_path)
                result.add_value(key_path, value, alias)
        
        return result
    
    def _extract_configmap_file(self, resource: Resource, 
                               config: Dict[str, Any], 
                               result: ExtractionResult):
        """
        从ConfigMap/Secret中提取文件内容
        
        Args:
            resource: 资源对象
            config: 提取配置
            result: 提取结果
        """
        file_key = config.get('file_key', '')
        file_type = config.get('file_type', 'text')
        extract_key = config.get('extract_key', '')  # 文件内容中要提取的key
        alias = config.get('alias', '')
        
        # 提取data字段
        data = resource.yaml_content.get('data', {})
        
        # 获取文件内容
        file_content = data.get(file_key, '')
        
        if file_type == 'text':
            # 直接文本提取
            full_path = f"data.{file_key}"
            result.add_value(full_path, file_content, alias)
        
        elif file_type == 'yaml':
            # 解析YAML内容
            try:
                yaml_obj = yaml.safe_load(file_content) if file_content else {}
                
                if extract_key:
                    # 提取指定key
                    value = self.parser.extract_value_by_path(yaml_obj, extract_key)
                    full_path = f"data.{file_key}.{extract_key}"
                    result.add_value(full_path, value, alias)
                else:
                    # 提取整个YAML对象
                    full_path = f"data.{file_key}"
                    result.add_value(full_path, yaml_obj, alias)
            
            except Exception as e:
                self.errors.append(f"解析YAML文件内容失败: {str(e)}")
                result.add_value(f"data.{file_key}", f"解析失败: {str(e)}", alias)
        
        elif file_type == 'properties':
            # 解析properties内容
            props = parse_properties_content(file_content)
            
            if extract_key:
                # 提取指定key
                value = self.parser.extract_value_by_path(props, extract_key)
                full_path = f"data.{file_key}.{extract_key}"
                result.add_value(full_path, value, alias)
            else:
                # 提取所有属性
                full_path = f"data.{file_key}"
                result.add_value(full_path, props, alias)
    
    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors + self.parser.get_errors()
    
    def clear_errors(self):
        """清除错误列表"""
        self.errors = []
        self.parser.clear_errors()
