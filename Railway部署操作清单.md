# Railway 部署操作清单 - 从 0 到上线

> 本文档提供 Railway 部署的详细步骤，每一步都明确说明"在哪里点击什么、填写什么、看到什么结果"

---

## 📋 前置准备

### 步骤 0.1：确认代码已推送到 GitHub

**操作：**
1. 打开终端，进入项目目录
2. 执行：
```bash
git status
```

**预期结果：**
- 显示 `nothing to commit, working tree clean`（所有文件已提交）
- 或显示需要提交的文件列表

**如果未提交：**
```bash
git add .
git commit -m "准备部署到 Railway"
git push origin main
```

**预期结果：**
- 代码成功推送到 GitHub
- 可以在 GitHub 网页上看到最新提交

---

## 🚀 Railway 部署步骤

### 步骤 1：登录 Railway

**操作：**
1. 打开浏览器，访问：https://railway.app
2. 点击页面右上角的 **"Login"** 按钮
3. 选择 **"Login with GitHub"**
4. 如果首次使用，会跳转到 GitHub 授权页面
5. 点击 **"Authorize Railway"** 授权

**预期结果：**
- 跳转回 Railway Dashboard
- 页面显示 "Welcome to Railway" 或项目列表（如果已有项目）

---

### 步骤 2：创建新项目

**操作：**
1. 在 Railway Dashboard 页面，点击左上角的 **"New Project"** 按钮
2. 在弹出的选项中，选择 **"Deploy from GitHub repo"**

**预期结果：**
- 页面显示 GitHub 仓库列表
- 如果首次使用，可能显示 "Configure GitHub App" 提示

---

### 步骤 3：配置 GitHub App（首次使用）

**如果看到 "Configure GitHub App" 或仓库列表为空：**

**操作：**
1. 点击 **"Configure GitHub App"** 或 **"Configure"** 按钮
2. 跳转到 GitHub 授权页面
3. 选择授权范围：
   - **推荐**：选择 **"Only select repositories"**（更安全）
   - 然后在下拉列表中选择你的仓库
   - 或选择 **"All repositories"**（如果信任 Railway）
4. 点击 **"Install"** 按钮

**预期结果：**
- 显示 "Successfully installed Railway"
- 自动跳转回 Railway 页面
- 仓库列表显示你的 GitHub 仓库

---

### 步骤 4：选择仓库

**操作：**
1. 在仓库列表中，找到你的项目仓库（例如：`your-username/drama-checker`）
2. 点击仓库名称

**预期结果：**
- Railway 开始检测项目类型
- 页面显示 "Detecting project type..." 或类似提示
- 几秒后显示项目配置页面

---

### 步骤 5：配置 Root Directory

**操作：**
1. 在项目配置页面，找到 **"Settings"** 标签（通常在页面顶部）
2. 点击 **"Settings"** 标签
3. 向下滚动，找到 **"Root Directory"** 设置项
4. 点击 **"Root Directory"** 右侧的 **"Edit"** 或 **"Change"** 按钮
5. 在输入框中输入：`backend`
6. 点击 **"Save"** 或 **"Update"** 按钮

**预期结果：**
- Root Directory 显示为 `backend`
- 页面可能自动刷新或显示保存成功提示

**如果找不到 Root Directory 设置：**
- 在 Settings 页面查找 **"Deploy"** 部分
- 或在项目主页面查找 **"Configure"** 按钮

**替代方案（如果 Railway 不支持 Root Directory）：**
- 在项目根目录创建 `railway.json` 文件：
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

### 步骤 6：确认 Start Command / Procfile

**操作：**
1. 在 Settings 页面，找到 **"Deploy"** 部分
2. 查找 **"Start Command"** 设置项
3. **检查状态：**
   - 如果显示 **"Using Procfile"** 或 **"Detected Procfile"** → ✅ 无需操作
   - 如果显示输入框或 **"Not set"** → 继续下一步

**如果 Start Command 为空或未检测到 Procfile：**

**方案 A：让 Railway 自动检测 Procfile（推荐）**
1. 确认 `backend/Procfile` 文件存在且内容为：
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
2. 点击 **"Redeploy"** 或等待 Railway 重新检测

