from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://ftuser:ftpass@localhost:5432/factorytwin_demo"

    JWT_SECRET: str = "Testing_by_Syed"
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 120  # 2 hours

settings = Settings()
