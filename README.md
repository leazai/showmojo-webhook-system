"""
# ShowMojo Webhook System

This project is a real-time webhook listener and database system for ShowMojo. It captures lead and showing data, stores it in a PostgreSQL database, and provides a RESTful API for your frontend to access the data.

## Features

- **Real-time Webhook Listener**: Captures ShowMojo webhook events for leads and showings.
- **PostgreSQL Database**: Stores all data in a structured and reliable database.
- **RESTful API**: Provides endpoints for querying events, showings, listings, and prospects.
- **Data Validation**: Uses Pydantic for robust data validation.
- **Authentication**: Secures the webhook endpoint with a bearer token.
- **CORS Support**: Allows cross-origin requests from your frontend.
- **Paginated API Responses**: Efficiently handles large datasets.
- **Comprehensive Filtering**: Filter API results by various criteria.
- **Statistics Endpoints**: Get an overview of your ShowMojo data.

## Project Structure

```
showmojo-webhook-system/
├── src/                      # Source code
│   ├── __init__.py
│   ├── api_routes.py         # API endpoints for frontend
│   ├── database.py           # Database models and connection
│   ├── main.py               # FastAPI application
│   ├── schemas.py            # Pydantic schemas
│   └── webhook_service.py    # Webhook processing logic
├── database/                 # Database scripts
│   └── init.sql              # Database initialization script
├── tests/                    # Test files
│   └── test_webhook.py
├── .env.example              # Example environment file
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository_url>
cd showmojo-webhook-system
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL Database

1.  Install PostgreSQL on your system.
2.  Create a new database:

    ```sql
    CREATE DATABASE showmojo_db;
    ```

3.  Create a user and grant privileges:

    ```sql
    CREATE USER your_app_user WITH PASSWORD 'your_password';
    GRANT ALL PRIVILEGES ON DATABASE showmojo_db TO your_app_user;
    ```

### 5. Configure Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```
# Database Configuration
DATABASE_URL=postgresql://your_app_user:your_password@localhost:5432/showmojo_db

# ShowMojo API Configuration
SHOWMOJO_BEARER_TOKEN=27ac6aadb42bb1fa05ef6167c5572674

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# CORS Configuration (comma-separated list of allowed origins)
ALLOWED_ORIGINS=http://localhost:3000,https://your-lovable-site.com

# Security
SECRET_KEY=your_super_secret_key_that_you_should_change
```

### 6. Initialize the Database

Run the `database.py` script to create the tables:

```bash
python src/database.py
```

## Running the Application

To run the application, use `uvicorn`:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

For development with auto-reload, set `DEBUG=True` in your `.env` file and run:

```bash
uvicorn src.main:app --reload
```

## Webhook Configuration in ShowMojo

1.  Go to your ShowMojo settings.
2.  Find the **Leads Webhook** section.
3.  Add a new webhook endpoint with the URL of your deployed application (e.g., `https://your-domain.com/webhook`).
4.  Ensure the webhook is configured to send `POST` requests with a `Content-Type` of `application/json`.
5.  Set the **Bearer Token** in ShowMojo to match the `SHOWMOJO_BEARER_TOKEN` in your `.env` file.

## API Documentation

Once the application is running, you can access the interactive API documentation at `http://localhost:8000/docs`.

This will provide a complete overview of all available API endpoints, their parameters, and response schemas.

## Testing

To run the tests, use `pytest`:

```bash
pytest
```

This will run all tests in the `tests/` directory.

## Database Schema

The database schema consists of four main tables:

-   `events`: Stores all incoming webhook events.
-   `showings`: Stores details about each showing.
-   `listings`: Stores unique listing information.
-   `prospects`: Stores unique prospect information.

For detailed schema information, see `database/init.sql`.

## Deployment

This application is ready to be deployed to any platform that supports Python and PostgreSQL, such as Heroku, Render, or a VPS.

### Example: Deploying to Heroku

1.  Create a `Procfile`:

    ```
    web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    ```

2.  Create a Heroku app and add a PostgreSQL add-on.
3.  Set the environment variables in your Heroku app settings.
4.  Push your code to Heroku.

## Connecting to Your Lovable Frontend

Your Lovable frontend can now make requests to the API endpoints provided by this system. For example, to get a list of all showings, you can make a `GET` request to `https://your-domain.com/api/v1/showings`.

Make sure to handle authentication if you decide to protect the API endpoints further.
"""
