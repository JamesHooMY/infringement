import uuid
from datetime import datetime
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column
from typing import List, Dict, Optional, Union
from sqlalchemy.dialects.postgresql import JSON


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Shared properties for Patent
class PatentBase(SQLModel):
    publication_number: str = Field(max_length=50, index=True, unique=True)
    title: str = Field(min_length=1, max_length=255)
    ai_summary: Optional[str] = None
    raw_source_url: Optional[str] = None
    assignee: Optional[str] = Field(default=None, max_length=255)
    abstract: Optional[str] = None
    description: Optional[str] = None
    priority_date: Optional[datetime] = None
    application_date: Optional[datetime] = None
    grant_date: Optional[datetime] = None
    jurisdictions: Optional[str] = None
    classifications: Optional[str] = None
    application_events: Optional[Union[str, List[Dict[str, str]]]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    citations: Optional[Union[str, List[Dict[str, str]]]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    image_urls: Optional[Union[str, List[str]]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    landscapes: Optional[Union[str, List[str]]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    publish_date: Optional[datetime] = None
    citations_non_patent: Optional[str] = None
    provenance: Optional[str] = None
    attachment_urls: Optional[Union[str, List[str]]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    inventors: Optional[Union[str, List[Dict[str, str]]]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    claims: Optional[Union[str, List[Dict[str, str]]]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )


# Database model for Patent (independent, does not reference Company directly)
class Patent(PatentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Properties to return via API for patents
class PatentPublic(PatentBase):
    id: uuid.UUID


class PatentsPublic(SQLModel):
    data: list[PatentPublic]
    count: int


class Product(SQLModel):
    name: str
    description: str


# Shared properties for Company
class CompanyBase(SQLModel):
    name: str = Field(max_length=255, unique=True, index=True)
    products: List[Dict[str, str]] = Field(sa_column=Column(JSON), default_factory=list)


# Database model for Company (independent, does not reference Patent directly)
class Company(CompanyBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Properties to return via API for Company
class CompanyPublic(CompanyBase):
    id: uuid.UUID


class CompaniesPublic(SQLModel):
    data: list[CompanyPublic]
    count: int


# Nested model for top infringing products
class InfringingProductDetail(SQLModel):
    product_name: str
    infringement_likelihood: str
    relevant_claims: List[str]
    explanation: str
    specific_features: List[str]


# Infringement Analysis shared properties
class InfringementAnalysisBase(SQLModel):
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    overall_risk_assessment: str = Field(default="Not Assessed", min_length=1)


# Database model for Infringement Analysis
class InfringementAnalysis(InfringementAnalysisBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    patent_id: str = Field(foreign_key="patent.publication_number", nullable=False)
    company_name: str = Field(foreign_key="company.name", nullable=False)
    top_infringing_products: List[InfringingProductDetail] = Field(
        sa_column=Column(JSON), default_factory=list
    )
    explanation: Optional[str] = Field(default=None)


# Properties to return via API for Infringement Analysis
class InfringementAnalysisPublic(InfringementAnalysisBase):
    id: uuid.UUID
    patent_id: str
    company_name: str
    top_infringing_products: List[InfringingProductDetail] = Field(default_factory=list)
