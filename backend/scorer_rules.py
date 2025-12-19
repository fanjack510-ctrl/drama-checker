"""
基于规则的评分引擎
"""
import re
from typing import List, Tuple
from schema import AnalyzeResponse, IssueItem, EvidenceItem


# 信号词库
CONFLICT_WORDS = ["但是", "可是", "然而", "竟然", "居然", "没想到", "突然", "竟然", "居然", "却", "但"]
EMOTION_WORDS = ["愤怒", "震惊", "崩溃", "绝望", "惊喜", "激动", "紧张", "害怕", "开心", "难过", "伤心", "高兴", "兴奋", "焦虑", "担心"]
SUSPENSE_PATTERNS = ["为什么", "怎么会", "到底", "究竟", "原来", "竟然", "居然", "怎么", "如何"]
CONTRAST_PATTERNS = ["明明.*?却", "本来.*?结果", "以前.*?现在", "之前.*?现在"]
TURNING_POINTS = ["但是", "可是", "然而", "突然", "一下子", "瞬间", "终于", "原来"]
PROGRESSIVE_WORDS = ["越来越", "逐渐", "慢慢", "突然", "一下子", "瞬间"]
EMPTY_WORDS = ["然后", "接着", "之后", "后来", "接下来"]


def extract_first_n_chars(text: str, n: int) -> str:
    """提取前n个字符（用于前5秒判断）"""
    return text[:n] if len(text) >= n else text


def count_signals(text: str, patterns: List[str]) -> int:
    """统计文本中信号词的出现次数"""
    count = 0
    for pattern in patterns:
        if isinstance(pattern, str):
            if pattern in text:
                count += 1
        else:  # 正则表达式
            if re.search(pattern, text):
                count += 1
    return count


def find_evidence_snippets(text: str, max_length: int = 12, max_count: int = 6) -> List[EvidenceItem]:
    """查找证据片段"""
    evidence = []
    
    # 按句子分割
    sentences = re.split(r'[。！？\n]', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) > max_length:
            continue
        
        # 判断位置
        position = "中段"
        char_index = text.find(sentence)
        if char_index < len(text) * 0.3:
            position = "前段"
        elif char_index > len(text) * 0.7:
            position = "后段"
        
        # 检查是否包含信号词
        has_signal = False
        reason = ""
        
        if any(word in sentence for word in CONFLICT_WORDS):
            has_signal = True
            reason = "包含冲突词"
        elif any(word in sentence for word in EMOTION_WORDS):
            has_signal = True
            reason = "包含情绪词"
        elif any(pattern in sentence for pattern in SUSPENSE_PATTERNS):
            has_signal = True
            reason = "包含悬念句式"
        elif re.search("|".join(CONTRAST_PATTERNS), sentence):
            has_signal = True
            reason = "包含反差对比"
        elif all(word in sentence for word in EMPTY_WORDS[:2]):
            has_signal = True
            reason = "平铺直叙"
        
        if has_signal and len(evidence) < max_count:
            evidence.append(EvidenceItem(
                text=sentence[:max_length],
                position=position,
                reason=reason
            ))
    
    return evidence[:max_count]


