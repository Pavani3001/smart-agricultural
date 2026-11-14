"""
Farmer management router.

Provides CRUD endpoints for farmer registration and profiles.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.farmer import Farmer
from ..schemas.farmer import FarmerCreate, FarmerUpdate, FarmerResponse
from ..utils.exceptions import ResourceNotFoundError, DuplicateResourceError

router = APIRouter(prefix="/farmers", tags=["Farmers"])


@router.post("/", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
def create_farmer(farmer_in: FarmerCreate, db: Session = Depends(get_db)):
    """Register a new farmer."""
    existing = db.query(Farmer).filter(Farmer.email == farmer_in.email).first()
    if existing:
        raise DuplicateResourceError("Farmer", f"Farmer with email '{farmer_in.email}' already exists")

    farmer = Farmer(**farmer_in.model_dump())
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return farmer


@router.get("/", response_model=List[FarmerResponse])
def list_farmers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all registered farmers with pagination."""
    return db.query(Farmer).offset(skip).limit(limit).all()


@router.get("/{farmer_id}", response_model=FarmerResponse)
def get_farmer(farmer_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific farmer by ID."""
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise ResourceNotFoundError("Farmer", farmer_id)
    return farmer


@router.put("/{farmer_id}", response_model=FarmerResponse)
def update_farmer(farmer_id: int, farmer_in: FarmerUpdate, db: Session = Depends(get_db)):
    """Update profile information for a farmer."""
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise ResourceNotFoundError("Farmer", farmer_id)

    update_data = farmer_in.model_dump(exclude_unset=True)
    if "email" in update_data and update_data["email"] != farmer.email:
        email_check = db.query(Farmer).filter(Farmer.email == update_data["email"]).first()
        if email_check:
            raise DuplicateResourceError("Farmer", f"Email '{update_data['email']}' is already in use")

    for key, value in update_data.items():
        setattr(farmer, key, value)

    db.commit()
    db.refresh(farmer)
    return farmer


@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farmer(farmer_id: int, db: Session = Depends(get_db)):
    """Delete a farmer and associated fields/sensors via cascade."""
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise ResourceNotFoundError("Farmer", farmer_id)

    db.delete(farmer)
    db.commit()
    return None

