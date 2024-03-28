from fastapi import APIRouter, HTTPException, Request

from backend.api.services.chatbot import ChatBot
from fastapi.responses import JSONResponse
from backend.api.domain.models import Question


router = APIRouter()

chatbot = ChatBot("CERN-Brochure-2021-007-Eng.pdf")


@router.post("/question", response_class=JSONResponse)
async def get_response(question: Question) -> JSONResponse:
    answer = chatbot.get_answer(question.question)
    return JSONResponse(status_code=200, content={"answer": answer})