**方案 B：手动设置 Start Command**
1. 点击 **"Start Command"** 右侧的 **"Edit"** 按钮
2. 在输入框中输入：
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. 点击 **"Save"** 按钮

**预期结果：**
- Start Command 显示为 `uvicorn main:app --host 0.0.0.0 --port $PORT`
- 或显示 "Using Procfile: web"

---

### 步骤 7：配置环境变量

**操作：**
1. 在 Settings 页面，找到 **"Variables"** 部分（通常在页面中下部）
2. 点击 **"New Variable"** 按钮
3. **添加第一个变量：**
   - **Name** 输入框：输入 `LLM_ENABLED`
   - **Value** 输入框：输入 `false`
   - 点击 **"Add"** 按钮
4. **添加第二个变量（可选）：**
   - **Name** 输入框：输入 `QWEN_API_KEY`
   - **Value** 输入框：**留空** 或输入 `dummy`（如果 Railway 要求不能为空）
   - 点击 **"Add"** 按钮

**预期结果：**
- Variables 列表显示：
  - `LLM_ENABLED` = `false`
  - `QWEN_API_KEY` = （空或 dummy）

**注意：**
- 如果 `QWEN_API_KEY` 留空导致问题，可以暂时填 `dummy`，后续再更新

---

### 步骤 8：触发部署

**操作：**
1. 回到项目主页面（点击项目名称或 "Overview" 标签）
2. 查看 **"Deployments"** 部分
3. **如果已有部署记录：**
   - 点击最新的部署记录右侧的 **"Redeploy"** 按钮
   - 或点击 **"Deploy"** 按钮（如果有）
4. **如果是首次部署：**
   - Railway 会自动开始部署
   - 等待几秒，页面会自动刷新

**预期结果：**
- 页面显示部署进度
- 部署日志开始滚动显示
- 状态显示为 "Building..." 或 "Deploying..."

---

### 步骤 9：等待部署完成

**操作：**
1. 在项目主页面，点击 **"Deployments"** 标签
2. 点击最新的部署记录
3. 查看 **"Logs"** 标签

**预期看到的日志：**
```
Collecting fastapi==0.104.1
Collecting uvicorn[standard]==0.24.0
...
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:xxxx (Press CTRL+C to quit)
```

**预期结果：**
- 部署状态变为 **"Active"**（绿色）
- 日志显示 "Application startup complete"
- 无红色错误信息

**如果看到错误：**
- 参考下方"常见报错排查"部分

---

### 步骤 10：获取公网域名

**操作：**
1. 在项目主页面，找到 **"Domains"** 部分（通常在右侧或下方）
2. 如果显示 **"Generate Domain"** 按钮：
   - 点击 **"Generate Domain"** 按钮
3. 如果已有域名：
   - 直接复制显示的域名（例如：`xxx-production.up.railway.app`）

**预期结果：**
- 显示一个类似 `xxx-production.up.railway.app` 的域名
- 域名可以点击复制

**记录这个域名，后续验证需要使用！**

---

## ✅ 部署后验证

### 步骤 11：验证健康检查端点

**操作：**
1. 打开浏览器
2. 在地址栏输入：`https://你的railway域名/health`
   - 例如：`https://xxx-production.up.railway.app/health`
3. 按回车访问

**预期结果：**
- 页面显示：`{"ok":true}`
- 无错误页面

**如果看到错误：**
- 404 Not Found → 检查 Root Directory 是否正确设置为 `backend`
- 500 Internal Server Error → 查看 Railway 日志
- 连接超时 → 检查部署是否完成（状态是否为 Active）

---

### 步骤 12：验证 API 端点（使用 curl）

