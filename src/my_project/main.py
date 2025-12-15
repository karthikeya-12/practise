from my_project.routes import router
from fastapi import FastAPI

# import uvicorn

app = FastAPI()
app.include_router(router=router)

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
