from dotenv import load_dotenv
from langchain_core.messages import (
    HumanMessage,
    messages_to_dict,
    messages_from_dict,
)
from langchain_mistralai import ChatMistralAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from typing_extensions import TypedDict
from mongoengine import (
    Document,
    ListField,
    DictField,
    StringField,
    DateTimeField,
    connect,
)
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown
import os
from uuid import uuid4

load_dotenv()

connect(
    db=os.getenv("mongo_db"),
    host=os.getenv("mongo_host"),
    port=int(os.getenv("mongo_port")),
)

llm = ChatMistralAI(model="mistral-small-2506")
console = Console()


class ChatSession(Document):
    ids = StringField(required=True, unique=True)
    messages = ListField(DictField(), default=list)
    verify = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "chat_sessions"}


class State(MessagesState, TypedDict):
    verify: str


def chat(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response], "verify": "yes"}


flow = StateGraph(State)
flow.add_node("chat", chat)
flow.add_edge(START, "chat")
flow.add_edge("chat", END)
graph = flow.compile()


# ------------------------------------------------------------------
# Chat Loop
# ------------------------------------------------------------------
def in_file_func():
    global session_id
    session_id = str(uuid4())

    # Create session once
    session = ChatSession(ids=session_id)
    session.save()

    print(f"Session started: {session_id}")
    print("Type 'q' to quit\n")

    while True:
        try:
            print()
            user_input = input("Enter your query: ").strip()

            if user_input.lower() == "q":
                print("Bye 👋")
                break

            # Reload latest session state
            session.reload()

            # Rehydrate messages
            messages = messages_from_dict(session.messages)

            # Add user message
            messages.append(HumanMessage(content=user_input))

            # Invoke graph
            result = graph.invoke({"messages": messages})

            # Append assistant response
            messages.extend(result["messages"])

            # Print assistant message
            print("=" * 15, "AIMESSAGE", "=" * 15)
            console.print(Markdown(result["messages"][-1].content))

            # Persist
            session.messages = messages_to_dict(messages)
            session.verify = result.get("verify")
            session.save()

        except KeyboardInterrupt:
            print("\nInterrupted. Exiting.")
            break

        except Exception as e:
            print("Error:", e)


# ------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------
if __name__ == "__main__":
    in_file_func()
    print(session_id)
