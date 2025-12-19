"""
FastAPI 主入口
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from schema import AnalyzeRequest, AnalyzeResponse, HealthResponse
from scorer_rules import score_by_rules
from config import MIN_TEXT_LENGTH, MAX_TEXT_LENGTH, DEFAULT_ENGINE, API_VERSION

app = FastAPI(title="剧情短视频体检器 API", version=API_VERSION)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(ok=True)


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_script(request: AnalyzeRequest):
    """
    分析剧情短视频脚本
    
    - **text**: 要分析的脚本文本
    - **mode**: 分析模式（目前仅支持 drama_emotion）
    """
    text = request.text.strip()
    
    # 验证文本长度
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文本内容不能为空"
        )
    
    if len(text) < MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文本长度过短，至少需要 {MIN_TEXT_LENGTH} 个字符"
        )
    
    if len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文本长度超过限制，最多支持 {MAX_TEXT_LENGTH} 个字符"
        )
    
    # 根据配置选择评分引擎
    if DEFAULT_ENGINE == "rule":
        result = score_by_rules(text)
    else:
        # LLM 模式（预留，暂未实现）
        # 这里可以调用 LLM API
        result = score_by_rules(text)  # 暂时回退到规则引擎
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

