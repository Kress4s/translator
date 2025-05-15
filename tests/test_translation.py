#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import sys

# 服务器URL
URL = "http://localhost:8000/translate"

def print_result(response):
    """美化打印翻译结果"""
    try:
        result = response.json()
        print("\n" + "="*50)
        print(f"✅ 翻译结果: {result['translated_text']}")
        
        if result.get("detected_language"):
            print(f"🔍 检测到的语言: {result['detected_language']}")
        
        if result.get("terminology_matches") and len(result["terminology_matches"]) > 0:
            print("\n📚 匹配到的术语:")
            for term in result["terminology_matches"]:
                print(f"  • {term['term']} ➜ {term['translation']}")
        
        print("="*50 + "\n")
        return result
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        if hasattr(response, 'text'):
            print(f"响应内容: {response.text}")
        return None

def test_simple_en_to_zh():
    """测试简单的英译中"""
    print("\n🔤 测试简单英译中...")
    data = {
        "text": "Artificial intelligence and machine learning are transforming our world.",
        "source_language": "en",
        "target_language": "zh"
    }
    response = requests.post(URL, json=data)
    return print_result(response)

def test_simple_zh_to_en():
    """测试简单的中译英"""
    print("\n🔤 测试简单中译英...")
    data = {
        "text": "人工智能和机器学习正在改变我们的世界。",
        "source_language": "zh",
        "target_language": "en"
    }
    response = requests.post(URL, json=data)
    return print_result(response)

def test_auto_detect():
    """测试语言自动检测"""
    print("\n🔍 测试语言自动检测...")
    data = {
        "text": "深度学习是机器学习的一个子领域，它使用多层神经网络进行模式识别。",
        "source_language": "auto",
        "target_language": "en"
    }
    response = requests.post(URL, json=data)
    return print_result(response)

def test_with_terminology():
    """测试带术语库的翻译"""
    print("\n📚 测试术语库匹配...")
    data = {
        "text": "通义千问是阿里云推出的大模型，用于自然语言处理。",
        "source_language": "zh",
        "target_language": "en",
        "use_terminology": True
    }
    response = requests.post(URL, json=data)
    return print_result(response)

def test_with_context():
    """测试带上下文的翻译"""
    print("\n🔄 测试上下文翻译...")
    # 第一段翻译
    first_data = {
        "text": "LangChain框架使开发者能够创建由大型语言模型驱动的应用程序。",
        "source_language": "zh",
        "target_language": "en"
    }
    first_response = requests.post(URL, json=first_data)
    first_result = print_result(first_response)
    
    if not first_result:
        return None
    
    # 使用第一段的翻译作为上下文
    time.sleep(1)  # 稍作暂停，避免请求过快
    
    second_data = {
        "text": "这个框架提供了许多工具和链，简化了大模型应用的开发流程。",
        "source_language": "zh", 
        "target_language": "en",
        "context": [
            {
                "source": "LangChain框架",
                "target": "LangChain framework" if "LangChain framework" in first_result["translated_text"] else "LangChain"
            },
            {
                "source": "大型语言模型",
                "target": "large language models" if "large language models" in first_result["translated_text"].lower() else "LLMs"
            }
        ]
    }
    second_response = requests.post(URL, json=second_data)
    return print_result(second_response)

def test_complex_text():
    """测试复杂文本翻译"""
    print("\n📝 测试复杂文本翻译...")
    data = {
        "text": """向量数据库在大模型应用中扮演着重要角色。
它们能够存储文本的嵌入表示，并支持语义搜索功能。
常见的向量数据库包括Faiss、Pinecone和Milvus等。
这些工具与LangChain结合使用，可以增强大模型的上下文理解能力。""",
        "source_language": "zh",
        "target_language": "en"
    }
    response = requests.post(URL, json=data)
    return print_result(response)

def run_health_check():
    """检查API服务是否正常运行"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200 and response.json().get("status") == "健康":
            print("✅ API服务正常运行")
            return True
        else:
            print(f"❌ API服务返回异常状态: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到API服务: {str(e)}")
        return False

def main():
    """主函数，运行所有测试"""
    print("🚀 开始翻译服务测试...")
    
    # 检查API服务是否运行
    if not run_health_check():
        print("❌ 请确保翻译服务已启动，并在http://localhost:8000运行")
        sys.exit(1)
    
    # 运行所有测试
    tests = [
        test_simple_en_to_zh,
        test_simple_zh_to_en,
        test_auto_detect,
        test_with_terminology,
        test_with_context,
        test_complex_text
    ]
    
    for test in tests:
        try:
            test()
            time.sleep(1)  # 避免请求过快
        except Exception as e:
            print(f"❌ 测试出错: {str(e)}")
    
    print("\n✨ 所有测试完成!")

if __name__ == "__main__":
    main() 