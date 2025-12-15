from pydantic import BaseModel as BM


class Struct(BM):
    query: str
