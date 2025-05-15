from typing import Dict, List, Any
from langchain.chains.base import Chain
from pydantic import Field
from langchain.chains import TransformChain
from langchain.schema.runnable import RunnableSequence
from tools.translation_tool import TranslationTool

class TranslationChain(Chain):
    """处理翻译请求的链"""
    
    translation_tool: TranslationTool = Field(default_factory=TranslationTool)
    
    @property
    def input_keys(self) -> List[str]:
        """链的输入键"""
        return ["text", "source_language", "target_language", "context", "use_terminology"]
    
    @property
    def output_keys(self) -> List[str]:
        """链的输出键"""
        return ["translated_text", "detected_language", "terminology_matches"]
    
    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """运行链
        
        Args:
            inputs: 包含翻译输入的字典
            
        Returns:
            包含翻译结果的字典
        """
        # 提取输入
        text = inputs["text"]
        source_language = inputs.get("source_language", "auto")
        target_language = inputs.get("target_language", "en")
        context = inputs.get("context", [])
        use_terminology = inputs.get("use_terminology", True)
        
        # 运行翻译工具
        result = self.translation_tool._run(
            text=text,
            source_language=source_language,
            target_language=target_language,
            context=context,
            use_terminology=use_terminology
        )
        
        return result
    
    async def _acall(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """_call的异步版本"""
        # 提取输入
        text = inputs["text"]
        source_language = inputs.get("source_language", "auto")
        target_language = inputs.get("target_language", "en")
        context = inputs.get("context", [])
        use_terminology = inputs.get("use_terminology", True)
        
        # 运行翻译工具
        result = await self.translation_tool._arun(
            text=text,
            source_language=source_language,
            target_language=target_language,
            context=context,
            use_terminology=use_terminology
        )
        
        return result

def create_translation_chain() -> TranslationChain:
    """创建并返回翻译链
    
    Returns:
        已配置的TranslationChain
    """
    return TranslationChain(translation_tool=TranslationTool()) 