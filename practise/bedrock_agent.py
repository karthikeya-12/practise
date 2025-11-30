from langchain_aws import BedrockLLM as BL
from dotenv import load_dotenv
import logging
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import MessagesState
from langchain_core.exceptions import LangChainException
from langchain_core.messages import (
    AIMessage as AM,
    HumanMessage as HM
)
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

llm = BL(model_id="qwen.qwen3-32b-v1:0", region_name="us-east-1")


class State(BaseModel):
    query: str


class Agent:
    def chat(self, state: MessagesState):
        logger.info("In chat node")
        try:
            res = llm.invoke(state["messages"][-1].content)
            return {"messages": [AM(content=res.content)]}
        except LangChainException as e:
            logger.error(str(e))
            return {"messages": [AM(content=str(e))]}

    def compile(self):
        flow = StateGraph(MessagesState)
        flow.add_node("chat", self.chat)
        flow.add_edge(START, "chat")
        flow.add_edge("chat", END)
        graph = flow.compile()
        return graph


agent = Agent().compile()


@app.post("/chat")
def invoke(query: State):
    try:
        if isinstance(query.query, str):
            res = agent.invoke({"messages": [HM(content=query.query)]})
            return JSONResponse(content={"response": res["messages"][-1].content}, status_code=200)
        else:
            raise ValueError("Entere payload is wrong")
    except Exception as e:
        logger.error(str(e))
        raise e
