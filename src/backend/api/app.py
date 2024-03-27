from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers import chat

app = FastAPI()

origins = ["http://localhost:3000", "localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.router.include_router(chat.router, prefix="/chat")
