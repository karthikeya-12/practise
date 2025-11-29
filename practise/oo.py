from sqlalchemy import Column, JSON, Integer, create_engine, String, VARCHAR
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from contextlib import contextmanager
import os
import traceback
load_dotenv()

Base = declarative_base()


class Retrieve(Base):
    # __tablename__ = "ai_chatbot"
    __tablename__ = "usecases"
    __table_args__ = {"schema": "ai_compute_modeller"}

    # id = Column(Integer, primary_key=True)
    usecase_id = Column(Integer, primary_key=True)
    usecase_name = Column(VARCHAR)
    usecase_state = Column(JSON)


class Checkpoints(Base):
    __tablename__ = "tool_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)


engine = create_engine(f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")
Session = sessionmaker(bind=engine)


@contextmanager
def get_db_session():
    session = Session()
    try:
        yield session
    except Exception:
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()


def get_db(usecase_name: str):
    with get_db_session() as session:
        er = session.query(Retrieve).filter_by(usecase_name=usecase_name).first()
        # print(er.id)
        # print(er.message)
        # return {"id": er.id, "usecase_name": er.usecase_name, "usecase_state": er.usecase_state}
        return er.usecase_state


async def get_checkpoints():
    with get_db_session() as session:
        users = session.query(Checkpoints).all()
        # for i in users:
        # yield {"id": i.id, "code": i.code, "name": i.name}
        return [{"id": i.id, "code": i.code, "name": i.name} for i in users]


if __name__ == "__main__":
    with get_db_session() as session:
        users = session.query(Checkpoints).all()
        for i in users:
            print(i.id)
            print(i.code)
            print(i.name)
            print("__ " * 48)
    print("== " * 48)
    get_db(2)
    print("== " * 48)