def analyze_rhythm(text: str) -> Tuple[int, List[IssueItem], List[str]]:
    """分析节奏维度（35分）"""
    score = 35
    issues = []
    evidence_texts = []
    
    # A1. 前5秒信息密度（12分）
    first_part = extract_first_n_chars(text, min(50, len(text)))
    signal_count = (
        count_signals(first_part, CONFLICT_WORDS) +
        count_signals(first_part, EMOTION_WORDS) +
        count_signals(first_part, SUSPENSE_PATTERNS) +
        (1 if re.search("|".join(CONTRAST_PATTERNS), first_part) else 0)
    )
    
    if signal_count == 0:
        score -= 10
        issues.append(IssueItem(
            text="前5秒缺乏明确冲突或悬念，容易让人划走",
            reason="前5秒内无任何冲突词、情绪词、悬念句式、反差对比"
        ))
        evidence_texts.append(first_part[:12] if len(first_part) >= 12 else first_part)
    elif signal_count == 1:
        score -= 7
        issues.append(IssueItem(
            text="前5秒信息密度偏低，吸引力不足",
            reason="前5秒仅有1个弱信号"
        ))
    elif signal_count == 2:
        score -= 3
        issues.append(IssueItem(
            text="前5秒有一定吸引力，但可以更强",
            reason="前5秒有1-2个中等信号"
        ))
    
    # A2. 中段推进速度（12分）
    mid_start = int(len(text) * 0.2)
    mid_end = int(len(text) * 0.7)
    mid_text = text[mid_start:mid_end] if mid_end > mid_start else ""
    
    if mid_text:
        # 检查连续平铺直叙
        empty_count = sum(1 for word in EMPTY_WORDS if word in mid_text)
        turning_count = count_signals(mid_text, TURNING_POINTS)
        
        if empty_count >= 3 and turning_count == 0:
            score -= 9
            issues.append(IssueItem(
                text="中段节奏偏慢，存在明显拖沓段落",
                reason="中段存在连续3句以上平铺直叙，无转折"
            ))
            # 找一段平铺直叙的证据
            for word in EMPTY_WORDS:
                idx = mid_text.find(word)
                if idx >= 0:
                    snippet = mid_text[idx:idx+20]
                    if len(snippet) <= 12:
                        evidence_texts.append(snippet)
                    break
        elif empty_count >= 2 and turning_count <= 1:
            score -= 6
            issues.append(IssueItem(
                text="中段节奏可以更快，信息密度有待提升",
                reason="中段存在连续2句平铺直叙"
            ))
        elif turning_count <= 1:
            score -= 3
            issues.append(IssueItem(
                text="中段节奏尚可，但仍有优化空间",
                reason="中段有1-2次推进，但节奏不够紧凑"
            ))
    
    # A3. 整体信息密度（11分）
    total_signals = (
        count_signals(text, CONFLICT_WORDS) +
        count_signals(text, EMOTION_WORDS) +
        count_signals(text, TURNING_POINTS)
    )
    
    if total_signals == 0:
        score -= 8
        issues.append(IssueItem(
            text="整体信息密度过低，缺乏吸引人的元素",
            reason="全文无明显冲突、转折、情绪变化"
        ))
    elif total_signals <= 2:
        score -= 5
        issues.append(IssueItem(
            text="整体信息密度偏低，可以增加更多冲突或转折",
            reason=f"全文仅有{total_signals}个弱信号点"
        ))
    elif total_signals <= 5:
        score -= 2
        issues.append(IssueItem(
            text="整体信息密度尚可，但可以更均衡",
            reason=f"全文有{total_signals}个信号点，但分布不均"
        ))
    
    return max(0, score), issues, evidence_texts


def analyze_emotion_curve(text: str) -> Tuple[int, List[IssueItem], List[str]]:
    """分析情绪曲线维度（35分）"""
    score = 35
    issues = []
    evidence_texts = []
    
    # B1. 情绪转折点（15分）
    turning_count = count_signals(text, TURNING_POINTS)
    emotion_count = count_signals(text, EMOTION_WORDS)
    
    if turning_count == 0 and emotion_count <= 1:
        score -= 12
        issues.append(IssueItem(
            text="缺乏情绪转折，情绪曲线平直，难以产生代入感",
            reason="全文无任何情绪转折"
        ))
        # 找一段无转折的证据
        sentences = re.split(r'[。！？]', text)
        for s in sentences[:3]:
            if len(s) <= 12 and s.strip():
                evidence_texts.append(s.strip())
                break
    elif turning_count == 1 and emotion_count <= 2:
        score -= 8
        issues.append(IssueItem(
            text="情绪转折较弱，变化不够明显",
            reason="全文仅有1次弱转折"
        ))
    elif turning_count <= 2:
        score -= 4
        issues.append(IssueItem(
            text="存在情绪转折，但可以更强烈或增加转折次数",
            reason=f"全文有{turning_count}次转折"
        ))
    
    # B2. 情绪递进（10分）
    progressive_count = count_signals(text, PROGRESSIVE_WORDS)
    
    if progressive_count == 0:
        score -= 8
        issues.append(IssueItem(
            text="情绪缺乏递进，始终停留在同一强度",
            reason="情绪始终停留在同一强度，无递进或变化"
        ))
    elif progressive_count == 1:
        score -= 5
        issues.append(IssueItem(
            text="情绪递进较弱，可以更明显",
            reason="情绪有轻微递进，但变化不明显"
        ))
    elif progressive_count == 2:
        score -= 2
        issues.append(IssueItem(
            text="情绪递进尚可，但可以更强烈",
            reason="情绪有明显递进，但可以更强"
        ))
    
    # B3. 情绪多样性（10分）
    unique_emotions = set()
    for word in EMOTION_WORDS:
        if word in text:
            unique_emotions.add(word)
    
    emotion_variety = len(unique_emotions)
    
    if emotion_variety == 0:
        score -= 8
        issues.append(IssueItem(
            text="情绪过于单一，缺乏层次感",
            reason="全文无明显情绪词"
        ))
    elif emotion_variety == 1:
        score -= 5
        issues.append(IssueItem(
            text="情绪种类较少，可以增加更多情绪层次",
            reason=f"全文仅有{emotion_variety}种情绪"
        ))
    elif emotion_variety == 2:
        score -= 2
        issues.append(IssueItem(
            text="情绪多样性尚可，但可以更均衡",
            reason=f"全文有{emotion_variety}种情绪，但分布不均"
        ))
    
    return max(0, score), issues, evidence_texts


