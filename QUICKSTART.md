# 快速入门指南

## 1. 安装和运行

### Windows用户（推荐）

#### 方式A: 直接运行（需要Python环境）
1. 双击 `run.bat` 文件
2. 脚本会自动检查并安装依赖
3. 程序将自动启动

#### 方式B: 打包成exe（无需Python环境）
1. 双击 `build.bat` 文件
2. 等待打包完成
3. 运行 `dist\K8s_YAML管理工具.exe`

### macOS/Linux用户

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py

# 打包（可选）
python build.py
```

## 2. 准备测试数据

创建以下文件夹结构用于测试：

```
test_cluster/
├── namespace1/
│   ├── Application/
│   │   └── my-app.yaml
│   ├── Service/
│   │   └── my-service.yaml
│   └── ConfigMap/
│       └── my-config.yaml
```

### 示例YAML文件

**Application示例 (my-app.yaml):**
```yaml
apiVersion: apps/v1
kind: Application
metadata:
  name: my-app
  namespace: namespace1
spec:
  replicas: 3
  image: nginx:latest
```

**Service示例 (my-service.yaml):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: namespace1
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 8080
```

**ConfigMap示例 (my-config.yaml):**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
  namespace: namespace1
data:
  application.yaml: |
    server:
      port: 8080
    logging:
      level: INFO
```

## 3. 功能演示

### 功能1: 命令生成器

1. 启动程序，切换到"命令生成器"标签
2. 点击"选择集群文件夹"，选择 `test_cluster` 文件夹
3. 点击"解析并显示资源"
4. 查看解析出的资源列表
5. 点击"生成部署命令"，保存为 `deploy.sh`
6. 点击"生成删除命令"，保存为 `delete.sh`
7. 点击"导出资源表到Excel"，保存资源清单

### 功能2: YAML比较器

#### 集群比较模式：
1. 准备两个集群文件夹（如 `cluster1` 和 `cluster2`）
2. 切换到"YAML比较器"标签
3. 选择"集群文件夹比较"模式
4. 分别选择两个集群
5. 添加比较Key（如 `spec.replicas`）
6. 点击"执行比较"
7. 点击"导出比较结果到Excel"

#### 单文件比较模式：
1. 准备两个YAML文件
2. 选择"单文件比较"模式
3. 分别选择两个文件
4. 添加比较Key
5. 执行比较并导出

#### ConfigMap文件内容比较：
1. 添加Key配置行
2. 勾选"ConfigMap文件"复选框
3. 填写文件Key（如 `application.yaml`）
4. 选择文件类型（yaml/properties/text）
5. 可选：填写比较Key（如 `server.port`）
6. 执行比较

### 功能3: 信息提取器

1. 切换到"信息提取器"标签
2. 点击"选择文件夹"或"选择文件"
3. 添加提取Key配置：
   - Key路径：`spec.replicas`
   - 别名：`副本数`
4. 点击"提取信息"
5. 点击"导出提取结果到Excel"

## 4. 高级用法

### Key路径语法

支持以下格式：
- 简单路径: `metadata.name`
- 嵌套路径: `spec.template.spec.containers`
- 数组索引: `spec.containers[0].image`
- 混合路径: `spec.containers[0].env[1].value`

### ConfigMap/Secret文件处理

对于ConfigMap或Secret中的文件内容，有三种处理方式：

1. **文本模式**: 直接比较文本内容
2. **YAML模式**: 解析为YAML后比较指定Key
3. **Properties模式**: 解析为Properties后比较指定Key

### 批量操作技巧

1. **按资源类型筛选**: 使用资源类型复选框快速筛选
2. **表格多选**: 按住Ctrl键点击可选择多个资源
3. **全选**: 不勾选任何资源类型且不选择表格行时，处理所有资源

## 5. 常见问题

### Q: 程序无法启动？
A: 确保已安装Python 3.9+和所有依赖包

### Q: 解析失败？
A: 检查YAML文件格式和文件夹结构是否正确

### Q: 命令生成顺序是否正确？
A: 是的，删除和部署命令已按正确顺序生成

### Q: Excel导出的Sheet数量限制？
A: 单文件最多250个Sheet，超出会自动分文件

### Q: 支持哪些资源类型？
A: 目前支持：Application、Deployment、ConfigMap、PersistentVolumeClaim、Secret、Service

## 6. 下一步

- 探索更多Key路径组合
- 尝试比较大型集群
- 自定义提取规则
- 将工具集成到CI/CD流程

## 7. 获取帮助

程序内置了使用说明，点击菜单栏"帮助" -> "使用说明"查看详细指南。
