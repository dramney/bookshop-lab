from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Profile
from passlib.hash import bcrypt

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/userdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

users = [
    {"username": "ivan", "email": "ivan@example.com", "role": "client", "password": "password1"},
    {"username": "olga", "email": "olga@example.com", "role": "seller", "password": "password2"},
    {"username": "maria", "email": "maria@example.com", "role": "manager", "password": "password3"}
]

for u in users:
    user = Profile(username=u["username"], email=u["email"], role=u["role"], password_hash=bcrypt.hash(u["password"]))
    db.add(user)

db.commit()
db.close()
print("User DB seeded ✅")
