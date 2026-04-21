# Product Search Agent - API Documentation

Complete REST API documentation for the Product Search Agent application.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Root & Health](#root--health)
  - [Search Requests](#search-requests)
  - [Products](#products)
- [Status Codes](#status-codes)
- [Examples](#examples)

---

## Overview

The Product Search Agent API provides endpoints for managing automated product searches across multiple platforms (Craigslist, Facebook Marketplace, eBay ....). The API follows REST principles and returns JSON responses.

**Key Features:**
- Create and manage search requests
- View scraped products and matches
- Real-time notifications (WebSocket - coming soon)
- Multi-platform search support

---

## Base URL

**Development:**
```
http://localhost:8000
```

**Production:**
```
https://your-domain.com
```

---

## Authentication

🔓 **Current Version:** No authentication required (development)

🔐 **Future Version:** JWT-based authentication will be added for production use.

---

## Response Format

All API responses follow a consistent JSON format:

### Success Response
```json
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2"
}
```

### List Response (Paginated)
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 50
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages.

### Common Error Codes

| Status Code | Meaning | Description |
|------------|---------|-------------|
| 400 | Bad Request | Invalid request data or parameters |
| 404 | Not Found | Resource does not exist |
| 422 | Unprocessable Entity | Validation error in request body |
| 500 | Internal Server Error | Server-side error |

### Error Response Example
```json
{
  "detail": "Search request with id 123e4567-e89b-12d3-a456-426614174000 not found"
}
```

---

## Endpoints

### Root & Health

#### Get API Information
```http
GET /
```

Returns basic API information and links to documentation.

**Response (200 OK):**
```json
{
  "name": "Product Search Agent API",
  "version": "1.0.0",
  "description": "Automated product search across multiple platforms",
  "status": "running",
  "documentation": {
    "swagger": "/docs",
    "redoc": "/redoc",
    "openapi": "/openapi.json"
  },
  "endpoints": {
    "health": "/api/health",
    "search_requests": "/api/search-requests",
    "products": "/api/products"
  }
}
```

---

#### Health Check
```http
GET /api/health
```

Check if the API is running and responsive.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "message": "Product Search Agent API is running",
  "timestamp": "2024-01-01T12:00:00.000000",
  "version": "1.0.0"
}
```

**Use Cases:**
- Monitoring and alerting
- Load balancer health checks
- Container orchestration readiness probes

---

### Search Requests

#### List All Search Requests
```http
GET /api/search-requests
```

Retrieve a paginated list of all search requests with optional filtering.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip (pagination) |
| limit | integer | No | 50 | Maximum records to return (1-100) |
| status | string | No | null | Filter by status: `active`, `paused`, `completed`, `cancelled` |

**Example Requests:**
```bash
# Get first 10 search requests
GET /api/search-requests?skip=0&limit=10

# Get only active searches
GET /api/search-requests?status=active

# Pagination - page 2 with 20 items per page
GET /api/search-requests?skip=20&limit=20
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "product_name": "iPhone 13",
      "product_description": "Looking for iPhone 13 in good condition, 128GB or more",
      "budget": 600.0,
      "location": "Boston, MA",
      "match_threshold": 75.0,
      "status": "active",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

---

#### Get Single Search Request
```http
GET /api/search-requests/{search_request_id}
```

Retrieve detailed information about a specific search request.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| search_request_id | string (UUID) | Yes | Unique identifier of the search request |

**Example Request:**
```bash
GET /api/search-requests/123e4567-e89b-12d3-a456-426614174000
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "product_name": "iPhone 13",
  "product_description": "Looking for iPhone 13 in good condition, 128GB or more",
  "budget": 600.0,
  "location": "Boston, MA",
  "match_threshold": 75.0,
  "status": "active",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Search request with id 123e4567-e89b-12d3-a456-426614174000 not found"
}
```

---

#### Get Search Request Statistics
```http
GET /api/search-requests/{search_request_id}/stats
```

Get summary statistics about a search request's execution history.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| search_request_id | string (UUID) | Yes | Unique identifier of the search request |

**Example Request:**
```bash
GET /api/search-requests/123e4567-e89b-12d3-a456-426614174000/stats
```

**Response (200 OK):**
```json
{
  "search_request_id": "123e4567-e89b-12d3-a456-426614174000",
  "product_name": "iPhone 13",
  "status": "active",
  "total_executions": 5,
  "total_products_found": 125,
  "total_matches_found": 8,
  "average_match_rate": 6.4,
  "last_execution": "2024-01-01T12:00:00"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Search request with id 123e4567-e89b-12d3-a456-426614174000 not found"
}
```

---

#### Create Search Request
```http
POST /api/search-requests
```

Create a new automated search request.

**Request Body:**
```json
{
  "product_name": "iPhone 13",
  "product_description": "Looking for iPhone 13 in good condition, 128GB or more, unlocked preferred",
  "budget": 600.0,
  "location": "Boston, MA",
  "match_threshold": 75.0
}
```

**Request Body Schema:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| product_name | string | Yes | - | Name/title of product to search for |
| product_description | string | Yes | - | Detailed description of desired product |
| budget | number | Yes | - | Maximum price willing to pay |
| location | string | No | null | Geographic location for search |
| match_threshold | number | No | 70.0 | Minimum similarity score (0-100) |

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/search-requests \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 13",
    "product_description": "Looking for iPhone 13 in good condition",
    "budget": 600.0,
    "location": "Boston, MA",
    "match_threshold": 75.0
  }'
```

**Response (201 Created):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "product_name": "iPhone 13",
  "product_description": "Looking for iPhone 13 in good condition",
  "budget": 600.0,
  "location": "Boston, MA",
  "match_threshold": 75.0,
  "status": "active",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "budget"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

#### Update Search Request
```http
PUT /api/search-requests/{search_request_id}
```

Update an existing search request. Only provided fields will be updated.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| search_request_id | string (UUID) | Yes | Unique identifier of the search request |

**Request Body (all fields optional):**
```json
{
  "product_name": "iPhone 13 Pro",
  "product_description": "Updated description",
  "budget": 700.0,
  "location": "Cambridge, MA",
  "match_threshold": 80.0
}
```

**Example Request:**
```bash
curl -X PUT http://localhost:8000/api/search-requests/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "budget": 700.0,
    "match_threshold": 80.0
  }'
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "product_name": "iPhone 13",
  "product_description": "Looking for iPhone 13 in good condition",
  "budget": 700.0,
  "location": "Boston, MA",
  "match_threshold": 80.0,
  "status": "active",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Search request with id 123e4567-e89b-12d3-a456-426614174000 not found"
}
```

---

#### Delete Search Request
```http
DELETE /api/search-requests/{search_request_id}
```

Delete a search request and all associated data (executions, products, notifications).

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| search_request_id | string (UUID) | Yes | Unique identifier of the search request |

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/api/search-requests/123e4567-e89b-12d3-a456-426614174000
```

**Response (204 No Content):**
```
(Empty response body)
```

**Response (404 Not Found):**
```json
{
  "detail": "Search request with id 123e4567-e89b-12d3-a456-426614174000 not found"
}
```

---

#### Pause Search Request
```http
POST /api/search-requests/{search_request_id}/pause
```

Pause an active search request. The search will stop running until resumed.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| search_request_id | string (UUID) | Yes | Unique identifier of the search request |

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/search-requests/123e4567-e89b-12d3-a456-426614174000/pause
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "product_name": "iPhone 13",
  "product_description": "Looking for iPhone 13 in good condition",
  "budget": 600.0,
  "location": "Boston, MA",
  "match_threshold": 75.0,
  "status": "paused",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Search request with id 123e4567-e89b-12d3-a456-426614174000 not found"
}
```

---

#### Resume Search Request
```http
POST /api/search-requests/{search_request_id}/resume
```

Resume a paused search request. The search will start running again.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| search_request_id | string (UUID) | Yes | Unique identifier of the search request |

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/search-requests/123e4567-e89b-12d3-a456-426614174000/resume
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "product_name": "iPhone 13",
  "product_description": "Looking for iPhone 13 in good condition",
  "budget": 600.0,
  "location": "Boston, MA",
  "match_threshold": 75.0,
  "status": "active",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Search request with id 123e4567-e89b-12d3-a456-426614174000 not found"
}
```

