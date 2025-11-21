"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Microcredit Company schema
class Company(BaseModel):
    """Microcredit company profile
    Collection name: "company"
    """
    name: str = Field(..., description="Company legal name")
    license_id: Optional[str] = Field(None, description="Regulatory license or registration ID")
    country: str = Field(..., description="Country of operation")
    region: Optional[str] = Field(None, description="Region/State/Province")
    portfolio_usd: float = Field(0, ge=0, description="Gross loan portfolio in USD")
    active_borrowers: int = Field(0, ge=0, description="Number of active borrowers")
    par30: float = Field(0, ge=0, le=100, description="Portfolio at Risk > 30 days in %")
    avg_interest_rate: float = Field(0, ge=0, le=200, description="Average annualized interest rate in %")
    status: str = Field("active", description="Operating status: active, suspended, closed")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Internal rating 0-5")
