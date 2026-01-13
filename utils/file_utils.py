"""
文件操作工具类
提供文件和文件夹操作的辅助函数
"""

import os
from typing import List
from config import YAML_EXTENSIONS


def is_yaml_file(file_path: str) -> bool:
    """判断是否为YAML文件"""
    _, ext = os.path.splitext(file_path)
    return ext.lower() in YAML_EXTENSIONS


def scan_yaml_files(directory: str) -> List[str]:
    """递归扫描目录下的所有YAML文件"""
    yaml_files = []
    
    if not os.path.exists(directory):
        raise FileNotFoundError(f"目录不存在: {directory}")
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if is_yaml_file(file):
                full_path = os.path.join(root, file)
                yaml_files.append(full_path)
    
    return yaml_files


def get_relative_path(full_path: str, base_path: str) -> str:
    """获取相对路径"""
    return os.path.relpath(full_path, base_path)


def ensure_dir(directory: str):
    """确保目录存在，不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def validate_cluster_structure(cluster_path: str) -> bool:
    """
    验证集群文件夹结构是否符合要求
    结构：集群名/命名空间/资源类型/yaml文件
    """
    if not os.path.exists(cluster_path):
        return False
    
    if not os.path.isdir(cluster_path):
        return False
    
    # 检查是否有子文件夹（命名空间）
    has_subdir = False
    for item in os.listdir(cluster_path):
        item_path = os.path.join(cluster_path, item)
        if os.path.isdir(item_path):
            has_subdir = True
            break
    
    return has_subdir
