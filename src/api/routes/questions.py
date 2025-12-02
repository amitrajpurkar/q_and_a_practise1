"""
Questions API routes for Q&A Practice Application.

Implements endpoints for question management following SOLID principles.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import logging

from src.services.interfaces import IQuestionService
from src.utils.container import get_container

router = APIRouter()
logger = logging.getLogger(__name__)


class QuestionResponse(BaseModel):
    """Question response model."""

    id: str
    topic: str
    question_text: str
    options: List[str]
    difficulty: str
    tag: str


class AnswerRequest(BaseModel):
    """Answer submission request model."""

    question_id: str
    answer: str


class AnswerResponse(BaseModel):
    """Answer response model."""

    correct: bool
    correct_answer: str
    explanation: Optional[str] = None


@router.get("/random", response_model=QuestionResponse)
async def get_random_question(
    topic: str = Query(..., description="Question topic"),
    difficulty: str = Query(..., description="Question difficulty"),
    exclude_ids: Optional[List[str]] = Query(
        None, description="Question IDs to exclude"
    ),
) -> QuestionResponse:
    """
    Get a random question matching criteria.

    Args:
        topic: Question topic
        difficulty: Question difficulty
        exclude_ids: Optional list of question IDs to exclude

    Returns:
        Random question
    """
    try:
        container = get_container()
        question_service = container.resolve(IQuestionService)

        question = question_service.get_random_question(
            topic=topic, difficulty=difficulty, exclude_ids=exclude_ids or []
        )

        if not question:
            raise HTTPException(
                status_code=404,
                detail=f"No questions available for {topic}-{difficulty}",
            )

        return QuestionResponse(
            id=question.id,
            topic=question.topic,
            question_text=question.question_text,
            options=question.get_options(),
            difficulty=question.difficulty,
            tag=question.tag,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get random question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve question")


@router.post("/validate", response_model=AnswerResponse)
async def validate_answer(request: AnswerRequest) -> AnswerResponse:
    """
    Validate a user's answer.

    Args:
        request: Answer submission request

    Returns:
        Answer validation result
    """
    try:
        container = get_container()
        question_service = container.resolve(IQuestionService)

        is_correct = question_service.validate_answer(
            question_id=request.question_id, user_answer=request.answer
        )

        # Get question for correct answer
        question = question_service.get_question_by_id(request.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        return AnswerResponse(
            correct=is_correct,
            correct_answer=question.correct_answer,
            explanation=(
                "The correct answer is highlighted above." if not is_correct else None
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate answer: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate answer")