def analyze_retention_triggers(text: str) -> Tuple[int, List[IssueItem], List[str]]:
    """分析留存钩子维度（30分）"""
    score = 30
    issues = []
    evidence_texts = []
    
    # C1. 前5秒吸引力（15分）
    first_part = extract_first_n_chars(text, min(50, len(text)))
    strong_signals = (
        (1 if any(cw in first_part for cw in CONFLICT_WORDS[:3]) and any(ew in first_part for ew in EMOTION_WORDS[:5]) else 0) +
        (1 if any(sp in first_part for sp in SUSPENSE_PATTERNS[:4]) else 0) +
        (1 if re.search("|".join(CONTRAST_PATTERNS), first_part) else 0)
    )
    weak_signals = (
        count_signals(first_part, EMOTION_WORDS) +
        (1 if any(word in first_part for word in ["今天", "昨天", "刚才"]) else 0)
    ) - strong_signals
    
    if strong_signals == 0 and weak_signals == 0:
        score -= 12
        issues.append(IssueItem(
            text="前5秒缺乏吸引力，容易被划走",
            reason="前5秒无冲突、无悬念、无反差、无强情绪"
        ))
        evidence_texts.append(first_part[:12] if len(first_part) >= 12 else first_part)
    elif strong_signals == 0 and weak_signals == 1:
        score -= 9
        issues.append(IssueItem(
            text="前5秒吸引力不足，需要更强的钩子",
            reason="前5秒仅有1个弱信号"
        ))
    elif strong_signals == 1:
        score -= 6
        issues.append(IssueItem(
            text="前5秒有一定吸引力，但可以更强",
            reason="前5秒有1个中等信号"
        ))
    elif strong_signals == 2:
        score -= 3
        issues.append(IssueItem(
            text="前5秒吸引力较强，能抓住注意力",
            reason="前5秒有1个强信号"
        ))
    
    # C2. 中段留存点（10分）
    mid_start = int(len(text) * 0.2)
    mid_end = int(len(text) * 0.8)
    mid_text = text[mid_start:mid_end] if mid_end > mid_start else ""
    
    if mid_text:
        mid_signals = (
            count_signals(mid_text, CONFLICT_WORDS) +
            count_signals(mid_text, TURNING_POINTS) +
            count_signals(mid_text, SUSPENSE_PATTERNS)
        )
        
        if mid_signals == 0:
            score -= 8
            issues.append(IssueItem(
                text="中段缺乏留存点，容易让人中途划走",
                reason="中段无任何冲突、转折、悬念"
            ))
        elif mid_signals == 1:
            score -= 5
            issues.append(IssueItem(
                text="中段留存点较弱，可以增加更多钩子",
                reason="中段有1个弱信号点"
            ))
        elif mid_signals == 2:
            score -= 2
            issues.append(IssueItem(
                text="中段留存点尚可，但可以更强",
                reason="中段有1-2个中等信号点"
            ))
    
    # C3. 结尾落点（5分）
    last_part = text[-min(50, len(text)):] if len(text) > 50 else text
    ending_signals = (
        (1 if any(word in last_part for word in ["终于", "释然", "明白", "懂了"]) else 0) +
        (1 if any(word in last_part for word in ["原来", "其实"]) else 0) +
        (1 if any(word in last_part for word in ["每个人", "我们都", "生活"]) else 0)
    )
    
    if ending_signals == 0:
        score -= 4
        issues.append(IssueItem(
            text="结尾缺乏落点，没有留下印象",
            reason="结尾无情绪收束、无思考点、无共鸣点"
        ))
    elif ending_signals == 1:
        score -= 2
        issues.append(IssueItem(
            text="结尾落点较弱，可以更明显",
            reason="结尾有轻微情绪收束，但不够明显"
        ))
    
    return max(0, score), issues, evidence_texts


