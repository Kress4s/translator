import json
import os
import time
from typing import Any, Dict, List, Optional

import dashscope
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def validate_credentials() -> bool:
    """验证阿里云凭证是否正确设置

    Returns:
        是否正确设置凭证
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key:
        return False

    # 为DashScope设置API凭证
    dashscope.api_key = api_key

    return True


def detect_language(text: str) -> str:
    """检测提供文本的语言

    Args:
        text: 要检测语言的文本

    Returns:
        语言代码 ('en' 或 'zh')
    """
    # 简化的启发式方法：检查是否存在中文字符
    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            return "zh"
    return "en"


def create_tongyi_messages(
    text: str,
    source_language: str,
    target_language: str,
    context: Optional[List[Dict[str, str]]] = None,
    terminology: Optional[List[Dict[str, str]]] = None,
) -> List[Dict[str, str]]:
    """为通义千问API创建消息格式

    Args:
        text: 要翻译的文本
        source_language: 源语言代码 ('en'、'zh' 或 'auto')
        target_language: 目标语言代码 ('en' 或 'zh')
        context: 上下文的先前翻译
        terminology: 要使用的术语匹配

    Returns:
        格式化的通义千问API消息
    """
    # 如果需要，自动检测语言
    if source_language == "auto":
        source_language = detect_language(text)

    # 基础系统提示词
    system_content = f"""你是一位专业翻译，专门从事{source_language}到{target_language}的翻译。
准确翻译提供的文本，同时保持原始含义、语调和格式。
"""

    # 如果有术语指导，则添加
    if terminology and len(terminology) > 0:
        terms_str = "\n".join(
            [f"- {item['term']}: {item['translation']}" for item in terminology]
        )
        system_content += f"\n在翻译中请一致使用以下术语：\n{terms_str}\n"

    # 如果有上下文指导，则添加
    if context and len(context) > 0:
        context_str = "\n".join(
            [f"'{item['source']}' 被翻译为 '{item['target']}'" for item in context]
        )
        system_content += f"\n请与这些先前的翻译保持一致：\n{context_str}\n"

    messages = [
        {"role": "system", "content": system_content},
        {
            "role": "user",
            "content": f"请将此文本从{source_language}翻译成{target_language}：\n\n{text}",
        },
    ]

    return messages


def call_tongyi_api(
    messages: List[Dict[str, str]], max_retries: int = 3
) -> Dict[str, Any]:
    """调用通义千问API，包含重试逻辑

    Args:
        messages: 发送到API的消息
        max_retries: 最大重试次数

    Returns:
        API响应
    """
    retry_count = 0
    backoff_time = 1

    while retry_count < max_retries:
        try:
            response = dashscope.Generation.call(
                model="qwen-plus",
                messages=messages,
                result_format="message",
                temperature=0.3,  # 较低的温度以提高翻译准确性
                max_tokens=4096,
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "content": response.output.choices[0].message.content,
                    "usage": response.usage,
                }
            else:
                print(f"API错误：{response.code} - {response.message}")

        except Exception as e:
            print(f"调用通义API时出错：{str(e)}")

        # 指数退避
        print(f"{backoff_time}秒后重试...")
        time.sleep(backoff_time)
        backoff_time *= 2
        retry_count += 1

    return {"success": False, "error": "超出最大重试次数"}


def extract_translation(response: Dict[str, Any]) -> str:
    """从API响应中提取翻译文本

    Args:
        response: API响应

    Returns:
        翻译后的文本
    """
    if not response["success"]:
        raise Exception(f"翻译失败：{response.get('error', '未知错误')}")

    return response["content"]
