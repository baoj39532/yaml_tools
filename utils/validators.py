"""
数据验证工具
提供各种数据验证函数
"""

from typing import Any, Dict


def validate_yaml_resource(yaml_obj: Dict[str, Any]) -> tuple:
    """
    验证YAML对象是否为有效的K8s资源
    返回: (is_valid, kind, name, namespace, error_msg)
    """
    if not isinstance(yaml_obj, dict):
        return False, None, None, None, "YAML对象必须是字典类型"
    
    # 检查kind字段
    kind = yaml_obj.get('kind')
    if not kind:
        return False, None, None, None, "缺少kind字段"
    
    # 检查metadata字段
    metadata = yaml_obj.get('metadata')
    if not metadata or not isinstance(metadata, dict):
        return False, kind, None, None, "缺少metadata字段或格式不正确"
    
    # 检查name字段
    name = metadata.get('name')
    if not name:
        return False, kind, None, None, "metadata中缺少name字段"
    
    # 检查namespace字段（有些资源可能没有namespace，如ClusterRole）
    namespace = metadata.get('namespace', 'default')
    
    return True, kind, name, namespace, ""


def validate_key_path(key_path: str) -> bool:
    """
    验证key路径格式是否正确
    格式: a.b.c 或 a.b[0].c
    """
    if not key_path or not isinstance(key_path, str):
        return False
    
    # 简单验证：不能为空且不能以.开头或结尾
    key_path = key_path.strip()
    if not key_path or key_path.startswith('.') or key_path.endswith('.'):
        return False
    
    return True
