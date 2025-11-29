import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from sqlalchemy import (
    Integer,
    Text,
    VARCHAR,
    Column,
    Boolean,
    DateTime,
    select
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from time import perf_counter
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


async def _get_info(history_id: str = None):
    async with _get_db() as session:
        chatbotid = await session.execute(
            select(ChatBot.chat_bot_id).where(ChatBot.history_id == history_id)
        )
        ids = chatbotid.scalars().one()
        print(f"chatbot id is {ids}")
        users = await session.execute(
            select(GetChatHistory.message_content, GetChatHistory.message_type).where(GetChatHistory.chat_bot_id == ids)
        )
        messages = users.all()
        # print(messages)
        for i in messages:
            print("\n\n")
            print("==" * 15, i[1], "==" * 15)
            print(i[0])
            print("\n\n", "__ " * 40)


if __name__ == "__main__":
    start = perf_counter()
    # asyncio.run(_get_info(history_id="ecc14e3a-fcf8-40ac-abc4-8f3b82766bea"))
    asyncio.run(_get_info(history_id="be02f5dd-c943-40a7-a9e4-84018cb4e53b"))
    end = perf_counter()
    print("$$" * 40)
    print(f"time is {end - start:.6f}")
