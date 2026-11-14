"""
Pydantic schemas for the Farmer entity.

Defines request/response models for farmer CRUD operations.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class FarmerCreate(BaseModel):
    """Schema for creating a new farmer."""

    name: str = Field(..., min_length=1, max_length=100, description="Full name of the farmer")
    email: str = Field(..., max_length=150, description="Unique email address")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    address: Optional[str] = Field(None, description="Full mailing address")


class FarmerUpdate(BaseModel):
    """Schema for updating an existing farmer. All fields optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class FarmerResponse(BaseModel):
    """Schema for farmer data returned in API responses."""

    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
