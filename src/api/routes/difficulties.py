"""
Difficulties API routes for Q&A Practice Application.

Implements endpoints for difficulty level management following SOLID principles.
"""

from fastapi import APIRouter, HTTPException
from typing import List
import logging

from src.services.interfaces import IQuestionService
from src.utils.container import get_container

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[str])
async def get_difficulties() -> List[str]:
    """
    Get list of available difficulty levels.

    Returns:
        List of difficulty names
    """
    try:
        container = get_container()
        question_service = container.resolve(IQuestionService)
        difficulties = question_service.get_available_difficulties()
        return difficulties
    except Exception as e:
        logger.error(f"Failed to get difficulties: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve difficulties")
