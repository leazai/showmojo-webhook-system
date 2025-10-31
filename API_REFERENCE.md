# ShowMojo Webhook System - API Reference

Complete reference for all API endpoints available in the ShowMojo Webhook System.

## Base URL

```
https://your-api-url.com
```

## Authentication

The webhook endpoint (`/webhook`) requires a Bearer token in the Authorization header:

```
Authorization: Bearer 27ac6aadb42bb1fa05ef6167c5572674
```

All other API endpoints are currently public. Consider adding authentication for production use.

---

## Endpoints

### Health Check

#### `GET /health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Webhook Endpoint

#### `POST /webhook`

Receive webhook events from ShowMojo.

**Headers:**
- `Authorization: Bearer 27ac6aadb42bb1fa05ef6167c5572674`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "event": {
    "id": "evt-123",
    "action": "lead_created",
    "actor": "prospect",
    "team_member_name": "John Manager",
    "team_member_uid": "tm-001",
    "created_at": "2025-10-31T10:00:00Z",
    "showing": {
      "uid": "shw-456",
      "created_at": "2025-10-31T10:00:00Z",
      "showtime": "2025-11-01T14:00:00Z",
      "showing_time_zone": "Central Time (US & Canada)",
      "showing_time_zone_utc_offset": -5,
      "name": "Jane Prospect",
      "phone": "+14155551234",
      "email": "jane@example.com",
      "notes": "Interested in 2BR unit",
      "listing_uid": "lst-789",
      "listing_full_address": "123 Main St, Chicago, IL 60601",
      "is_self_show": true,
      "confirmed_at": "2025-10-31T11:00:00Z",
      "canceled_at": null,
      "self_show_code_distributed_at": "2025-10-31T11:05:00Z"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Webhook processed successfully",
  "event_id": "evt-123"
}
```

---

## Events API

### Get All Events

#### `GET /api/v1/events`

Retrieve a paginated list of all webhook events.

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50, max: 100): Items per page
- `action` (string, optional): Filter by event action type
- `start_date` (datetime, optional): Filter events from this date
- `end_date` (datetime, optional): Filter events until this date

**Example Request:**
```
GET /api/v1/events?page=1&page_size=20&action=lead_created
```

**Response:**
```json
{
  "total": 150,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "event_id": "evt-123",
      "action": "lead_created",
      "actor": "prospect",
      "team_member_name": "John Manager",
      "team_member_uid": "tm-001",
      "created_at": "2025-10-31T10:00:00Z",
      "received_at": "2025-10-31T10:00:01Z"
    }
  ]
}
```

---

### Get Event by ID

#### `GET /api/v1/events/{event_id}`

Retrieve a specific event by its event_id.

**Response:**
```json
{
  "id": 1,
  "event_id": "evt-123",
  "action": "lead_created",
  "actor": "prospect",
  "team_member_name": "John Manager",
  "team_member_uid": "tm-001",
  "created_at": "2025-10-31T10:00:00Z",
  "received_at": "2025-10-31T10:00:01Z"
}
```

---

### Get Event Actions

#### `GET /api/v1/events/actions/list`

Get a list of all unique event action types.

**Response:**
```json
{
  "actions": [
    "lead_created",
    "showing_scheduled",
    "showing_confirmed",
    "showing_canceled"
  ]
}
```

---

## Showings API

### Get All Showings

#### `GET /api/v1/showings`

Retrieve a paginated list of all showings.

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50, max: 100): Items per page
- `listing_uid` (string, optional): Filter by listing UID
- `email` (string, optional): Filter by prospect email
- `start_date` (datetime, optional): Filter showings from this date
- `end_date` (datetime, optional): Filter showings until this date
- `is_self_show` (boolean, optional): Filter by self-show status
- `status_filter` (string, optional): Filter by status (confirmed, canceled, pending)

**Example Request:**
```
GET /api/v1/showings?page=1&page_size=20&status_filter=confirmed
```

**Response:**
```json
{
  "total": 85,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "uid": "shw-456",
      "event_id": "evt-123",
      "created_at": "2025-10-31T10:00:00Z",
      "showtime": "2025-11-01T14:00:00Z",
      "showing_time_zone": "Central Time (US & Canada)",
      "showing_time_zone_utc_offset": -5,
      "name": "Jane Prospect",
      "phone": "+14155551234",
      "email": "jane@example.com",
      "notes": "Interested in 2BR unit",
      "listing_uid": "lst-789",
      "listing_full_address": "123 Main St, Chicago, IL 60601",
      "is_self_show": true,
      "confirmed_at": "2025-10-31T11:00:00Z",
      "canceled_at": null,
      "self_show_code_distributed_at": "2025-10-31T11:05:00Z",
      "updated_at": "2025-10-31T11:00:00Z"
    }
  ]
}
```

---

### Get Showing by UID

#### `GET /api/v1/showings/{showing_uid}`

Retrieve a specific showing by its UID.

**Response:**
```json
{
  "id": 1,
  "uid": "shw-456",
  "event_id": "evt-123",
  "created_at": "2025-10-31T10:00:00Z",
  "showtime": "2025-11-01T14:00:00Z",
  "showing_time_zone": "Central Time (US & Canada)",
  "showing_time_zone_utc_offset": -5,
  "name": "Jane Prospect",
  "phone": "+14155551234",
  "email": "jane@example.com",
  "notes": "Interested in 2BR unit",
  "listing_uid": "lst-789",
  "listing_full_address": "123 Main St, Chicago, IL 60601",
  "is_self_show": true,
  "confirmed_at": "2025-10-31T11:00:00Z",
  "canceled_at": null,
  "self_show_code_distributed_at": "2025-10-31T11:05:00Z",
  "updated_at": "2025-10-31T11:00:00Z"
}
```

---

### Get Upcoming Showings

#### `GET /api/v1/showings/upcoming/list`

Get upcoming showings within the next N days.

**Query Parameters:**
- `days` (integer, default: 7, max: 90): Number of days ahead
- `limit` (integer, default: 100, max: 500): Maximum number of results

**Example Request:**
```
GET /api/v1/showings/upcoming/list?days=14&limit=50
```

**Response:**
```json
[
  {
    "id": 1,
    "uid": "shw-456",
    "showtime": "2025-11-01T14:00:00Z",
    "name": "Jane Prospect",
    "email": "jane@example.com",
    "listing_full_address": "123 Main St, Chicago, IL 60601"
  }
]
```

---

## Listings API

### Get All Listings

#### `GET /api/v1/listings`

Retrieve a paginated list of all listings.

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50, max: 100): Items per page
- `search` (string, optional): Search in address
- `min_showings` (integer, optional): Minimum number of showings

**Example Request:**
```
GET /api/v1/listings?page=1&page_size=20&search=Chicago
```

**Response:**
```json
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "uid": "lst-789",
      "full_address": "123 Main St, Chicago, IL 60601",
      "first_seen_at": "2025-10-01T10:00:00Z",
      "last_seen_at": "2025-10-31T10:00:00Z",
      "total_showings": 15
    }
  ]
}
```

---

### Get Listing by UID

#### `GET /api/v1/listings/{listing_uid}`

Retrieve a specific listing by its UID.

**Response:**
```json
{
  "id": 1,
  "uid": "lst-789",
  "full_address": "123 Main St, Chicago, IL 60601",
  "first_seen_at": "2025-10-01T10:00:00Z",
  "last_seen_at": "2025-10-31T10:00:00Z",
  "total_showings": 15
}
```

---

### Get Listing Showings

#### `GET /api/v1/listings/{listing_uid}/showings`

Get all showings for a specific listing.

**Query Parameters:**
- `limit` (integer, default: 100, max: 500): Maximum number of results

**Response:**
```json
[
  {
    "id": 1,
    "uid": "shw-456",
    "showtime": "2025-11-01T14:00:00Z",
    "name": "Jane Prospect",
    "email": "jane@example.com",
    "listing_uid": "lst-789"
  }
]
```

---

## Prospects API

### Get All Prospects

#### `GET /api/v1/prospects`

Retrieve a paginated list of all prospects.

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50, max: 100): Items per page
- `search` (string, optional): Search in name, email, or phone
- `min_showings` (integer, optional): Minimum number of showings

**Example Request:**
```
GET /api/v1/prospects?page=1&page_size=20&search=jane
```

**Response:**
```json
{
  "total": 120,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "email": "jane@example.com",
      "name": "Jane Prospect",
      "phone": "+14155551234",
      "first_contact_at": "2025-10-01T10:00:00Z",
      "last_contact_at": "2025-10-31T10:00:00Z",
      "total_showings": 3
    }
  ]
}
```

---

### Get Prospect by Email

#### `GET /api/v1/prospects/{email}`

Retrieve a specific prospect by email.

**Response:**
```json
{
  "id": 1,
  "email": "jane@example.com",
  "name": "Jane Prospect",
  "phone": "+14155551234",
  "first_contact_at": "2025-10-01T10:00:00Z",
  "last_contact_at": "2025-10-31T10:00:00Z",
  "total_showings": 3
}
```

---

### Get Prospect Showings

#### `GET /api/v1/prospects/{email}/showings`

Get all showings for a specific prospect.

**Query Parameters:**
- `limit` (integer, default: 100, max: 500): Maximum number of results

**Response:**
```json
[
  {
    "id": 1,
    "uid": "shw-456",
    "showtime": "2025-11-01T14:00:00Z",
    "email": "jane@example.com",
    "listing_full_address": "123 Main St, Chicago, IL 60601"
  }
]
```

---

## Statistics API

### Get Overview Statistics

#### `GET /api/v1/stats/overview`

Get overview statistics for all data.

**Response:**
```json
{
  "total_events": 250,
  "total_showings": 180,
  "total_listings": 45,
  "total_prospects": 120,
  "upcoming_showings": 25,
  "recent_events_24h": 12
}
```

---

### Get Showings by Date

#### `GET /api/v1/stats/showings-by-date`

Get showings count grouped by date.

**Query Parameters:**
- `days` (integer, default: 30, max: 365): Number of days to include

**Example Request:**
```
GET /api/v1/stats/showings-by-date?days=7
```

**Response:**
```json
{
  "data": [
    {
      "date": "2025-10-25",
      "count": 5
    },
    {
      "date": "2025-10-26",
      "count": 8
    },
    {
      "date": "2025-10-27",
      "count": 3
    }
  ]
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently, there are no rate limits. Consider implementing rate limiting in production using tools like `slowapi` or nginx.

---

## Interactive Documentation

Visit `https://your-api-url.com/docs` for interactive API documentation powered by Swagger UI.
