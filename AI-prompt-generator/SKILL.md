---
name: AI绘画提示词生成器
description: "根据视频脚本文案生成高精准AI绘画提示词，解决提示词调试效率低、生成内容不符合专业调性的痛点。支持Midjourney、Stable Diffusion、DALL-E、FLUX、即梦等主流工具。"
description_zh: "视频文案 → AI绘画提示词，一键生成可直接复制使用的专业提示词"
description_en: "Video script to AI image prompt generator"
version: 2.0.0
agent_created: true
tags: ["AI绘画", "提示词", "视频素材", "内容创作"]
---

# AI绘画提示词生成器

## 核心定位

**只做一件事**：接收视频文案 → 输出可直接复制使用的AI绘画提示词

不生成图片，只给提示词。用户复制提示词到自己习惯的工具里使用。

---

## 工作流程

1. 接收用户文案
2. 提取关键画面
3. 输出多平台提示词（Midjourney / Stable Diffusion / DALL-E / FLUX / 即梦）
4. 每条提示词可直接复制

---

## 输出格式规范

```
═══════════════════════════════════════
【画面X】：[一句话描述画面]
═══════════════════════════════════════

🎯 核心描述：
[画面核心内容的中文描述]

📋 Midjourney：
[完整英文提示词，含参数]

📋 Stable Diffusion：
[含权重和否定词]

📋 即梦/国产工具：
[中文友好型提示词]

💡 使用建议：
- 比例参数：[推荐比例]
- 风格强化词：[可追加的关键词]
```

---

## 质量标准

### 必须包含
- ✅ 主体：具体是谁/什么
- ✅ 场景：地点、环境、光线
- ✅ 风格：明确参考风格
- ✅ 参数：画质、比例等

### 避免
- ❌ 模糊词：好看的、漂亮的 → 具体描述
- ❌ 风格冲突：写实+卡通同时出现
- ❌ 参数缺失：没有比例/画质标签

---

## 示例

### 输入
"以前属于企业级AI的合同能力，现在每个人都能用。3D皮克斯动漫风格。"

### 输出

```
═══════════════════════════════════════
【画面1】：AI从企业级到个人用户的转变
═══════════════════════════════════════

🎯 核心描述：
从巨大企业服务器，小人伸手触碰发光的AI能力，数字粒子流向手机电脑

📋 Midjourney：
Pixar 3D animated style, cinematic shot, visual metaphor of AI democratization, a small cute character reaching out to grab a glowing magical orb of technology from massive corporate server towers, while tiny digital particles flow down to ordinary laptop and smartphone, warm inspiring atmosphere, sunrise colors, volumetric lighting, Toy Story character design aesthetic, soft edges, vibrant colors --ar 16:9 --style raw --s 400 --v 6.1

📋 Stable Diffusion：
masterpiece, best quality, Pixar 3D animation style, corporate server room transitioning to personal device, cute cartoon character reaching for glowing AI orb, digital particles flowing to laptop and phone, warm lighting, inspirational mood, Toy Story aesthetic, soft character modeling, volumetric god rays, vibrant color palette, <lora:pixar_style:1.2>
Negative: anime, cartoon style, low quality, blurry

📋 即梦/国产工具：
皮克斯3D动画风格，电影感镜头，AI普惠化视觉隐喻，一个可爱的小人伸手触碰发光的科技魔法球，数字粒子从巨大的企业服务器流向普通人的笔记本电脑和手机，温暖励志氛围，日出色调，体积光，皮克斯角色设计美学，圆润边缘，鲜艳色彩
```

---

## 触发方式

用户可以用以下任一方式触发：

- "生成AI绘画提示词"
- "帮我生成[风格]风格的提示词"
- "这段文案生成图片素材的提示词"
- 直接粘贴文案并说明想要的风格

---

## 风格关键词库

### 3D动漫风格
```
Pixar 3D animation, Toy Story character design, Incredibles aesthetic, soft rounded forms, volumetric lighting
```

### 电影感
```
cinematic, dramatic lighting, film grain, anamorphic lens, shallow depth of field
```

### 写实摄影
```
photorealistic, editorial photography, shot on Canon/Sony, 85mm lens, f/1.8
```

### 插画风格
```
digital illustration, flat design, vector art, clean lines, minimalist
```

### 中国风
```
Chinese ink painting style, traditional Chinese art, shan shui, elegant ink wash aesthetic
```
