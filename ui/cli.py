import asyncio
import sys
from graph.workflow import build_atlas_graph
from graph.state import AtlasState, StudentProfile
from tools.streaming import StreamingCallback

AGENT_LABELS = {
    "planner":    "📅 计划专家",
    "notewriter": "📝 笔记专家",
    "advisor":    "💡 学习顾问",
}

TOOL_LABELS = {
    "tavily_search_results_json": "🔍 搜索中",
    "TavilySearch":               "🔍 搜索中",
    "tavily_search":              "🔍 搜索中",
    "save_note_tool":             "💾 保存笔记",
    "list_notes_tool":            "📂 查看笔记",
}

def collect_student_profile() -> StudentProfile:
    print("\n=== ATLAS 学生档案初始化 ===")
    name = input("你的名字：")
    print("\n学习风格:")
    print("1. visual  (视觉型)")
    print("2. reading (阅读型)")
    print("3. auditory(听觉型)")
    style_map = {"1": "visual", "2": "reading", "3": "auditory"}
    style = style_map.get(input("选择(1/2/3): "), "reading")
    print("\n精力高峰时段:")
    print("1. morning (早晨型)")
    print("2. evening (夜晚型)")
    energy_map = {"1": "morning", "2": "evening"}
    energy = energy_map.get(input("选择(1/2): "), "morning")
    courses_input = input("\n当前课程(用逗号分隔): ")
    courses = [c.strip() for c in courses_input.split(",") if c.strip()]
    challenges_input = input("主要挑战(用逗号分隔): ")
    challenges = [c.strip() for c in challenges_input.split(",") if c.strip()]
    return StudentProfile(
        name=name,
        learning_style=style,
        energy_pattern=energy,
        current_courses=courses or ["通识课程"],
        challenges=challenges or ["时间管理"]
    )


async def run_atlas():
    print("🎓 欢迎使用 ATLAS - 智能学术助手系统")
    print("=" * 50)

    atlas = build_atlas_graph()
    profile = collect_student_profile()
    messages = []

    print(f"\n✅ 档案已建立！你好，{profile['name']}！")
    print("💡 输入 'quit' 退出\n")

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！👋")
            break

        if user_input.lower() in ("quit", "exit", "退出", "q"):
            print("再见！祝学习顺利！👋")
            break
        if not user_input:
            continue

        # ── 每轮对话新建 queue 和 callback ──────────
        queue = asyncio.Queue()
        callback = StreamingCallback(queue)

        state: AtlasState = {
            "student_profile": profile,
            "user_input": user_input,
            "messages": messages,
            "coordinator_decision": "",
            "study_schedule": "",
            "study_notes": "",
            "advisor_feedback": "",
            "final_response": "",
            "next_agent": "",
            "iteration": 0,
            "callbacks": [callback],   # ✅ 注入 callback
        }

        print("\n⏳ ATLAS 思考中...", end="", flush=True)
        header_printed = False
        full_response = ""

        # ── 并发：图的执行 + token消费 ──────────────
        async def run_graph():
            """在后台运行图，完成后发送结束信号"""
            result = await atlas.ainvoke(state)
            await queue.put(("done", result))

        async def consume_stream():
            """从队列消费事件并打印"""
            nonlocal header_printed, full_response
            agent_used = ""

            while True:
                item = await queue.get()
                event_type = item[0]

                if event_type == "done":
                    # 图执行完毕，取最终结果
                    result = item[1]
                    agent_used = result.get("next_agent", "")
                    if not full_response:
                        full_response = result.get("final_response", "")
                        # 没有流式输出时回退到一次性打印
                        label = AGENT_LABELS.get(agent_used, agent_used.upper())
                        sys.stdout.write("\r" + " " * 30 + "\r")
                        print(f"\nATLAS [{label}]")
                        print("─" * 40)
                        print(full_response)
                        print("─" * 40)
                    break

                elif event_type == "token":
                    token = item[1]
                    if not header_printed:
                        # 第一个token到来时才打印标题
                        sys.stdout.write("\r" + " " * 30 + "\r")
                        # 此时还不知道是哪个agent，先用通用标题
                        print("\nATLAS 回复中...")
                        print("─" * 40)
                        header_printed = True
                    print(token, end="", flush=True)
                    full_response += token

                elif event_type == "tool_start":
                    tool_name = item[1]
                    tool_input = item[2] if len(item) > 2 else ""
                    label = TOOL_LABELS.get(tool_name, f"⚙ {tool_name}")
                    query = ""
                    if isinstance(tool_input, dict):
                        query = tool_input.get("query", "")
                    elif isinstance(tool_input, str):
                        query = tool_input[:40]
                    query_display = f"：{query[:35]}" if query else ""
                    print(f"\n  {label}{query_display}")

                elif event_type == "tool_end":
                    print()  # 工具结束换行

                elif event_type == "llm_end":
                    if header_printed:
                        print(f"\n{'─' * 40}\n")

        # 并发执行图和流消费
        try:
            await asyncio.gather(run_graph(), consume_stream())
        except Exception as e:
            print(f"\n❌ 出错了：{e}")
            continue

        # 更新对话历史
        if full_response:
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": full_response})