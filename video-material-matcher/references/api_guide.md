# Pexels API 使用指南

## 概述

Pexels 是一个提供免费高清视频和图片的平台，其 API 允许开发者程序化地搜索和下载素材。

## API 基本信息

- **官网**: https://www.pexels.com/
- **API 文档**: https://www.pexels.com/api/
- **Base URL**: `https://api.pexels.com`

## 申请 API Key

1. 访问 https://www.pexels.com/api/
2. 点击 "Your API Key" 获取 API Key
3. 免费账户限制：
   - 每月 200 次请求
   - 每请求最多 50 条结果

## 视频搜索 API

### Endpoint

```
GET https://api.pexels.com/videos/search
```

### 请求头

```
Authorization: YOUR_API_KEY
```

### 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| query | string | 必填 | 搜索关键词 |
| per_page | integer | 15 | 每页结果数（最大50） |
| page | integer | 1 | 页码 |
| orientation | string | any | 视频方向 (landscape/portrait/square) |
| size | string | any | 视频大小 (large/medium/small) |
| locale | string | en-US | 语言区域 |

### 响应示例

```json
{
  "page": 1,
  "per_page": 5,
  "total_results": 100,
  "videos": [
    {
      "id": 1234567,
      "width": 1920,
      "height": 1080,
      "duration": 30,
      "image": "https://images.pexels.com/videos/1234567/images/preview.jpg",
      "url": "https://www.pexels.com/video/1234567/",
      "user": {
        "id": 123,
        "name": "John Doe",
        "url": "https://www.pexels.com/@johndoe"
      },
      "video_files": [
        {
          "id": 12345,
          "quality": "hd",
          "file_type": "video/mp4",
          "width": 1920,
          "height": 1080,
          "link": "https://player.vimeo.com/..."
        }
      ],
      "video_pictures": [
        {
          "id": 0,
          "picture": "https://images.pexels.com/...",
          "nr": 0
        }
      ]
    }
  ]
}
```

## 热门视频 API

### Endpoint

```
GET https://api.pexels.com/videos/popular
```

### 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| per_page | integer | 15 | 每页结果数（最大50） |
| page | integer | 1 | 页码 |

## 视频详情 API

### Endpoint

```
GET https://api.pexels.com/videos/videos/{id}
```

## Python 调用示例

```python
import os
import requests

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "YOUR_API_KEY")

def search_videos(query, per_page=5):
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page}

    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 使用
results = search_videos("coffee shop writing")
for video in results["videos"]:
    print(f"ID: {video['id']}")
    print(f"链接: {video['url']}")
    print(f"时长: {video['duration']}秒")
```

## 使用注意事项

1. **速率限制**: 免费账户每分钟最多 200 请求
2. **必填署名**: 使用 Pexels 素材需署名作者
3. **禁止转售**: 不可单独出售 Pexels 素材
4. **修改限制**: 可修改但需遵守原授权

## 备选平台

如果 Pexels 不满足需求，可考虑：

| 平台 | 特点 | API 支持 |
|------|------|----------|
| Pixabay | 免费商用 | 是（需申请） |
| Videvo | 免费素材 | 否（浏览器） |
| Coverr | 免费商用 | 否（浏览器） |
| Life of Vids | 免费商用 | 否（浏览器） |

## 版权说明

所有 Pexels 素材遵循 Pexels License：
- ✅ 可用于商业和非商业项目
- ✅ 可免费下载和修改
- ✅ 无需事先征得同意
- ⚠️ 使用时需署名 Pexels 和原作者
- ❌ 不可单独出售素材本身
