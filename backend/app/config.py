from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    DATABASE_URL: str = "postgresql://localhost/sighub_db"
    STRIPE_SECRET_KEY: str = "sk_test_51MockStripeSecretKeyForTestingSigHub1234567890"
    STRIPE_WEBHOOK_SECRET: str = "whsec_MockStripeWebhookSecretForTestingSigHub12345"
    RESEND_API_KEY: str = "re_MockResendApiKeyForTestingSigHub12345"
    ADMIN_SECRET: str = "sighub_admin_secret_key_2026"
    BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
