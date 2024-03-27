from fastapi import APIRouter, HTTPException
from backend.rag.pipeline import answer_question
from backend.api.services.chatbot import ChatBot

router = APIRouter()

chatbot = ChatBot("CERN-Brochure-2021-007-Eng.pdf")


@router.get("/response")
async def get_response(question: str):
    return {"response": chatbot.get_answer(question)}
