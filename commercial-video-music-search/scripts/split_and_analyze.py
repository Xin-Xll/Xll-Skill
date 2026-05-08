#!/usr/bin/env python3
"""
split_and_analyze.py
用途：口播文案拆解 + 情绪标注 + 叙事节奏分析
用法：python3 split_and_analyze.py "文案内容"
     python3 split_and_analyze.py --file script.txt
输出：JSON 格式的分析结果
"""

import sys
import re
import json
import argparse


# ─────────────────────────────────────────────
# 情绪关键词词典
# ─────────────────────────────────────────────
EMOTION_KEYWORDS = {
    "激昂": ["奋斗", "梦想", "拼搏", "突破", "冲", "加油", "赢", "成功", "目标", "改变",
             "力量", "行动", "挑战", "超越", "绝不放弃", "勇气", "燃", "破局", "逆袭"],
    "感动": ["感谢", "泪", "哭", "感恩", "陪伴", "珍惜", "告别", "想念", "思念", "爱",
             "妈妈", "爸爸", "家人", "成长", "回忆", "曾经", "那年", "亲情", "温柔"],
    "悬念": ["但是", "然而", "没想到", "突然", "竟然", "其实", "真相", "发现", "问题",
             "为什么", "怎么", "意外", "震惊", "颠覆", "不为人知", "揭秘", "背后"],
    "轻松": ["哈哈", "笑", "好玩", "有趣", "日常", "分享", "推荐", "试试", "好吃", "美味",
             "旅游", "打卡", "种草", "好用", "安利", "测评", "体验"],
    "温暖": ["暖", "温暖", "幸福", "快乐", "美好", "生活", "家", "陪伴", "平静", "满足",
             "简单", "治愈", "舒适", "放松", "享受", "岁月"],
    "舒缓": ["清晨", "阳光", "微风", "轻轻", "静静", "慢慢", "悄悄", "远方", "自然",
             "山", "海", "云", "花", "风景", "漫步", "安静", "宁静", "沉浸"],
}

DEFAULT_EMOTION = "舒缓"


def detect_emotion(sentence: str) -> str:
    """根据关键词检测句子主情绪"""
    scores = {emotion: 0 for emotion in EMOTION_KEYWORDS}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in sentence:
                scores[emotion] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else DEFAULT_EMOTION


def split_sentences(text: str) -> list:
    """按标点符号拆分文案为句子列表"""
    # 按主要断句标点拆分
    pattern = r'[。！？\n]+'
    parts = re.split(pattern, text)
    # 过长的句子按逗号进一步拆分（超过 30 字）
    result = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) > 30:
            sub_parts = re.split(r'[，,；;]+', part)
            for sp in sub_parts:
                sp = sp.strip()
                if sp and len(sp) >= 4:
                    result.append(sp)
        else:
            if len(part) >= 4:
                result.append(part)
    return result


def detect_narrative_stage(sentences: list) -> list:
    """
    根据句子在全文中的位置推断叙事节奏阶段
    简单三段式：前 25% 铺垫 / 中间 50% 发展 / 后 25% 收尾
    如果检测到激昂/感动情绪的高峰，标为"高潮"
    """
    n = len(sentences)
    stages = []
    for i, sent in enumerate(sentences):
        ratio = i / max(n - 1, 1)
        emotion = detect_emotion(sent)
        if emotion in ("激昂", "感动") and 0.3 <= ratio <= 0.85:
            stage = "高潮"
        elif ratio < 0.25:
            stage = "铺垫"
        elif ratio >= 0.85:
            stage = "收尾"
        else:
            stage = "发展"
        stages.append(stage)
    return stages


def extract_visual_keywords(sentence: str, emotion: str) -> str:
    """提取适合视频检索的英文关键词（简化版，LLM 调用时可覆盖）"""
    # 场景词映射（中文 → 英文）
    scene_map = {
        "咖啡": "coffee", "咖啡馆": "coffee shop", "海": "ocean sea",
        "山": "mountain", "城市": "city urban", "森林": "forest",
        "家": "home interior", "办公室": "office workplace",
        "街道": "street", "夜晚": "night", "清晨": "morning sunrise",
        "阳光": "sunlight", "雨": "rain", "雪": "snow",
        "孩子": "child kid", "老人": "elderly", "女性": "woman",
        "男性": "man", "团队": "team people", "朋友": "friends",
    }
    emotion_visual_map = {
        "舒缓": "calm peaceful",
        "激昂": "energetic powerful",
        "感动": "emotional touching",
        "悬念": "dramatic cinematic",
        "轻松": "cheerful happy",
        "温暖": "warm cozy",
    }
    keywords = []
    for cn, en in scene_map.items():
        if cn in sentence:
            keywords.append(en)
    keywords.append(emotion_visual_map.get(emotion, "cinematic"))
    # 去重并截取前 5 个词
    unique_kw = list(dict.fromkeys(" ".join(keywords).split()))[:5]
    return " ".join(unique_kw) if unique_kw else "lifestyle cinematic"


def analyze(text: str) -> dict:
    """主分析入口"""
    sentences = split_sentences(text)
    stages = detect_narrative_stage(sentences)

    # 整体情绪投票
    emotion_counts = {}
    analyzed = []
    for i, (sent, stage) in enumerate(zip(sentences, stages)):
        emotion = detect_emotion(sent)
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        visual_kw = extract_visual_keywords(sent, emotion)
        analyzed.append({
            "index": i + 1,
            "sentence": sent,
            "emotion": emotion,
            "narrative_stage": stage,
            "visual_keywords": visual_kw,
        })

    overall_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else DEFAULT_EMOTION

    return {
        "total_sentences": len(sentences),
        "overall_emotion": overall_emotion,
        "sentences": analyzed,
    }


def main():
    parser = argparse.ArgumentParser(description="口播文案拆解与情绪分析")
    parser.add_argument("text", nargs="?", help="直接输入文案文本")
    parser.add_argument("--file", help="从文件读取文案")
    parser.add_argument("--pretty", action="store_true", help="格式化 JSON 输出")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        print("请提供文案文本或使用 --file 参数", file=sys.stderr)
        sys.exit(1)

    result = analyze(text)
    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
