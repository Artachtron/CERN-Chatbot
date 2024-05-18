from fastapi import APIRouter, HTTPException, Request

from api.services.chatbot import get_chatbot
from fastapi.responses import JSONResponse, StreamingResponse
from api.domain.models import Question


router = APIRouter()


@router.post("/question", response_class=StreamingResponse)
async def get_response(question: Question):
    chatbot = get_chatbot("LHC_Brochure_2021")
    # answer = chatbot.get_answer(question.question)
    # answer = "not implemented yet"
    return StreamingResponse(chatbot.get_answer(question.question))