---

### Products

#### List All Products
```http
GET /api/products
```

Retrieve a paginated list of all scraped products with optional filtering.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip (pagination) |
| limit | integer | No | 50 | Maximum records to return |
| platform | string | No | null | Filter by platform: `craigslist`, `facebook`, `ebay` |
| min_price | number | No | null | Minimum price filter |
| max_price | number | No | null | Maximum price filter |

**Example Requests:**
```bash
# Get first 10 products
GET /api/products?skip=0&limit=10

# Get products from Craigslist only
GET /api/products?platform=craigslist

# Get products in price range $100-$500
GET /api/products?min_price=100&max_price=500

# Combined filters
GET /api/products?platform=facebook&min_price=200&max_price=600&limit=20
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "prod-123e4567-e89b-12d3-a456-426614174000",
      "search_execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
      "title": "iPhone 13 128GB Blue - Excellent Condition",
      "description": "Barely used iPhone 13, 128GB, unlocked, comes with original box",
      "price": 550.0,
      "url": "https://boston.craigslist.org/product/123456",
      "image_url": "https://images.craigslist.org/image123.jpg",
      "platform": "craigslist",
      "location": "Boston, MA",
      "posted_date": "2024-01-01T10:00:00",
      "match_score": 85.5,
      "is_match": true,
      "created_at": "2024-01-01T12:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

---

#### List Matching Products
```http
GET /api/products/matches
```

Retrieve only products that meet the match criteria, sorted by match score (highest first).

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip (pagination) |
| limit | integer | No | 50 | Maximum records to return |
| min_score | number | No | 70.0 | Minimum match score (0-100) |

**Example Requests:**
```bash
# Get all matches
GET /api/products/matches

