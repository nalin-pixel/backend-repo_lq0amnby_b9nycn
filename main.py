import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import db, create_document, get_documents

app = FastAPI(title="Microcredit Companies API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompanyIn(BaseModel):
    name: str = Field(..., description="Company legal name")
    license_id: Optional[str] = Field(None, description="Regulatory license or registration ID")
    country: str
    region: Optional[str] = None
    portfolio_usd: float = Field(0, ge=0)
    active_borrowers: int = Field(0, ge=0)
    par30: float = Field(0, ge=0, le=100)
    avg_interest_rate: float = Field(0, ge=0, le=200)
    status: str = Field("active")
    rating: Optional[float] = Field(None, ge=0, le=5)


@app.get("/")
def read_root():
    return {"message": "Microcredit Companies Backend is running"}


@app.get("/api/companies")
def list_companies(
    q: Optional[str] = Query(None, description="Search by name"),
    country: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
):
    """List companies with optional filters."""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    filter_dict = {}
    if q:
        # Simple case-insensitive search on name
        filter_dict["name"] = {"$regex": q, "$options": "i"}
    if country:
        filter_dict["country"] = country
    if status:
        filter_dict["status"] = status

    docs = get_documents("company", filter_dict, limit)

    # Transform ObjectId and datetime to strings
    def serialize(doc):
        doc["id"] = str(doc.pop("_id"))
        for k, v in list(doc.items()):
            if hasattr(v, "isoformat"):
                doc[k] = v.isoformat()
        return doc

    return [serialize(d) for d in docs]


@app.post("/api/companies", status_code=201)
def create_company(payload: CompanyIn):
    """Create a new company document."""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    company_id = create_document("company", payload.model_dump())
    return {"id": company_id}


@app.get("/api/companies/stats")
def company_stats():
    """Aggregate stats for dashboard cards."""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    companies = list(db["company"].find({}))
    total_companies = len(companies)
    if total_companies == 0:
        return {
            "total_companies": 0,
            "total_portfolio_usd": 0.0,
            "avg_par30": 0.0,
            "active_borrowers": 0,
            "countries_count": 0,
        }

    total_portfolio = sum(float(c.get("portfolio_usd", 0) or 0) for c in companies)
    total_borrowers = sum(int(c.get("active_borrowers", 0) or 0) for c in companies)
    avg_par30 = sum(float(c.get("par30", 0) or 0) for c in companies) / total_companies
    countries = {c.get("country", "") for c in companies if c.get("country")}

    return {
        "total_companies": total_companies,
        "total_portfolio_usd": round(total_portfolio, 2),
        "avg_par30": round(avg_par30, 2),
        "active_borrowers": total_borrowers,
        "countries_count": len(countries),
    }


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
