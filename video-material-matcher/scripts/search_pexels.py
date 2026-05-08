#!/usr/bin/env python3
"""
Pexels 视频素材检索脚本
通过 Pexels API 搜索免费商用视频素材
"""

import os
import requests
import json
from typing import List, Dict, Optional


# 默认 API Key（用户需要替换为自己的）
DEFAULT_API_KEY = "YOUR_PEXELS_API_KEY"


def search_pexels(
    query: str,
    api_key: Optional[str] = None,
    per_page: int = 5,
    orientation: str = "landscape",
    page: int = 1
) -> Dict:
    """
    搜索 Pexels 视频素材

    Args:
        query: 搜索关键词
        api_key: Pexels API Key
        per_page: 每页返回数量（最大50）
        orientation: 视频方向 (landscape/portrait/square)
        page: 页码

    Returns:
        dict: API 响应结果
    """
    api_key = api_key or os.environ.get("PEXELS_API_KEY") or DEFAULT_API_KEY

    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": api_key
    }
    params = {
        "query": query,
        "per_page": min(per_page, 50),
        "orientation": orientation,
        "page": page
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "videos": []}


def parse_video_result(video_data: Dict) -> Dict:
    """
    解析单个视频结果

    Args:
        video_data: 原始视频数据

    Returns:
        dict: 格式化后的视频信息
    """
    # 获取最佳质量预览图
    video_files = video_data.get("video_files", [])
    best_preview = None
    for vf in video_files:
        if vf.get("quality") == "hd":
            best_preview = vf.get("link")
            break
    if not best_preview and video_files:
        best_preview = video_files[0].get("link")

    return {
        "id": video_data.get("id"),
        "url": f"https://www.pexels.com/video/{video_data.get('id')}/",
        "duration": video_data.get("duration"),
        "width": video_data.get("width"),
        "height": video_data.get("height"),
        "image": video_data.get("image"),
        "download_url": best_preview,
        "user": video_data.get("user", {}).get("name", "Unknown"),
        "user_url": f"https://www.pexels.com/@{video_data.get('user', {}).get('url', '')}",
    }


def format_results(search_result: Dict, top_n: int = 5) -> List[Dict]:
    """
    格式化搜索结果

    Args:
        search_result: API 原始响应
        top_n: 返回前 N 个结果

    Returns:
        list: 格式化后的结果列表
    """
    if "error" in search_result:
        return []

    videos = search_result.get("videos", [])[:top_n]
    return [parse_video_result(v) for v in videos]


def display_results(results: List[Dict], query: str, top_n: int = 5):
    """
    打印搜索结果

    Args:
        results: 格式化后的结果
        query: 搜索关键词
        top_n: 显示数量
    """
    print(f"\n🔍 搜索关键词: {query}")
    print(f"📹 找到 {len(results)} 个素材:\n")

    for i, video in enumerate(results[:top_n], 1):
        duration = video.get("duration", 0)
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        print(f"  【素材 {i}】")
        print(f"    时长: {minutes:02d}:{seconds:02d}")
        print(f"    尺寸: {video.get('width', 'N/A')}x{video.get('height', 'N/A')}")
        print(f"    作者: {video.get('user', 'Unknown')}")
        print(f"    链接: {video.get('url', 'N/A')}")
        print()


def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 search_pexels.py \"搜索关键词\" [API_KEY]")
        print("或设置环境变量: export PEXELS_API_KEY='your-api-key'")
        return None

    query = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None

    result = search_pexels(query, api_key=api_key, per_page=5)

    if "error" in result:
        print(f"❌ 搜索失败: {result['error']}")
        return None

    formatted = format_results(result)
    display_results(formatted, query)

    return formatted


if __name__ == "__main__":
    main()
