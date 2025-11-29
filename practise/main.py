from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routes import router

app = FastAPI(title="ORM Demonstration", description="SQLALCHEMY", version="1.1.90.2")
app.include_router(router=router)


@app.get("/")
async def home():
    return JSONResponse({"data": "Welcome"})
