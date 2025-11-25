from pydantic import BaseModel

class ProfileOut(BaseModel):
    username: str
    display_name: str | None
    bio: str | None
    contact_email: str | None