# Get matches with score >= 80
GET /api/products/matches?min_score=80

# Pagination
GET /api/products/matches?skip=0&limit=10
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "prod-123e4567-e89b-12d3-a456-426614174000",
      "search_execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
      "title": "iPhone 13 128GB Blue - Excellent Condition",
      "description": "Barely used iPhone 13, 128GB, unlocked",
      "price": 550.0,
      "url": "https://boston.craigslist.org/product/123456",
      "image_url": "https://images.craigslist.org/image123.jpg",
      "platform": "craigslist",
      "location": "Boston, MA",
      "posted_date": "2024-01-01T10:00:00",
      "match_score": 85.5,
      "is_match": true,
      "created_at": "2024-01-01T12:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

---

## Status Codes

### Success Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |

### Client Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |

### Server Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 500 | Internal Server Error | Server-side error |

---

## Examples

### Complete Workflow Example

Here's a complete example of using the API to create and manage a search:

```bash
# 1. Check API health
curl http://localhost:8000/api/health

# 2. Create a new search request
curl -X POST http://localhost:8000/api/search-requests \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "MacBook Pro 14",
    "product_description": "Looking for MacBook Pro 14-inch, M1 Pro or better, 16GB RAM minimum",
    "budget": 1500.0,
    "location": "San Francisco, CA",
    "match_threshold": 75.0
  }'

# Response: {"id": "abc-123", ...}

# 3. List all search requests
curl http://localhost:8000/api/search-requests

# 4. Get specific search request
curl http://localhost:8000/api/search-requests/abc-123

# 5. Get search statistics
curl http://localhost:8000/api/search-requests/abc-123/stats

# 6. View matching products
curl http://localhost:8000/api/products/matches?min_score=80

# 7. Pause the search
curl -X POST http://localhost:8000/api/search-requests/abc-123/pause

# 8. Resume the search
curl -X POST http://localhost:8000/api/search-requests/abc-123/resume

# 9. Update search budget
curl -X PUT http://localhost:8000/api/search-requests/abc-123 \
  -H "Content-Type: application/json" \
  -d '{"budget": 1800.0}'

# 10. Delete the search
curl -X DELETE http://localhost:8000/api/search-requests/abc-123
```

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Create a search request
search_data = {
    "product_name": "iPhone 13",
    "product_description": "Looking for iPhone 13 in good condition",
    "budget": 600.0,
    "location": "Boston, MA",
    "match_threshold": 75.0
}

