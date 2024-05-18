from fastapi import APIRouter, HTTPException, Request

from api.services.chatbot import get_chatbot
from fastapi.responses import JSONResponse, StreamingResponse
from api.domain.models import Question, QuestionRequest


router = APIRouter()


@router.post("/question", response_class=StreamingResponse)
async def get_response(request: QuestionRequest):
    chatbot = get_chatbot("LHC_Brochure_2021")

    return StreamingResponse(
        chatbot.get_answer(request.question, history=request.history)
    )
