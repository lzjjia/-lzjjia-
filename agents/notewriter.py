from langchain.agents import create_agent
from langchain.tools import tool
from config.llm_config import get_llm
from tools.search_tool import get_search_tool
from tools.notes_tool import save_note, list_notes
from graph.state import AtlasState
from tools.rag_tool import search_textbook, search_my_notes

@tool
async def save_note_tool(course: str, title: str, content: str) -> str:
    """将整理好的学习笔记保存到本地文件。整理完笔记后主动调用此工具。"""
    filepath = await save_note(course, title, content)
    return f"✅ 笔记已保存至: {filepath}"

@tool
async def list_notes_tool(course: str = "") -> str:
    """列出已保存的笔记。当用户问'我有哪些笔记'时调用。"""
    notes = await list_notes(course if course else None)
    if not notes:
        return "暂无已保存的笔记。"
    lines = [f"  - {n['filename']} ({n['modified']})" for n in notes]
    return "📚 已保存的笔记:\n" + "\n".join(lines)

# ✅ 改动1：更新 system prompt，告诉 LLM 优先用哪个工具
NOTEWRITER_SYSTEM_PROMPT = """你是ATLAS的智能笔记专家。

【工具使用优先级】
1. search_my_notes  → 先检查学生是否已有相关笔记，避免重复
2. search_textbook  → 从学生上传的教材原文获取内容（最权威）
3. tavily_search    → 教材中没有时，再用网络补充
4. save_note_tool   → 整理完后必须保存

【笔记格式】Markdown，含核心概念、重点公式、举例、考点提示。
整理完成后必须调用 save_note_tool 保存。
"""

async def notewriter_node(state: AtlasState) -> AtlasState:
    callbacks = state.get("callbacks", [])
    llm = get_llm(callbacks=callbacks)

    agent = create_agent(
        model=llm,
        # ✅ 改动2：加入 search_my_notes 和 search_textbook
        tools=[
            search_my_notes,    # RAG：检索已有笔记
            search_textbook,    # RAG：检索教材原文
            get_search_tool(),  # 网络搜索兜底
            save_note_tool,
            list_notes_tool,
        ],
        system_prompt=NOTEWRITER_SYSTEM_PROMPT,
    )

    profile = state["student_profile"]

    
    full_input = (
        f"[学生档案]\n"
        f"  姓名: {profile.get('name', '未知')}\n"
        f"  课程: {', '.join(profile.get('current_courses', []))}\n\n"
        f"[请求]\n{state['user_input']}"
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": full_input}]}
    )
    output = result["messages"][-1].content

    return {**state, "study_notes": output, "final_response": output}