response = requests.post(f"{BASE_URL}/api/search-requests", json=search_data)
search_id = response.json()["id"]
print(f"Created search: {search_id}")

# Get matching products
matches = requests.get(f"{BASE_URL}/api/products/matches?min_score=80")
print(f"Found {matches.json()['total']} matches")

# Pause the search
requests.post(f"{BASE_URL}/api/search-requests/{search_id}/pause")
print("Search paused")
```

### JavaScript/Fetch Example

```javascript
const BASE_URL = 'http://localhost:8000';

// Create a search request
async function createSearch() {
  const response = await fetch(`${BASE_URL}/api/search-requests`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      product_name: 'iPhone 13',
      product_description: 'Looking for iPhone 13 in good condition',
      budget: 600.0,
      location: 'Boston, MA',
      match_threshold: 75.0
    })
  });
  
  const search = await response.json();
  console.log('Created search:', search.id);
  return search.id;
}

// Get matching products
async function getMatches() {
  const response = await fetch(`${BASE_URL}/api/products/matches?min_score=80`);
  const data = await response.json();
  console.log(`Found ${data.total} matches`);
  return data.items;
}

// Usage
createSearch().then(searchId => {
  console.log('Search created:', searchId);
  return getMatches();
}).then(matches => {
  console.log('Matches:', matches);
});
```

---

## Interactive Documentation

The API provides interactive documentation through Swagger UI and ReDoc:

### Swagger UI (Recommended)
```
http://localhost:8000/docs
```
- Interactive API explorer
- Try out endpoints directly in the browser
- See request/response schemas
- Test with different parameters

### ReDoc
```
http://localhost:8000/redoc
```
- Clean, readable documentation
- Better for reading and understanding
- Organized by tags

### OpenAPI Schema
```
http://localhost:8000/openapi.json
```
- Raw OpenAPI 3.0 specification
- Use with API clients and code generators

---

## Rate Limiting

⚠️ **Current Version:** No rate limiting implemented

🔜 **Future Version:** Rate limiting will be added to prevent abuse:
- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## Pagination Best Practices

When working with paginated endpoints:

1. **Start with reasonable page sizes** (10-50 items)
2. **Use skip/limit for pagination:**
   ```
   Page 1: skip=0, limit=20
   Page 2: skip=20, limit=20
   Page 3: skip=40, limit=20
   ```
3. **Check the `total` field** to know how many pages exist
4. **Don't request more than 100 items** at once

---

## Support & Resources

- **API Documentation:** http://localhost:8000/docs
- **GitHub Repository:** https://github.com/yourusername/product-search-agent
- **Issue Tracker:** https://github.com/yourusername/product-search-agent/issues

---

## Changelog

### Version 1.0.0 (Current)
- Initial API release
- Search request CRUD operations
- Product listing and filtering
- Health check endpoint
- Statistics endpoint

### Upcoming Features
- WebSocket support for real-time notifications
- User authentication (JWT)
- Rate limiting
- Advanced search filters
- Bulk operations

---

**Last Updated:** 2024-01-01  
**API Version:** 1.0.0  
**Documentation Version:** 1.0.0

---

Made with ❤️ by Bob