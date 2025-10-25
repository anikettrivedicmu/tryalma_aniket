# Lead Management System

A FastAPI-based application for managing leads with resume handling and email notifications.

## Features

- Lead Management:
  - Create and manage leads with contact information
  - Status tracking for leads
  - User authentication and authorization
  - Rate limiting using Redis

- File Handling:
  - Resume upload and storage
  - Support for both local and S3 storage
  - PDF file validation
  - Secure file downloads

- Email Notifications:
  - Automated email notifications for new leads
  - PDF resume attachments
  - Background task processing
  - Error handling and retries

## Tech Stack

- **Backend**: FastAPI (Python 3.9)
- **Database**: PostgreSQL
- **Caching**: Redis
- **Storage**: AWS S3 / Local filesystem
- **Email**: SMTP with async support
- **Authentication**: JWT
- **Docker**: Container orchestration

## Setup

### Prerequisites

- Docker and Docker Compose
- AWS Account (for S3 storage)
- SMTP Server credentials

### Environment Variables

Create a `.env` file in the `app` directory with the following variables:

```env
# Database
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=your_db_name
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_SECRET=your_jwt_secret

# Email
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password
FROM_EMAIL=your_from_email
ATTORNEY_EMAIL=attorney@example.com

# Storage
STORAGE_TYPE=s3  # or 'local'
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET_NAME=your_bucket_name
AWS_REGION=your_aws_region
```

### Running the Application

1. Build and start the containers:
   ```bash
   docker-compose up --build -d
   ```

2. Create initial database tables:
   ```bash
   docker-compose exec app alembic upgrade head
   ```

3. Create an initial admin user:
   ```bash
   docker-compose exec app python scripts/create_user.py
   ```

The application will be available at `http://localhost:8000`.

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## File Storage Configuration

The application supports two storage backends:

### Local Storage
- Set `STORAGE_TYPE=local` in `.env`
- Files are stored in the `uploads` directory
- Suitable for development and testing

### S3 Storage
- Set `STORAGE_TYPE=s3` in `.env`
- Configure AWS credentials and bucket settings
- Recommended for production use
- Ensures scalable and reliable file storage

## Email Configuration

The application sends email notifications for new leads with the following features:
- Async email sending using background tasks
- PDF resume attachments (from both local and S3 storage)
- Error handling and logging
- TLS support for secure email transmission

## Security Features

- JWT-based authentication
- Rate limiting for API endpoints
- Secure file handling
- TLS for email transmission
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
