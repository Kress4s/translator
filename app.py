import os
from typing import Dict, List, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chains.translation_chain import create_translation_chain
from utils.tongyi_utils import validate_credentials

# 加载环境变量
load_dotenv()

# 初始化FastAPI应用
app = FastAPI()

# 挂载静态文件
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 检查是否设置了凭证
if not validate_credentials():
    print("警告：通义千问API密钥未正确配置！请检查DASHSCOPE_API_KEY环境变量。")


# 请求模型
class TranslationRequest(BaseModel):
    text: str
    source_language: str = "auto"  # 'zh'、'en'或'auto'
    target_language: str
    context: Optional[List[Dict[str, str]]] = None
    use_terminology: bool = True


class TranslationResponse(BaseModel):
    translated_text: str
    detected_language: Optional[str] = None
    terminology_matches: Optional[List[Dict[str, str]]] = None


# 初始化翻译链
translation_chain = create_translation_chain()


@app.get("/")
async def root():
    return {"message": "翻译插件API正在运行"}


@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    try:
        # 通过LangChain处理翻译请求
        result = translation_chain.invoke(
            {
                "text": request.text,
                "source_language": request.source_language,
                "target_language": request.target_language,
                "context": request.context or [],
                "use_terminology": request.use_terminology,
            }
        )

        return result
    except Exception as e:
        print(f"翻译错误：{str(e)}")
        raise HTTPException(status_code=500, detail=f"翻译错误：{str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "健康"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
