import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, BaseSettings, EmailStr, validator
import yaml


def load_yaml_config() -> Dict[str, Any]:
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
    with open(config_path) as f:
        return yaml.safe_load(f)


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

    @classmethod
    def from_yaml(cls) -> "Settings":
        yaml_config = load_yaml_config()
        return cls(**yaml_config)


settings = Settings.from_yaml()