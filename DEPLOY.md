# 部署指南

## 一、后端上线准备（Railway）

### 1. FastAPI 启动确认

✅ **已确认** `backend/main.py` 中存在：
- `app = FastAPI()` ✓
- `POST /api/analyze` ✓
- `GET /health` ✓

### 2. Railway 启动命令

在 Railway 项目设置中，填写以下 **Start Command**：

```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**或者**（如果 Railway 自动检测到 Python 项目）：

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**注意：** Railway 会自动提供 `$PORT` 环境变量，无需手动设置。

### 3. requirements.txt 检查

✅ **已确认** `backend/requirements.txt` 包含：
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pydantic==2.5.0
- requests>=2.31.0（用于调用通义千问 API）

### 4. Railway 环境变量配置

在 Railway 项目设置 → Variables 中添加以下环境变量：

| 变量名 | 值 | 说明 | 是否必需 |
|--------|-----|------|---------|
| `LLM_ENABLED` | `false` | 是否启用 LLM 模式 | 否（默认 false） |
| `LLM_API_KEY` | `你的通义千问API密钥` | 通义千问 API Key | 否（仅在启用 LLM 时需要） |
| `LLM_API_URL` | `https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation` | LLM API 地址 | 否（仅在启用 LLM 时需要） |

**注意：**
- 如果 `LLM_ENABLED=false` 或不设置，系统将使用规则引擎（默认模式）
- 如果 `LLM_ENABLED=true`，必须同时设置 `LLM_API_KEY`
- 通义千问 API Key 仅在后端使用，不会暴露给前端

### 5. Railway 部署步骤

1. 登录 [Railway](https://railway.app)
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择你的 GitHub 仓库
5. Railway 会自动检测到 Python 项目
6. 在 Settings → Deploy 中设置：
   - **Root Directory**: `backend`（如果代码在 backend 目录）
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. 在 Variables 中添加环境变量（如需要）
8. 点击 "Deploy"
9. 等待部署完成，Railway 会提供一个公网 URL，例如：`https://your-app.railway.app`

---

## 二、前端上线准备（Vercel）

### 1. 前端文件整理

✅ **已完成**：
- `index.html` 已创建在项目根目录
- 前端 API 地址已配置为可配置模式

### 2. 前端 API 地址修改

在 `index.html` 的第 395 行，找到：

```javascript
const API_BASE_URL = ''; // 留空使用相对路径，或填入完整后端地址
```

**部署后修改为：**

```javascript
const API_BASE_URL = 'https://your-app.railway.app'; // 替换为你的 Railway 后端地址
```

**说明：**
- 开发环境：留空 `''`，使用相对路径 `/api/analyze`（需要代理）
- 生产环境：填入 Railway 提供的完整后端地址，例如 `'https://your-app.railway.app'`
- 当前阶段可以先硬编码测试

### 3. Vercel 部署步骤

