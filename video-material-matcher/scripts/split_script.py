#!/usr/bin/env python3
"""
文案智能拆解脚本
将口播文案按句子/意群拆分为独立片段
"""

import re
import sys


def split_script(text):
    """
    将文案拆分为独立句子/意群

    Args:
        text: 输入文案

    Returns:
        list: 拆分后的句子列表
    """
    if not text:
        return []

    # 清理文本
    text = text.strip()

    # 按句子结束符拆分
    sentences = re.split(r'[。！？\n]+', text)

    # 过滤空句子并清理空白
    result = []
    for s in sentences:
        s = s.strip()
        if s and len(s) > 2:  # 至少3个字符
            result.append(s)

    return result


def extract_keywords(sentence):
    """
    从句子中提取关键词

    Args:
        sentence: 输入句子

    Returns:
        dict: 关键词分类
    """
    # 简化的关键词提取（实际可接入NLP服务）
    keywords = {
        '主体': [],
        '动作': [],
        '场景': [],
        '情绪': [],
        '物体': []
    }

    # 常见主体词
    subjects = ['人', '人', '年轻人', '老人', '孩子', '男人', '女人', '员工', '老板', '朋友', '家人']
    # 常见动作
    actions = ['走', '跑', '坐', '站', '工作', '学习', '吃饭', '睡觉', '说话', '笑', '哭', '写', '读', '看', '开车']
    # 常见场景
    scenes = ['家', '办公室', '学校', '商场', '街道', '公园', '海边', '咖啡馆', '餐厅', '厨房', '卧室']
    # 常见情绪
    emotions = ['开心', '难过', '紧张', '平静', '兴奋', '忧郁', '温暖', '孤独']
    # 常见物体
    objects = ['手机', '电脑', '书', '咖啡', '水', '食物', '衣服', '包', '车', '自行车']

    sentence_lower = sentence.lower()

    for word in subjects:
        if word in sentence:
            keywords['主体'].append(word)

    for word in actions:
        if word in sentence:
            keywords['动作'].append(word)

    for word in scenes:
        if word in sentence:
            keywords['场景'].append(word)

    for word in emotions:
        if word in sentence:
            keywords['情绪'].append(word)

    for word in objects:
        if word in sentence:
            keywords['物体'].append(word)

    return keywords


def format_keywords_for_search(keywords):
    """
    将关键词格式化为搜索字符串

    Args:
        keywords: 关键词字典

    Returns:
        str: 搜索字符串
    """
    parts = []

    # 优先使用主体和动作
    if keywords['主体']:
        parts.extend(keywords['主体'][:2])
    if keywords['动作']:
        parts.extend(keywords['动作'][:2])
    if keywords['场景']:
        parts.append(keywords['场景'][0])
    if keywords['物体']:
        parts.append(keywords['物体'][0])

    return ' '.join(parts) if parts else None


def main():
    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
    else:
        print("请输入文案内容")
        print("用法: python3 split_script.py \"你的文案内容\"")
        return

    sentences = split_script(text)

    print(f"📝 文案拆解结果（共 {len(sentences)} 句）：\n")

    results = []
    for i, sentence in enumerate(sentences, 1):
        print(f"【第{i}句】{sentence}")

        keywords = extract_keywords(sentence)
        search_query = format_keywords_for_search(keywords)

        print(f"   关键词: {search_query or '未识别到明确关键词'}")

        if any(keywords.values()):
            for cat, words in keywords.items():
                if words:
                    print(f"   {cat}: {', '.join(words)}")

        print()

        results.append({
            'index': i,
            'sentence': sentence,
            'keywords': keywords,
            'search_query': search_query
        })

    return results


if __name__ == "__main__":
    main()
