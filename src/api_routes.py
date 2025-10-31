"""
REST API routes for frontend data access
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional
from datetime import datetime, timedelta

from .database import get_db, Event, Showing, Listing, Prospect
from .schemas import (
    EventResponse,
    ShowingResponse,
    ListingResponse,
    ProspectResponse,
    PaginatedResponse
)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["API"])


# ==================== EVENTS ENDPOINTS ====================

@router.get("/events", response_model=PaginatedResponse)
async def get_events(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    action: Optional[str] = Query(None, description="Filter by event action"),
    start_date: Optional[datetime] = Query(None, description="Filter events from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events until this date"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of events
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 100)
    - action: Filter by event action type
    - start_date: Filter events from this date
    - end_date: Filter events until this date
    """
    query = db.query(Event)
    
    # Apply filters
    if action:
        query = query.filter(Event.action == action)
    if start_date:
        query = query.filter(Event.created_at >= start_date)
    if end_date:
        query = query.filter(Event.created_at <= end_date)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    events = query.order_by(desc(Event.created_at)).offset(offset).limit(page_size).all()
    
    # Convert to response schema
    items = [EventResponse.model_validate(event) for event in events]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: Session = Depends(get_db)):
    """Get a specific event by event_id"""
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found"
        )
    return EventResponse.model_validate(event)


@router.get("/events/actions/list")
async def get_event_actions(db: Session = Depends(get_db)):
    """Get list of all unique event actions"""
    actions = db.query(Event.action).distinct().all()
    return {"actions": [action[0] for action in actions]}


# ==================== SHOWINGS ENDPOINTS ====================

@router.get("/showings", response_model=PaginatedResponse)
async def get_showings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    listing_uid: Optional[str] = Query(None, description="Filter by listing UID"),
    email: Optional[str] = Query(None, description="Filter by prospect email"),
    start_date: Optional[datetime] = Query(None, description="Filter showings from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter showings until this date"),
    is_self_show: Optional[bool] = Query(None, description="Filter by self-show status"),
    status_filter: Optional[str] = Query(None, description="Filter by status: confirmed, canceled, pending"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of showings
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 100)
    - listing_uid: Filter by listing UID
    - email: Filter by prospect email
    - start_date: Filter showings from this date
    - end_date: Filter showings until this date
    - is_self_show: Filter by self-show status
    - status_filter: Filter by status (confirmed, canceled, pending)
    """
    query = db.query(Showing)
    
    # Apply filters
    if listing_uid:
        query = query.filter(Showing.listing_uid == listing_uid)
    if email:
        query = query.filter(Showing.email == email)
    if start_date:
        query = query.filter(Showing.showtime >= start_date)
    if end_date:
        query = query.filter(Showing.showtime <= end_date)
    if is_self_show is not None:
        query = query.filter(Showing.is_self_show == is_self_show)
    
    # Status filter
    if status_filter:
        if status_filter == "confirmed":
            query = query.filter(Showing.confirmed_at.isnot(None), Showing.canceled_at.is_(None))
        elif status_filter == "canceled":
            query = query.filter(Showing.canceled_at.isnot(None))
        elif status_filter == "pending":
            query = query.filter(Showing.confirmed_at.is_(None), Showing.canceled_at.is_(None))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    showings = query.order_by(desc(Showing.showtime)).offset(offset).limit(page_size).all()
    
    # Convert to response schema
    items = [ShowingResponse.model_validate(showing) for showing in showings]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/showings/{showing_uid}", response_model=ShowingResponse)
async def get_showing(showing_uid: str, db: Session = Depends(get_db)):
    """Get a specific showing by UID"""
    showing = db.query(Showing).filter(Showing.uid == showing_uid).first()
    if not showing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Showing {showing_uid} not found"
        )
    return ShowingResponse.model_validate(showing)


@router.get("/showings/upcoming/list", response_model=List[ShowingResponse])
async def get_upcoming_showings(
    days: int = Query(7, ge=1, le=90, description="Number of days ahead"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get upcoming showings within the next N days"""
    now = datetime.utcnow()
    future_date = now + timedelta(days=days)
    
    showings = db.query(Showing).filter(
        Showing.showtime >= now,
        Showing.showtime <= future_date,
        Showing.canceled_at.is_(None)
    ).order_by(Showing.showtime).limit(limit).all()
    
    return [ShowingResponse.model_validate(showing) for showing in showings]


# ==================== LISTINGS ENDPOINTS ====================

