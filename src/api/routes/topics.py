"""
Topics API routes for Q&A Practice Application.

Implements endpoints for topic management following SOLID principles.
"""

from fastapi import APIRouter, HTTPException
from typing import List
import logging

from src.services.interfaces import IQuestionService
from src.utils.container import get_container

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[str])
async def get_topics() -> List[str]:
    """
    Get list of available topics.

    Returns:
        List of topic names
    """
    try:
        container = get_container()
        question_service = container.resolve(IQuestionService)
        topics = question_service.get_available_topics()
        return topics
    except Exception as e:
        logger.error(f"Failed to get topics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve topics")
