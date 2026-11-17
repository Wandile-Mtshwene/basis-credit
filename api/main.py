"""Loan Affordability & Credit Decision API - FastAPI service."""
from __future__ import annotations

from dataclasses import asdict
from typing import Literal

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from basis.credit import assess_credit, DEFAULT_POLICY

app = FastAPI(title="Loan Affordability & Credit Decision API", version="1.0.0",
    docs_url="/api/docs", openapi_url="/api/openapi.json",
    description="Affordability assessment and an auditable credit scorecard.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
router = APIRouter(prefix="/api")


@router.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "service": "basis-credit"}


class CreditRequest(BaseModel):
    age: int = Field(35, ge=16, le=90)
    employment_type: Literal["permanent", "contract", "self_employed", "unemployed"] = "permanent"
    employment_months: int = Field(36, ge=0, le=600)
    existing_accounts: int = Field(2, ge=0, le=50)
    adverse_history: bool = False
    gross_monthly_income: float = Field(45_000, gt=0)
    net_monthly_income: float = Field(33_000, gt=0)
    monthly_living_expenses: float = Field(12_000, ge=0)
    existing_monthly_debt: float = Field(4_000, ge=0)
    loan_amount: float = Field(150_000, gt=0)
    annual_rate: float = Field(0.18, ge=0, le=0.6)
    term_months: int = Field(48, ge=1, le=360)


@router.post("/credit/assess", tags=["pricing"])
def credit(req: CreditRequest) -> dict:
    return asdict(assess_credit(**req.model_dump()))


@router.get("/credit/policy", tags=["admin"])
def credit_policy() -> dict:
    return DEFAULT_POLICY.as_dict()

app.include_router(router)
