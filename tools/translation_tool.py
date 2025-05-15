from typing import Any, ClassVar, Dict, List, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from utils.terminology_db import TerminologyDatabase
from utils.tongyi_utils import (
    call_tongyi_api,
    create_tongyi_messages,
    detect_language,
    extract_translation,
)


class TranslationInput(BaseModel):
    """翻译工具的输入"""

    text: str = Field(description="要翻译的文本")
    source_language: str = Field(
        default="auto", description="源语言代码（'en'、'zh'或'auto'）"
    )
    target_language: str = Field(description="目标语言代码（'en'或'zh'）")
    context: Optional[List[Dict[str, str]]] = Field(
        default=None, description="用于上下文一致性的先前翻译"
    )
    use_terminology: bool = Field(default=True, description="是否使用术语数据库")


class TranslationTool(BaseTool):
    """使用通义千问API进行翻译的工具"""

    name: ClassVar[str] = "translate"
    description: ClassVar[str] = "在语言之间翻译文本，保持上下文和术语一致性"
    args_schema: Type[BaseModel] = TranslationInput

    # 添加terminology_db作为模型字段
    terminology_db: Any = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.terminology_db = TerminologyDatabase()

    def _run(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "en",
        context: Optional[List[Dict[str, str]]] = None,
        use_terminology: bool = True,
    ) -> Dict[str, Any]:
        """执行翻译

        Args:
            text: 要翻译的文本
            source_language: 源语言代码（'en'、'zh'或'auto'）
            target_language: 目标语言代码（'en'或'zh'）
            context: 上下文翻译
            use_terminology: 是否使用术语数据库

        Returns:
            包含翻译结果的字典
        """
        # 如果需要，自动检测语言
        detected_language = None
        if source_language == "auto":
            detected_language = detect_language(text)
            source_language = detected_language

        # 如果启用，查找术语匹配
        terminology_matches = []
        if use_terminology and self.terminology_db:
            terminology_matches = self.terminology_db.batch_search(text)

        # 为API创建消息
        messages = create_tongyi_messages(
            text=text,
            source_language=source_language,
            target_language=target_language,
            context=context,
            terminology=terminology_matches,
        )

        # 调用API
        response = call_tongyi_api(messages)

        # 提取翻译
        translated_text = extract_translation(response)

        # 返回结果
        return {
            "translated_text": translated_text,
            "detected_language": detected_language,
            "terminology_matches": terminology_matches,
        }

    async def _arun(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "en",
        context: Optional[List[Dict[str, str]]] = None,
        use_terminology: bool = True,
    ) -> Dict[str, Any]:
        """_run的异步版本"""
        return self._run(
            text=text,
            source_language=source_language,
            target_language=target_language,
            context=context,
            use_terminology=use_terminology,
        )
