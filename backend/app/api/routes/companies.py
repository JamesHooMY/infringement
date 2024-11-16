import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from app.api.deps import SessionDep
from sqlmodel import func, select
from app.models import (
    CompaniesPublic,
    CompanyPublic,
    Company,
)

router = APIRouter()


@router.get(
    "/",
    response_model=CompaniesPublic,
)
def read_items(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve companies.
    """

    count_statement = select(func.count()).select_from(Company)
    count = session.exec(count_statement).one()
    statement = select(Company).offset(skip).limit(limit)
    companies = session.exec(statement).all()

    return CompaniesPublic(data=companies, count=count)


@router.get("/{id}", response_model=CompanyPublic)
def read_item(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Get company by ID.
    """
    company = session.get(Company, id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
