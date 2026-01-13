"""
命令生成核心模块
负责生成Kubernetes资源的部署和删除命令
"""

from typing import List
from models.resource import Resource
from config import DELETE_ORDER, DEPLOY_ORDER, RESOURCE_TYPE_MAPPING


class CommandGenerator:
    """命令生成器"""
    
    def __init__(self):
        self.errors = []
    
    def generate_delete_commands(self, resources: List[Resource]) -> List[str]:
        """
        生成删除命令
        顺序: Service → Application → ConfigMap → Secret → PersistentVolumeClaim
        注意: Deployment不包含在删除命令中
        
        Args:
            resources: 资源列表
            
        Returns:
            命令字符串列表
        """
        commands = []
        
        # 按删除顺序分组
        grouped_resources = self._group_resources_by_order(resources, DELETE_ORDER)
        
        # 按顺序生成命令
        for kind in DELETE_ORDER:
            if kind in grouped_resources:
                for resource in grouped_resources[kind]:
                    cmd = self._generate_single_delete_command(resource)
                    if cmd:
                        commands.append(cmd)
        
        return commands
    
    def _generate_single_delete_command(self, resource: Resource) -> str:
        """
        生成单个资源的删除命令
        格式: condep delete -t {type} -n {namespace} -c {cluster} {name}
        """
        # 获取资源类型对应的命令参数
        resource_type = RESOURCE_TYPE_MAPPING.get(resource.kind)
        
        if not resource_type:
            self.errors.append(f"不支持的资源类型用于删除: {resource.kind}")
            return ""
        
        # 构建命令
        cmd = f"condep delete -t {resource_type} -n {resource.namespace} -c {resource.cluster} {resource.name}"
        
        return cmd
    
    def generate_deploy_commands(self, resources: List[Resource]) -> List[str]:
        """
        生成部署命令
        顺序: PersistentVolumeClaim → Secret → ConfigMap → Application → Service
        
        Args:
            resources: 资源列表
            
        Returns:
            命令字符串列表
        """
        commands = []
        
        # 按部署顺序分组
        grouped_resources = self._group_resources_by_order(resources, DEPLOY_ORDER)
        
        # 按顺序生成命令
        for kind in DEPLOY_ORDER:
            if kind in grouped_resources:
                for resource in grouped_resources[kind]:
                    cmd = self._generate_single_deploy_command(resource)
                    if cmd:
                        commands.append(cmd)
        
        return commands
    
    def _generate_single_deploy_command(self, resource: Resource) -> str:
        """
        生成单个资源的部署命令
        Application格式: condep deploy -f {file_path} -n {namespace} -c {cluster} --app yes
        其他格式: condep deploy -f {file_path} -n {namespace} -c {cluster} --app no
        """
        # 判断是否为Application
        app_flag = "yes" if resource.kind == "Application" else "no"
        
        # 构建命令
        cmd = f"condep deploy -f {resource.file_path} -n {resource.namespace} -c {resource.cluster} --app {app_flag}"
        
        return cmd
    
    def _group_resources_by_order(self, resources: List[Resource], order: List[str]) -> dict:
        """
        按指定顺序分组资源
        
        Args:
            resources: 资源列表
            order: 顺序列表
            
        Returns:
            分组后的资源字典
        """
        grouped = {kind: [] for kind in order}
        
        for resource in resources:
            if resource.kind in grouped:
                grouped[resource.kind].append(resource)
        
        return grouped
    
    def save_commands_to_file(self, commands: List[str], output_path: str) -> bool:
        """
        将命令保存到文件
        
        Args:
            commands: 命令列表
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # 添加shebang
                f.write("#!/bin/bash\n\n")
                
                # 写入每条命令
                for cmd in commands:
                    f.write(cmd + "\n")
            
            return True
            
        except Exception as e:
            self.errors.append(f"保存命令文件失败: {str(e)}")
            return False
    
    def filter_resources_by_types(self, resources: List[Resource], 
                                  selected_types: List[str]) -> List[Resource]:
        """
        根据资源类型过滤资源
        
        Args:
            resources: 资源列表
            selected_types: 选中的资源类型列表
            
        Returns:
            过滤后的资源列表
        """
        if not selected_types:
            return resources
        
        return [r for r in resources if r.kind in selected_types]
    
    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors
    
    def clear_errors(self):
        """清除错误列表"""
        self.errors = []
