from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter, HTTPException
import logging
from fastapi.responses import StreamingResponse
import json
from agents import Agent
from langchain_core.messages import (
    HumanMessage as HM,
    AIMessage as AM,
)
from models import Struct
import asyncio
from contextlib import asynccontextmanager
graph = None
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_graph(app: APIRouter):
    global graph
    graph = await Agent().compile()
    yield

router = APIRouter(lifespan=get_graph)


# @router.post("/backend/llm/api/chat")
async def chat(req: Struct, queue: asyncio.Queue):
    logger.info("In chat endpoint")
    try:
        messages = [HM(content=req.query)]
        res = await graph.ainvoke({"messages": messages, "queue": queue})
        messages.append(AM(content=res["messages"][-1].content))
        await queue.put({"message": res["messages"][-1].content})
        """ logger.info("response generated")
        if isinstance(res["messages"][-1], AM) and res["messages"][-1].content:
            return JSONResponse(content={"response": res["messages"][-1].content})
        else:
            raise ValueError("No response was generated") """
    except Exception as e:
        return HTTPException(detail=str(e), status_code=500)
    finally:
        await queue.put(None)


async def handler(queue: asyncio.Queue):
    while True:
        event = await queue.get()
        if event is None:
            break
        yield f"data: {json.dumps(event)}\n\n"


@router.post("/backend/llm/api/chat")
async def chat_handler(req: Struct):
    queue = asyncio.Queue()
    asyncio.create_task(chat(req, queue))
    return StreamingResponse(handler(queue=queue), media_type="text/event-stream")
