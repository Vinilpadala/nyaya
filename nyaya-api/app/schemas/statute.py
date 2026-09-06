from typing import List, Optional
from pydantic import BaseModel


class StatuteSectionDTO(BaseModel):
    id: str
    statute_id: str
    section_number: str
    heading: str
    content: str
    is_amended: bool
    amendment_notes: str
    is_demo_data: bool

    class Config:
        from_attributes = True


class StatuteDTO(BaseModel):
    id: str
    short_title: str
    act_number: str
    enactment_year: int
    jurisdiction: str
    is_demo_data: bool

    class Config:
        from_attributes = True


class StatuteDetailDTO(StatuteDTO):
    sections: List[StatuteSectionDTO] = []
