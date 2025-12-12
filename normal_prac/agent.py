# from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from typing_extensions import TypedDict

load_dotenv()

# llm = ChatOpenAI(model="gpt-4o")
# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
# llm = ChatMistralAI(model="mistral-small-latest")
llm = ChatMistralAI(model="mistral-small-2506")


class State(MessagesState, TypedDict):
    verify: str


def chat(state: State):
    res = llm.invoke(state["messages"])
    return {"messages": [res], "verify": "yes"}


flow = StateGraph(State)
flow.add_node("chat", chat)
flow.add_edge(START, "chat")
flow.add_edge("chat", END)
graph = flow.compile()


res = graph.invoke({"messages": [HumanMessage(content="Hello")]})
print(res)
print(res.get("verify"))
