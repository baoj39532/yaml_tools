# GitHub设置指南

## ✅ 当前状态

Git仓库已初始化并提交完成：
- ✅ 35个文件已提交
- ✅ 提交哈希: 0a29b73
- ✅ 分支: main
- ✅ 准备推送到GitHub

---

## 📋 接下来的步骤

### 步骤2: 在GitHub创建仓库（3分钟）

#### 1. 访问GitHub
打开浏览器，访问: https://github.com

#### 2. 登录账号
- 如果没有账号，点击 "Sign up" 注册（免费）
- 如果有账号，点击 "Sign in" 登录

#### 3. 创建新仓库
- 点击右上角的 "+" 号
- 选择 "New repository"

#### 4. 填写仓库信息

**Repository name** (仓库名):
```
yaml_tools
```

**Description** (描述):
```
K8s YAML管理工具 - 可视化的Kubernetes YAML文件管理工具，支持命令生成、YAML比较和信息提取
```

**Public or Private** (公开或私有):
- 选择 **Public** (公开) - 推荐
  - ✅ GitHub Actions完全免费
  - ✅ 可以分享给其他人
  - ✅ 可以展示在您的Profile中
- 或选择 **Private** (私有)
  - ⚠️ 每月2000分钟Actions免费额度
  - 足够使用，但有限制

**初始化选项**:
- ❌ **不要**勾选 "Add a README file"
- ❌ **不要**勾选 "Add .gitignore"
- ❌ **不要**选择 License
- （因为我们本地已经有这些文件了）

#### 5. 创建仓库
点击绿色的 "Create repository" 按钮

---

### 步骤3: 推送代码到GitHub（2分钟）

创建仓库后，GitHub会显示一个页面，复制您的仓库URL。

#### 获取仓库URL

URL格式如下：
```
https://github.com/你的用户名/yaml_tools.git
```

例如，如果用户名是 `baojunyuan`，URL就是：
```
https://github.com/baojunyuan/yaml_tools.git
```

#### 在终端执行推送命令

**重要**: 将下面命令中的 `你的用户名` 替换为您的实际GitHub用户名

```bash
# 方法1: 在终端运行（推荐）
cd /Users/baojunyuan/codeplace/yaml_tools

# 添加远程仓库（替换你的用户名）
git remote add origin https://github.com/你的用户名/yaml_tools.git

# 推送代码
git push -u origin main
```

如果遇到权限问题，GitHub可能会弹出登录窗口，输入您的GitHub账号和密码即可。

---

### 步骤4: 等待自动构建（8-10分钟）

#### 1. 查看Actions运行状态

推送完成后：
1. 访问: `https://github.com/你的用户名/yaml_tools/actions`
2. 您会看到 "构建多平台应用" 工作流正在运行
3. 三个并行任务:
   - 🔄 build-windows (构建Windows版本)
   - 🔄 build-macos (构建macOS版本)
   - 🔄 build-linux (构建Linux版本)

#### 2. 监控构建进度

- 点击具体的构建任务查看详细日志
- 🟡 黄色圆点 = 正在运行
- ✅ 绿色勾号 = 构建成功
- ❌ 红色叉号 = 构建失败（可查看日志排查）

#### 3. 预计时间

- Windows构建: 约6-8分钟
- macOS构建: 约5-7分钟
- Linux构建: 约5-7分钟

---

### 步骤5: 下载构建产物（1分钟）

#### 1. 进入完成的构建任务

构建全部完成后（三个都显示绿色✅）：
1. 点击任意一个成功的构建
2. 滚动到页面底部

#### 2. 下载Artifacts

在底部的 **Artifacts** 区域，您会看到：

```
📦 K8s_YAML管理工具-Windows    [Download]  ⭐ 重点
📦 K8s_YAML管理工具-macOS      [Download]
📦 K8s_YAML管理工具-Linux      [Download]
```

#### 3. 获取Windows版本

1. 点击 **K8s_YAML管理工具-Windows** 下载
2. 下载的是一个 `.zip` 文件
3. 解压后得到: `K8s_YAML管理工具.exe` ✅

**大小**: 约30-40 MB
**系统**: Windows 10/11 (x64)
**依赖**: 无（独立运行）

---

## 🎉 完成！

现在您有了三个平台的可执行文件：

| 平台 | 文件 | 状态 |
|------|------|------|
| Windows | K8s_YAML管理工具.exe | ✅ 通过GitHub Actions构建 |
| macOS | K8s_YAML管理工具.app | ✅ 本地已构建 |
| Linux | K8s_YAML管理工具 | ✅ 通过GitHub Actions构建 |

---

## 📝 快速命令参考

### 完整命令序列

```bash
# 1. 进入项目目录
cd /Users/baojunyuan/codeplace/yaml_tools

# 2. 添加远程仓库（替换你的用户名！）
git remote add origin https://github.com/你的GitHub用户名/yaml_tools.git

# 3. 推送代码
git push -u origin main

# 完成！访问GitHub查看Actions构建进度
```

### 如果推送失败

如果提示需要认证：

```bash
# GitHub推荐使用Personal Access Token
# 1. 访问: https://github.com/settings/tokens
# 2. 生成新token（勾选repo权限）
# 3. 使用token作为密码
```

或使用GitHub CLI:
```bash
# 安装GitHub CLI
brew install gh

# 登录
gh auth login

# 推送
git push -u origin main
```

---

## 🔄 后续更新

以后如果修改了代码，只需：

```bash
# 1. 提交更改
git add .
git commit -m "更新说明"

# 2. 推送
git push

# GitHub Actions会自动重新构建！
```

---

## ❓ 常见问题

### Q: 推送时提示"Permission denied"？
**A**: 需要配置GitHub认证
- 方案1: 使用Personal Access Token
- 方案2: 配置SSH Key
- 方案3: 使用GitHub Desktop（图形界面）

### Q: Actions显示红色❌构建失败？
**A**: 点击查看日志，通常是依赖问题
- 检查requirements.txt是否正确
- 查看具体错误信息
- 可能需要调整build.yml配置

### Q: 找不到Artifacts下载链接？
**A**: 确保：
- 构建已完成（绿色✅）
- 滚动到页面最底部
- Artifacts保留30天，过期自动删除

### Q: 下载的是.zip但找不到.exe？
**A**: 
- 解压.zip文件
- Windows: 右键 → 解压到...
- macOS: 双击.zip自动解压

---

## 📞 需要帮助？

如果遇到问题：

1. **查看GitHub文档**: https://docs.github.com
2. **查看Actions日志**: 点击失败的构建任务
3. **检查网络**: 确保可以访问GitHub
4. **尝试GitHub Desktop**: 如果命令行有问题

---

## 🎯 下一步检查清单

完成后请验证：

- [ ] GitHub仓库已创建
- [ ] 代码已推送成功
- [ ] Actions标签页显示工作流
- [ ] 三个构建任务都是绿色✅
- [ ] 已下载Windows .exe文件
- [ ] 在Windows上测试.exe可以运行
- [ ] 三个功能（命令生成、比较、提取）都正常

---

**祝您成功！** 🚀

有任何问题随时告诉我！
