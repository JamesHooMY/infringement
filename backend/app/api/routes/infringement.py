import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import SessionDep
from app.models import (
    InfringementAnalysis,
    InfringementAnalysisPublic,
)

router = APIRouter()


@router.post("/check/", response_model=InfringementAnalysisPublic)
def check_infringement(
    *, session: SessionDep, analysis_in: InfringementAnalysis
) -> Any:
    """
    Check infringement.
    """
    analysis = InfringementAnalysis(**analysis_in.dict())
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


@router.get("/{id}", response_model=InfringementAnalysisPublic)
def read_infringement(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Get infringement analysis by ID.
    """
    analysis = session.get(InfringementAnalysis, id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
