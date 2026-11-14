"""
Field management router.

Provides CRUD endpoints for agricultural fields with GPS coordinates
and relationships to farmers, crops, and sensors.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.field import Field
from ..models.farmer import Farmer
from ..models.crop import Crop
from ..schemas.field import FieldCreate, FieldUpdate, FieldResponse
from ..utils.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/fields", tags=["Fields"])


@router.post("/", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
def create_field(field_in: FieldCreate, db: Session = Depends(get_db)):
    """Register a new agricultural field."""
    farmer = db.query(Farmer).filter(Farmer.id == field_in.farmer_id).first()
    if not farmer:
        raise ResourceNotFoundError("Farmer", field_in.farmer_id)

    if field_in.crop_id:
        crop = db.query(Crop).filter(Crop.id == field_in.crop_id).first()
        if not crop:
            raise ResourceNotFoundError("Crop", field_in.crop_id)

    field = Field(**field_in.model_dump())
    db.add(field)
    db.commit()
    db.refresh(field)
    return field


@router.get("/", response_model=List[FieldResponse])
def list_fields(
    farmer_id: Optional[int] = Query(None, description="Filter fields by farmer ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all registered fields, optionally filtered by farmer ID."""
    query = db.query(Field)
    if farmer_id is not None:
        query = query.filter(Field.farmer_id == farmer_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{field_id}", response_model=FieldResponse)
def get_field(field_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific field, including registered sensors."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise ResourceNotFoundError("Field", field_id)
    return field


@router.put("/{field_id}", response_model=FieldResponse)
def update_field(field_id: int, field_in: FieldUpdate, db: Session = Depends(get_db)):
    """Update details for an existing field."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise ResourceNotFoundError("Field", field_id)

    update_data = field_in.model_dump(exclude_unset=True)

    if "farmer_id" in update_data and update_data["farmer_id"] is not None:
        farmer = db.query(Farmer).filter(Farmer.id == update_data["farmer_id"]).first()
        if not farmer:
            raise ResourceNotFoundError("Farmer", update_data["farmer_id"])

    if "crop_id" in update_data and update_data["crop_id"] is not None:
        crop = db.query(Crop).filter(Crop.id == update_data["crop_id"]).first()
        if not crop:
            raise ResourceNotFoundError("Crop", update_data["crop_id"])

    for key, value in update_data.items():
        setattr(field, key, value)

    db.commit()
    db.refresh(field)
    return field


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field(field_id: int, db: Session = Depends(get_db)):
    """Delete a field and its attached sensors."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise ResourceNotFoundError("Field", field_id)

    db.delete(field)
    db.commit()
    return None

