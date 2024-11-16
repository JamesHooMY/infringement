import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import SessionDep
from app.models import (
    PatentsPublic,
    PatentPublic,
    Patent,
)

router = APIRouter()


@router.get("/", response_model=PatentsPublic)
def read_items(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve companies.
    """

    count_statement = select(func.count()).select_from(Patent)
    count = session.exec(count_statement).one()
    statement = select(Patent).offset(skip).limit(limit)
    patents = session.exec(statement).all()

    return PatentsPublic(data=patents, count=count)


@router.get("/{patent_id}", response_model=PatentPublic)
def read_item(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Get patent by ID.
    """
    patent = session.get(Patent, id)
    if not patent:
        raise HTTPException(status_code=404, detail="patent not found")
    return patent