**Windows PowerShell：**
```powershell
$body = @{
    text = "今天天气真好，我出门了。但是突然下雨了，我很生气。然后我跑回家了。"
    mode = "drama_emotion"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://你的railway域名/api/analyze" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

**Windows CMD：**
```cmd
curl.exe -X POST https://你的railway域名/api/analyze -H "Content-Type: application/json" -d "{\"text\":\"今天天气真好，我出门了。但是突然下雨了，我很生气。然后我跑回家了。\",\"mode\":\"drama_emotion\"}"
```

**Linux/Mac：**
```bash
curl -X POST https://你的railway域名/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"今天天气真好，我出门了。但是突然下雨了，我很生气。然后我跑回家了。","mode":"drama_emotion"}'
```

**预期结果：**
返回 JSON，包含以下字段：
```json
{
  "score": 65,
  "risk_level": "warn",
  "summary": ["前5秒缺乏明确冲突或悬念", "..."],
  "issues_high": [...],
  "issues_mid": [...],
  "risky_section": "前段",
  "viewer_reaction": "如果我是观众，我会在前5秒觉得没什么意思就划走了",
  "directions": ["在开头建立明确的冲突或悬念", "..."],
  "evidence": [...],
  "meta": {"version": "1.0.0", "engine": "rule"}
}
```

**如果看到错误：**
- 400 Bad Request → 检查请求体格式是否正确
- 500 Internal Server Error → 查看 Railway 日志
- CORS 错误 → 检查 CORS 配置（应该允许所有来源）

---

### 步骤 13：查看 API 文档（可选）

**操作：**
1. 在浏览器访问：`https://你的railway域名/docs`
2. 查看 Swagger UI 界面

**预期结果：**
- 显示 Swagger API 文档页面
- 可以看到 `GET /health` 和 `POST /api/analyze` 两个端点
- 可以点击 "Try it out" 测试 API

---

## 🔧 常见报错排查

### 错误 1：ModuleNotFoundError

**症状：**
部署日志显示：
```
ModuleNotFoundError: No module named 'fastapi'
```
或
```
ModuleNotFoundError: No module named 'xxx'
```

**排查步骤：**
1. 在 Railway 项目页面，点击 **"Settings"** 标签
2. 找到 **"Deployments"** 部分
3. 检查 **"Build Command"** 是否为空
   - 如果为空 → ✅ 正确（Railway 会自动运行 `pip install -r requirements.txt`）
   - 如果有自定义命令 → 检查是否正确

4. 检查 `backend/requirements.txt` 文件：
   - 确认文件在 `backend/` 目录下
   - 确认包含缺失的模块（例如：`fastapi==0.104.1`）

5. 查看部署日志的 **"Build"** 阶段：
   - 查找 `Collecting fastapi` 或 `Installing collected packages`
   - 确认是否成功安装

**解决方法：**
- 如果 `requirements.txt` 缺少模块，添加后重新提交代码
- 如果文件位置不对，确认 Root Directory 设置为 `backend`
- 点击 **"Redeploy"** 重新部署

---

### 错误 2：Port binding

**症状：**
部署日志显示：
```
Error: listen EADDRINUSE: address already in use :::xxxx
```
或
```
Address already in use
```

**排查步骤：**
1. 检查 `backend/Procfile` 内容：
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
   - ✅ 确认使用 `$PORT`（Railway 会自动提供）
   - ❌ 不要硬编码端口号（如 `--port 8000`）

2. 检查 `backend/main.py` 中的启动命令：
   - 如果使用 `uvicorn.run()`，确认使用 `$PORT` 环境变量
   - Railway 会自动设置 `$PORT`，无需手动读取

**解决方法：**
- 确认 Procfile 使用 `$PORT`
- 如果手动设置了 Start Command，确保使用 `$PORT` 而不是固定端口
- 重新部署

---

### 错误 3：Procfile 未生效

**症状：**
- Start Command 显示为其他命令，而不是 Procfile 中的内容
- 或部署失败，提示找不到命令

**排查步骤：**
1. 在 Railway 项目页面，点击 **"Settings"** 标签
2. 找到 **"Deploy"** 部分
3. 检查 **"Start Command"** 显示：
   - 如果显示 **"Using Procfile: web"** → ✅ 正确
   - 如果显示其他命令 → 继续排查