@router.get("/listings", response_model=PaginatedResponse)
async def get_listings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in address"),
    min_showings: Optional[int] = Query(None, description="Minimum number of showings"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of listings
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 100)
    - search: Search in address
    - min_showings: Minimum number of showings
    """
    query = db.query(Listing)
    
    # Apply filters
    if search:
        query = query.filter(Listing.full_address.ilike(f"%{search}%"))
    if min_showings is not None:
        query = query.filter(Listing.total_showings >= min_showings)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    listings = query.order_by(desc(Listing.last_seen_at)).offset(offset).limit(page_size).all()
    
    # Convert to response schema
    items = [ListingResponse.model_validate(listing) for listing in listings]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/listings/{listing_uid}", response_model=ListingResponse)
async def get_listing(listing_uid: str, db: Session = Depends(get_db)):
    """Get a specific listing by UID"""
    listing = db.query(Listing).filter(Listing.uid == listing_uid).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing {listing_uid} not found"
        )
    return ListingResponse.model_validate(listing)


@router.get("/listings/{listing_uid}/showings", response_model=List[ShowingResponse])
async def get_listing_showings(
    listing_uid: str,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get all showings for a specific listing"""
    showings = db.query(Showing).filter(
        Showing.listing_uid == listing_uid
    ).order_by(desc(Showing.showtime)).limit(limit).all()
    
    return [ShowingResponse.model_validate(showing) for showing in showings]


# ==================== PROSPECTS ENDPOINTS ====================

@router.get("/prospects", response_model=PaginatedResponse)
async def get_prospects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in name, email, or phone"),
    min_showings: Optional[int] = Query(None, description="Minimum number of showings"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of prospects
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 100)
    - search: Search in name, email, or phone
    - min_showings: Minimum number of showings
    """
    query = db.query(Prospect)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Prospect.name.ilike(f"%{search}%"),
                Prospect.email.ilike(f"%{search}%"),
                Prospect.phone.ilike(f"%{search}%")
            )
        )
    if min_showings is not None:
        query = query.filter(Prospect.total_showings >= min_showings)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    prospects = query.order_by(desc(Prospect.last_contact_at)).offset(offset).limit(page_size).all()
    
    # Convert to response schema
    items = [ProspectResponse.model_validate(prospect) for prospect in prospects]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/prospects/{email}", response_model=ProspectResponse)
async def get_prospect(email: str, db: Session = Depends(get_db)):
    """Get a specific prospect by email"""
    prospect = db.query(Prospect).filter(Prospect.email == email).first()
    if not prospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prospect {email} not found"
        )
    return ProspectResponse.model_validate(prospect)


@router.get("/prospects/{email}/showings", response_model=List[ShowingResponse])
async def get_prospect_showings(
    email: str,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get all showings for a specific prospect"""
    showings = db.query(Showing).filter(
        Showing.email == email
    ).order_by(desc(Showing.showtime)).limit(limit).all()
    
    return [ShowingResponse.model_validate(showing) for showing in showings]


# ==================== STATISTICS ENDPOINTS ====================

@router.get("/stats/overview")
async def get_stats_overview(db: Session = Depends(get_db)):
    """Get overview statistics"""
    total_events = db.query(func.count(Event.id)).scalar()
    total_showings = db.query(func.count(Showing.id)).scalar()
    total_listings = db.query(func.count(Listing.id)).scalar()
    total_prospects = db.query(func.count(Prospect.id)).scalar()
    
    # Upcoming showings (next 7 days)
    now = datetime.utcnow()
    future_date = now + timedelta(days=7)
    upcoming_showings = db.query(func.count(Showing.id)).filter(
        Showing.showtime >= now,
        Showing.showtime <= future_date,
        Showing.canceled_at.is_(None)
    ).scalar()
    
    # Recent events (last 24 hours)
    past_24h = now - timedelta(hours=24)
    recent_events = db.query(func.count(Event.id)).filter(
        Event.created_at >= past_24h
    ).scalar()
    
    return {
        "total_events": total_events,
        "total_showings": total_showings,
        "total_listings": total_listings,
        "total_prospects": total_prospects,
        "upcoming_showings": upcoming_showings,
        "recent_events_24h": recent_events
    }


@router.get("/stats/showings-by-date")
async def get_showings_by_date(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: Session = Depends(get_db)
):
    """Get showings count grouped by date"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        func.date(Showing.showtime).label('date'),
        func.count(Showing.id).label('count')
    ).filter(
        Showing.showtime >= start_date
    ).group_by(
        func.date(Showing.showtime)
    ).order_by('date').all()
    
    return {
        "data": [
            {"date": str(result.date), "count": result.count}
            for result in results
        ]
    }
