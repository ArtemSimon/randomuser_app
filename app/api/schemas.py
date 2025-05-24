from pydantic import BaseModel, Field

class SUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    street: str
    city: str
    state: str
    country: str
    postcode: str
    profile_url: str
    picture_thumbnail: str

    class Config:
        orm_mode = True

class SUserFind(BaseModel):
    id: int = Field(...)    