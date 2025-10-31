"""
Webhook processing service for ShowMojo webhooks
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Dict, Any
import logging

from .database import Event, Showing, Listing, Prospect
from .schemas import WebhookPayload

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebhookService:
    """Service for processing ShowMojo webhook payloads"""

    @staticmethod
    def process_webhook(payload: Dict[Any, Any], db: Session) -> Dict[str, Any]:
        """
        Process incoming webhook payload and store in database
        
        Args:
            payload: Raw webhook payload dictionary
            db: Database session
            
        Returns:
            Dictionary with processing status and details
        """
        try:
            # Validate payload structure
            webhook_data = WebhookPayload(**payload)
            event_data = webhook_data.event

            # Check if event already exists (idempotency)
            existing_event = db.query(Event).filter(Event.event_id == event_data.id).first()
            if existing_event:
                logger.info(f"Event {event_data.id} already processed, skipping")
                return {
                    "status": "duplicate",
                    "message": "Event already processed",
                    "event_id": event_data.id
                }

            # Create event record
            event = Event(
                event_id=event_data.id,
                action=event_data.action,
                actor=event_data.actor,
                team_member_name=event_data.team_member_name,
                team_member_uid=event_data.team_member_uid,
                created_at=event_data.created_at,
                received_at=datetime.utcnow(),
                raw_payload=payload
            )
            db.add(event)
            db.flush()  # Flush to get event ID for foreign key

            # Process showing data if present
            if event_data.showing:
                showing_data = event_data.showing
                
                # Check if showing already exists
                existing_showing = db.query(Showing).filter(Showing.uid == showing_data.uid).first()
                
                if existing_showing:
                    # Update existing showing
                    existing_showing.event_id = event_data.id
                    existing_showing.showtime = showing_data.showtime
                    existing_showing.showing_time_zone = showing_data.showing_time_zone
                    existing_showing.showing_time_zone_utc_offset = showing_data.showing_time_zone_utc_offset
                    existing_showing.name = showing_data.name
                    existing_showing.phone = showing_data.phone
                    existing_showing.email = showing_data.email
                    existing_showing.notes = showing_data.notes
                    existing_showing.listing_uid = showing_data.listing_uid
                    existing_showing.listing_full_address = showing_data.listing_full_address
                    existing_showing.is_self_show = showing_data.is_self_show
                    existing_showing.confirmed_at = showing_data.confirmed_at
                    existing_showing.canceled_at = showing_data.canceled_at
                    existing_showing.self_show_code_distributed_at = showing_data.self_show_code_distributed_at
                    logger.info(f"Updated showing {showing_data.uid}")
                else:
                    # Create new showing
                    showing = Showing(
                        uid=showing_data.uid,
                        event_id=event_data.id,
                        created_at=showing_data.created_at,
                        showtime=showing_data.showtime,
                        showing_time_zone=showing_data.showing_time_zone,
                        showing_time_zone_utc_offset=showing_data.showing_time_zone_utc_offset,
                        name=showing_data.name,
                        phone=showing_data.phone,
                        email=showing_data.email,
                        notes=showing_data.notes,
                        listing_uid=showing_data.listing_uid,
                        listing_full_address=showing_data.listing_full_address,
                        is_self_show=showing_data.is_self_show,
                        confirmed_at=showing_data.confirmed_at,
                        canceled_at=showing_data.canceled_at,
                        self_show_code_distributed_at=showing_data.self_show_code_distributed_at
                    )
                    db.add(showing)
                    logger.info(f"Created showing {showing_data.uid}")

                # Update or create listing
                if showing_data.listing_uid and showing_data.listing_full_address:
                    WebhookService._upsert_listing(
                        db,
                        showing_data.listing_uid,
                        showing_data.listing_full_address
                    )

                # Update or create prospect
                if showing_data.email:
                    WebhookService._upsert_prospect(
                        db,
                        showing_data.email,
                        showing_data.name,
                        showing_data.phone
                    )

            # Commit transaction
            db.commit()
            logger.info(f"Successfully processed event {event_data.id} with action {event_data.action}")

            return {
                "status": "success",
                "message": "Webhook processed successfully",
                "event_id": event_data.id
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def _upsert_listing(db: Session, listing_uid: str, full_address: str):
        """
        Update or insert listing record
        
        Args:
            db: Database session
            listing_uid: Listing unique identifier
            full_address: Full address of the listing
        """
        listing = db.query(Listing).filter(Listing.uid == listing_uid).first()
        
        if listing:
            # Update existing listing
            listing.last_seen_at = datetime.utcnow()
            listing.total_showings = db.query(func.count(Showing.id)).filter(
                Showing.listing_uid == listing_uid
            ).scalar()
            logger.info(f"Updated listing {listing_uid}")
        else:
            # Create new listing
            listing = Listing(
                uid=listing_uid,
                full_address=full_address,
                first_seen_at=datetime.utcnow(),
                last_seen_at=datetime.utcnow(),
                total_showings=1
            )
            db.add(listing)
            logger.info(f"Created listing {listing_uid}")

    @staticmethod
    def _upsert_prospect(db: Session, email: str, name: str = None, phone: str = None):
        """
        Update or insert prospect record
        
        Args:
            db: Database session
            email: Prospect email address
            name: Prospect name
            phone: Prospect phone number
        """
        prospect = db.query(Prospect).filter(Prospect.email == email).first()
        
        if prospect:
            # Update existing prospect
            if name:
                prospect.name = name
            if phone:
                prospect.phone = phone
            prospect.last_contact_at = datetime.utcnow()
            prospect.total_showings = db.query(func.count(Showing.id)).filter(
                Showing.email == email
            ).scalar()
            logger.info(f"Updated prospect {email}")
        else:
            # Create new prospect
            prospect = Prospect(
                email=email,
                name=name,
                phone=phone,
                first_contact_at=datetime.utcnow(),
                last_contact_at=datetime.utcnow(),
                total_showings=1
            )
            db.add(prospect)
            logger.info(f"Created prospect {email}")
