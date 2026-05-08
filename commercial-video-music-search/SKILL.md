---
name: "商用视频音乐搜索大王"
description: "根据口播文案的语义、情绪、叙事节奏，同步匹配免版权 BGM 与画面素材。输入任意口播文案，自动完成：1）文案拆解与多维度分析（语义/情绪/节奏段落）；2）全局 BGM 推荐方案（情绪匹配搜索词 + Pixabay Music 精准链接）；3）逐句画面素材匹配（Pexels Video API + Pixabay Video API）；4）输出「分段文案 + BGM 推荐 + 画面素材」三列对照表。适用场景：口播视频剪辑素材准备、快速生成配乐方案、大批量减少人工试听和素材查找耗时。"
agent_created: true
---

# 商用视频音乐搜索大王

## TL;DR 快速参考

```
用户输入文案
  → Step 0 验证
  → Step 1 文案分析（语义 + 情绪 + 叙事节奏）
  → Step 2A BGM 推荐（情绪匹配搜索词 + Pixabay Music 精准搜索链接）
  → Step 2B 画面素材匹配（Pexels Video API + Pixabay Video API，逐句搜索）
  → Step 3 汇总输出三列对照表
```

**触发词**：配乐、BGM 推荐、配画面、口播配素材、视频素材匹配、配音乐

**最小输入**：10 字以上的口播文案或视频脚本

**核心输出**：
- 整体 BGM 推荐方案（3~5 个精准搜索链接）+ 分段 BGM 交替策略
- 「句子 → 关键词 → 画面素材链接」对照表

---

## 核心流程

### Step 0：输入验证

- 如果输入为空或不足 10 字 → 提示补充完整文案，停止
- 如果输入是"如何使用/怎么做"类问题 → 解答后引导用户提交文案
- 否则 → 继续 Step 1

---

### Step 1：文案分析

调用脚本完成三层标注：

```bash
python3 ~/.workbuddy/skills/commercial-video-music-search/scripts/split_and_analyze.py "文案内容"
```

**三层标注说明**：

| 维度 | 说明 | 示例 |
|------|------|------|
| 语义分段 | 按标点+意群拆分为独立句子 | ["句子1", "句子2", ...] |
| 情绪标注 | 每句标注主情绪 | 舒缓/激昂/感动/悬念/轻松/紧张/温暖 |
| 叙事节奏 | 整体节奏阶段 | 铺垫(开场) / 发展(中段) / 高潮 / 收尾 |

**情绪判断规则**（内联分析时参考）：
- 舒缓：描述风景、回忆、慢节奏生活
- 激昂：号召、目标、成就、行动
- 感动：亲情、成长、感谢、告别
- 悬念：疑问、转折、意外、冲突
- 轻松：幽默、生活日常、轻描淡写
- 温暖：陪伴、关怀、温情

**⚠️ 关键提醒**：脚本的关键词匹配对商业推广类文案不够精准（容易大量标为"舒缓"），对这类文案需要 AI 人工修正情绪标注，更关注转折、悬念、紧张等情绪。

---

### Step 2A：BGM 推荐

> **重要说明**：Pixabay 公开 API 不提供音乐搜索端点（仅支持图片和视频搜索），因此 BGM 推荐采用**情绪匹配搜索词 + 生成精准搜索链接**的方案。

调用脚本生成 BGM 搜索方案：

```bash
python3 ~/.workbuddy/skills/commercial-video-music-search/scripts/bgm_matcher.py --emotion "感动" --count 3
```

如需生成 BGM 交替策略（含高潮段落切换）：

```bash
python3 ~/.workbuddy/skills/commercial-video-music-search/scripts/bgm_matcher.py --emotion "感动" --emotions-list "舒缓,舒缓,悬念,激昂,激昂,感动,温暖"
```

**情绪 → BGM 参数映射**（完整版见 `references/bgm_emotion_map.md`）：

| 情绪 | 搜索关键词 | BPM 倾向 | 乐器倾向 |
|------|-----------|---------|---------|
| 舒缓 | ambient relaxing calm | 60-80 | piano, acoustic guitar, ambient synth |
| 激昂 | energetic motivational epic | 120-160 | orchestra, drums, brass |
| 感动 | emotional touching heartfelt | 80-100 | piano, strings, cello |
| 悬念 | suspense cinematic tension | 90-110 | synth, bass, percussion |
| 轻松 | upbeat happy cheerful | 100-120 | ukulele, clapping, whistling |
| 温暖 | warm cozy acoustic | 70-90 | acoustic guitar, piano |

**输出格式**：

```
🎵 BGM 推荐（适配情绪：感动）
   BPM 范围: 80-100  |  乐器倾向: piano, strings, cello

   📋 BGM 策略：双曲交替
      主曲情绪：舒缓（铺垫/发展/收尾段）
      高潮曲情绪：激昂（高潮段落切入）

   🔗 精准搜索链接（点击直达 Pixabay Music 搜索结果）：

   ├ [搜索1] 关键词: emotional touching heartfelt
   │         链接: https://pixabay.com/music/search/emotional%20touching%20heartfelt/
   │         BPM: 80-100  乐器: piano, strings, cello
   ...
```

---

