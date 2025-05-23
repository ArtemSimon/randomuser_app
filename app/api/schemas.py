from pydantic import BaseModel, Field

class SUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    profile_url: str

    class Config:
        orm_mode = True

class SUserFind(BaseModel):
    id: int = Field(...)    