from app.core.config import Settings

def validate_config():
    try:
        settings = Settings.from_yaml()
        print("Configuration validated successfully!")
        print(f"App Name: {settings.app_name}")
        print(f"Debug Mode: {settings.debug}")
        print(f"CORS Origins: {settings.cors_origins}")
        print(f"Database URL: {settings.database.url}")
        print(f"Redis URL: {settings.redis.url}")
        return True
    except Exception as e:
        print(f"Configuration validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    validate_config()