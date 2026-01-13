# 测试指南

本文档提供详细的测试数据准备和功能测试指南。

## 创建测试数据

### 1. 基本测试结构

创建以下文件夹结构：

```
test_data/
├── cluster1/
│   ├── prod-namespace/
│   │   ├── Application/
│   │   │   ├── web-app.yaml
│   │   │   └── api-app.yaml
│   │   ├── Service/
│   │   │   ├── web-svc.yaml
│   │   │   └── api-svc.yaml
│   │   ├── ConfigMap/
│   │   │   ├── web-config.yaml
│   │   │   └── api-config.yaml
│   │   ├── Secret/
│   │   │   └── db-secret.yaml
│   │   └── PersistentVolumeClaim/
│   │       └── data-pvc.yaml
│   └── test-namespace/
│       └── Application/
│           └── test-app.yaml
└── cluster2/
    └── prod-namespace/
        ├── Application/
        │   └── web-app.yaml
        └── ConfigMap/
            └── web-config.yaml
```

### 2. 示例YAML文件内容

#### Application: web-app.yaml (cluster1)
```yaml
apiVersion: apps/v1
kind: Application
metadata:
  name: web-app
  namespace: prod-namespace
spec:
  replicas: 3
  image: nginx:1.21
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi
```

#### Application: web-app.yaml (cluster2 - 用于比较)
```yaml
apiVersion: apps/v1
kind: Application
metadata:
  name: web-app
  namespace: prod-namespace
spec:
  replicas: 5  # 不同：副本数改为5
  image: nginx:1.22  # 不同：镜像版本不同
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi
```

#### Service: web-svc.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-svc
  namespace: prod-namespace
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: 8080
  selector:
    app: web-app
```

#### ConfigMap: web-config.yaml (cluster1)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
  namespace: prod-namespace
data:
  application.yaml: |
    server:
      port: 8080
      host: 0.0.0.0
    logging:
      level: INFO
      format: json
    database:
      host: db.example.com
      port: 5432
  application.properties: |
    server.port=8080
    server.host=0.0.0.0
    logging.level=INFO
    database.host=db.example.com
```

#### ConfigMap: web-config.yaml (cluster2 - 用于比较)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
  namespace: prod-namespace
data:
  application.yaml: |
    server:
      port: 9090  # 不同：端口改为9090
      host: 0.0.0.0
    logging:
      level: DEBUG  # 不同：日志级别改为DEBUG
      format: json
    database:
      host: db.example.com
      port: 5432
  application.properties: |
    server.port=9090
    server.host=0.0.0.0
    logging.level=DEBUG
    database.host=db.example.com
```

#### Secret: db-secret.yaml
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: prod-namespace
type: Opaque
data:
  username: YWRtaW4=  # base64: admin
  password: cGFzc3dvcmQ=  # base64: password
```

#### PersistentVolumeClaim: data-pvc.yaml
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
  namespace: prod-namespace
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

#### 多资源文件示例 (api-app.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deploy
  namespace: prod-namespace
spec:
  replicas: 2
---
apiVersion: apps/v1
kind: Application
metadata:
  name: api-app
  namespace: prod-namespace
spec:
  replicas: 2
  image: myapi:1.0
