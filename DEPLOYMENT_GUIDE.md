# ShowMojo Webhook System - Deployment Guide

This comprehensive guide will help you deploy the ShowMojo Webhook System to production and connect it to your Lovable website frontend.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment Options](#production-deployment-options)
4. [Database Setup](#database-setup)
5. [Connecting to Lovable Frontend](#connecting-to-lovable-frontend)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Prerequisites

Before deploying, ensure you have:

- **Python 3.11+** installed
- **PostgreSQL 12+** database (or access to a hosted PostgreSQL service)
- **ShowMojo API Token**: `27ac6aadb42bb1fa05ef6167c5572674`
- **Git** for version control
- A hosting platform account (Heroku, Render, Railway, or VPS)

---

## Local Development Setup

### Step 1: Install Dependencies

```bash
cd showmojo-webhook-system
pip install -r requirements.txt
```

### Step 2: Configure Environment

Copy the example environment file and update it:

```bash
cp .env.example .env
```

Edit `.env` with your local PostgreSQL credentials:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/showmojo_db
SHOWMOJO_BEARER_TOKEN=27ac6aadb42bb1fa05ef6167c5572674
HOST=0.0.0.0
PORT=8000
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
SECRET_KEY=dev_secret_key_change_in_production
```

### Step 3: Initialize Database

```bash
# Create database
createdb showmojo_db

# Initialize tables
python src/database.py
```

### Step 4: Run the Application

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` to see the API documentation.

---

## Production Deployment Options

### Option 1: Deploy to Render (Recommended)

**Render** provides free PostgreSQL hosting and easy Python deployment.

#### Steps:

1. **Create a Render Account**: Sign up at [render.com](https://render.com)

2. **Create a PostgreSQL Database**:
   - Go to Dashboard → New → PostgreSQL
   - Name: `showmojo-db`
   - Plan: Free or Starter
   - Copy the **Internal Database URL** (starts with `postgresql://`)

3. **Create a Web Service**:
   - Go to Dashboard → New → Web Service
   - Connect your Git repository
   - Name: `showmojo-webhook-system`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**:
   ```
   DATABASE_URL=<your_internal_database_url>
   SHOWMOJO_BEARER_TOKEN=27ac6aadb42bb1fa05ef6167c5572674
   HOST=0.0.0.0
   PORT=10000
   DEBUG=False
   ALLOWED_ORIGINS=https://your-lovable-site.com
   SECRET_KEY=<generate_a_strong_random_key>
   ```

5. **Deploy**: Click "Create Web Service"

6. **Initialize Database**: After deployment, run:
   ```bash
   # Using Render Shell
   python src/database.py
   ```

Your webhook URL will be: `https://showmojo-webhook-system.onrender.com/webhook`

---

### Option 2: Deploy to Railway

**Railway** offers simple deployment with automatic PostgreSQL provisioning.

#### Steps:

1. **Create a Railway Account**: Sign up at [railway.app](https://railway.app)

2. **Create a New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Add PostgreSQL**:
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically create a `DATABASE_URL` variable

4. **Set Environment Variables**:
   ```
   SHOWMOJO_BEARER_TOKEN=27ac6aadb42bb1fa05ef6167c5572674
   DEBUG=False
   ALLOWED_ORIGINS=https://your-lovable-site.com
   SECRET_KEY=<generate_a_strong_random_key>
   ```

5. **Configure Start Command**:
   - In Settings → Deploy, set:
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

6. **Deploy**: Railway will automatically deploy

7. **Initialize Database**: Use Railway CLI or web shell:
   ```bash
   python src/database.py
   ```

Your webhook URL will be: `https://your-app.up.railway.app/webhook`

---

### Option 3: Deploy to Heroku

**Heroku** is a classic PaaS with excellent PostgreSQL support.

#### Steps:

1. **Install Heroku CLI**: Download from [heroku.com/cli](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create a Heroku App**:
   ```bash
   heroku create showmojo-webhook-system
   ```

4. **Add PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **Set Environment Variables**:
   ```bash
   heroku config:set SHOWMOJO_BEARER_TOKEN=27ac6aadb42bb1fa05ef6167c5572674
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_ORIGINS=https://your-lovable-site.com
   heroku config:set SECRET_KEY=<generate_a_strong_random_key>
   ```

6. **Create a `Procfile`** in the project root:
   ```
   web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

7. **Deploy**:
   ```bash
   git push heroku main
   ```

8. **Initialize Database**:
   ```bash
   heroku run python src/database.py
   ```

Your webhook URL will be: `https://showmojo-webhook-system.herokuapp.com/webhook`

---

## Database Setup

### PostgreSQL Configuration

The system uses PostgreSQL with the following schema:

- **events**: Stores all webhook events
- **showings**: Stores showing details
- **listings**: Stores unique listings
- **prospects**: Stores unique prospects

### Manual Database Initialization

If automatic initialization doesn't work, run the SQL script manually:

```bash
psql $DATABASE_URL < database/init.sql
```

### Database Migrations

For schema changes, consider using **Alembic**:

```bash
pip install alembic
alembic init alembic
# Configure alembic.ini and create migrations
```

---

## Connecting to Lovable Frontend

### Step 1: Get Your API Base URL

After deployment, your API base URL will be:
- Render: `https://showmojo-webhook-system.onrender.com`
- Railway: `https://your-app.up.railway.app`
- Heroku: `https://showmojo-webhook-system.herokuapp.com`

### Step 2: Configure CORS

Ensure your Lovable frontend URL is in the `ALLOWED_ORIGINS` environment variable:

```env
ALLOWED_ORIGINS=https://your-lovable-site.com,https://www.your-lovable-site.com
```

### Step 3: API Endpoints for Frontend

Your Lovable frontend can use these endpoints:

#### Get All Showings
```javascript
fetch('https://your-api-url.com/api/v1/showings?page=1&page_size=50')
  .then(response => response.json())
  .then(data => console.log(data));
```

#### Get Upcoming Showings
```javascript
fetch('https://your-api-url.com/api/v1/showings/upcoming/list?days=7')
  .then(response => response.json())
  .then(data => console.log(data));
```

#### Get All Listings
```javascript
fetch('https://your-api-url.com/api/v1/listings?page=1&page_size=50')
  .then(response => response.json())
  .then(data => console.log(data));
```

#### Get Listing Details
```javascript
fetch('https://your-api-url.com/api/v1/listings/lst-456')
  .then(response => response.json())
  .then(data => console.log(data));
```

#### Get Statistics Overview
```javascript
fetch('https://your-api-url.com/api/v1/stats/overview')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Step 4: Example React Component

```jsx
import React, { useEffect, useState } from 'react';

function ShowingsTable() {
  const [showings, setShowings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://your-api-url.com/api/v1/showings?page=1&page_size=50')
      .then(response => response.json())
      .then(data => {
        setShowings(data.items);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching showings:', error);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Showtime</th>
          <th>Address</th>
        </tr>
      </thead>
      <tbody>
        {showings.map(showing => (
          <tr key={showing.uid}>
            <td>{showing.name}</td>
            <td>{showing.email}</td>
            <td>{new Date(showing.showtime).toLocaleString()}</td>
            <td>{showing.listing_full_address}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default ShowingsTable;
```

---

## Monitoring and Maintenance

### Logging

The application logs all webhook events and errors. To view logs:

- **Render**: Dashboard → Logs
- **Railway**: Project → Deployments → Logs
- **Heroku**: `heroku logs --tail`

### Health Checks

Monitor the application health using the `/health` endpoint:

```bash
curl https://your-api-url.com/health
```

Expected response:
```json
{"status": "healthy"}
```

### Database Backups

**Render**: Automatic daily backups on paid plans
**Railway**: Automatic backups on Pro plan
**Heroku**: Use `heroku pg:backups:capture`

### Scaling

If you receive high webhook traffic, consider:

1. **Increase worker processes**: Use Gunicorn with multiple workers
   ```
   gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Add connection pooling**: Already configured in `database.py`

3. **Enable database read replicas**: For heavy read operations

---

## Troubleshooting

### Webhook Not Receiving Data

1. Check ShowMojo webhook configuration
2. Verify bearer token matches
3. Check application logs for errors
4. Test webhook manually:
   ```bash
   curl -X POST https://your-api-url.com/webhook \
     -H "Authorization: Bearer 27ac6aadb42bb1fa05ef6167c5572674" \
     -H "Content-Type: application/json" \
     -d '{"event":{"id":"test-123","action":"lead_created","created_at":"2025-10-31T10:00:00Z"}}'
   ```

### Database Connection Issues

1. Verify `DATABASE_URL` is correct
2. Check database is running
3. Ensure firewall allows connections
4. Test connection:
   ```bash
   psql $DATABASE_URL
   ```

### CORS Errors

1. Add your frontend URL to `ALLOWED_ORIGINS`
2. Restart the application
3. Clear browser cache

---

## Next Steps

1. **Configure ShowMojo Webhook**: Add your deployed webhook URL to ShowMojo
2. **Test Webhook**: Trigger a test event in ShowMojo
3. **Build Frontend**: Use the API endpoints in your Lovable frontend
4. **Monitor**: Check logs regularly for errors
5. **Scale**: Upgrade your hosting plan as traffic grows

For support, refer to the API documentation at `https://your-api-url.com/docs`.
