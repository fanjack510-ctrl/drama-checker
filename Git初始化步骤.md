# Git 仓库初始化步骤

## 问题诊断

**错误信息：** `fatal: not a git repository (or any of the parent directories): .git`

**原因：** 当前目录 `E:\00-个人开发\Drama` 还没有初始化为 Git 仓库。

---

## 解决方案

### 方案 A：初始化新的 Git 仓库（推荐）

**适用场景：** 项目还没有 Git 仓库，需要从头开始

**操作步骤：**

#### 步骤 1：初始化 Git 仓库

在项目根目录执行：
```bash
git init
```

**预期结果：**
```
Initialized empty Git repository in E:/00-个人开发/Drama/.git/
```

#### 步骤 2：添加所有文件

```bash
git add .
```

**预期结果：**
- 无错误信息
- 文件被添加到暂存区

#### 步骤 3：创建首次提交

```bash
git commit -m "Initial commit: 准备部署到 Railway"
```

**预期结果：**
```
[main (root-commit) xxxxxx] Initial commit: 准备部署到 Railway
 X files changed, X insertions(+)
```

#### 步骤 4：在 GitHub 创建新仓库

1. 登录 GitHub：https://github.com
2. 点击右上角 **"+"** → **"New repository"**
3. 填写仓库信息：
   - **Repository name**：`drama-checker`（或你喜欢的名字）
   - **Description**：`剧情短视频体检器`（可选）
   - **Visibility**：选择 **Public** 或 **Private**
   - **不要**勾选 "Initialize this repository with a README"（因为本地已有代码）
4. 点击 **"Create repository"**

**预期结果：**
- GitHub 显示仓库创建成功
- 显示 "Quick setup" 页面，包含仓库 URL（例如：`https://github.com/your-username/drama-checker.git`）

#### 步骤 5：添加远程仓库

复制 GitHub 显示的仓库 URL，然后执行：
```bash
git remote add origin https://github.com/your-username/drama-checker.git
```

**注意：** 将 `your-username/drama-checker` 替换为你的实际仓库地址

**预期结果：**
- 无错误信息

#### 步骤 6：推送到 GitHub

```bash
git branch -M main
git push -u origin main
```

**预期结果：**
- 如果首次推送，可能需要输入 GitHub 用户名和密码（或 Personal Access Token）
- 显示推送进度：
```
Enumerating objects: X, done.
Counting objects: 100% (X/X), done.
Writing objects: 100% (X/X), done.
To https://github.com/your-username/drama-checker.git
 * [new branch]      main -> main
Branch 'main' set up to track 'remote/origin/main'.
```

---

### 方案 B：连接现有 GitHub 仓库

**适用场景：** 已经在 GitHub 创建了仓库，需要连接本地代码

**操作步骤：**

#### 步骤 1：初始化 Git 仓库

```bash
git init
```

#### 步骤 2：添加所有文件

```bash
git add .
```

#### 步骤 3：创建首次提交

```bash
git commit -m "Initial commit: 准备部署到 Railway"
```

#### 步骤 4：添加远程仓库

```bash
git remote add origin https://github.com/your-username/your-repo-name.git
```

**注意：** 将 URL 替换为你的实际仓库地址

#### 步骤 5：推送到 GitHub

```bash
git branch -M main
git push -u origin main
```

---

## 完整操作示例（方案 A）

```bash
# 1. 初始化仓库
git init

# 2. 添加所有文件
git add .

# 3. 创建提交
git commit -m "Initial commit: 准备部署到 Railway"

# 4. 添加远程仓库（替换为你的实际 URL）
git remote add origin https://github.com/your-username/drama-checker.git

# 5. 重命名分支为 main（如果当前是 master）
git branch -M main

# 6. 推送到 GitHub
git push -u origin main
```

---

## 常见问题

### Q1: 推送时提示需要认证

**错误信息：**
```
remote: Support for password authentication was removed...
```

**解决方法：**
1. 使用 Personal Access Token（推荐）：
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 点击 "Generate new token"
   - 勾选 `repo` 权限
   - 复制生成的 token
   - 推送时，密码输入框输入 token（不是密码）

2. 或使用 SSH（推荐长期使用）：
   ```bash
   # 生成 SSH 密钥（如果还没有）
   ssh-keygen -t ed25519 -C "your_email@example.com"
   
   # 复制公钥
   cat ~/.ssh/id_ed25519.pub
   
   # 在 GitHub → Settings → SSH and GPG keys → New SSH key
   # 粘贴公钥并保存
   
   # 修改远程仓库 URL 为 SSH
   git remote set-url origin git@github.com:your-username/drama-checker.git
   ```

### Q2: 推送时提示分支冲突

**错误信息：**
```
error: failed to push some refs to 'origin'
hint: Updates were rejected because the remote contains work...
```

**解决方法：**
如果远程仓库有内容（如 README），需要先拉取：
```bash
git pull origin main --allow-unrelated-histories
# 解决冲突后
git push -u origin main
```

### Q3: 如何检查远程仓库是否添加成功

```bash
git remote -v
```

**预期结果：**
```
origin  https://github.com/your-username/drama-checker.git (fetch)
origin  https://github.com/your-username/drama-checker.git (push)
```

---

## 验证步骤

完成上述步骤后，验证：

```bash
# 1. 检查 Git 状态
git status

# 预期结果：显示 "nothing to commit, working tree clean"

# 2. 检查远程仓库
git remote -v

# 预期结果：显示你的 GitHub 仓库 URL

# 3. 检查提交历史
git log --oneline

# 预期结果：显示至少一条提交记录
```

---

## 完成后继续 Railway 部署

完成 Git 初始化后，可以继续执行 `Railway部署操作清单.md` 的步骤 1（登录 Railway）。

---

**提示：** 如果遇到其他问题，可以：
1. 查看 Git 帮助：`git help`
2. 查看 GitHub 文档：https://docs.github.com
3. 检查网络连接和 GitHub 访问

