from langchain.agents import create_agent
from config.llm_config import get_llm
from graph.state import AtlasState

llm = get_llm()

COORDINATOR_SYSTEM_PROMPT = """你是ATLAS系统的协调者，负责分析学生请求并决定路由。

根据用户输入，判断应该交给哪个专业Agent处理：
- 如果需要制定学习计划、时间安排、复习策略 → 回复 ROUTE: planner
- 如果需要整理笔记、总结内容、处理学习材料 → 回复 ROUTE: notewriter  
- 如果需要学习建议、解答疑惑、心理支持     → 回复 ROUTE: advisor

你的回复必须包含 ROUTE: <agent_name> 这一行。
"""

# 新版 create_agent：不需要 AgentExecutor，不需要 Prompt 模板
coordinator_agent = create_agent(
    model=llm,
    tools=[],           # coordinator 不需要工具，只负责路由
    system_prompt=COORDINATOR_SYSTEM_PROMPT,
)

async def coordinator_node(state: AtlasState) -> AtlasState:
    profile = state["student_profile"]
    user_input = state["user_input"]

    # 把学生档案也带进去
    full_input = f"学生档案: {profile}\n\n学生请求: {user_input}"

    result = await coordinator_agent.ainvoke(
        {"messages": [{"role": "user", "content": full_input}]}
    )

    # 提取最后一条 AI 消息
    content = result["messages"][-1].content

    # 解析路由
    next_agent = "advisor"  # 默认
    if "ROUTE: planner" in content:
        next_agent = "planner"
    elif "ROUTE: notewriter" in content:
        next_agent = "notewriter"
    elif "ROUTE: advisor" in content:
        next_agent = "advisor"

    return {
        **state,
        "coordinator_decision": content,
        "next_agent": next_agent,
    }