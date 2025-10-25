import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, BaseSettings, EmailStr, validator
import yaml
from pathlib import Path


def load_yaml_config() -> Dict[str, Any]:
    config = {
        'app_name': "Lead Management System",
        'debug': False,
        'cors_origins': [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost:5000"
        ],
        'database': {
            'url': f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}",
            'pool_size': 5,
            'max_overflow': 10
        },
        'redis': {
            'url': f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}",
            'rate_limit': {
                'times': 100,
                'seconds': 60
            }
        },
        'security': {
            'jwt_secret': os.getenv('JWT_SECRET'),
            'jwt_algorithm': "HS256",
            'access_token_expire_minutes': 30
        },
        'email': {
            'smtp_host': os.getenv('SMTP_HOST'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_user': os.getenv('SMTP_USER'),
            'smtp_password': os.getenv('SMTP_PASSWORD'),
            'from_email': os.getenv('FROM_EMAIL'),
            'attorney_email': os.getenv('ATTORNEY_EMAIL')
        },
        'storage': {
            'upload_dir': "uploads",
            'max_file_size': 10485760,
            'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            's3_bucket_name': os.getenv('S3_BUCKET_NAME'),
            'aws_region': os.getenv('AWS_REGION', 'us-east-1'),
            'storage_type': os.getenv('STORAGE_TYPE', 'local')
        }
    }
    return config


class DatabaseConfig(BaseModel):
    url: str
    pool_size: int
    max_overflow: int


class RedisConfig(BaseModel):
    url: str
    rate_limit: Dict[str, int]


class SecurityConfig(BaseModel):
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int


class EmailConfig(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    from_email: EmailStr
    attorney_email: EmailStr


class StorageConfig(BaseModel):
    upload_dir: str
    max_file_size: int
    aws_access_key_id: str
    aws_secret_access_key: str
    s3_bucket_name: str
    aws_region: str
    storage_type: str = "s3"  # Can be "local" or "s3"


class Settings(BaseSettings):
    app_name: str
    debug: bool
    database: DatabaseConfig
    redis: RedisConfig
    security: SecurityConfig
    email: EmailConfig
    storage: StorageConfig
    cors_origins: List[str]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

    @classmethod
    def from_yaml(cls) -> "Settings":
        yaml_config = load_yaml_config()
        return cls(**yaml_config)


settings = Settings.from_yaml()