4. 检查 `backend/Procfile` 文件：
   - 确认文件在 `backend/` 目录下
   - 确认文件名是 `Procfile`（首字母大写，无扩展名）
   - 确认内容格式：
     ```
     web: uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
     - 注意：`web:` 后面有空格
     - 注意：使用 `$PORT` 而不是固定端口

**解决方法：**
- 如果 Procfile 位置不对，确认 Root Directory 设置为 `backend`
- 如果格式不对，修正后重新提交代码
- 在 Settings 中手动设置 Start Command：
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
- 点击 **"Redeploy"** 重新部署

---

### 错误 4：requirements.txt 不生效

**症状：**
- 部署日志中没有显示 `pip install` 的过程
- 或依赖安装失败

**排查步骤：**
1. 检查 `backend/requirements.txt` 文件：
   - 确认文件在 `backend/` 目录下
   - 确认文件名是 `requirements.txt`（全小写）
   - 确认文件内容格式正确：
     ```
     fastapi==0.104.1
     uvicorn[standard]==0.24.0
     pydantic==2.5.0
     requests>=2.31.0
     ```

2. 查看部署日志的 **"Build"** 阶段：
   - 查找 `Collecting fastapi` 或 `Installing collected packages`
   - 如果没有这些日志 → Railway 可能没有检测到 requirements.txt

3. 检查 Root Directory：
   - 确认设置为 `backend`
   - Railway 会在 Root Directory 下查找 `requirements.txt`

**解决方法：**
- 确认 `requirements.txt` 在 `backend/` 目录下
- 确认 Root Directory 设置为 `backend`
- 如果文件格式有问题，修正后重新提交代码
- 点击 **"Redeploy"** 重新部署

---

### 错误 5：ImportError 或找不到模块

**症状：**
部署日志显示：
```
ImportError: cannot import name 'AnalyzeRequest' from 'schema'
```
或
```
ModuleNotFoundError: No module named 'schema'
```

**排查步骤：**
1. 检查所有 Python 文件是否在 `backend/` 目录下：
   - ✅ `backend/main.py`
   - ✅ `backend/schema.py`
   - ✅ `backend/scorer_rules.py`
   - ✅ `backend/config.py`

2. 检查 `backend/main.py` 中的导入语句：
   ```python
   from schema import AnalyzeRequest, AnalyzeResponse, HealthResponse
   ```
   - 确认使用相对导入或绝对导入
   - 如果使用相对导入，确保所有文件在同一目录

3. 检查 Root Directory：
   - 确认设置为 `backend`
   - Railway 会在 Root Directory 下查找所有文件

**解决方法：**
- 确认所有文件在 `backend/` 目录下
- 确认 Root Directory 设置为 `backend`
- 如果导入路径有问题，修正后重新提交代码
- 点击 **"Redeploy"** 重新部署

---

### 错误 6：部署成功但 API 返回 500

**症状：**
- 部署状态显示 "Active"
- 访问 `/health` 返回 500 错误
- 或访问 `/api/analyze` 返回 500 错误

**排查步骤：**
1. 在 Railway 项目页面，点击 **"Deployments"** 标签
2. 点击最新的部署记录
3. 查看 **"Logs"** 标签
4. 查找红色错误信息：
   - `AttributeError`
   - `TypeError`
   - `ValueError`
   - `KeyError`
   等

**常见原因：**
- 代码逻辑错误
- 环境变量未设置（但代码中使用了）
- 依赖版本不兼容

**解决方法：**
- 根据日志中的错误信息修正代码
- 检查环境变量是否正确设置
- 检查依赖版本是否兼容
- 修正后重新提交代码并部署

---

## 📝 部署检查清单

部署完成后，确认以下项目：

- [ ] Railway 部署状态显示 "Active"（绿色）
- [ ] 部署日志显示 "Application startup complete"
- [ ] 访问 `/health` 返回 `{"ok":true}`
- [ ] 访问 `/docs` 显示 Swagger API 文档
- [ ] `POST /api/analyze` 返回完整的 JSON 响应
- [ ] 响应中包含 `score`、`risk_level`、`summary` 等字段
- [ ] `meta.engine` 显示 `"rule"`（使用规则引擎）

---

## 🎯 下一步

部署成功后：

1. **记录 Railway 域名**：用于前端配置
2. **更新前端配置**：修改 `config.js` 中的 `API_BASE_URL`
3. **部署前端到 Vercel**：参考 `部署步骤清单.md` 的 B 部分

---

## 📞 获取帮助

如果遇到问题：

1. **查看 Railway 日志**：项目页面 → Deployments → 最新部署 → Logs
2. **检查 Railway 文档**：https://docs.railway.app
3. **Railway Discord**：https://discord.gg/railway

---

**文档生成时间**：2024年  
**适用版本**：Railway 最新版本

