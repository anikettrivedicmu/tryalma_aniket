# API Documentation

## Authentication

### Login
```http
POST /api/v1/login
```

Log in as an attorney to get an access token.

**Request Body:**
```json
{
  "username": "attorney@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /api/v1/me
```

Get information about the currently logged-in user.

**Headers:**
- Authorization: Bearer {access_token}

**Response:**
```json
{
  "id": 1,
  "email": "attorney@example.com",
  "is_active": true,
  "is_superuser": false
}
```

## Leads

### Submit Lead
```http
POST /api/v1/leads/
```

Submit a new lead (public endpoint).

**Request Body (multipart/form-data):**
- first_name: string
- last_name: string
- email: string
- resume: file (PDF, DOC, or DOCX)

**Response:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "resume_path": "uploads/20231024_123456_abcd1234.pdf",
  "status": "PENDING",
  "created_at": "2023-10-24T12:34:56",
  "updated_at": "2023-10-24T12:34:56"
}
```

### List Leads
```http
GET /api/v1/leads/
```

Get a list of all leads (authenticated endpoint).

**Headers:**
- Authorization: Bearer {access_token}

**Query Parameters:**
- skip: integer (default: 0)
- limit: integer (default: 100)
- status: string (optional, "PENDING" or "REACHED_OUT")

**Response:**
```json
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "resume_path": "uploads/20231024_123456_abcd1234.pdf",
    "status": "PENDING",
    "created_at": "2023-10-24T12:34:56",
    "updated_at": "2023-10-24T12:34:56"
  }
]
```

### Get Lead
```http
GET /api/v1/leads/{lead_id}
```

Get a specific lead by ID (authenticated endpoint).

**Headers:**
- Authorization: Bearer {access_token}

**Response:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "resume_path": "uploads/20231024_123456_abcd1234.pdf",
  "status": "PENDING",
  "created_at": "2023-10-24T12:34:56",
  "updated_at": "2023-10-24T12:34:56"
}
```

### Update Lead Status
```http
PATCH /api/v1/leads/{lead_id}/status
```

Update a lead's status (authenticated endpoint).

**Headers:**
- Authorization: Bearer {access_token}

**Request Body:**
```json
{
  "status": "REACHED_OUT"
}
```

**Response:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "resume_path": "uploads/20231024_123456_abcd1234.pdf",
  "status": "REACHED_OUT",
  "created_at": "2023-10-24T12:34:56",
  "updated_at": "2023-10-24T12:34:56"
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough privileges"
}
```

### 404 Not Found
```json
{
  "detail": "Lead not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error"
    }
  ]
}
```

## Rate Limiting

Public endpoints are rate-limited to 100 requests per minute per IP address. When the rate limit is exceeded, you'll receive a 429 Too Many Requests response:

```json
{
  "detail": "Rate limit exceeded"
}
```

## File Upload Restrictions

- Maximum file size: 10MB
- Allowed file types: PDF, DOC, DOCX
- Files are stored in the configured uploads directory
- File names are sanitized and made unique using timestamps and UUIDs

## Email Notifications

The system sends two types of email notifications:

1. To the prospect:
   - Confirmation of form submission
   - Next steps information

2. To the attorney:
   - New lead notification
   - Lead details
   - Direct link to view the lead in the system