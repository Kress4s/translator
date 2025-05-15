# GPT 翻译插件

一个基于LangChain和阿里云通义千问API的GPT翻译插件。

## 功能特点
- 中英双向翻译
- 术语库匹配与一致性维护
- 上下文感知翻译
- 基于向量的术语查询

## 安装配置

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 在.env文件中配置阿里云通义千问API密钥：
```
DASHSCOPE_API_KEY={{YOUR_DASHSCOPE_API_KEY}}
```

3. 启动服务器：
```bash
python app.py
```

4. 向ChatGPT注册插件

## 项目结构
- `app.py`: 主FastAPI应用程序
- `ai_plugin.json`: 插件清单
- `.well-known/`: OpenAPI规范
- `chains/`: LangChain组件
- `tools/`: 自定义LangChain工具
- `utils/`: 实用工具函数
- `data/`: 术语数据库 