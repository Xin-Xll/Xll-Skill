#!/usr/bin/env python3
"""
video_searcher.py
用途：根据关键词从 Pexels + Pixabay Video API 检索免版权视频素材
用法：
  python3 video_searcher.py --query "calm ocean sunset" --pexels-key KEY --pixabay-key KEY
  python3 video_searcher.py --query "energetic team" --source both --count 3
  环境变量：PEXELS_API_KEY, PIXABAY_API_KEY（优先于参数）
输出：JSON 格式的视频候选列表
"""

import sys
import os
import json
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error


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
# Pexels Video API
# ─────────────────────────────────────────────
def search_pexels_video(query: str, api_key: str, per_page: int = 3, page: int = 1) -> dict:
    """
    调用 Pexels Video API 检索免版权视频
    
    API 文档：https://www.pexels.com/api/documentation/
    Endpoint：https://api.pexels.com/videos/search
    """
    base_url = "https://api.pexels.com/videos/search"
    params = {
        "query": query,
        "per_page": min(max(per_page, 1), 80),
        "page": page,
        "orientation": "landscape",
    }
    url = base_url + "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url, headers={
        "Authorization": api_key,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
            else:
                raise Exception(f"HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise Exception("Pexels API Key 无效或已过期")
        elif e.code == 429:
            raise Exception("Pexels 请求频率超限（200次/月），请稍后重试")
        else:
            raise Exception(f"Pexels API 请求失败: HTTP {e.code}")
    except urllib.error.URLError as e:
        raise Exception(f"网络错误: {e.reason}")


def format_pexels_results(data: dict, max_count: int = 5) -> list:
    """格式化 Pexels 视频结果"""
    results = []
    for v in data.get("videos", [])[:max_count]:
        # 提取最高质量视频链接
        best_quality = None
        for file_info in v.get("video_files", []):
            if file_info.get("quality") == "hd" and file_info.get("width", 0) >= 1920:
                best_quality = file_info
                break
        if not best_quality:
            # 退而求其次
            for file_info in v.get("video_files", []):
                if file_info.get("quality") == "sd":
                    best_quality = file_info
                    break
        if not best_quality and v.get("video_files"):
            best_quality = v["video_files"][0]

        results.append({
            "id": v["id"],
            "duration": v.get("duration", 0),
            "width": v.get("width", 0),
            "height": v.get("height", 0),
            "url": v.get("url", ""),
            "image_preview": v.get("image", ""),
            "download_link": best_quality.get("link", "") if best_quality else "",
            "quality": best_quality.get("quality", "") if best_quality else "",
            "source": "pexels",
        })
    return results


# ─────────────────────────────────────────────
# Pixabay Video API
# ─────────────────────────────────────────────
def search_pixabay_video(query: str, api_key: str, per_page: int = 3, page: int = 1) -> dict:
    """
    调用 Pixabay Video API 检索免版权视频
    
    API 文档：https://pixabay.com/api/docs/#api_videos
    Endpoint：https://pixabay.com/api/videos/
    注意：per_page 最小值为 3，最大值为 200
    """
    base_url = "https://pixabay.com/api/videos/"
    params = {
        "key": api_key,
        "q": query,
        "per_page": min(max(per_page, 3), 200),
        "page": page,
        "order": "popular",
    }
    url = base_url + "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
            else:
                raise Exception(f"HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        if e.code == 400:
            raise Exception("Pixabay API 请求参数错误，请检查搜索词")
        elif e.code == 429:
            raise Exception("Pixabay 请求频率超限（100次/小时），请稍后重试")
        else:
            raise Exception(f"Pixabay API 请求失败: HTTP {e.code}")
    except urllib.error.URLError as e:
        raise Exception(f"网络错误: {e.reason}")


def format_pixabay_results(data: dict, max_count: int = 5) -> list:
    """格式化 Pixabay 视频结果"""
    results = []
    for v in data.get("hits", [])[:max_count]:
        # 提取视频质量信息
        videos_info = v.get("videos", {})
        best_quality = None
        for quality in ["large", "medium", "small", "tiny"]:
            if quality in videos_info:
                best_quality = videos_info[quality]
                break

        results.append({
            "id": v["id"],
            "duration": v.get("duration", 0),
            "width": best_quality.get("width", 0) if best_quality else 0,
            "height": best_quality.get("height", 0) if best_quality else 0,
            "url": v.get("pageURL", ""),
            "image_preview": v.get("userImageURL", ""),
            "download_link": best_quality.get("url", "") if best_quality else "",
            "quality": list(videos_info.keys()) if videos_info else [],
            "tags": v.get("tags", ""),
            "source": "pixabay",
        })
    return results


# ─────────────────────────────────────────────
# 综合搜索
# ─────────────────────────────────────────────
def search_video(query: str, pexels_key: str = "", pixabay_key: str = "",
                 count: int = 3, source: str = "both") -> dict:
    """
    综合搜索视频素材，合并 Pexels + Pixabay 结果
    
    Args:
        query: 英文搜索关键词
        pexels_key: Pexels API Key
        pixabay_key: Pixabay API Key
        count: 每个源返回的最大数量
        source: "pexels" / "pixabay" / "both"
    """
    results = {"query": query, "videos": []}

    if source in ("pexels", "both") and pexels_key:
        try:
            data = search_pexels_video(query, pexels_key, per_page=count)
            pexels_results = format_pexels_results(data, max_count=count)
            results["videos"].extend(pexels_results)
            results["pexels_total"] = data.get("total_results", 0)
        except Exception as e:
            results["pexels_error"] = str(e)

    if source in ("pixabay", "both") and pixabay_key:
        try:
            data = search_pixabay_video(query, pixabay_key, per_page=max(count, 3))
            pixabay_results = format_pixabay_results(data, max_count=count)
            results["videos"].extend(pixabay_results)
            results["pixabay_total"] = data.get("totalHits", 0)
        except Exception as e:
            results["pixabay_error"] = str(e)

    return results


def print_video_results(query: str, video_list: list):
    """格式化打印视频搜索结果"""
    print(f"\n🎬 视频素材（关键词: {query}）\n")
    if not video_list:
        print("  未找到匹配的视频素材")
        return
    
    for i, v in enumerate(video_list, 1):
        source_label = "Pexels" if v["source"] == "pexels" else "Pixabay"
        duration_str = f"{v['duration']}s" if v.get("duration") else "?"
        print(f"  ├ [视频{i}] [{source_label}] {v['url']}")
        print(f"  │         时长: {duration_str}  分辨率: {v.get('width', '?')}x{v.get('height', '?')}")
        if v.get("tags"):
            print(f"  │         标签: {v['tags'][:60]}")
        print()


def main():
    parser = argparse.ArgumentParser(description="视频素材检索（Pexels + Pixabay）")
    parser.add_argument("--query", required=True, help="英文搜索关键词")
    parser.add_argument("--count", type=int, default=3, help="每个源返回数量（默认: 3）")
    parser.add_argument("--source", choices=["pexels", "pixabay", "both"], default="both",
                        help="搜索源（默认: both）")
    parser.add_argument("--pexels-key", help="Pexels API Key（优先级低于环境变量）")
    parser.add_argument("--pixabay-key", help="Pixabay API Key（优先级低于环境变量）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    # 获取 API Key（环境变量 > 参数 > .env 自动加载）
    pexels_key = os.environ.get("PEXELS_API_KEY") or args.pexels_key
    pixabay_key = os.environ.get("PIXABAY_API_KEY") or args.pixabay_key

    if not pexels_key and not pixabay_key:
        print("错误：未配置任何 API Key", file=sys.stderr)
        print("请设置环境变量 PEXELS_API_KEY / PIXABAY_API_KEY 或使用对应参数", file=sys.stderr)
        sys.exit(1)

    try:
        result = search_video(args.query, pexels_key, pixabay_key, args.count, args.source)
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_video_results(args.query, result["videos"])


if __name__ == "__main__":
    main()