#### 步骤 1：新建项目
1. 登录 [Vercel](https://vercel.com)
2. 点击 "Add New..." → "Project"

#### 步骤 2：选择 GitHub 仓库
1. 选择你的 GitHub 账户
2. 选择包含 `index.html` 的仓库
3. 点击 "Import"

#### 步骤 3：配置项目设置
在项目配置页面：

- **Framework Preset**: 选择 `Other` 或 `Other`
- **Root Directory**: 留空（如果 `index.html` 在根目录）
- **Build Command**: **留空**（纯 HTML 文件无需构建）
- **Output Directory**: **留空**（Vercel 会自动识别）
- **Install Command**: **留空**（无需安装依赖）

#### 步骤 4：环境变量（可选）
如果需要，可以在 Environment Variables 中添加：
- `NEXT_PUBLIC_API_URL` = `https://your-app.railway.app`（如果使用环境变量方式）

#### 步骤 5：部署
1. 点击 "Deploy"
2. 等待部署完成（通常 1-2 分钟）
3. Vercel 会提供一个公网 URL，例如：`https://your-project.vercel.app`

#### 步骤 6：更新前端 API 地址
部署完成后，编辑 `index.html`，将 `API_BASE_URL` 修改为 Railway 后端地址，然后重新提交代码（Vercel 会自动重新部署）。

---

## 三、CORS 配置确认

✅ **已确认** `backend/main.py` 中已配置 CORS：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**生产环境建议：**
将 `allow_origins=["*"]` 改为：
```python
allow_origins=[
    "https://your-project.vercel.app",
    "https://your-custom-domain.com"
]
```

---

## 四、最终验证清单

### ✅ 后端验证

- [ ] Railway 部署成功，可以访问 `https://your-app.railway.app/health`
- [ ] 健康检查返回：`{"ok": true}`
- [ ] API 文档可访问：`https://your-app.railway.app/docs`
- [ ] 测试 POST `/api/analyze` 返回 JSON 格式结果
- [ ] 规则引擎评分正常工作（默认模式）
- [ ] 如果启用 LLM，通义千问调用正常
- [ ] LLM 异常时能回退到规则引擎（代码中已实现）

### ✅ 前端验证

- [ ] Vercel 部署成功，可以访问前端页面
- [ ] 页面正常加载，无控制台错误
- [ ] 输入脚本 → 点击"开始体检" → 正常返回结果
- [ ] 结果正确渲染（评分、问题列表、证据等）
- [ ] 错误提示正常显示（网络错误、超时等）
- [ ] 复制报告功能正常
- [ ] 导出 JSON 功能正常

### ✅ 安全验证

- [ ] **API Key 泄露检查**：前端代码中不包含任何 API Key（✓ 已确认，API Key 仅在后端使用）
- [ ] CORS 配置正确（允许前端域名访问）
- [ ] 后端环境变量正确配置（不在代码中硬编码）

### ✅ 功能验证

- [ ] 输入空文本 → 显示错误提示
- [ ] 输入超长文本（>5000字） → 返回 413 错误
- [ ] 正常脚本 → 返回完整体检报告
- [ ] 网络断开 → 显示友好错误提示
- [ ] 后端超时 → 前端显示超时提示

---

## 五、常见问题

### Q1: Railway 部署失败，提示找不到模块

**A:** 检查 `requirements.txt` 是否完整，确保所有依赖都已列出。Railway 会自动安装 `requirements.txt` 中的依赖。

### Q2: 前端无法连接到后端 API

**A:** 
1. 检查 `API_BASE_URL` 是否正确配置为 Railway 地址
2. 检查后端 CORS 配置是否允许前端域名
3. 检查浏览器控制台错误信息

### Q3: 通义千问 API 调用失败

**A:**
1. 检查 `LLM_API_KEY` 是否正确设置
2. 检查 `LLM_ENABLED` 是否为 `true`
3. 查看 Railway 日志确认错误信息
4. 如果 LLM 失败，系统会自动回退到规则引擎

### Q4: Vercel 部署后页面空白

**A:**
1. 确认 `index.html` 在项目根目录
2. 检查 Vercel 项目设置中的 Root Directory 是否正确
3. 查看 Vercel 部署日志

---

## 六、快速部署检查表

**后端（Railway）：**
- [ ] 代码已推送到 GitHub
- [ ] Railway 项目已创建并连接 GitHub
- [ ] Start Command 已配置
- [ ] 环境变量已设置（如需要）
- [ ] 部署成功，获得公网 URL

**前端（Vercel）：**
- [ ] `index.html` 在项目根目录
- [ ] `API_BASE_URL` 已更新为 Railway 后端地址
- [ ] Vercel 项目已创建并连接 GitHub
- [ ] Framework 选择 Other
- [ ] Build Command 留空
- [ ] 部署成功，获得公网 URL

**联调：**
- [ ] 前端页面可访问
- [ ] 前端可以成功调用后端 API
- [ ] 体检功能正常工作
- [ ] 错误处理正常

---

## 七、后续优化建议

1. **自定义域名**：为前后端配置自定义域名
2. **CORS 优化**：将 `allow_origins` 改为具体域名列表
3. **环境变量管理**：使用 Vercel 环境变量管理前端 API 地址
4. **监控告警**：添加 Railway/Vercel 监控和告警
5. **CDN 加速**：Vercel 自动提供 CDN，无需额外配置

