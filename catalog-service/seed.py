from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Book

# Підключення до PostgreSQL (з docker-compose)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/catalogdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Створюємо таблиці, якщо їх ще немає
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Книги
books = [
    Book(
        title="Harry Potter and the Philosopher's Stone",
        author="J.K. Rowling",
        publisher="Bloomsbury",
        genre="Fantasy",
        price=20.5,
        description="First book in the series"
    ),
    Book(
        title="Harry Potter and the Chamber of Secrets",
        author="J.K. Rowling",
        publisher="Bloomsbury",
        genre="Fantasy",
        price=21.0,
        description="Second book in the series"
    ),
    Book(
        title="A Game of Thrones",
        author="George R.R. Martin",
        publisher="HarperCollins",
        genre="Fantasy",
        price=25.0,
        description="First book in the series"
    ),
    Book(
        title="Murder on the Orient Express",
        author="Agatha Christie",
        publisher="HarperCollins",
        genre="Mystery",
        price=18.0,
        description="Classic detective novel"
    ),
    Book(
        title="The Hobbit",
        author="J.R.R. Tolkien",
        publisher="HarperCollins",
        genre="Adventure",
        price=22.0,
        description="Fantasy adventure"
    )
]

db.add_all(books)
db.commit()
db.close()
print("Catalog DB seeded ✅")
