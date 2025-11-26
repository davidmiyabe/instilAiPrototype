# API Setup Guide

## Problem Solved

The error you were seeing (`ECONNREFUSED`) was caused by the frontend trying to connect to a backend API server that wasn't running. I've created and started a FastAPI server that provides the dashboard endpoints your frontend needs.

## What's Been Set Up

### 1. FastAPI Backend Server (`api.py`)

Created a complete REST API with the following endpoints:

- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/dashboard/recent-activity` - Recent activity feed
- `GET /api/v1/constituents` - List all constituents (with pagination)
- `GET /api/v1/constituents/{id}` - Get specific constituent details
- `GET /health` - Health check endpoint

### 2. Database with Sample Data

- Initialized the SQLite database (`nonprofit_crm.db`)
- Added sample data:
  - 5 constituents
  - 4 contributions
  - 3 interactions
  - 2 opportunities

### 3. Server Running

The API server is currently running on **http://localhost:8000**

You can test it:
```bash
curl http://localhost:8000/api/v1/dashboard/stats
curl http://localhost:8000/api/v1/dashboard/recent-activity
```

## Connecting Your Frontend

### Option 1: Configure Vite Proxy (Recommended)

If you're using Vite for your frontend, add this to your `vite.config.ts` or `vite.config.js`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
```

After adding this configuration, restart your Vite dev server.

### Option 2: Update API Base URL

If your frontend uses an API client or base URL configuration, update it to point to:
```
http://localhost:8000
```

## Starting the API Server (Future Sessions)

To start the API server in future sessions:

```bash
# Install dependencies (if needed)
pip install -r requirements.txt

# Start the server
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables auto-reload during development.

## API Response Examples

### Dashboard Stats
```json
{
  "total_constituents": 5,
  "total_contributions": {
    "count": 4,
    "amount": 31500.0
  },
  "average_gift": 7875.0,
  "recent_interactions": 3,
  "active_opportunities": {
    "count": 2,
    "pipeline_value": 60000.0
  },
  "constituent_breakdown": {
    "Board Member": 1,
    "Donor": 2,
    "Major Donor": 1,
    "Volunteer": 1
  }
}
```

### Recent Activity
```json
{
  "activities": [
    {
      "id": "interaction-3",
      "type": "interaction",
      "date": "2025-11-26",
      "title": "Email",
      "description": "Email with Emily Davis",
      "subject": "Major gift proposal follow-up",
      "constituent_name": "Emily Davis",
      "constituent_id": 4,
      "staff_member": "Development Director"
    },
    {
      "id": "contribution-4",
      "type": "contribution",
      "date": "2025-11-25",
      "title": "New Stock Contribution",
      "description": "Emily Davis contributed $25000.00",
      "amount": 25000.0,
      "constituent_name": "Emily Davis",
      "constituent_id": 4
    }
  ]
}
```

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (common Vite default)
- `http://localhost:5173` (Vite's fallback port)

If your frontend runs on a different port, update the CORS configuration in `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:YOUR_PORT"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Next Steps

1. Update your Vite configuration to proxy API requests to port 8000
2. Restart your Vite dev server
3. The frontend should now successfully connect to the API

If you continue to see errors, check:
- The API server is running (`curl http://localhost:8000/health`)
- Your Vite config has the correct proxy settings
- No firewall is blocking port 8000
