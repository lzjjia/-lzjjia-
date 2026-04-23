# ATLAS - 多智能体学术助手（持续更新中！！！）

ATLAS 是一个基于 LangGraph 的命令行学术学习助手。它会先根据你的请求进行“路由”，再交给对应的专业 Agent 输出学习计划、结构化笔记或学习建议，并支持工具调用与流式输出。

## 功能概览

- 协调者（Coordinator）：判断你的请求应该交给哪个专业 Agent
- 计划专家（Planner）：生成学习计划（周计划表 + 复习节点 + 方法建议）
- 笔记专家（NoteWriter）：整理学习内容并可保存为本地 Markdown 笔记
- 学习顾问（Advisor）：结合学生档案与对话历史给出针对性建议
- 工具：
  - Tavily 搜索工具（需要 `TAVILY_API_KEY`）
  - 本地笔记存储（写入 `notes/` 目录）

## 目录结构

- [main.py](file:///e:/agent_learning/ATLAS/main.py)：程序入口
- [ui/cli.py](file:///e:/agent_learning/ATLAS/ui/cli.py)：命令行交互与流式输出
- [graph/workflow.py](file:///e:/agent_learning/ATLAS/graph/workflow.py)：LangGraph 工作流构建与路由
- [graph/state.py](file:///e:/agent_learning/ATLAS/graph/state.py)：全局状态定义（AtlasState / StudentProfile）
- [agents/](file:///e:/agent_learning/ATLAS/agents)：各专业 Agent
- [tools/](file:///e:/agent_learning/ATLAS/tools)：工具（搜索、笔记、流式 callback）
- [config/llm_config.py](file:///e:/agent_learning/ATLAS/config/llm_config.py)：LLM 配置与环境变量加载
- [requirements.txt](file:///e:/agent_learning/ATLAS/requirements.txt)：Python 依赖

## 环境要求

- Windows（当前项目在 Windows 环境开发）
- Python 3.10+
- 推荐使用 conda 环境

## 安装依赖

在项目根目录执行：

```powershell
python -m pip install -r requirements.txt
```

## 配置环境变量（.env）

项目使用 `python-dotenv` 读取 `.env`。你需要配置：

### 1) DashScope（通义千问，OpenAI 兼容接口）

当前代码使用 `langchain_openai.ChatOpenAI`，你可以用 OpenAI 兼容变量名保证 SDK 识别：

```env
OPENAI_API_KEY="你的DashScope Key"
OPENAI_API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

如果你希望保留自定义变量名（例如 `DASHSCOPE_API_KEY`），需要保证代码里读取并正确传给 `ChatOpenAI`（以你当前安装的 `langchain-openai` 版本为准）。

### 2) Tavily 搜索（可选）

搜索工具需要：

```env
TAVILY_API_KEY="你的Tavily Key"
```

## 运行

在项目根目录执行：

```powershell
python main.py
```

启动后会先引导你填写学生档案，然后进入多轮对话；输入 `quit/exit/退出/q` 退出。

## 笔记输出

当走到笔记专家并触发保存工具时，会在 `notes/` 下生成 Markdown 文件，命名包含课程与时间戳。

## 常见报错与处理

### 1) `OpenAIError: ... set OPENAI_API_KEY ...`

原因：OpenAI SDK 没拿到 API Key。  
处理：确保 `.env` 中存在 `OPENAI_API_KEY`（以及需要时的 `OPENAI_API_BASE`），并确认程序运行时有加载到 `.env`。

### 2) `ImportError: cannot import name ... from langchain.agents`

原因：LangChain API 在不同版本之间有变动，某些函数在你的安装版本里不存在或不从该模块导出。  
处理：对齐 `requirements.txt` 中的依赖版本范围，或调整导入路径以匹配当前版本。

### 3) `.env 已写但运行仍读取不到`

处理建议：

```powershell
python -c "import os,dotenv; dotenv.load_dotenv(); print('OPENAI_API_KEY?', bool(os.getenv('OPENAI_API_KEY'))); print('OPENAI_API_BASE', os.getenv('OPENAI_API_BASE'))"
```

