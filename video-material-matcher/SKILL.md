---
name: 商用视频素材搜索大师
description: 商用视频素材搜索大师。当用户需要根据口播文案/视频主题匹配商用视频素材时使用。支持：1）文案智能拆解分句；2）Pexels商用素材检索；3）关键词语义匹配；4）分句画面对应结果展示。此技能可大幅缩短素材查找时间，解决版权风险，提升视频可视化效果。
agent_created: true
disable: false
---

# 商用视频素材搜索大师

## TL;DR 快速参考

```
用户输入文案/主题 → Step 0验证 → Step 1拆解 → Step 2提取关键词
→ Step 3检查API Key → Step 3.1检索 → Step 4展示结果
```

**触发词**：匹配素材、文案配画面、视频素材搜索、商用视频

**最小输入**：10字以上的口播文案或视频主题

**核心输出**：`📍 句子 + 关键词 + 匹配素材链接`

---

## 技能概述

根据用户提供的口播文案或视频主题，自动完成：
1. **文案拆解** - 按句子/意群智能拆分
2. **关键词提取** - 提取画面关键词、主体、动作、场景
3. **素材检索** - 调用 Pexels/Pixabay 免费商用视频 API
4. **画面匹配** - 按文案顺序匹配合适素材并展示

## 使用场景

- 用户提供口播文案，需要匹配对应画面素材
- 用户给定视频主题，需要批量检索可用素材
- 用户想快速获取"文案-素材"对照表

**⚠️ 本技能不处理的场景**：
- 内容合规/审核问题（如"敏感内容怎么办"）→ 请咨询相关领域专家
- 非素材请求的咨询问题

## 流程决策树

```
                    ┌─────────────────────┐
                    │     用户输入         │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Step 0: 输入验证   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        "怎么办"类问题      素材请求         输入过短
              │                │                │
              ▼                ▼                ▼
        提示不处理      继续 Step 1     提示补充输入
              │                │
              ▼                ▼
         停止执行    ┌─────────────────────┐
                    │  Step 1: 文案拆解   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Step 2: 关键词提取 │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Step 3: API Key检查 │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
          Key有效           Key无效         用户选择
              │                │           备选方案
              ▼                ▼                ▼
    ┌─────────────────┐   提示配置      浏览器搜索
    │ Step 3.1: 检索  │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Step 4: 结果展示 │
    └─────────────────┘
```

## 核心流程

### Step 0: 输入验证（检查点）

**⚠️ 在执行前，检查用户输入类型：**

```
用户输入类型判断：
├─ 如果是"怎么办/如何处理/是否..."类问题
│   → 本技能专注于素材匹配，请告知用户：
│   → "我专注于视频素材搜索，关于XX问题建议咨询专业人士"
│   → 停止执行，等待用户明确素材需求
│
├─ 如果是素材请求（口播文案/视频主题）
│   → 继续 Step 1
│
└─ 如果输入为空或过短（<10字）
    → 提示用户："请提供更完整的文案或视频主题"
    → 停止执行，等待用户补充
```

### Step 1: 文案拆解

将输入文案按标点符号和语义拆分为独立句子/意群。

使用 `scripts/split_script.py` 进行拆解：

```python
python3 ~/.workbuddy/skills/video-material-matcher/scripts/split_script.py "你的文案内容"
```

或直接在上下文中使用以下拆解规则：
- 按句号（。）、问号（？）、感叹号（！）拆分
- 过长句子按逗号（，）进一步拆分
- 每段独立描述一个画面/动作的句子为最小单元

**输入**：用户提供的口播文案或视频主题
**输出**：拆分后的句子列表

### Step 2: 关键词提取

对每个拆分后的句子，提取以下信息：

| 类型 | 说明 | 示例 |
|------|------|------|
| 主体 | 画面核心对象 | 人、产品、风景 |
| 动作 | 动态描述 | 行走、烹饪、工作 |
| 场景 | 环境/地点 | 办公室、海边、厨房 |
| 情绪 | 情感基调 | 活力、平静、紧张 |
| 物体 | 重要物品 | 手机、电脑、咖啡杯 |

**输入**：拆分后的句子列表
**输出**：每个句子的关键词表格

### Step 3: API Key 检查（检查点）

**⚠️ 在调用Pexels API前，必须检查API Key配置：**

```
API Key 状态检查：
├─ 如果 PEXELS_API_KEY 环境变量已设置
│   → 继续执行 Step 3.1
│
├─ 如果 PEXELS_API_KEY 未设置
│   → 提示用户："需要配置 Pexels API Key 才能调用素材搜索"
│   → 提供获取方式：
│     1. 访问 https://www.pexels.com/api/
│     2. 注册并申请免费API Key（每月200次请求）
│   → ⚠️ 询问用户：
│     - "请提供您的API Key" → 继续执行
│     - "使用备选方案" → 跳至备选流程
│     - "暂不执行" → 停止
│
└─ 如果API Key疑似无效（如返回401）
    → 提示用户检查API Key是否正确
    → 提供备选方案选项
```

### Step 3.1: 素材检索

使用 Pexels API 检索商用视频素材：

**API Endpoint**: `https://api.pexels.com/videos/search`

