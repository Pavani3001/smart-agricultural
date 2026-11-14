"""
Crop configuration router.

Provides CRUD endpoints for crop types, growth stages, and optimal moisture limits.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.crop import Crop
from ..schemas.crop import CropCreate, CropUpdate, CropResponse
from ..utils.exceptions import ResourceNotFoundError, DuplicateResourceError

router = APIRouter(prefix="/crops", tags=["Crops"])


@router.post("/", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
def create_crop(crop_in: CropCreate, db: Session = Depends(get_db)):
    """Add a new crop configuration."""
    existing = db.query(Crop).filter(Crop.crop_name == crop_in.crop_name).first()
    if existing:
        raise DuplicateResourceError("Crop", f"Crop '{crop_in.crop_name}' already exists")

    crop = Crop(**crop_in.model_dump())
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


@router.get("/", response_model=List[CropResponse])
def list_crops(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all registered crop configurations."""
    return db.query(Crop).offset(skip).limit(limit).all()


@router.get("/{crop_id}", response_model=CropResponse)
def get_crop(crop_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific crop by ID."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise ResourceNotFoundError("Crop", crop_id)
    return crop


@router.put("/{crop_id}", response_model=CropResponse)
def update_crop(crop_id: int, crop_in: CropUpdate, db: Session = Depends(get_db)):
    """Update configuration for an existing crop."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise ResourceNotFoundError("Crop", crop_id)

    update_data = crop_in.model_dump(exclude_unset=True)
    if "crop_name" in update_data and update_data["crop_name"] != crop.crop_name:
        name_check = db.query(Crop).filter(Crop.crop_name == update_data["crop_name"]).first()
        if name_check:
            raise DuplicateResourceError("Crop", f"Crop name '{update_data['crop_name']}' is already in use")

    for key, value in update_data.items():
        setattr(crop, key, value)

    db.commit()
    db.refresh(crop)
    return crop

