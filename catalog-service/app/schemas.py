from pydantic import BaseModel

class BookIn(BaseModel):
    title: str
    author: str
    publisher: str | None = None
    genre: str | None = None
    price: float
    description: str | None = None

class BookOut(BookIn):
    id: int
