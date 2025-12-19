"""
通义千问 LLM 评分引擎

说明：
- 只有在环境变量 LLM_ENABLED=true 且提供 QWEN_API_KEY/LLM_API_KEY 时才会被调用
- 调用失败时，调用方必须回退到规则引擎（见 main.py）
"""

from __future__ import annotations

import json
import logging
from typing import Optional

import requests

from config import LLM_API_KEY, LLM_API_URL, API_VERSION
from schema import AnalyzeResponse

logger = logging.getLogger(__name__)


DEFAULT_QWEN_API_URL = (
    LLM_API_URL
    or "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
)


def _build_system_prompt() -> str:
    """构造发给千问的 System Prompt（简化版，保证可维护）"""

    return (
        "你是一个【剧情/情绪类短视频脚本评分专家】。\n"
        "现在会给你一段 30-90 秒的剧情/情绪类短视频脚本，请只做诊断，不要改写脚本。\n"
        "你需要从三大维度给出评分：节奏（Rhythm）、情绪曲线（Emotion Curve）、留存钩子（Retention Triggers）。\n"
        "评分范围 0-100，分数越高代表脚本越不容易让人划走。\n"
        "你必须严格返回一个 JSON，对应后端的结构：\n"
        "{\n"
        '  "score": 0-100 的整数,\n'
        '  "risk_level": "safe" 或 "warn" 或 "bad",\n'
        "  \"summary\": 不超过 4 条的一句话问题总结数组,\n"
        "  \"issues_high\": 高风险问题数组，每项包含 text 和 reason 字段,\n"
        "  \"issues_mid\": 可优化问题数组，每项包含 text 和 reason 字段,\n"
        '  "risky_section": "前段" 或 "中段" 或 "后段",\n'
        "  \"viewer_reaction\": 一句“如果我是观众，我会……”开头的话,\n"
        "  \"directions\": 2-3 条方向性建议，只给方向，不给具体改写,\n"
        "  \"evidence\": 最多 6 条证据片段，每条包含 text(<=12字)、position(前段/中段/后段)、reason,\n"
        '  "meta": { "version": "API 版本号", "engine": "llm-qwen" }\n'
        "}\n"
        "要求：\n"
        "1. 只输出 JSON，不要带解释文字或 Markdown。\n"
        "2. 所有字符串使用普通文本，不要包含换行符转义问题。\n"
        "3. evidence.text 必须来自原文片段，尽量截取关键位置，且不超过 12 个汉字。\n"
    )


def _build_user_prompt(script_text: str) -> str:
    """构造用户 Prompt，把脚本包装进去。"""

    return f"下面是一段短视频脚本，请按照上面的规则进行体检和评分，只返回 JSON：\n\n{script_text}"


def score_by_llm(text: str) -> Optional[AnalyzeResponse]:
    """
    使用通义千问进行评分。

    返回：
    - 成功：AnalyzeResponse 实例
    - 失败：None（调用方需要回退到规则引擎）
    """

    if not LLM_API_KEY:
        logger.warning("LLM_API_KEY 未配置，跳过 LLM 调用。")
        return None

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "qwen-plus",
        "input": {
            "messages": [
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user", "content": _build_user_prompt(text)},
            ]
        },
        "parameters": {
            # 降低随机性，保证评分稳定
            "temperature": 0.3,
            "max_tokens": 1500,
        },
    }

    try:
        resp = requests.post(DEFAULT_QWEN_API_URL, headers=headers, json=payload, timeout=40)
        resp.raise_for_status()
    except Exception as e:  # noqa: BLE001
        logger.error("调用通义千问 API 失败：%s", e)
        return None

    try:
        data = resp.json()
    except Exception as e:  # noqa: BLE001
        logger.error("解析通义千问响应为 JSON 失败：%s", e)
        return None

    # 通义千问典型响应结构：output.choices[0].message.content
    raw_content = None
    try:
        output = data.get("output") or {}
        choices = output.get("choices") or []
        if choices:
            message = choices[0].get("message") or {}
            raw_content = message.get("content")
    except Exception:  # noqa: BLE001
        raw_content = None

    if not raw_content:
        # 有些情况下模型直接返回 JSON 对象
        if isinstance(data, dict) and {"score", "risk_level"} <= data.keys():
            raw_content = data
        else:
            logger.error("通义千问响应中未找到 content 字段：%s", data)
            return None

    # raw_content 可能是字符串形式的 JSON，也可能已经是 dict
    if isinstance(raw_content, str):
        try:
            parsed = json.loads(raw_content)
        except Exception as e:  # noqa: BLE001
            logger.error("解析通义千问 content 字符串为 JSON 失败：%s；content=%r", e, raw_content)
            return None
    elif isinstance(raw_content, dict):
        parsed = raw_content
    else:
        logger.error("未知的 content 类型：%r", type(raw_content))
        return None

    # 补充 meta 信息
    meta = parsed.get("meta") or {}
    meta.setdefault("version", API_VERSION)
    meta.setdefault("engine", "llm-qwen")
    parsed["meta"] = meta

    try:
        # 使用 Pydantic 校验并构造响应对象（Pydantic v2 API）
        result = AnalyzeResponse.model_validate(parsed)
    except Exception as e:  # noqa: BLE001
        logger.error("将通义千问结果转换为 AnalyzeResponse 失败：%s；parsed=%r", e, parsed)
        return None

    return result


