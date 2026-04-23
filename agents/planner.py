from langchain.agents import create_agent
from config.llm_config import get_llm
from tools.search_tool import get_search_tool
from graph.state import AtlasState

PLANNER_SYSTEM_PROMPT = """你是ATLAS的学习计划专家。
你可以使用搜索工具查找高效学习方法、课程学习路径、时间管理技巧。
输出格式：每周时间表（表格）+ 关键复习节点 + 学习方法建议。
"""

async def planner_node(state: AtlasState) -> AtlasState:
    callbacks = state.get("callbacks", [])
    llm = get_llm(callbacks=callbacks)

    agent = create_agent(
        model=llm,
        tools=[get_search_tool()],
        system_prompt=PLANNER_SYSTEM_PROMPT,
    )

    profile = state["student_profile"]
    full_input = (
        f"[学生档案]\n"
        f"  姓名: {profile.get('name', '未知')}\n"
        f"  精力模式: {profile.get('energy_pattern', 'morning')}\n"
        f"  当前课程: {', '.join(profile.get('current_courses', []))}\n"
        f"  主要挑战: {', '.join(profile.get('challenges', []))}\n\n"
        f"[学生请求]\n{state['user_input']}"
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": full_input}]}
    )
    output = result["messages"][-1].content

    return {**state, "study_schedule": output, "final_response": output}