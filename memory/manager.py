"""
记忆管理器
负责：
  1. extract_and_save：对话结束后，用 LLM 判断哪些内容值得记住，存入 SQLite
  2. recall：对话开始前，取出历史记忆，格式化成字符串注入 Prompt
"""
import os
from langchain_openai import ChatOpenAI
from memory.database import save_memory, get_memories
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    return ChatOpenAI(
        model="qwen-plus",
        openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        streaming=False,
        temperature=0,
    )

async def extract_and_save(
    student: str,
    user_input: str,
    agent_response: str
):
    """
    对话结束后调用
    让 LLM 判断这轮对话里有没有值得长期记住的信息
    如果有，提取出来存入数据库
    """
    llm = get_llm()
    
    prompt = f"""你是一个记忆提取助手。分析下面这段对话，判断是否有值得长期记住的学生信息。

值得记住的信息包括：
- 学生表达的学习困难或薄弱点（如"我对指针一直不理解"）
- 学生完成的学习里程碑（如"我今天学完了Redis持久化"）
- 学生的偏好或习惯（如"我喜欢用思维导图学习"）
- 学生的目标（如"我要准备字节跳动的面试"）

不值得记住的信息：
- 普通的问答内容
- 已经在档案里有的基本信息

对话内容：
用户：{user_input}
助手：{agent_response[:500]}

如果有值得记住的信息，请用一句话概括，格式如下：
MEMORY: [一句话概括]
TYPE: [preference/progress/goal/weakness 四选一]

如果没有值得记住的信息，只输出：
NONE"""

    response = await llm.ainvoke(prompt)
    content = response.content.strip()
    
    if content.startswith("NONE") or "MEMORY:" not in content:
        return  # 没有值得记住的内容，直接返回
    
    # 解析 LLM 的输出
    lines = content.split("\n")
    memory_text = ""
    memory_type = "general"
    
    for line in lines:
        if line.startswith("MEMORY:"):
            memory_text = line.replace("MEMORY:", "").strip()
        elif line.startswith("TYPE:"):
            memory_type = line.replace("TYPE:", "").strip()
    
    if memory_text:
        save_memory(student, memory_text, memory_type)


def recall(student: str, limit: int = 8) -> str:
    """
    对话开始前调用
    取出最近的历史记忆，格式化成字符串
    返回空字符串表示没有历史记忆
    """
    memories = get_memories(student, limit=limit)
    
    if not memories:
        return ""
    
    lines = []
    for m in memories:
        date = m["created_at"][:10]  # 只取日期部分
        lines.append(f"  [{date}] ({m['memory_type']}) {m['content']}")
    
    return "\n".join(lines)