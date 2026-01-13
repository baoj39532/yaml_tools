"""
资源数据模型
定义Kubernetes资源的数据结构
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Resource:
    """Kubernetes资源模型"""
    kind: str  # 资源类型（如Application, Service等）
    name: str  # 资源名称（metadata.name）
    namespace: str  # 命名空间（metadata.namespace）
    cluster: str  # 集群名称（顶层文件夹名）
    file_path: str  # YAML文件路径（相对于集群根目录）
    yaml_content: Dict[str, Any]  # YAML内容（完整的字典）
    abs_file_path: str = ""  # 绝对文件路径
    resource_type_folder: str = ""  # 资源类型文件夹名
    
    def __post_init__(self):
        """数据验证"""
        if not self.kind:
            raise ValueError("kind不能为空")
        if not self.name:
            raise ValueError("name不能为空")
        if not self.namespace:
            raise ValueError("namespace不能为空")
    
    def get_identifier(self) -> str:
        """获取资源唯一标识符"""
        return f"{self.cluster}/{self.namespace}/{self.kind}/{self.name}"
    
    def __str__(self) -> str:
        return f"Resource(kind={self.kind}, name={self.name}, namespace={self.namespace}, cluster={self.cluster})"
    
    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class ComparisonResult:
    """比较结果数据模型"""
    resource_left: Resource  # 左侧资源
    resource_right: Optional[Resource]  # 右侧资源（可能不存在）
    differences: list = field(default_factory=list)  # 差异列表
    
    def add_difference(self, key_path: str, left_value: Any, right_value: Any):
        """添加差异项"""
        self.differences.append({
            'key_path': key_path,
            'left_value': left_value,
            'right_value': right_value
        })
    
    def has_differences(self) -> bool:
        """是否有差异"""
        return len(self.differences) > 0 or self.resource_right is None


@dataclass
class ExtractionResult:
    """信息提取结果数据模型"""
    resource: Resource  # 资源对象
    extracted_values: Dict[str, Any] = field(default_factory=dict)  # 提取的值字典 {key_path: value}
    
    def add_value(self, key_path: str, value: Any, alias: str = ""):
        """添加提取的值"""
        display_key = f"{key_path} ({alias})" if alias else key_path
        self.extracted_values[display_key] = value
