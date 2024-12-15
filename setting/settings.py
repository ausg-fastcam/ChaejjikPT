from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SLACK_BOT_TOKEN: str
    SLACK_APP_TOKEN: str
    SLACK_APP_ID: str
    OPENAI_API_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"
