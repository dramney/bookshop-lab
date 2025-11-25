from pydantic import BaseModel

class RegisterIn(BaseModel):
    username: str
    password: str
    role: str
    email: str | None = None

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
