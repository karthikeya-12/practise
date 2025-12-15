from dotenv import load_dotenv

load_dotenv()
import asyncio
import json
import logging
from contextlib import asynccontextmanager

from my_project.agents import Agent
from fastapi import (
    APIRouter,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from fastapi.responses import StreamingResponse
from langchain_core.messages import (
    AIMessage as AM,
)
from langchain_core.messages import (
    HumanMessage as HM,
)
from my_project.models import Struct

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


@router.websocket("/backend/llm/api/websocket/testing")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    logger.info("Websocket is connected!")
    try:
        while True:
            data = await websocket.receive_json()
            send = data["query"]
            await websocket.send_json({"data": send})
    except WebSocketDisconnect as e:
        logger.error(str(e))
        await websocket.close()
    except WebSocketException as e:
        logger.error(str(e))
        await websocket.close()
    except Exception as e:
        logger.error(str(e))
        await websocket.close()


@router.websocket("/backend/llm/api/websocket/chat")
async def websocket_chats(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            user_query = data.get("query")

            if not user_query:
                await websocket.send_json({"error": "Missing 'query' field"})
                continue

            queue = asyncio.Queue()

            messages = [HM(content=user_query)]

            async def run_llm():
                try:
                    res = await graph.ainvoke({"messages": messages, "queue": queue})

                    final_output = res["messages"][-1].content
                    await websocket.send_json({"final": final_output})
                except Exception as e:
                    await websocket.send_json({"error": str(e)})
                finally:
                    await queue.put(None)

            asyncio.create_task(run_llm())

            while True:
                event = await queue.get()
                if event is None:
                    break
                await websocket.send_json({"token": event.get("message")})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))
