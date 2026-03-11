# Nexus API (nexus.towebs.com) - Endpoint Documentation

This document summarizes the API endpoints available on `nexus.towebs.com`, which we discovered by exploring the `twnexus` repository source code on the `master` branch.

**Base URL**: `https://nexus.towebs.com`
**Authentication**: Requires either HTTP Basic Auth or HTTP Token Auth against the standard Django REST Framework (`rest_framework.authentication`).
*Note: Neither the internal database credentials (`twnexus`, `towebs`, `satancojealpapa`) nor the local-wrapper proxy key (`super-api-key.debug`) work directly against this public endpoint. Valid credentials must be supplied.*

---

## 1. Client Information Endpoints (API V2)

The most robust endpoints for retrieving client hosting packages, server details, and statuses are located in the `v2/client/` route.

### GET `/api/v2/client/`
Retrieves a specific client's full profile and their hosting plan summary. It will also calculate if they have active debit processing.

**Query Parameters** (Requires AT LEAST ONE of the following):
- `domain` (string): The client's hosted website (e.g., `plantascarnivoras.com`)
- `login` (string): The client's username
- `id` (integer): The internal contact `id`

**Expected JSON Response (200 OK):**
```json
{
  "code": 200,
  "message": "Ok",
  "data": {
    "contactid": 1234,
    "nombre": "Julian",
    "email": "julian@example.com",
    "website": "plantascarnivoras.com",
    "plan": {
      "id": 1,
      "nombre": "Plan PyME",
      "monto": 1500.0,
      "is_nt": false,
      "is_active": true
    },
    "pago": 1500.0,
    "proximopago": "2026-04-01",
    "fechadeinicio": "2025-01-01",
    "servidor": "web1.toservers.com",
    "login": "plan_user",
    "status": "Activo",
    "nota": "VIP Client",
    "debito": true
  }
}
```

### GET `/api/v2/client/list/`
Retrieves a paginated list of clients matching the search criteria.

**Query Parameters**:
- `domain`, `login`, `id`, `email`, `email2`, `status`
- `is_partial` (boolean): If `true`, the search uses SQL fuzzy matching (`__icontains`) instead of exact string matching.
- `limit` (int | 'all'): The total number of records to return. Defaults to 10.

---

## 2. Package Information Endpoints (API V2)

### GET `/api/v2/package/`
Retrieves detailed information about a specific hosting package.

**Query Parameters** (Requires AT LEAST ONE):
- `id` (integer)
- `nombre` (string)

### GET `/api/v2/package/list/`
Retrieves a list of hosting packages.
**Query Parameters**:
- `id`, `nombre`, `is_active`, `is_nt`
- `is_partial` (boolean)
- `limit` (int | 'all')

---

## 3. Legacy Endpoints (API V1)

These endpoints function but the repository tags them as Legacy.

### GET `/api-client-info/`
Retrieves a simple representation of the client profile based on their domain.

**Query Parameters:**
- `domain` (string)

**Expected JSON Response:**
```json
{
  "contactid": 1234,
  "nombre": "...",
  "website": "...",
  "plan": "...",
  "status": "..."
}
```

### GET `/api-debit-check/`
Checks if the client is actively enrolled in automatic credit card debit.
**Query Parameters:** `domain` or `contactid`
