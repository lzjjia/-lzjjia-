import asyncio
from langchain_core.callbacks.base import AsyncCallbackHandler

class StreamingCallback(AsyncCallbackHandler):
    """
    自定义异步 callback handler
    每当 LLM 生成一个 token，on_llm_new_token 就会被调用
    我们把 token 放进 asyncio.Queue，由 CLI 消费打印
    """
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_llm_new_token(self, token: str, **kwargs):
        await self.queue.put(("token", token))

    async def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name", "")
        await self.queue.put(("tool_start", tool_name, input_str))

    async def on_tool_end(self, output, **kwargs):
        await self.queue.put(("tool_end", ""))

    async def on_llm_end(self, response, **kwargs):
        await self.queue.put(("llm_end", ""))