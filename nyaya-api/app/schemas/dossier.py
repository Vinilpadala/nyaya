from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class DossierItemCreateDTO(BaseModel):
    item_type: str = "CASE"  # CASE, SECTION, NOTE
    reference_id: str = ""
    title: str
    excerpt: str = ""
    pinpoint: str = ""


class DossierItemDTO(DossierItemCreateDTO):
    id: str
    dossier_id: str

    class Config:
        from_attributes = True


class DossierCreateDTO(BaseModel):
    matter_title: str
    suit_number: str
    judicial_notes: str = ""
    items: List[DossierItemCreateDTO] = []


class DossierDTO(BaseModel):
    id: str
    user_id: str
    matter_title: str
    suit_number: str
    judicial_notes: str
    created_at: datetime
    updated_at: datetime
    items: List[DossierItemDTO] = []

    class Config:
        from_attributes = True


class DossierUpdateDTO(BaseModel):
    matter_title: Optional[str] = None
    suit_number: Optional[str] = None
    judicial_notes: Optional[str] = None