### Step 2B：画面素材匹配

对 Step 1 拆解出的每个句子，提取画面关键词并调用 Pexels + Pixabay Video API 检索。

**API Key 已配置**：Key 存储在 `scripts/.env` 文件中，脚本自动加载。

**调用脚本**：

```bash
python3 ~/.workbuddy/skills/commercial-video-music-search/scripts/video_searcher.py \
  --query "woman album sunlight warm indoor" \
  --count 3 \
  --source both
```

**关键词提取规则**：

| 类型 | 说明 |
|------|------|
| 主体 | 人物/产品/动物/场景核心对象 |
| 动作 | 正在发生的动态 |
| 场景 | 地点/环境/时间 |
| 情绪氛围 | 与情绪对应的视觉描述词 |

关键词须翻译为英文，组合格式：`主体 动作 场景 氛围`，不超过 5 个词。

**双源搜索**：

| 源 | API Endpoint | 免费额度 | 特点 |
|----|-------------|---------|------|
| Pexels Video | `api.pexels.com/videos/search` | 200次/月 | 高质量，精准匹配 |
| Pixabay Video | `pixabay.com/api/videos/` | 100次/小时 | 数量丰富，多分辨率 |

**输出格式**：

```
📍 第1句: "阳光洒进来，她低头翻着相册"

   情绪: 温暖  节奏段落: 铺垫
   关键词: woman album sunlight warm indoor
   匹配画面:
   ├ [视频1] [Pexels] https://www.pexels.com/video/xxx  (时长: 15s, 1920x1080)
   ├ [视频2] [Pixabay] https://pixabay.com/videos/id-xxx  (时长: 20s, 1280x720)
   └ [视频3] [Pexels] https://www.pexels.com/video/yyy  (时长: 12s, 1920x1080)
```

---

### Step 3：汇总输出

最终以结构化对照表形式展示，供剪辑使用：

```
═══════════════════════════════════════════════════════
 商用视频音乐搜索大王 · 对照表
═══════════════════════════════════════════════════════

【整体 BGM 推荐】
  → 主曲搜索：https://pixabay.com/music/search/ambient%20relaxing%20calm/
  → 高潮曲搜索：https://pixabay.com/music/search/energetic%20motivational%20epic/
  → BGM 策略：双曲交替（铺垫/收尾用主曲低音量，高潮切换高音量）

【逐句画面 + 配乐建议】

  句子 1 | 情绪: 温暖 | 段落: 铺垫
  文案: "阳光洒进来，她低头翻着相册"
  BGM: 保持主曲，音量 60%
  画面: [视频1] [视频2] [视频3]

  句子 2 | 情绪: 感动 | 段落: 高潮
  文案: "那一刻，我才明白什么叫做陪伴"
  BGM: 切换高潮曲，音量 80%
  画面: [视频4] [视频5] [视频6]

  ...（以此类推）

═══════════════════════════════════════════════════════
 使用建议：
 · BGM 建议从铺垫段低音量渐入，高潮段拉满
 · 画面素材优先选与文案情绪一致的
 · Pexels/Pixabay 素材均可免费商用，无需署名
═══════════════════════════════════════════════════════
```

---

## API Key 配置说明

| 服务 | 环境变量 | 获取地址 | 免费额度 | 状态 |
|------|---------|---------|---------|------|
| Pexels 视频 | `PEXELS_API_KEY` | https://www.pexels.com/api/ | 200次/月 | ✅ 已配置 |
| Pixabay 图片/视频 | `PIXABAY_API_KEY` | https://pixabay.com/api/docs/ | 100次/小时 | ✅ 已配置 |
| Pixabay 音乐 | — | 无公开 API | — | ❌ 不提供 |

**API Key 存储位置**：`scripts/.env` 文件，脚本运行时自动加载。

**如需更换 Key**：编辑 `scripts/.env` 文件中对应的值即可。

**BGM 方案**：因 Pixabay 无公开音乐 API，BGM 推荐通过情绪匹配生成精准搜索链接，用户点击直达搜索结果页。

**如画面 API Key 未配置**：提供 Pexels/Pixabay 手动搜索链接作为降级方案。

---

## 错误处理

| 错误 | 处理 |
|------|------|
| API 401 | 提示检查 Key，提供配置指引 |
| API 429 | Pexels 等待后重试；Pixabay 等待 3 秒后重试，最多 3 次 |
| 搜索无结果 | 放宽关键词（去掉氛围词），再试一次 |
| 网络超时 | 降级为手动搜索链接 |
| Pexels 403 | 需要添加浏览器 UA 请求头（脚本已内置） |
| Pixabay per_page < 3 | Pixabay API 要求 per_page 最小值为 3（脚本已处理） |

---

## 相关文件

- `scripts/.env` - API Key 配置文件（已配置 Pexels + Pixabay）
- `scripts/split_and_analyze.py` - 文案拆解 + 情绪/节奏分析脚本
- `scripts/bgm_matcher.py` - BGM 情绪匹配推荐脚本（生成搜索链接方案）
- `scripts/video_searcher.py` - 视频素材检索脚本（Pexels + Pixabay 双源）
- `references/bgm_emotion_map.md` - 完整情绪-BGM 映射参考表
