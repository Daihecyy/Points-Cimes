# JSON payload containing access token
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: str | None = None


class NewPassword(BaseModel):
    token: str
    new_password: str  # TODO : = Field(min_length=8, max_length=40) ?


class AccountActivation(BaseModel):
    email: str
    token: str
