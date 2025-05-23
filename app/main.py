from app.api.router import router as router_randomuser
from app.database import create_tables
from fastapi import FastAPI,Depends


app= FastAPI()

app.include_router(router_randomuser)



@app.on_event("startup")
async def on_startup():
    await create_tables()