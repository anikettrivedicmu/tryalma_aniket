# Deployment Guide

This guide covers deploying the Lead Management System to various cloud platforms.

## Prerequisites

- Docker and Docker Compose installed
- A PostgreSQL database instance
- A Redis instance
- SMTP server credentials

## Environment Setup

1. Copy the example environment file:
```bash
cp app/.env.example app/.env
```

2. Update the environment variables:
```bash
# Database
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=lead_management
POSTGRES_HOST=your_db_host
POSTGRES_PORT=5432

# Redis
REDIS_HOST=your_redis_host
REDIS_PORT=6379

# JWT
JWT_SECRET=your_secure_jwt_secret

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com
ATTORNEY_EMAIL=attorney@yourcompany.com
```

## Local Deployment with Docker

1. Build and start the containers:
```bash
docker-compose up -d --build
```

2. Run database migrations:
```bash
docker-compose exec app alembic upgrade head
```

3. Create an initial attorney user:
```bash
docker-compose exec app python -m scripts.create_user
```

## Cloud Deployment Options

### AWS Elastic Container Service (ECS)

1. Create an ECR repository:
```bash
aws ecr create-repository --repository-name lead-management
```

2. Build and push the Docker image:
```bash
aws ecr get-login-password --region region | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker build -t lead-management .
docker tag lead-management:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/lead-management:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/lead-management:latest
```

3. Create an ECS cluster and service using the AWS console or CLI

### Google Cloud Run

1. Build and push the image:
```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/lead-management
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy lead-management \
  --image gcr.io/$PROJECT_ID/lead-management \
  --platform managed \
  --allow-unauthenticated
```

### Heroku

1. Log in to Heroku Container Registry:
```bash
heroku container:login
```

2. Create a new Heroku app:
```bash
heroku create your-app-name
```

3. Push the container:
```bash
heroku container:push web
heroku container:release web
```

## Post-Deployment Steps

1. Set up SSL/TLS certificates
2. Configure domain names
3. Set up monitoring and logging
4. Configure backups for the database
5. Set up CI/CD pipelines

## Scaling Considerations

- Use managed database services (RDS, Cloud SQL)
- Implement CDN for static file serving
- Use container orchestration for high availability
- Set up load balancers
- Configure auto-scaling policies

## Monitoring and Maintenance

1. Set up health checks:
```bash
curl https://your-domain.com/health
```

2. Monitor system metrics:
- CPU and memory usage
- Database connections
- API response times
- Error rates

3. Regular maintenance:
- Database backups
- Log rotation
- Security updates
- SSL certificate renewal