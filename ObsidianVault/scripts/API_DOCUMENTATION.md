# Web API Documentation

**Status:** Planned (LTE5) - Not yet implemented

## Overview

REST API for managing PDF ingestion, viewing status, and configuring the system.

## Endpoints (Planned)

### POST /api/ingest
Trigger PDF ingestion.

**Request:**
```json
{
  "pdf_path": "/path/to/file.pdf",
  "overwrite": false
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "pending"
}
```

### GET /api/status/{job_id}
Get ingestion job status.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 50,
  "message": "Processing PDF..."
}
```

### GET /api/config
Get current configuration.

### PUT /api/config
Update configuration.

### GET /api/sources
List all source notes.

### GET /api/health
Health check endpoint.

## WebSocket (Planned)

### WS /api/ws/status
Real-time status updates for ingestion jobs.

## Authentication

Planned: API key or JWT-based authentication.

## Rate Limiting

Planned: Configurable rate limits per endpoint.

---

**Note:** This API is not yet implemented. See `web_api.py` for stub implementation.
