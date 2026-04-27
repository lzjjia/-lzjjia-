from langchain.agents import create_agent
from config.llm_config import get_llm
from tools.search_tool import get_search_tool
from graph.state import AtlasState
from tools.rag_tool import search_textbook, search_my_notes
from memory.manager import recall

PLANNER_SYSTEM_PROMPT = """你是ATLAS的学习计划专家。

【工具使用优先级】
1. search_my_notes  → 了解已完成的学习进度
2. search_textbook  → 了解教材章节结构，安排合理顺序
3. tavily_search    → 搜索高效学习方法

输出：当前进度评估 + 剩余内容清单 + 每周时间表。
"""

async def planner_node(state: AtlasState) -> AtlasState:
    callbacks = state.get("callbacks", [])
    llm = get_llm(callbacks=callbacks)

    agent = create_agent(
        model=llm,
        tools=[
            search_my_notes,
            search_textbook,
            get_search_tool()
            ],
        system_prompt=PLANNER_SYSTEM_PROMPT,
    )

    profile = state["student_profile"]
    name  = profile.get("name","未知")
    #召回长期记忆
    long_term_memory = recall(name)
    memory_section = ""
    if long_term_memory:
        memory_section = f"\n[历史记忆]\n{long_term_memory}\n"
    full_input = (
        f"[学生档案]\n"
        f"  姓名: {name}\n"
        f"  精力模式: {profile.get('energy_pattern', 'morning')}\n"
        f"  当前课程: {', '.join(profile.get('current_courses', []))}\n"
        f"  主要挑战: {', '.join(profile.get('challenges', []))}\n\n"
        f'{memory_section}\n'
        f"[学生请求]\n{state['user_input']}"
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": full_input}]}
    )
    output = result["messages"][-1].content

    return {**state, "study_schedule": output, "final_response": output}