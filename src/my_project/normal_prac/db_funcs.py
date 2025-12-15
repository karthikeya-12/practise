import asyncio
import os
from contextlib import asynccontextmanager
from datetime import date, datetime
from time import perf_counter
from uuid import uuid4

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from sqlalchemy import VARCHAR, Boolean, Column, Date, DateTime, Integer, Text, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

load_dotenv()

Base = declarative_base()


class GetChatHistory(Base):
    __tablename__ = "chat_bot_history"
    __table_args__ = {"schema": "hpip"}

    chat_history_id = Column(Integer, primary_key=True)
    chat_bot_id = Column(Integer)
    message_content = Column(Text)
    message_type = Column(VARCHAR)
    updated_on = Column(DateTime)
    status = Column(Boolean)
    created_by = Column(VARCHAR)
    updated_by = Column(VARCHAR)


class ChatBot(Base):
    __tablename__ = "chat_bot"
    __table_args__ = {"schema": "hpip"}

    chat_bot_id = Column(Integer, primary_key=True)
    history_id = Column(VARCHAR)
    user_id = Column(Integer)
    chat_title = Column(Text)
    status = Column(Boolean)
    created_by = Column(VARCHAR)
    updated_by = Column(VARCHAR)


class CoachingScheduledStatus(Base):
    __tablename__ = "coaching_schedule_status"
    __table_args__ = {"schema": "hpip"}

    coaching_schedule_status_id = Column(Integer, primary_key=True)
    staff_id = Column(Integer)
    scheduled_date = Column(Date)
    status = Column(VARCHAR)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    created_by = Column(VARCHAR)
    updated_by = Column(VARCHAR)


class CoachingSummary(Base):
    __tablename__ = "coaching_summary"
    __table_args__ = {"schema": "hpip"}

    coaching_summary_id = Column(Integer, primary_key=True)
    coaching_schedule_status_id = Column(Integer)
    staff_id = Column(Integer)
    scheduled_date = Column(Date)
    message = Column(Text)
    reason = Column(Text)
    status = Column(VARCHAR)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    created_by = Column(VARCHAR)
    updated_by = Column(VARCHAR)


class Staffs(Base):
    __tablename__ = "staffs"
    __table_args__ = {"schema": "hpip"}

    staff_id = Column(Integer, primary_key=True)
    staff_code = Column(VARCHAR)
    user_id = Column(Integer)
    department_id = Column(Integer)
    staff_name = Column(VARCHAR)
    reported_to = Column(VARCHAR)
    status = Column(VARCHAR)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    created_by = Column(VARCHAR)
    updated_by = Column(VARCHAR)


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
        raise e
    finally:
        await session.close()


async def _get_chat_history(user_id: int = None, chat_title: str = None, history_id: str = None):
    if not history_id:
        new_history_id = str(uuid4())

        async with _get_db() as session:
            new_chat = ChatBot(
                user_id=user_id,
                chat_title=chat_title,
                status=True,
                history_id=new_history_id,
                created_by=str(user_id)
            )
            session.add(new_chat)
            await session.flush()

            return {"chat_bot_id": new_history_id, "chat_id": new_chat.chat_bot_id}

    else:
        async with _get_db() as session:
            result = await session.execute(
                select(ChatBot.chat_bot_id).where(ChatBot.history_id == history_id)
            )
            chat = result.scalars().one_or_none()
            if not chat:
                return {"error": "ChatBot not found"}

            result = await session.execute(
                select(GetChatHistory)
                .where(GetChatHistory.chat_bot_id == chat)
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
                "chat_id": chat,
            }


async def _insert_chat_history(messages: list, chatbot_id: int, staff_id: int):
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
                    updated_by=str(staff_id),
                    created_by=str(staff_id)
                )
                session.add(new_entry)
        except Exception as e:
            raise e


async def save_coaching_summary(message: str, staff_id: int, reason: str, coaching_scheduled_status_id: int):
    """Saves the latest coaching summary into the coaching summary tables"""
    async with _get_db() as session:
        try:
            existing = await session.scalar(
                select(CoachingSummary)
                .where(CoachingSummary.coaching_schedule_status_id == coaching_scheduled_status_id)
            )

            if existing:
                existing.message = message
                existing.staff_id = staff_id
                existing.reason = reason
                existing.updated_on = datetime.now()
                existing.updated_by = str(staff_id)
            else:
                new_data = CoachingSummary(
                    message=message,
                    staff_id=staff_id,
                    reason=reason,
                    coaching_schedule_status_id=coaching_scheduled_status_id,
                    created_on=datetime.now(),
                    created_by=str(staff_id),
                    updated_on=datetime.now(),
                    updated_by=str(staff_id),
                    scheduled_date=date.today()
                )
                session.add(new_data)

                await session.commit()
                return {"message": "Data added succesfully"}
        except Exception as e:
            return {"error": str(e)}


async def get_coaching_summary_id(coaching_scheduled_status_id: int = 0, staff_id: int = None, status: str = None):
    """Gets coaching_summary_id and relevant details from the rdbms"""
    async with _get_db() as session:
        try:
            if coaching_scheduled_status_id != 0:
                result = await session.execute(select(CoachingSummary.scheduled_date, CoachingSummary.status).where(CoachingSummary.coaching_schedule_status_id == coaching_scheduled_status_id))
                data = result.fetchone()
                return {"coaching_summary_id": coaching_scheduled_status_id, "data": {"date": data[0].isoformat(), "record_status": data[1]}}
            else:
                new_data = CoachingScheduledStatus(
                    staff_id=staff_id,
                    scheduled_date=date.today(),
                    status=status,
                    updated_on=datetime.now(),
                    updated_by=str(staff_id) if staff_id is not None else None,
                    created_by=str(staff_id) if staff_id is not None else None
                )
                session.add(new_data)
                await session.flush()
                await session.commit()
                return {"coaching_summary_id": new_data.coaching_schedule_status_id, "data": {"date": new_data.scheduled_date, "record_status": new_data.status}}
        except Exception as e:
            raise e


async def get_staff_details(user_id: int):
    async with _get_db() as session:
        try:
            data = await session.execute(select(Staffs).where(Staffs.user_id == user_id))
            row = data.scalar_one_or_none()
            if row:
                return {
                    "staff_code": row.staff_code,
                    "user_id": row.staff_code,
                    "department_id": row.department_id,
                    "staff_name": row.staff_name,
                    "reported_to": row.reported_to,
                    "status": row.status,
                    "created_on": row.created_on,
                    "updated_on": row.updated_on,
                    "created_by": row.created_by,
                    "updated_by": row.updated_by
                }
            else:
                return None
        except Exception as e:
            raise e

if __name__ == "__main__":
    # res = asyncio.run(_get_chat_history(chat_title="Testing", staff_id=1))
    # res = asyncio.run(get_coaching_summary_id(coaching_summary_id=1))
    start = perf_counter()
    res = asyncio.run(get_staff_details(user_id=226))
    end = perf_counter()
    print(f"Execution time: {end - start:.6f} seconds")
    print(res)
    print(res["staff_name"].lower())
