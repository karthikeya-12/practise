from sqlalchemy import Integer, Text, VARCHAR, Column, create_engine, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from uuid import uuid4
from contextlib import contextmanager
import os
load_dotenv()

Base = declarative_base()


class GetChatHistory(Base):
    __tablename__ = "chat_bot_history"
    __table_args__ = {"schema": "ai_compute_modeller"}

    chat_history_id = Column(Integer, primary_key=True)
    chat_bot_id = Column(Integer)
    message_content = Column(Text)
    message_type = Column(VARCHAR)
    updated_on = Column(DateTime)
    status = Column(Boolean)


class ChatBot(Base):
    __tablename__ = "chat_bot"
    __table_args__ = {"schema": "ai_compute_modeller"}

    chat_bot_id = Column(Integer, primary_key=True)
    history_id = Column(VARCHAR)
    staff_id = Column(Integer)
    chat_title = Column(Text)
    status = Column(Boolean)


engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

Session = sessionmaker(bind=engine)


@contextmanager
def _get_db():
    with Session() as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            print(str(e))
        finally:
            session.close()


def _get_chat_history(staff_id: int = None, chat_title: str = None, chatbot_id: int = None):
    if not chatbot_id:
        ids = str(uuid4())

        with _get_db() as session:
            try:
                new_data = ChatBot(staff_id=staff_id, chat_title=chat_title, status=True, history_id=ids)
                session.add(new_data)
                session.commit()
                data = session.query(ChatBot).filter_by(history_id=ids).first()
                return {"chat_bot_id": data.chat_bot_id}
            except Exception as e:
                return {"error": str(e)}
            finally:
                session.close()
    else:
        with _get_db() as session:
            messages = []
            try:
                history = session.query(GetChatHistory).filter_by(chat_bot_id=chatbot_id).order_by(GetChatHistory.updated_on.asc()).all()
                for i in history:
                    if i.message_type == "HumanMessage":
                        messages.append(HumanMessage(content=i.message_content))
                    elif i.message_type == "AIMessage":
                        messages.append(AIMessage(content=i.message_content))
                    else:
                        messages.append(ToolMessage(i.message_content))

                return {"chat_history": messages, "chat_bot_id": chatbot_id}
            except Exception as e:
                return {"error": str(e)}
            finally:
                session.close()


def _insert_chat_history(messages: list, chatbot_id: int):
    with _get_db() as session:
        try:
            for i in messages:
                if isinstance(i, HumanMessage):
                    message_type = "HumanMessage"
                    message_content = i.content
                    new_data = GetChatHistory(chat_bot_id=chatbot_id, message_type=message_type, message_content=message_content, status=True)
                    session.add(new_data)
                    session.commit()
                elif isinstance(i, AIMessage):
                    message_type = "AIMessage"
                    message_content = i.content
                    new_data = GetChatHistory(chat_bot_id=chatbot_id, message_type=message_type, message_content=message_content, status=True)
                    session.add(new_data)
                    session.commit()
                else:
                    message_type = "ToolMessage"
                    message_content = i.content
                    new_data = GetChatHistory(chat_bot_id=chatbot_id, message_type=message_type, message_content=message_content, status=True)
                    session.add(new_data)
                    session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()


if __name__ == "__main__":
    res = _get_chat_history(chat_title="Testing", staff_id=1)
    print(res)
