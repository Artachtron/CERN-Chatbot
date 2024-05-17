from fastapi import APIRouter, HTTPException, Request

from api.services.chatbot import get_chatbot
from fastapi.responses import JSONResponse
from api.domain.models import Question


router = APIRouter()


@router.post("/question", response_class=JSONResponse)
async def get_response(question: Question) -> JSONResponse:
    chatbot = get_chatbot("CERN-Brochure-2021-007-Eng.pdf")
    answer = chatbot.get_answer(question.question)
    # answer = "not implemented yet"
    return JSONResponse(status_code=200, content={"answer": answer})
