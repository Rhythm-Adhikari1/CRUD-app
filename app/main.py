
from fastapi import FastAPI
from . import models
from . database import engine
from .routers import post , user, auth, vote
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

models.Base.metadata.create_all(bind=engine)  # type: ignore

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],

)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():

    return {"message": "succesfully deployed fastapi app"}







if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render provides this PORT
    uvicorn.run("main:app", host="0.0.0.0", port=port)

