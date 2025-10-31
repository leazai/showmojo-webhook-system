"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class ShowingData(BaseModel):
    """Schema for showing data within webhook payload"""
    uid: str
    created_at: Optional[datetime] = None
    showtime: Optional[datetime] = None
    showing_time_zone: Optional[str] = None
    showing_time_zone_utc_offset: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    listing_uid: Optional[str] = None
    listing_full_address: Optional[str] = None
    is_self_show: Optional[bool] = None
    confirmed_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    self_show_code_distributed_at: Optional[datetime] = None


class EventData(BaseModel):
    """Schema for event data within webhook payload"""
    id: str = Field(..., alias="id")
    action: str
    actor: Optional[str] = None
    team_member_name: Optional[str] = None
    team_member_uid: Optional[str] = None
    created_at: datetime
    showing: Optional[ShowingData] = None


class WebhookPayload(BaseModel):
    """Schema for complete webhook payload from ShowMojo"""
    event: EventData

    class Config:
        allow_population_by_field_name = True


class WebhookResponse(BaseModel):
    """Schema for webhook response"""
    status: str
    message: str
    event_id: Optional[str] = None


class EventResponse(BaseModel):
    """Schema for event response"""
    id: int
    event_id: str
    action: str
    actor: Optional[str] = None
    team_member_name: Optional[str] = None
    team_member_uid: Optional[str] = None
    created_at: datetime
    received_at: datetime

    class Config:
        orm_mode = True


class ShowingResponse(BaseModel):
    """Schema for showing response"""
    id: int
    uid: str
    event_id: str
    created_at: Optional[datetime] = None
    showtime: Optional[datetime] = None
    showing_time_zone: Optional[str] = None
    showing_time_zone_utc_offset: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    listing_uid: Optional[str] = None
    listing_full_address: Optional[str] = None
    is_self_show: Optional[bool] = None
    confirmed_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    self_show_code_distributed_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        orm_mode = True


class ListingResponse(BaseModel):
    """Schema for listing response"""
    id: int
    uid: str
    full_address: str
    first_seen_at: datetime
    last_seen_at: datetime
    total_showings: int

    class Config:
        orm_mode = True


class ProspectResponse(BaseModel):
    """Schema for prospect response"""
    id: int
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    first_contact_at: datetime
    last_contact_at: datetime
    total_showings: int

    class Config:
        orm_mode = True


class PaginatedResponse(BaseModel):
    """Schema for paginated responses"""
    total: int
    page: int
    page_size: int
    items: list
