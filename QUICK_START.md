# 快速部署检查清单

## 一、后端上线（Railway）

### ✅ 1. FastAPI 启动确认
- [x] `backend/main.py` 存在 `app = FastAPI()`
- [x] `POST /api/analyze` 端点已实现
- [x] `GET /health` 端点已实现

### ✅ 2. Railway 启动命令
在 Railway 项目设置中填写：

```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**或者** Railway 会自动检测 `backend/Procfile`，其中已包含启动命令。

### ✅ 3. requirements.txt
已包含所有必需依赖：
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pydantic==2.5.0
- requests>=2.31.0

### ✅ 4. Railway 环境变量
在 Railway → Variables 中添加：

| 变量名 | 值 | 必需 |
|--------|-----|------|
| `LLM_ENABLED` | `false` | 否（默认 false，使用规则引擎） |
| `LLM_API_KEY` | `你的API密钥` | 否（仅在启用 LLM 时需要） |

---

## 二、前端上线（Vercel）

### ✅ 1. 前端文件
- [x] `index.html` 已在项目根目录
- [x] API 地址已配置为可配置模式

### ✅ 2. 修改 API 地址
编辑 `index.html` 第 395 行：

```javascript
// 部署后修改为你的 Railway 后端地址
const API_BASE_URL = 'https://your-app.railway.app';
```

### ✅ 3. Vercel 部署设置
- Framework Preset: **Other**
- Build Command: **留空**
- Output Directory: **留空**
- Root Directory: **留空**（index.html 在根目录）

---

## 三、部署步骤

### Railway（后端）
1. 登录 https://railway.app
2. New Project → Deploy from GitHub
3. 选择仓库
4. Settings → Deploy：
   - Root Directory: `backend`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Variables → 添加环境变量（如需要）
6. 获得公网 URL：`https://xxx.railway.app`

### Vercel（前端）
1. 登录 https://vercel.com
2. Add New → Project
3. 选择 GitHub 仓库
4. Framework: **Other**
5. Build Command: **留空**
6. Deploy
7. 获得公网 URL：`https://xxx.vercel.app`

### 联调
1. 修改 `index.html` 中的 `API_BASE_URL` 为 Railway 地址
2. 提交代码，Vercel 自动重新部署
3. 访问 Vercel URL 测试

---

## 四、验证清单

- [ ] Railway 健康检查：`https://xxx.railway.app/health` 返回 `{"ok": true}`
- [ ] Railway API 文档：`https://xxx.railway.app/docs` 可访问
- [ ] Vercel 前端页面可访问
- [ ] 前端输入脚本 → 点击体检 → 正常返回结果
- [ ] 前端代码中不包含 API Key（安全）

---

## 五、重要提示

1. **API Key 安全**：通义千问 API Key 仅在后端使用，不会暴露给前端 ✓
2. **CORS 配置**：后端已配置允许所有来源，生产环境建议改为具体域名
3. **默认模式**：如果不设置 `LLM_ENABLED=true`，系统使用规则引擎（无需 API Key）

