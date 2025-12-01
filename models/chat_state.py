from langgraph.graph.message import MessagesState
from typing_extensions import Optional, TypedDict
import asyncio


class AgentState(MessagesState, TypedDict):
    queue: Optional[asyncio.Queue]