**完整请求参数**：
| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `query` | string | ✅ | 搜索关键词（建议用英文+中文） | `"coffee shop writing"` |
| `per_page` | int | ✅ | 每页返回数量（1-80） | `5-10` |
| `page` | int | ❌ | 页码（默认1） | `1` |
| `orientation` | string | ❌ | 视频方向 | `landscape` / `portrait` / `square` |
| `size` | string | ❌ | 视频大小 | `small` / `medium` / `large` |
| `min_duration` | int | ❌ | 最小时长（秒） | `10` |
| `max_duration` | int | ❌ | 最大时长（秒） | `60` |

**Headers**:
```
Authorization: {PEXELS_API_KEY}
```

**完整示例调用**：

```python
import requests

def search_pexels(query, api_key, per_page=5, page=1, orientation="landscape"):
    """
    搜索Pexels商用视频素材

    参数:
        query: 搜索关键词（推荐英文，或英文+中文组合）
        api_key: Pexels API Key
        per_page: 每页数量
        page: 页码
        orientation: landscape(横屏) / portrait(竖屏) / square(方形)
    """
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": per_page,
        "page": page,
        "orientation": orientation
    }
    response = requests.get(url, headers=headers, params=params)

    # 错误码处理
    if response.status_code == 401:
        raise Exception("API Key无效，请检查配置")
    elif response.status_code == 429:
        raise Exception("速率限制，请稍后重试")
    elif response.status_code != 200:
        raise Exception(f"API请求失败: {response.status_code}")

    return response.json()

# 关键词构建技巧：主体+动作+场景，用英文逗号分隔
# 示例: "young woman, reading book, coffee shop, window, sunlight"
```

**关键词构建技巧**：
- 中文 → 英文翻译：使用常见英文词汇（如"咖啡馆"→"coffee shop"）
- 组合方式：`主体, 动作, 场景, 氛围`
- 避免：过长关键词（>5个词）、专有名词、拼写错误

**API响应解析**：

```python
# response 格式
{
    "page": 1,
    "per_page": 5,
    "total_results": 100,
    "videos": [
        {
            "id": 123456,
            "width": 1920,
            "height": 1080,
            "duration": 15,
            "url": "https://www.pexels.com/video/...",
            "image": "https://images.pexels.com/...",
            "user": {"name": "摄影师名", "url": "..."},
            "video_files": [
                {"quality": "hd", "file_type": "video/mp4", "width": 1920, "link": "..."},
                {"quality": "sd", "file_type": "video/mp4", "width": 640, "link": "..."}
            ]
        }
    ]
}

# 提取素材信息
for video in response["videos"]:
    print(f"ID: {video['id']}")
    print(f"时长: {video['duration']}秒")
    print(f"链接: {video['url']}")
    print(f"下载: {video['video_files'][0]['link']}")  # 取最高质量
```

**输入**：关键词
**输出**：Pexels API 响应（视频素材列表）

### Step 4: 结果展示

按以下格式展示匹配结果：

```
📍 第1句: "阳光照进咖啡馆，一位年轻人正在窗边写作"

   关键词: 年轻人 | 写作 | 咖啡馆 | 窗边 | 阳光
   匹配素材:
   ├ [素材1] Coffee Shop Writing - https://www.pexels.com/video/xxx
   ├ [素材2] Young Woman Working - https://www.pexels.com/video/yyy
   └ [素材3] Sunlight Window Cafe - https://www.pexels.com/video/zzz

📍 第2句: "窗外海鸥飞过，远处帆船点点"

   关键词: 海鸥 | 帆船 | 大海 | 飞翔
   匹配素材:
   ├ [素材1] Seagulls Flying Ocean - https://www.pexels.com/video/aaa
   ...
```

**输入**：Pexels 素材列表
**输出**：格式化展示的文案-素材对照表

## API Key 配置

首次使用时，检查是否已配置 Pexels API Key：

```python
import os
api_key = os.environ.get("PEXELS_API_KEY") or "your-api-key-here"
```

**获取 Pexels API Key**:
1. 访问 https://www.pexels.com/api/
2. 注册账号并申请 API Key（免费额度：每月 200 次请求）
3. 设置环境变量或告知用户配置

## 备选方案

**⚠️ 启用备选方案前，提示用户**："将使用浏览器搜索作为备选，搜索结果可能不如API精确"

如 Pexels API 不可用，使用备用流程：
1. 直接在浏览器中打开 Pexels/Pixabay 搜索页面
2. 使用 `browser` 工具进行网页搜索
3. 手动提取视频链接返回给用户

## 版权说明

所有通过 Pexels/Pixabay 获取的素材：
- ✓ 可免费商用（需要署名 Pexels/Pixabay）
- ✓ 可用于商业项目
- ✓ 可修改和再分发

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| API 请求失败（网络错误） | 降级到浏览器搜索，提示用户 |
| API 超时（>10s） | 降级到浏览器搜索，提示用户 |
| API 返回401（无效Key） | 提示检查API Key配置，提供备选方案 |
| API 返回429（速率限制） | 添加2-3秒延迟后重试，最多重试3次 |
| 搜索无结果 | 尝试放宽关键词或使用同义词，最多3次 |
| 关键词全部无结果 | 提示用户更换搜索词或使用备选方案 |

## 相关文件

- `scripts/split_script.py` - 文案拆解脚本
- `scripts/search_pexels.py` - Pexels API 搜索脚本
- `references/api_guide.md` - Pexels API 完整文档
