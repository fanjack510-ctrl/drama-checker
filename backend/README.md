# 剧情短视频体检器 - 后端服务

## 项目结构

```
backend/
├── main.py              # FastAPI 主入口
├── scorer_rules.py      # 规则评分引擎
├── schema.py            # Pydantic 数据模型
├── config.py            # 配置管理
├── requirements.txt     # 依赖列表
└── README.md           # 说明文档
```

## 快速开始

### 一键启动（推荐）

**Windows 系统：**
```bash
cd backend
start.bat
```

**Linux/Mac 系统：**
```bash
cd backend
chmod +x start.sh
./start.sh
```

**跨平台（Python 脚本）：**
```bash
cd backend
python start.py
```

**如果虚拟环境创建卡住，可以使用简化版（不使用虚拟环境）：**
```bash
cd backend
start_simple.bat  # Windows
# 或直接运行: python run.py
```

一键启动脚本会自动：
1. 检查 Python 环境
2. 创建虚拟环境（如果不存在，可能需要1-2分钟）
3. 安装依赖
4. 启动服务

**注意：** 如果虚拟环境创建过程卡住或很慢，这是正常现象，请耐心等待。如果超过2分钟仍未完成，可以：
- 使用 `start_simple.bat`（不使用虚拟环境）
- 或手动创建虚拟环境：`python -m venv venv`

### 手动启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

**方式一：使用启动脚本（推荐）**

在 `backend` 目录下运行：

```bash
cd backend
python run.py
```

**方式二：使用 uvicorn 命令**

在 `backend` 目录下运行：

```bash
cd backend
uvicorn main:app --reload --port 8000
```

**方式三：使用 Python 模块方式**

从项目根目录运行：

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

服务启动后，访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## API 接口

### POST /api/analyze

分析剧情短视频脚本。

**请求体：**
```json
{
  "text": "你的脚本内容...",
  "mode": "drama_emotion"
}
```

**响应示例：**
```json
{
  "score": 65,
  "risk_level": "warn",
  "summary": [
    "前5秒缺乏明确冲突或悬念，容易让人划走",
    "情绪曲线较为平直，缺少明显的转折点"
  ],
  "issues_high": [
    {
      "text": "前5秒缺乏吸引力，容易被划走",
      "reason": "前5秒无冲突、无悬念、无反差、无强情绪"
    }
  ],
  "issues_mid": [
    {
      "text": "中段节奏可以更快，信息密度有待提升",
      "reason": "中段存在连续2句平铺直叙"
    }
  ],
  "risky_section": "前段",
  "viewer_reaction": "如果我是观众，我会在前5秒觉得没什么意思就划走了",
  "directions": [
    "在开头建立明确的冲突或悬念",
    "增加至少一次情绪或剧情转折"
  ],
  "evidence": [
    {
      "text": "今天天气真好",
      "position": "前段",
      "reason": "包含冲突词"
    }
  ],
  "meta": {
    "version": "1.0.0",
    "engine": "rule"
  }
}
```

### GET /health

健康检查接口。

**响应：**
```json
{
  "ok": true
}
```

## 与前端联调

### 方式一：修改前端 API 地址

如果前端 HTML 文件在本地打开（file://），需要：

1. 启动后端服务（确保运行在 http://localhost:8000）
2. 使用本地服务器打开前端 HTML（如使用 Python 的 http.server）：

```bash
# 在前端 HTML 文件所在目录
python -m http.server 8080
```

然后访问 http://localhost:8080/剧情短视频体检器.html

### 方式二：使用代理

如果前端使用开发服务器（如 Vite、Webpack Dev Server），可以配置代理：

```javascript
// vite.config.js 示例
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}
```

### 方式三：直接修改前端 fetch URL

在前端 HTML 中，将 `/api/analyze` 改为完整 URL：

```javascript
const response = await fetchWithTimeout('http://localhost:8000/api/analyze', {
  // ...
});
```

## 环境变量配置

### 启用 LLM 模式（可选）

```bash
export ENABLE_LLM=true
export LLM_API_KEY=your_api_key
export LLM_API_URL=https://api.example.com/v1/chat
```

注意：LLM 模式目前未实现，即使设置也会回退到规则引擎。

## 评分规则说明

### 评分维度

1. **节奏（Rhythm）** - 35分
   - 前5秒信息密度：12分
   - 中段推进速度：12分
   - 整体信息密度：11分

2. **情绪曲线（Emotion Curve）** - 35分
   - 情绪转折点：15分
   - 情绪递进：10分
   - 情绪多样性：10分

3. **留存钩子（Retention Triggers）** - 30分
   - 前5秒吸引力：15分
   - 中段留存点：10分
   - 结尾落点：5分

### 风险等级

- **safe**：总分 ≥ 75
- **warn**：总分 60-74
- **bad**：总分 < 60

## 错误处理

- **400 Bad Request**：文本为空或过短
- **413 Request Entity Too Large**：文本超过 5000 字符
- **500 Internal Server Error**：服务器内部错误

## 开发说明

### 添加新的评分规则

在 `scorer_rules.py` 中修改对应的分析函数：
- `analyze_rhythm()` - 节奏分析
- `analyze_emotion_curve()` - 情绪曲线分析
- `analyze_retention_triggers()` - 留存钩子分析

### 修改信号词库

在 `scorer_rules.py` 文件顶部修改对应的词库常量：
- `CONFLICT_WORDS` - 冲突词
- `EMOTION_WORDS` - 情绪词
- `SUSPENSE_PATTERNS` - 悬念句式
- 等等

## 常见问题

### Q: 为什么评分结果不稳定？

A: 规则引擎基于文本信号匹配，如果脚本中信号词分布变化，评分会相应变化。这是正常的。

### Q: 如何提高评分精度？

A: 可以：
1. 扩展信号词库
2. 优化评分规则逻辑
3. 启用 LLM 模式（需要实现）

### Q: CORS 错误怎么办？

A: 确保后端 CORS 中间件已正确配置，允许前端域名访问。

