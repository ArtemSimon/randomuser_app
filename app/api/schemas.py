from pydantic import BaseModel, Field,ConfigDict
from typing import List,Dict

class SUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    gender:str
    email: str
    phone: str
    street: str
    city: str
    state: str
    country: str
    postcode: str
    profile_url: str
    picture_thumbnail: str

    model_config = ConfigDict(from_attributes=True)

class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int


class SUserListResponce(BaseModel):
    data:List[SUserResponse]
    meta:PaginationMeta


class SUserFind(BaseModel):
    id: int = Field(...)    