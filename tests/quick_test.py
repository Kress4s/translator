#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速测试脚本 - 可以根据需要修改text和其他参数进行快速测试
"""

import json

import requests

# 服务器URL
URL = "http://localhost:8000/translate"

# 要翻译的文本 (修改这里进行不同的测试)
TEXT = "人工智能和机器学习技术正在快速发展，为各行各业带来变革。"
SOURCE_LANGUAGE = "auto"  # 可选: "zh", "en", "auto"
TARGET_LANGUAGE = "en"  # 可选: "zh", "en"


def run_test():
    """运行单一翻译测试"""
    print(f"🔤 原始文本: {TEXT}")
    print(f"📌 源语言: {SOURCE_LANGUAGE}, 目标语言: {TARGET_LANGUAGE}")

    # 准备请求数据
    data = {
        "text": TEXT,
        "source_language": SOURCE_LANGUAGE,
        "target_language": TARGET_LANGUAGE,
        "use_terminology": True,
    }

    # 发送请求
    try:
        response = requests.post(URL, json=data)
        result = response.json()

        # 打印结果
        print("\n" + "=" * 50)
        print(f"📒result原文: {result}")
        print(f"✅ 翻译结果: {result['translated_text']}")

        if result.get("detected_language"):
            print(f"🔍 检测到的语言: {result['detected_language']}")

        if result.get("terminology_matches") and len(result["terminology_matches"]) > 0:
            print("\n📚 匹配到的术语:")
            for term in result["terminology_matches"]:
                print(f"  • {term['term']} ➜ {term['translation']}")

        print("=" * 50)

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        if hasattr(response, "text"):
            print(f"响应内容: {response.text}")


if __name__ == "__main__":
    print("🚀 开始快速翻译测试...\n")

    # 检查API服务是否运行
    try:
        health_check = requests.get("http://localhost:8000/health")
        if health_check.status_code == 200:
            run_test()
        else:
            print("❌ API服务未正常响应，请确保服务已启动")
    except Exception as e:
        print(f"❌ 无法连接到API服务: {str(e)}")
        print("请确保翻译服务已启动，并在http://localhost:8000运行")
