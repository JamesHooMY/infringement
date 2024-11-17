import uuid
import logging
from datetime import datetime
from typing import Any
from venv import logger
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select
from app.models import Company, Patent, InfringementAnalysis, InfringementAnalysisPublic
from app.api.deps import SessionDep
from app.core.openai import PatentInfringementAnalyzer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()

class InfringementAnalysisRequest(BaseModel):
    patent_id: str
    company_name: str

@router.post("/check", response_model=InfringementAnalysisPublic)
def check_infringement(
    *, session: SessionDep, data: InfringementAnalysisRequest
) -> Any:
    """
    Check infringement.
    """
    # * create infringement analysis
    # analysis = InfringementAnalysis(**analysis_in.dict(exclude_unset=True))
    # session.add(analysis)
    # session.commit()
    # session.refresh(analysis)

    # Query the company data from the database
    company = session.exec(
        select(Company).where(Company.name == data.company_name)
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Query the patent data from the database
    patent = session.exec(
        select(Patent).where(Patent.publication_number == data.patent_id)
    ).first()
    if not patent:
        raise HTTPException(status_code=404, detail="Patent not found")

    # Call the OpenAI API to analyze infringement
    analyzer = PatentInfringementAnalyzer()
    analysis_response = analyzer.analyze_infringement(company, patent)

    return analysis_response


@router.get("/{id}", response_model=InfringementAnalysisPublic)
def read_infringement(session: SessionDep, analysis_id: uuid.UUID) -> Any:
    """
    Get infringement analysis by ID.
    """
    analysis = session.get(InfringementAnalysis, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=404, detail=f"Analysis with ID {analysis_id} not found"
        )
    return analysis
