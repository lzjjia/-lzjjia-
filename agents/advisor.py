from langchain.agents import create_agent
from config.llm_config import get_llm
from tools.search_tool import get_search_tool
from graph.state import AtlasState

ADVISOR_SYSTEM_PROMPT = """你是ATLAS的学习顾问，提供个性化学习建议和心理支持。

你可以用搜索工具查找：
- 针对具体挑战的学习策略
- 科学的记忆和专注方法
- 应对学业压力的技巧

回答要有针对性，结合学生的具体情况，不要泛泛而谈。
"""

async def advisor_node(state: AtlasState) -> AtlasState:
    # 从 state 里取出 callback（由 CLI 注入）
    callbacks = state.get("callbacks", [])
    llm = get_llm(callbacks=callbacks)

    agent = create_agent(
        model=llm,
        tools=[get_search_tool()],
        system_prompt=ADVISOR_SYSTEM_PROMPT,
    )

    profile = state["student_profile"]
    history = state.get("messages", [])[-6:]

    messages = list(history)
    current = (
        f"[学生档案]\n"
        f"  姓名: {profile.get('name', '未知')}\n"
        f"  学习风格: {profile.get('learning_style', '')}\n"
        f"  精力模式: {profile.get('energy_pattern', '')}\n"
        f"  当前课程: {', '.join(profile.get('current_courses', []))}\n"
        f"  主要挑战: {', '.join(profile.get('challenges', []))}\n\n"
        f"[学生问题]\n{state['user_input']}"
    )
    messages.append({"role": "user", "content": current})

    result = await agent.ainvoke({"messages": messages})
    output = result["messages"][-1].content

    return {**state, "advisor_feedback": output, "final_response": output}