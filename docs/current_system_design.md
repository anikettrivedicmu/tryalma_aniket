# Current System Design

## System Architecture

```mermaid
graph TB
    Client[Client/Browser] -->|HTTP/REST| API[FastAPI Application]
    
    subgraph Application
        API -->|JWT Auth| Auth[Authentication Service]
        API -->|Rate Limit| Redis[(Redis Cache)]
        API -->|ORM| DB[(PostgreSQL)]
        API -->|Upload| Storage[Storage Service]
        API -->|Notify| Email[Email Service]
        
        Auth -->|Verify| JWT[JWT Service]
        Auth -->|Query| DB
        
        Storage -->|Local| Local[Local FileSystem]
        Storage -->|Cloud| S3[AWS S3]
        
        Email -->|SMTP| SMTP[SMTP Server]
        Email -->|Download| Storage
    end
    
    subgraph External Services
        S3 -->|Store| S3Bucket[S3 Bucket]
        SMTP -->|Send| EmailProvider[Email Provider]
    end
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant DB as PostgreSQL
    participant JWT as JWT Service
    
    U->>API: POST /api/v1/token
    API->>DB: Query User
    DB-->>API: User Data
    API->>API: Verify Password
    API->>JWT: Generate Token
    JWT-->>API: Access Token
    API-->>U: Token Response
```

## Lead Submission Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant Redis as Redis
    participant Storage as Storage Service
    participant DB as PostgreSQL
    participant Email as Email Service
    
    C->>API: POST /api/v1/leads/
    API->>Redis: Check Rate Limit
    Redis-->>API: Allow Request
    API->>Storage: Upload Resume
    Storage-->>API: File Path/URL
    API->>DB: Create Lead Record
    DB-->>API: Lead Data
    API->>Email: Send Attorney Notification
    Email->>Storage: Download Resume
    Storage-->>Email: Resume Content
    Email-->>API: Email Sent
    API-->>C: Success Response
```

## Lead Management Flow

```mermaid
sequenceDiagram
    participant A as Attorney
    participant API as FastAPI
    participant Auth as Auth Service
    participant DB as PostgreSQL
    
    A->>API: GET /api/v1/leads/
    API->>Auth: Validate JWT
    Auth-->>API: Token Valid
    API->>DB: Query Leads
    DB-->>API: Lead Records
    API-->>A: Leads List
    
    A->>API: PATCH /api/v1/leads/{id}/status
    API->>Auth: Validate JWT
    Auth-->>API: Token Valid
    API->>DB: Update Status
    DB-->>API: Updated Lead
    API-->>A: Success Response
```

## File Storage Service

```mermaid
graph TB
    subgraph Storage Service
        Upload[Upload Request] -->|Check Type| Validate[File Validation]
        Validate -->|Size & Type| Decision{Storage Type}
        Decision -->|S3| S3Upload[Upload to S3]
        Decision -->|Local| LocalUpload[Save to Filesystem]
        
        S3Upload -->|Success| S3URL[Return S3 URL]
        LocalUpload -->|Success| LocalPath[Return File Path]
    end
    
    subgraph Validation
        Validate -->|Check| Size[Size Limit]
        Validate -->|Verify| Type[File Type]
        Validate -->|Scan| Security[Security Check]
    end
```

## Email Service Architecture

```mermaid
graph TB
    subgraph Email Processing
        New[New Lead] -->|Trigger| Queue[Background Task]
        Queue -->|Process| Email[Email Service]
        
        Email -->|Get File| Storage[Storage Service]
        Email -->|Create| Message[Create Message]
        Message -->|Attach| Resume[Resume PDF]
        Message -->|Send| SMTP[SMTP Server]
    end
    
    subgraph Error Handling
        SMTP -->|Success| Sent[Email Sent]
        SMTP -->|Failure| Retry[Retry Logic]
        Retry -->|Max Retries| Log[Log Error]
    end
```

## Database Schema

```mermaid
erDiagram
    User {
        int id PK
        string email
        string hashed_password
        boolean is_active
        boolean is_superuser
        datetime created_at
        datetime updated_at
    }
    
    Lead {
        int id PK
        string first_name
        string last_name
        string email
        string resume_path
        enum status
        datetime created_at
        datetime updated_at
    }
```

## Key Components:

1. **FastAPI Application**
   - JWT-based authentication
   - Rate limiting with Redis
   - Async request handling
   - Input validation with Pydantic

2. **Storage Service**
   - Hybrid storage (Local/S3)
   - File validation
   - Secure file handling
   - Async operations

3. **Email Service**
   - Background task processing
   - SMTP integration
   - Resume attachment handling
   - Error handling & retries

4. **Database Layer**
   - PostgreSQL with SQLAlchemy ORM
   - Connection pooling
   - Migration support with Alembic
   - Audit fields (created_at, updated_at)

5. **Security Features**
   - JWT authentication
   - Rate limiting
   - File type validation
   - CORS configuration
   - Environment-based settings