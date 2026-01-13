"""
配置文件
包含应用程序的全局配置
"""

# 应用程序信息
APP_NAME = "K8s YAML管理工具"
APP_VERSION = "1.0.0"
APP_AUTHOR = "YAML Tools"

# 支持的资源类型
SUPPORTED_RESOURCE_TYPES = [
    "Application",
    "Deployment",
    "ConfigMap",
    "PersistentVolumeClaim",
    "Secret",
    "Service"
]

# 资源类型到condep命令参数的映射
RESOURCE_TYPE_MAPPING = {
    "Application": "app",
    "Service": "svc",
    "ConfigMap": "cfgm",
    "Secret": "scrt",
    "PersistentVolumeClaim": "pvc"
}

# 删除命令资源顺序（注意：Deployment不包含在删除命令中）
DELETE_ORDER = [
    "Service",
    "Application",
    "ConfigMap",
    "Secret",
    "PersistentVolumeClaim"
]

# 部署命令资源顺序
DEPLOY_ORDER = [
    "PersistentVolumeClaim",
    "Secret",
    "ConfigMap",
    "Application",
    "Service"
]

# YAML文件扩展名
YAML_EXTENSIONS = [".yaml", ".yml"]

# Excel相关配置
MAX_SHEETS_PER_FILE = 250  # Excel单文件最大Sheet数量限制

# UI配置
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
