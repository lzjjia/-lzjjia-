from langchain.agents import create_agent
from config.llm_config import get_llm
from tools.search_tool import get_search_tool
from graph.state import AtlasState
from memory.manager import recall, extract_and_save
from tools.rag_tool import search_textbook, search_my_notes
ADVISOR_SYSTEM_PROMPT = """你是ATLAS的学习顾问。

【工具使用优先级】
1. search_my_notes  → 了解学生已掌握内容和知识盲区
2. search_textbook  → 查看教材对应章节，给出针对性建议
3. tavily_search    → 搜索通用学习方法

回答时要结合学生的笔记和教材内容，而不是泛泛而谈。
"""

async def advisor_node(state: AtlasState) -> AtlasState:
    # 从 state 里取出 callback（由 CLI 注入）
    callbacks = state.get("callbacks", [])
    llm = get_llm(callbacks=callbacks)

    agent = create_agent(
        model=llm,
        tools=[
            search_my_notes,
            search_textbook,
            get_search_tool()
            ],
        system_prompt=ADVISOR_SYSTEM_PROMPT,
    )

    profile = state["student_profile"]
    name = profile.get('name', '未知')
    history = state.get("messages", [])[-6:]
    messages = list(history)
    long_term_memory = recall(name)
    memory_section = ""
    if long_term_memory:
        memory_section = f"\n[长期记忆 - 关于这位学生你应该知道的]\n{long_term_memory}"
    
    current = (
        f"[学生档案]\n"
        f"  姓名: {name}\n"
        f"  学习风格: {profile.get('learning_style', '')}\n"
        f"  精力模式: {profile.get('energy_pattern', '')}\n"
        f"  当前课程: {', '.join(profile.get('current_courses', []))}\n"
        f"  主要挑战: {', '.join(profile.get('challenges', []))}\n\n"
        f"{memory_section}\n"
        f"[学生问题]\n{state['user_input']}"
    )
    messages.append({"role": "user", "content": current})

    result = await agent.ainvoke({"messages": messages})
    output = result["messages"][-1].content
    await extract_and_save(
        student = name,
        user_input = state["user_input"],
        agent_response = output,
    )
    return {**state, "advisor_feedback": output, "final_response": output}