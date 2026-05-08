#!/usr/bin/env python3
"""
bgm_matcher.py
用途：根据情绪 + 节奏，生成 Pixabay Music 精准搜索链接（免版权 BGM 推荐方案）

注意：Pixabay 公开 API 不提供音乐搜索端点（仅支持图片和视频），
      因此本脚本通过情绪匹配生成精准搜索链接，用户可直接点击跳转搜索。

用法：
  python3 bgm_matcher.py --emotion 感动
  python3 bgm_matcher.py --emotion 激昂 --tempo fast --count 5
输出：JSON 格式的 BGM 推荐方案（含搜索链接）
"""

import sys
import os
import json
import argparse
import urllib.parse


# ─────────────────────────────────────────────
# 自动加载 .env 文件中的 API Key
# ─────────────────────────────────────────────
def load_env():
    """从脚本同目录的 .env 文件加载环境变量"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value and key not in os.environ:
                        os.environ[key] = value


load_env()


# ─────────────────────────────────────────────
# 情绪 → BGM 搜索词映射
# ─────────────────────────────────────────────
EMOTION_QUERY_MAP = {
    "舒缓": {
        "search_terms": ["ambient relaxing calm", "peaceful piano background", "soft acoustic chill"],
        "bpm_range": "60-80",
        "instrument": "piano, acoustic guitar, ambient synth",
        "mood_tags": ["relaxing", "calm", "peaceful", "meditation", "chill"],
    },
    "激昂": {
        "search_terms": ["energetic motivational epic", "cinematic powerful orchestra", "uplifting inspirational"],
        "bpm_range": "120-160",
        "instrument": "orchestra, drums, brass, electric guitar",
        "mood_tags": ["energetic", "epic", "motivational", "powerful", "inspiring"],
    },
    "感动": {
        "search_terms": ["emotional touching heartfelt", "cinematic sad beautiful", "tender sentimental piano"],
        "bpm_range": "80-100",
        "instrument": "piano, strings, cello, violin",
        "mood_tags": ["emotional", "touching", "sentimental", "heartfelt", "beautiful"],
    },
    "悬念": {
        "search_terms": ["suspense cinematic tension", "mystery dark atmosphere", "thriller ambient"],
        "bpm_range": "90-110",
        "instrument": "synth, bass, percussion, strings",
        "mood_tags": ["suspense", "tension", "mystery", "dark", "cinematic"],
    },
    "轻松": {
        "search_terms": ["upbeat happy cheerful", "fun playful ukulele", "positive morning fresh"],
        "bpm_range": "100-120",
        "instrument": "ukulele, clapping, whistling, acoustic",
        "mood_tags": ["happy", "cheerful", "playful", "upbeat", "fun"],
    },
    "温暖": {
        "search_terms": ["warm cozy acoustic", "heartwarming gentle folk", "cozy ambient background"],
        "bpm_range": "70-90",
        "instrument": "acoustic guitar, piano, soft percussion",
        "mood_tags": ["warm", "cozy", "gentle", "heartwarming", "folk"],
    },
}

DEFAULT_QUERY = {
    "search_terms": ["background music cinematic", "ambient instrumental"],
    "bpm_range": "80-120",
    "instrument": "various",
    "mood_tags": ["background", "cinematic", "instrumental"],
}


def get_emotion_config(emotion: str) -> dict:
    """根据情绪返回搜索配置"""
    return EMOTION_QUERY_MAP.get(emotion, DEFAULT_QUERY)


def generate_pixabay_music_url(query: str) -> str:
    """生成 Pixabay Music 搜索页 URL"""
    return f"https://pixabay.com/music/search/{urllib.parse.quote(query)}/"


def generate_search_links(emotion: str) -> list:
    """根据情绪生成 BGM 搜索链接方案"""
    config = get_emotion_config(emotion)
    links = []

    for term in config["search_terms"]:
        links.append({
            "search_term": term,
            "pixabay_url": generate_pixabay_music_url(term),
            "bpm_range": config["bpm_range"],
            "instrument": config["instrument"],
            "mood_tags": config["mood_tags"],
        })

    return links


def generate_narrative_bgm_strategy(emotions_list: list) -> dict:
    """
    根据全文情绪分布生成 BGM 交替策略
    
    Args:
        emotions_list: 各段落的情绪列表
    
    Returns:
        BGM 交替策略（主曲 + 切换点）
    """
    if not emotions_list:
        return {"strategy": "single", "main_emotion": "舒缓"}

    # 统计主情绪
    emotion_counts = {}
    for e in emotions_list:
        emotion_counts[e] = emotion_counts.get(e, 0) + 1
    main_emotion = max(emotion_counts, key=emotion_counts.get)

    # 检测是否有高潮段落需要切换
    has_climax = any(e in ("激昂", "感动", "悬念") for e in emotions_list)

    if has_climax and len(set(emotions_list)) >= 2:
        # 找到高潮情绪
        climax_emotions = [e for e in emotions_list if e in ("激昂", "感动", "悬念")]
        climax_emotion = max(set(climax_emotions), key=climax_emotions.count)
        return {
            "strategy": "alternating",
            "main_emotion": main_emotion,
            "climax_emotion": climax_emotion,
            "switch_points": "高潮段落切入 climax BGM，其余段落保持 main BGM",
        }
    else:
        return {
            "strategy": "single",
            "main_emotion": main_emotion,
        }


def print_bgm_results(emotion: str, links: list, strategy: dict = None):
    """格式化打印 BGM 推荐结果"""
    config = get_emotion_config(emotion)
    print(f"\n🎵 BGM 推荐（适配情绪：{emotion}）")
    print(f"   BPM 范围: {config['bpm_range']}  |  乐器倾向: {config['instrument']}")
    print()

    if strategy:
        if strategy["strategy"] == "alternating":
            print(f"   📋 BGM 策略：双曲交替")
            print(f"      主曲情绪：{strategy['main_emotion']}（铺垫/发展/收尾段）")
            print(f"      高潮曲情绪：{strategy['climax_emotion']}（高潮段落切入）")
            print(f"      {strategy['switch_points']}")
        else:
            print(f"   📋 BGM 策略：单曲贯穿")
            print(f"      整体情绪：{strategy['main_emotion']}")
        print()

    print("   🔗 精准搜索链接（点击直达 Pixabay Music 搜索结果）：")
    print()
    for i, link in enumerate(links, 1):
        print(f"   ├ [搜索{i}] 关键词: {link['search_term']}")
        print(f"   │         链接: {link['pixabay_url']}")
        print(f"   │         BPM: {link['bpm_range']}  乐器: {link['instrument']}")
        if i < len(links):
            print()

    # 附加免费 BGM 源推荐
    print()
    print("   💡 其他免版权 BGM 来源：")
    print("   ├ Free Music Archive: https://freemusicarchive.org/")
    print("   ├ Mixkit: https://mixkit.co/free-stock-music/")
    print("   ├ BenSound: https://www.bensound.com/")
    print("   └ Incompetech: https://incompetech.com/music/")


def main():
    parser = argparse.ArgumentParser(description="BGM 情绪匹配推荐（生成搜索链接方案）")
    parser.add_argument("--emotion", default="舒缓",
                        choices=list(EMOTION_QUERY_MAP.keys()),
                        help="文案整体情绪（默认: 舒缓）")
    parser.add_argument("--tempo", choices=["slow", "medium", "fast"],
                        help="节奏偏好（影响搜索词推荐）")
    parser.add_argument("--count", type=int, default=3,
                        help="搜索链接数量（默认: 3）")
    parser.add_argument("--emotions-list", help="全文情绪列表（逗号分隔，用于生成交替策略）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    # 生成搜索链接
    config = get_emotion_config(args.emotion)
    links = generate_search_links(args.emotion)[:args.count]

    # 生成 BGM 交替策略
    strategy = None
    if args.emotions_list:
        emotions = [e.strip() for e in args.emotions_list.split(",") if e.strip()]
        strategy = generate_narrative_bgm_strategy(emotions)

    if args.json:
        output = {
            "emotion": args.emotion,
            "bpm_range": config["bpm_range"],
            "instrument": config["instrument"],
            "search_links": links,
        }
        if strategy:
            output["strategy"] = strategy
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print_bgm_results(args.emotion, links, strategy)


if __name__ == "__main__":
    main()
