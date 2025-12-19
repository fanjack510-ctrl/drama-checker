"""
FastAPI 主入口
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from config import API_VERSION, DEFAULT_ENGINE, MAX_TEXT_LENGTH, MIN_TEXT_LENGTH
from llm_scorer import score_by_llm
from schema import AnalyzeRequest, AnalyzeResponse, HealthResponse
from scorer_rules import score_by_rules

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


@app.get("/debug/config")
async def debug_config():
    """调试端点：显示当前配置状态"""
    from config import ENABLE_LLM, LLM_API_KEY, DEFAULT_ENGINE, LLM_API_URL
    
    # 检查环境变量（不暴露完整 API Key）
    has_api_key = bool(LLM_API_KEY)
    api_key_preview = f"{LLM_API_KEY[:8]}..." if LLM_API_KEY else "未设置"
    
    import os
    env_enable_llm = os.getenv("ENABLE_LLM", "未设置")
    env_llm_enabled = os.getenv("LLM_ENABLED", "未设置")
    env_qwen_api_key = os.getenv("QWEN_API_KEY", "未设置")
    env_llm_api_key = os.getenv("LLM_API_KEY", "未设置")
    
    return {
        "config": {
            "ENABLE_LLM": ENABLE_LLM,
            "HAS_API_KEY": has_api_key,
            "API_KEY_PREVIEW": api_key_preview,
            "DEFAULT_ENGINE": DEFAULT_ENGINE,
            "LLM_API_URL": LLM_API_URL or "使用默认URL",
        },
        "environment_variables": {
            "ENABLE_LLM": env_enable_llm,
            "LLM_ENABLED": env_llm_enabled,
            "QWEN_API_KEY": f"{env_qwen_api_key[:8]}..." if env_qwen_api_key != "未设置" else "未设置",
            "LLM_API_KEY": f"{env_llm_api_key[:8]}..." if env_llm_api_key != "未设置" else "未设置",
            "LLM_API_URL": os.getenv("LLM_API_URL", "未设置"),
        },
        "diagnosis": {
            "llm_enabled_check": "✅ 通过" if ENABLE_LLM else "❌ 未启用",
            "api_key_check": "✅ 已设置" if has_api_key else "❌ 未设置",
            "engine_selection": DEFAULT_ENGINE,
            "expected_engine": "llm" if (ENABLE_LLM and has_api_key) else "rule",
        }
    }


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
        # 仅使用规则引擎
        result = score_by_rules(text)
    else:
        # 优先尝试 LLM，引擎失败时自动回退到规则引擎
        llm_result: AnalyzeResponse | None = None
        try:
            llm_result = score_by_llm(text)
        except Exception as e:  # noqa: BLE001
            # 这里不抛出错误，而是记录日志并回退规则引擎
            import logging

            logging.getLogger(__name__).error("LLM 评分失败，回退到规则引擎：%s", e)

        result = llm_result or score_by_rules(text)

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

