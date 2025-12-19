"""
配置管理模块
"""
import os
from typing import Literal

# 评分引擎类型
EngineType = Literal["rule", "llm"]

# 从环境变量读取配置
ENABLE_LLM = os.getenv("ENABLE_LLM", "false").lower() == "true"
# 支持 QWEN_API_KEY 和 LLM_API_KEY 两种环境变量名
LLM_API_KEY = os.getenv("QWEN_API_KEY") or os.getenv("LLM_API_KEY", "")
LLM_API_URL = os.getenv("LLM_API_URL", "")

# 默认使用规则引擎
DEFAULT_ENGINE: EngineType = "llm" if ENABLE_LLM and LLM_API_KEY else "rule"

# 文本长度限制
MIN_TEXT_LENGTH = 10
MAX_TEXT_LENGTH = 5000

# API 版本
API_VERSION = "1.0.0"

