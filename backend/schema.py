"""
请求和响应的数据模型
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    """分析请求模型"""
    text: str = Field(..., description="要分析的脚本文本")
    mode: str = Field(default="drama_emotion", description="分析模式")


class EvidenceItem(BaseModel):
    """证据片段模型"""
    text: str = Field(..., description="原文片段（不超过12个汉字）")
    position: str = Field(..., description="位置：前段/中段/后段")
    reason: str = Field(..., description="引用原因")


class IssueItem(BaseModel):
    """问题项模型"""
    text: str = Field(..., description="问题描述")
    reason: Optional[str] = Field(None, description="扣分原因")


class AnalyzeResponse(BaseModel):
    """分析响应模型"""
    score: int = Field(..., ge=0, le=100, description="综合评分（0-100）")
    risk_level: str = Field(..., description="风险等级：safe/warn/bad")
    summary: List[str] = Field(..., max_length=4, description="问题总结（不超过4条）")
    issues_high: List[IssueItem] = Field(default_factory=list, description="高风险问题列表")
    issues_mid: List[IssueItem] = Field(default_factory=list, description="可优化问题列表")
    risky_section: str = Field(..., description="最危险的位置：前段/中段/后段")
    viewer_reaction: str = Field(..., description="观众可能的真实反应")
    directions: List[str] = Field(..., min_length=2, max_length=3, description="优化方向（2-3条）")
    evidence: List[EvidenceItem] = Field(default_factory=list, max_length=6, description="证据片段（最多6条）")
    meta: dict = Field(..., description="元数据")

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v):
        if len(v) > 4:
            return v[:4]
        return v

    @field_validator("evidence")
    @classmethod
    def validate_evidence(cls, v):
        if len(v) > 6:
            return v[:6]
        return v


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    ok: bool = Field(..., description="服务状态")

