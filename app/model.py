from pydantic import BaseModel

class Login(BaseModel):
    email_id: str
    password: str

class Signup(BaseModel):
    email_id: str
    user_id: str
    first_name: str
    last_name: str
    password: str
    confirm_password: str