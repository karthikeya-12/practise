from sqlalchemy import create_engine, Column, JSON, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from contextlib import contextmanager
import os
load_dotenv()

Base = declarative_base()


class Retrieve(Base):
    __tablename__ = "ai_chatbot"
    id = Column(Integer, primary_key=True)
    message = Column(JSON)


class Checkpoints(Base):
    __tablename__ = "tool_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)


engine = create_engine(f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost/{os.getenv('DB_NAME')}")
Session = sessionmaker(bind=engine)


@contextmanager
def get_db_session():
    session = Session()
    try:
        yield session
    except Exception:
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    with get_db_session() as session:
        users = session.query(Retrieve).filter_by(id=1).all()
        print(type(users))
        # print(users.message)
        # print(users.id)
        # for i in users:
        print(users[0].id, users[0].message)
        # print(i.message)