```

## 测试场景

### 场景1: 命令生成测试

**目标**: 测试生成正确的部署和删除命令

**步骤**:
1. 选择 `test_data/cluster1`
2. 解析并显示资源
3. 验证资源数量和信息正确
4. 生成部署命令，检查顺序：
   - PersistentVolumeClaim → Secret → ConfigMap → Application → Service
5. 生成删除命令，检查顺序：
   - Service → Application → ConfigMap → Secret → PersistentVolumeClaim
6. 验证Deployment不在删除命令中

**预期结果**:
- 部署命令示例：
  ```bash
  condep deploy -f prod-namespace/PersistentVolumeClaim/data-pvc.yaml -n prod-namespace -c cluster1 --app no
  condep deploy -f prod-namespace/Secret/db-secret.yaml -n prod-namespace -c cluster1 --app no
  condep deploy -f prod-namespace/ConfigMap/web-config.yaml -n prod-namespace -c cluster1 --app no
  condep deploy -f prod-namespace/Application/web-app.yaml -n prod-namespace -c cluster1 --app yes
  condep deploy -f prod-namespace/Service/web-svc.yaml -n prod-namespace -c cluster1 --app no
  ```

### 场景2: 集群比较测试

**目标**: 测试两个集群之间的差异检测

**步骤**:
1. 选择集群文件夹比较模式
2. 选择 cluster1 和 cluster2
3. 添加比较Key:
   - `spec.replicas`
   - `spec.image`
4. 执行比较
5. 导出Excel结果

**预期结果**:
- 发现 web-app 的差异：
  - spec.replicas: 3 vs 5
  - spec.image: nginx:1.21 vs nginx:1.22

### 场景3: ConfigMap内容比较测试

**目标**: 测试ConfigMap文件内容的深度比较

**步骤**:
1. 选择集群文件夹比较模式
2. 选择 cluster1 和 cluster2
3. 添加ConfigMap文件比较Key:
   - 勾选"ConfigMap文件"
   - 文件Key: `application.yaml`
   - 文件类型: `yaml`
   - 比较Key: `server.port`
4. 添加另一个ConfigMap比较:
   - 文件Key: `application.yaml`
   - 文件类型: `yaml`
   - 比较Key: `logging.level`
5. 执行比较

**预期结果**:
- data.application.yaml.server.port: 8080 vs 9090
- data.application.yaml.logging.level: INFO vs DEBUG

### 场景4: Properties文件比较测试

**步骤**:
1. 添加ConfigMap文件比较Key:
   - 文件Key: `application.properties`
   - 文件类型: `properties`
   - 比较Key: `server.port`
2. 执行比较

**预期结果**:
- data.application.properties.server.port: 8080 vs 9090

### 场景5: 信息提取测试

**目标**: 测试从YAML中提取指定信息

**步骤**:
1. 选择 `test_data/cluster1` 文件夹
2. 添加提取Key:
   - Key路径: `spec.replicas`, 别名: `副本数`
   - Key路径: `spec.image`, 别名: `镜像`
   - Key路径: `spec.resources.limits.cpu`, 别名: `CPU限制`
3. 执行提取
4. 导出Excel

**预期结果**:
- Excel中包含所有Application资源的副本数、镜像和CPU限制信息

### 场景6: ConfigMap文件内容提取测试

**步骤**:
1. 选择 cluster1 文件夹
2. 添加ConfigMap文件提取:
   - 勾选"ConfigMap文件"
   - 文件Key: `application.yaml`
   - 文件类型: `yaml`
   - 提取Key: `server.port`
   - 别名: `服务端口`
3. 执行提取

**预期结果**:
- 提取出 web-config 和 api-config 的服务端口配置

### 场景7: Excel导出测试

**目标**: 测试Excel导出功能和Sheet限制处理

**准备**: 创建包含大量资源的测试数据（250+个不同名称的资源）

**步骤**:
1. 导出资源表
2. 导出比较结果
3. 导出提取结果

**验证**:
- 检查Excel文件格式正确
- 验证Sheet名称和内容
- 验证超过250个Sheet时自动分文件

### 场景8: 多文档YAML测试

**目标**: 测试单文件多资源（---分隔）的解析

**步骤**:
1. 解析包含 `api-app.yaml`（包含Deployment和Application）的集群
2. 验证两个资源都被正确识别

**预期结果**:
- 表格中显示2个资源（api-deploy和api-app）

## 边界条件测试

### 测试1: 空文件夹
- 选择空文件夹
- 验证友好的错误提示

### 测试2: 无效YAML格式
- 创建格式错误的YAML文件
- 验证错误被捕获并显示

### 测试3: 缺少必需字段
- 创建缺少kind或metadata.name的YAML
- 验证验证逻辑正常工作

### 测试4: 特殊字符处理
- 使用包含特殊字符的资源名
- 验证Excel Sheet名称正确处理

### 测试5: 大文件处理
- 创建包含大量数据的YAML文件
- 验证性能和内存使用

## 性能测试

### 测试数据规模
- 小型: 10个资源
- 中型: 100个资源
- 大型: 1000个资源

### 测试指标
- 解析时间
- 比较时间
- Excel导出时间
- 内存使用

## 回归测试清单

每次修改后执行以下检查：

- [ ] 所有三个功能标签页可以正常切换
- [ ] 文件/文件夹选择对话框正常工作
- [ ] 资源解析正确识别所有类型
- [ ] 命令生成顺序正确
- [ ] 比较功能正确识别差异
- [ ] 提取功能正确获取值
- [ ] Excel导出文件格式正确
- [ ] 错误提示友好且准确
- [ ] 状态栏显示正确信息
- [ ] 帮助菜单内容完整

## 自动化测试建议

未来可以考虑添加：
1. 单元测试（pytest）
2. UI自动化测试（pytest-qt）
3. 集成测试
4. 性能基准测试

## 报告问题

测试过程中发现问题时，请记录：
1. 操作步骤
2. 预期结果
3. 实际结果
4. 错误信息（如有）
5. 测试数据
6. 系统环境
