import os
import dotenv 
from langchain_openai import ChatOpenAI

#读取配置文件
dotenv.load_dotenv()

def get_llm(callbacks=None):
    """
    通过openai兼容接口接入qwen-plus
    阿里云DashScope完全兼容Openai SDK
    """
    return ChatOpenAI(
        model_name = "qwen-plus",
        api_key = os.getenv("DASHSCOPE_API_KEY"),
        base_url = os.getenv("DASHSCOPE_BASE_URL"),
        temperature=0.7,
        streaming=True,
        callbacks=callbacks or [],
    )