def score_by_rules(text: str) -> AnalyzeResponse:
    """基于规则进行评分"""
    # 分析三个维度
    rhythm_score, rhythm_issues, rhythm_evidence = analyze_rhythm(text)
    emotion_score, emotion_issues, emotion_evidence = analyze_emotion_curve(text)
    retention_score, retention_issues, retention_evidence = analyze_retention_triggers(text)
    
    # 计算总分
    total_score = rhythm_score + emotion_score + retention_score
    
    # 合并所有问题
    all_issues = rhythm_issues + emotion_issues + retention_issues
    
    # 分离高风险和中等风险问题
    high_risk_issues = []
    mid_risk_issues = []
    
    for issue in all_issues:
        # 根据扣分原因判断风险等级
        reason = issue.reason or ""
        if "无" in reason or "缺乏" in reason or "没有" in reason or "极低" in reason or "极弱" in reason:
            high_risk_issues.append(issue)
        else:
            mid_risk_issues.append(issue)
    
    # 限制问题数量
    high_risk_issues = high_risk_issues[:3]
    mid_risk_issues = mid_risk_issues[:3]
    
    # 生成总结（最多4条）
    summary = []
    if high_risk_issues:
        summary.extend([issue.text for issue in high_risk_issues[:2]])
    if mid_risk_issues:
        summary.extend([issue.text for issue in mid_risk_issues[:2]])
    summary = summary[:4]
    
    # 确定风险等级
    if total_score >= 75:
        risk_level = "safe"
    elif total_score >= 60:
        risk_level = "warn"
    else:
        risk_level = "bad"
    
    # 确定最危险位置
    risky_section = "前段"
    if total_score < 50:
        risky_section = "前段"
    elif rhythm_score < 20:
        risky_section = "中段"
    else:
        risky_section = "后段"
    
    # 生成观众反应
    if total_score < 50:
        viewer_reaction = "如果我是观众，我会在前5秒觉得没什么意思就划走了"
    elif total_score < 70:
        viewer_reaction = "如果我是观众，我会在中段觉得节奏太慢就划走了"
    else:
        viewer_reaction = "如果我是观众，我会看完但可能不会点赞"
    
    # 生成优化方向
    directions = []
    if rhythm_score < 25:
        directions.append("在开头建立明确的冲突或悬念")
    if emotion_score < 25:
        directions.append("增加至少一次情绪或剧情转折")
    if retention_score < 20:
        directions.append("提升中段的信息密度和节奏感")
    if not directions:
        directions = ["强化结尾的情绪收束或思考点"]
    directions = directions[:3]
    
    # 收集证据
    all_evidence_texts = list(set(rhythm_evidence + emotion_evidence + retention_evidence))
    evidence = find_evidence_snippets(text, max_length=12, max_count=6)
    
    # 如果证据不足，从问题中提取
    if len(evidence) < 3:
        for issue in all_issues[:3]:
            if issue.reason and len(issue.reason) <= 12:
                char_index = text.find(issue.reason[:6]) if len(issue.reason) >= 6 else -1
                position = "中段"
                if char_index >= 0:
                    if char_index < len(text) * 0.3:
                        position = "前段"
                    elif char_index > len(text) * 0.7:
                        position = "后段"
                evidence.append(EvidenceItem(
                    text=issue.reason[:12],
                    position=position,
                    reason=issue.text[:30]
                ))
    
    evidence = evidence[:6]
    
    return AnalyzeResponse(
        score=total_score,
        risk_level=risk_level,
        summary=summary,
        issues_high=high_risk_issues,
        issues_mid=mid_risk_issues,
        risky_section=risky_section,
        viewer_reaction=viewer_reaction,
        directions=directions,
        evidence=evidence,
        meta={
            "version": "1.0.0",
            "engine": "rule"
        }
    )

