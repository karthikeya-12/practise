from langchain_google_genai import ChatGoogleGenerativeAI as CG
from langchain_core.messages import (
    AIMessage as AM,
)
from langgraph.graph import StateGraph, END
from my_project.models import AgentState

# from dotenv import load_dotenv

# load_dotenv()
llm = CG(model="gemini-2.5-flash")


class Agent:
    async def chat(self, state: AgentState):
        res = await llm.ainvoke(state["messages"])
        if isinstance(res, AM):
            return {"messages": [AM(content=res.content)]}
        else:
            await state["queue"].put({"error": "Last message is not ai message"})

    async def compile(self):
        flow = StateGraph(AgentState)
        flow.set_entry_point("chat")
        flow.add_node("chat", self.chat)
        flow.add_edge("chat", END)
        graph = flow.compile()
        return graph
