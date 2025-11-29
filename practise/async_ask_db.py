import os
from uuid import uuid4
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from sqlalchemy import Integer, Text, VARCHAR, Column, Boolean, DateTime, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import asyncio

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


engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}",
    echo=False,
)

AsyncSession = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def _get_db():
    session = AsyncSession()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        print(str(e))
        raise
    finally:
        await session.close()


async def _get_chat_history(staff_id: int = None, chat_title: str = None, history_id: str = None):
    if not history_id:
        new_history_id = str(uuid4())

        async with _get_db() as session:
            new_chat = ChatBot(
                staff_id=staff_id,
                chat_title=chat_title,
                status=True,
                history_id=new_history_id,
            )
            session.add(new_chat)
            await session.flush()

            return {"chat_bot_id": new_history_id, "chat_id": new_chat.chat_bot_id}

    else:
        async with _get_db() as session:
            result = await session.execute(
                select(ChatBot.chat_bot_id).where(ChatBot.history_id == history_id)
            )
            chat_bot_id = result.scalars().one_or_none()
            print(chat_bot_id, '---chat_bot_id')
            if not chat_bot_id:
                return {"error": "ChatBot not found"}

            result = await session.execute(
                select(GetChatHistory)
                .where(GetChatHistory.chat_bot_id == chat_bot_id)
                .order_by(GetChatHistory.updated_on.asc())
            )
            history_rows = result.scalars().all()

            messages = []
            for row in history_rows:
                if row.message_type == "HumanMessage":
                    messages.append(HumanMessage(content=row.message_content))
                elif row.message_type == "AIMessage":
                    messages.append(AIMessage(content=row.message_content))
                else:
                    messages.append(ToolMessage(content=row.message_content))

            return {
                "chat_history": messages,
                "chat_bot_id": history_id,
                "chat_id": chat_bot_id,
            }


async def _insert_chat_history(messages: list, chatbot_id: int):
    async with _get_db() as session:
        try:
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    msg_type = "HumanMessage"
                elif isinstance(msg, AIMessage):
                    msg_type = "AIMessage"
                else:
                    msg_type = "ToolMessage"

                new_entry = GetChatHistory(
                    chat_bot_id=chatbot_id,
                    message_type=msg_type,
                    message_content=msg.content,
                    status=True,
                )
                session.add(new_entry)
        except Exception as e:
            raise e


if __name__ == "__main__":
    res = asyncio.run(_get_chat_history(history_id="ecc14e3a-fcf8-40ac-abc4-8f3b82766bea"))
    print(res)
