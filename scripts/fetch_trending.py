#!/usr/bin/env python3
"""
AI开源周报 - GitHub Trending 数据抓取
抓取指定时间段内的 AI/开源 相关热门项目
"""

import requests
import json
from datetime import datetime, timedelta

GITHUB_TOKEN = open("/home/lanxin/.github_token").read().strip()
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def search_ai_repos(created_within_days=7, limit=50):
    """搜索近N天内创建的AI相关仓库"""
    query = "AI OR artificial-intelligence OR LLM OR machine-learning in:name,description,readme"
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limit
    }
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()["items"]

def get_trending(lang="Python", days=7, limit=30):
    """获取指定语言的Trending仓库"""
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    url = f"https://api.github.com/search/repositories"
    params = {
        "q": f"language:{lang} created:>{since}",
        "sort": "stars",
        "order": "desc",
        "per_page": limit
    }
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()["items"]

def get_repo_details(owner, repo):
    """获取仓库详细信息"""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def fetch_weekly_data():
    """抓取本周热点数据"""
    print("正在抓取 GitHub AI 相关热门项目...")
    
    repos = search_ai_repos(created_within_days=7, limit=50)
    
    data = []
    for r in repos:
        owner = r["owner"]["login"]
        name = r["name"]
        try:
            detail = get_repo_details(owner, name)
            data.append({
                "name": name,
                "full_name": detail["full_name"],
                "description": detail["description"],
                "url": detail["html_url"],
                "stars": detail["stargazers_count"],
                "forks": detail["forks_count"],
                "language": detail["language"],
                "topics": detail.get("topics", []),
                "created_at": detail["created_at"],
                "pushed_at": detail["pushed_at"],
                "open_issues": detail["open_issues_count"],
                "license": detail.get("license", {}).get("spdx_id"),
                "owner_type": detail["owner"]["type"],
            })
        except Exception as e:
            print(f"  获取 {owner}/{name} 详情失败: {e}")
    
    # 按 stars 排序
    data.sort(key=lambda x: x["stars"], reverse=True)
    
    output_path = "/tmp/ai-weekly-data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 抓取完成，共 {len(data)} 个项目，已保存至 {output_path}")
    return data

if __name__ == "__main__":
    fetch_weekly_data()
