"""
Sessions API routes for Q&A Practice Application.

Implements endpoints for session management following SOLID principles.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from src.services.interfaces import ISessionService
from src.utils.exceptions import SessionError, ValidationError
from src.utils.container import get_container

router = APIRouter()
logger = logging.getLogger(__name__)


class SessionCreateRequest(BaseModel):
    """Session creation request model."""

    topic: str
    difficulty: str
    total_questions: int = 10


class SessionResponse(BaseModel):
    """Session response model."""

    session_id: str
    topic: str
    difficulty: str
    total_questions: int
    current_question_index: int
    is_active: bool
    progress: Dict[str, Any]


class QuestionSubmissionRequest(BaseModel):
    """Question submission request model."""

    session_id: str
    question_id: str
    answer: str


class NextQuestionResponse(BaseModel):
    """Next question response model."""

    question_id: Optional[str]
    question_text: Optional[str]
    options: Optional[List[str]]
    session_complete: bool


@router.post("/", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest) -> SessionResponse:
    """
    Create a new practice session.

    Args:
        request: Session creation request

    Returns:
        Created session details
    """
    try:
        container = get_container()
        session_service = container.resolve(ISessionService)

        session_id = session_service.create_session(
            topic=request.topic,
            difficulty=request.difficulty,
            total_questions=request.total_questions,
        )

        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=500, detail="Failed to create session")

        return SessionResponse(
            session_id=session.session_id,
            topic=session.topic,
            difficulty=session.difficulty,
            total_questions=session.total_questions,
            current_question_index=session.current_question_index,
            is_active=session.is_active,
            progress=session.get_progress(),
        )

    except HTTPException:
        raise
    except ValidationError as e:
        logger.warning(f"Validation error creating session: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "ValidationError",
                "message": str(e)
            }
        )
    except SessionError as e:
        logger.warning(f"Session error creating session: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "SessionError", 
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Failed to create session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """
    Get session details.

    Args:
        session_id: Session identifier

    Returns:
        Session details
    """
    try:
        container = get_container()
        session_service = container.resolve(ISessionService)

        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionResponse(
            session_id=session.session_id,
            topic=session.topic,
            difficulty=session.difficulty,
            total_questions=session.total_questions,
            current_question_index=session.current_question_index,
            is_active=session.is_active,
            progress=session.get_progress(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")


@router.post("/submit-answer")
async def submit_answer(request: QuestionSubmissionRequest) -> Dict[str, Any]:
    """
    Submit an answer for a question in a session.

    Args:
        request: Question submission request

    Returns:
        Submission result
    """
    try:
        container = get_container()
        session_service = container.resolve(ISessionService)

        success = session_service.submit_answer(
            session_id=request.session_id,
            question_id=request.question_id,
            answer=request.answer,
        )

        return {"success": success, "message": "Answer submitted successfully"}

    except Exception as e:
        logger.error(f"Failed to submit answer: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit answer")


@router.get("/{session_id}/next-question", response_model=NextQuestionResponse)
async def get_next_question(session_id: str) -> NextQuestionResponse:
    """
    Get the next question for a session.

    Args:
        session_id: Session identifier

    Returns:
        Next question or session completion indicator
    """
    try:
        container = get_container()
        session_service = container.resolve(ISessionService)

        question = session_service.get_next_question(session_id)

        if question is None:
            # Session is complete
            return NextQuestionResponse(
                question_id=None,
                question_text=None,
                options=None,
                session_complete=True,
            )

        return NextQuestionResponse(
            question_id=question.id,
            question_text=question.question_text,
            options=question.get_options(),
            session_complete=False,
        )

    except Exception as e:
        logger.error(f"Failed to get next question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve next question")


@router.post("/{session_id}/complete")
async def complete_session(session_id: str) -> Dict[str, Any]:
    """
    Complete a session and calculate final score.

    Args:
        session_id: Session identifier

    Returns:
        Session completion result
    """
    try:
        container = get_container()
        session_service = container.resolve(ISessionService)

        session_service.complete_session(session_id)

        return {
            "success": True,
            "message": "Session completed successfully",
            "session_id": session_id,
        }

    except Exception as e:
        logger.error(f"Failed to complete session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete session")
