#!/usr/bin/env python3
"""
AI开源周报 - 周报内容生成
使用 MiniMax API 生成中文解读和点评
"""

import json
import os
import sys
from datetime import datetime

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_API_HOST = "https://api.minimax.chat"

def load_data(path="/tmp/ai-weekly-data.json"):
    """加载抓取的数据"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def build_prompt(repos, week_str):
    """构建 Prompt"""
    repo_list = "\n".join([
        f"- **{r['name']}** (⭐{r['stars']:,} | {r['language'] or 'N/A'}): {r['description'] or '无描述'} {r['url']}"
        for r in repos[:20]
    ])
    
    prompt = f"""你是一位专业的 AI/开源技术观察者，为中国的技术从业者撰写每周开源热点解读。

## 本周（第 {week_str} 期）背景
时间范围：{datetime.now().strftime("%Y-%m-%d")} 起过去一周

## 本周热门项目 TOP 20
{repo_list}

## 写作要求
请撰写一期《AI开源周报》，包含：

### 一、本周热点 TOP 5 深度解读
从上述列表中选5个最有影响力的项目，每个写 150-200 字，包含：
- 项目是什么、解决什么问题
- 为何这周受关注（技术突破/市场热点/大厂动作）
- 对中国开发者的参考价值

### 二、开源风向标
总结本周开源社区3个值得关注的趋势，每个趋势写 80-100 字

### 三、一句话点评
对 TOP 10 项目各写一句精炼点评（不超过30字）

### 四、本周优质资源推荐
推荐3个学习资源（博客/文档/视频），每个写 50 字简介

格式要求：
- 使用 Markdown
- 使用中文
- 标题层级清晰
- 结尾附上「下期预告」
"""
    return prompt

def generate_with_minimax(prompt, model="MiniMax-M2.7"):
    """调用 MiniMax API 生成内容"""
    if not MINIMAX_API_KEY:
        print("⚠️ MINIMAX_API_KEY 未设置，返回占位内容")
        return f"# AI开源周报\n\n（API Key 未配置，内容待生成）\n\n## 本周热门项目\n\n共抓取 0 个项目。\n"

    import urllib.request
    import urllib.parse
    
    url = f"{MINIMAX_API_HOST}/v1/text/chatcompletion_pro"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一位专业的 AI/开源技术观察者，擅长撰写高质量技术解读文章。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MINIMAX_API_KEY}"
        },
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]

def generate_weekly(week_str, repos):
    """生成完整周报"""
    print(f"正在生成第 {week_str} 期周报...")
    
    prompt = build_prompt(repos, week_str)
    content = generate_with_minimax(prompt)
    
    # 格式化输出
    header = f"""---
title: "AI开源周报 · 第 {week_str} 期"
date: {datetime.now().strftime("%Y-%m-%d")}
draft: false
tags:
  - AI
  - 开源
  - 周报
description: "AI 与开源领域热点每周中文解读"
---

# 🤖 AI开源周报 · 第 {week_str} 期

> 本周发行日期：{datetime.now().strftime("%Y年%m月%d日")}  
> 编辑整理：OpenClaw AI 助手  
> 投稿/反馈：[GitHub Issues](https://github.com/lanxinAIhub/ai-weekly/issues)

---

{content}

---

*本周报由 OpenClaw 提供 AI 生成支持 · 每周日更新*
"""
    
    return header

if __name__ == "__main__":
    week_arg = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-W%W")
    output_dir = sys.argv[2] if len(sys.argv) > 2 else f"/tmp/ai-weekly/issues/{week_arg}"
    
    os.makedirs(output_dir, exist_ok=True)
    data = load_data()
    content = generate_weekly(week_arg, data)
    
    output_path = f"{output_dir}/README.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ 周报已生成：{output_path}")
