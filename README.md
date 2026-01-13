# K8s YAML管理工具

这是一个可视化的Kubernetes YAML管理工具，支持Windows运行，并具有良好的跨平台兼容性。

## 功能特性

### 1. YAML命令生成器
- 解析集群文件夹中的所有YAML资源
- 生成资源表格并支持Excel导出
- 批量生成删除命令（按正确顺序）
- 批量生成部署命令（按正确顺序）
- 支持资源类型筛选和手动选择

### 2. YAML比较器
- 支持两种比较模式：
  - 集群文件夹比较
  - 单文件比较
- 自定义比较Key（支持a.b.c路径格式）
- ConfigMap/Secret特殊处理：
  - 支持文件内容比较
  - 支持YAML和properties格式解析
- 比较结果导出为Excel（按资源类型分文件，按资源名分Sheet）

### 3. 信息提取器
- 从文件或文件夹提取YAML信息
- 支持自定义提取Key和别名
- ConfigMap/Secret文件内容提取
- 提取结果导出为Excel

## 文件夹结构要求

工具要求集群文件夹遵循以下结构：

```
集群名/
├── 命名空间1/
│   ├── Application/
│   │   └── app1.yaml
│   ├── Deployment/
│   │   └── deploy1.yaml
│   ├── ConfigMap/
│   │   └── config1.yaml
│   ├── Secret/
│   │   └── secret1.yaml
│   ├── Service/
│   │   └── service1.yaml
│   └── PersistentVolumeClaim/
│       └── pvc1.yaml
└── 命名空间2/
    └── ...
```

## 安装和运行

### 方式1: 使用源代码运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python main.py
```

### 方式2: 使用打包的可执行文件

1. 打包成exe（需要安装PyInstaller）：
```bash
python build.py
```

2. 运行生成的可执行文件：
```
dist/K8s_YAML管理工具.exe
```

## 系统要求

- **Python**: 3.9 或更高版本
- **操作系统**: Windows 10/11（推荐），也支持 Linux 和 macOS
- **内存**: 至少 512MB 可用内存
- **磁盘空间**: 至少 100MB 可用空间

## 依赖包

- PyQt5 5.15.10
- PyYAML 6.0.1
- openpyxl 3.1.2
- pyinstaller 6.3.0

## 使用说明

### 命令生成器

1. 点击"选择集群文件夹"选择包含YAML文件的集群根目录
2. 点击"解析并显示资源"，工具会扫描并显示所有资源
3. 在资源类型复选框中选择要生成命令的资源类型，或直接在表格中选择特定资源
4. 点击"生成删除命令"或"生成部署命令"
5. 选择保存位置，生成.sh脚本文件
6. 可点击"导出资源表到Excel"导出资源清单

### YAML比较器

1. 选择比较模式（集群文件夹比较或单文件比较）
2. 选择要比较的两个对象
3. 在"比较Key配置"区域添加要比较的Key：
   - 普通Key：直接输入路径，如`spec.replicas`
   - ConfigMap文件：勾选"ConfigMap文件"，填写文件名key和文件类型
4. 点击"执行比较"
5. 点击"导出比较结果到Excel"将结果保存

### 信息提取器

1. 点击"选择文件夹"或"选择文件"
2. 在"提取Key配置"区域添加要提取的Key和别名
3. 点击"提取信息"
4. 点击"导出提取结果到Excel"保存结果

## 注意事项

1. **YAML文件格式**：
   - 支持.yaml和.yml扩展名
   - 支持单文件多资源（使用`---`分隔）
   - 每个资源必须包含kind、metadata.name和metadata.namespace字段

2. **命令生成顺序**：
   - 删除顺序：Service → Application → ConfigMap → Secret → PersistentVolumeClaim
   - 部署顺序：PersistentVolumeClaim → Secret → ConfigMap → Application → Service
   - Deployment类型不包含在删除命令中

3. **Excel导出限制**：
   - 单个Excel文件最多250个Sheet
   - 超出限制会自动分成多个文件

4. **Key路径格式**：
   - 使用点号分隔：`a.b.c`
   - 支持数组索引：`a.b[0].c`

## 故障排除

### 程序无法启动
- 确保已安装所有依赖包
- 检查Python版本是否为3.9或更高

### 解析失败
- 检查YAML文件格式是否正确
- 确认文件夹结构符合要求
- 查看错误提示信息

### 导出失败
- 确保有写入权限
- 检查磁盘空间是否充足
- 关闭正在打开的Excel文件

## 开发信息

- **版本**: 1.0.0
- **开发语言**: Python 3.9+
- **GUI框架**: PyQt5
- **许可证**: MIT

## 更新日志

### v1.0.0 (2024)
- 初始版本发布
- 实现命令生成器功能
- 实现YAML比较器功能
- 实现信息提取器功能
- 支持Excel导出
- 支持打包成Windows可执行文件

## 联系方式

如有问题或建议，请联系开发团队。
