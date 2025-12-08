"""
Scores API routes for Q&A Practice Application.

Implements endpoints for score management following SOLID principles.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
import logging

from src.services.interfaces import IScoreService
from src.utils.container import get_container

router = APIRouter()
logger = logging.getLogger(__name__)


class ScoreResponse(BaseModel):
    """Score response model."""

    session_id: str
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    accuracy_percentage: float
    time_taken_seconds: int
    performance_grade: str
    topic_performance: Dict[str, Dict[str, int]]


@router.get("/{session_id}", response_model=ScoreResponse)
async def get_score(session_id: str) -> ScoreResponse:
    """
    Get score for a completed session.

    Args:
        session_id: Session identifier

    Returns:
        Session score details
    """
    try:
        container = get_container()
        score_service = container.resolve(IScoreService)

        score = score_service.calculate_score(session_id)
        if not score:
            raise HTTPException(status_code=404, detail="Score not found for session")

        return ScoreResponse(
            session_id=score.session_id,
            total_questions=score.total_questions,
            correct_answers=score.correct_answers,
            incorrect_answers=score.incorrect_answers,
            accuracy_percentage=score.accuracy_percentage,
            time_taken_seconds=score.time_taken_seconds,
            performance_grade=score._get_performance_grade(),
            topic_performance=score.topic_performance,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get score: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve score")


@router.get("/{session_id}/summary")
async def get_score_summary(session_id: str) -> Dict[str, Any]:
    """
    Get detailed performance summary for a session.

    Args:
        session_id: Session identifier

    Returns:
        Performance summary
    """
    try:
        container = get_container()
        score_service = container.resolve(IScoreService)

        summary = score_service.generate_summary(session_id)

        return summary

    except Exception as e:
        logger.error(f"Failed to get score summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve score summary")
