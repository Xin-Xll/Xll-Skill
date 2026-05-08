# Xll-Skill

WorkBuddy Skills Collection — AI 驱动的商用视频素材与 BGM 搜索工具集。

## 包含的 Skill

### 商用视频音乐搜索大王

根据口播文案的语义、情绪、叙事节奏，**同步匹配免版权 BGM 与画面素材**。

**核心功能**：
1. 文案拆解与多维度分析（语义 / 情绪 / 节奏段落）
2. 全局 BGM 推荐方案（情绪匹配搜索词 + Pixabay Music 精准链接）
3. 逐句画面素材匹配（Pexels Video API + Pixabay Video API）
4. 输出「分段文案 + BGM 推荐 + 画面素材」三列对照表

## 目录结构

```
commercial-video-music-search/
├── SKILL.md                          # Skill 定义文件
├── references/
│   └── bgm_emotion_map.md            # 情绪-BGM 映射参考表
└── scripts/
    ├── .env.example                  # API Key 配置模板（复制为 .env 使用）
    ├── .gitignore                    # Git 忽略规则（保护 .env）
    ├── split_and_analyze.py          # 文案拆解 + 情绪/节奏分析
    ├── bgm_matcher.py                # BGM 情绪匹配推荐（生成搜索链接）
    └── video_searcher.py             # 视频素材检索（Pexels + Pixabay 双源）
```

## 快速开始

### 1. 配置 API Key

```bash
cd commercial-video-music-search/scripts
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

| 服务 | 获取地址 | 免费额度 |
|------|---------|---------|
| Pexels 视频 | https://www.pexels.com/api/ | 200 次/月 |
| Pixabay 视频 | https://pixabay.com/api/docs/ | 100 次/小时 |

### 2. 运行脚本

```bash
# 文案分析与情绪标注
python3 split_and_analyze.py "你的口播文案内容"

# BGM 推荐
python3 bgm_matcher.py --emotion 感动 --count 3

# 视频素材搜索
python3 video_searcher.py --query "woman sunlight warm indoor" --source both --count 3
```

## 工作流

```
用户输入文案 (≥10字)
  → Step 0: 输入验证
  → Step 1: 文案分析（语义 + 情绪 + 叙事节奏）
  → Step 2A: BGM 推荐（情绪匹配搜索词 + 精准链接）
  → Step 2B: 画面素材匹配（Pexels + Pixabay 双源逐句搜索）
  → Step 3: 汇总输出三列对照表
```

## 免责声明

- Pexels 和 Pixabay 的素材均可免费商用，无需署名
- API Key 存储在本地 `.env` 文件中，**不会提交到仓库**
- 本工具仅生成搜索方案和链接，不存储或分发任何受版权保护的音频/视频内容

## License

MIT
