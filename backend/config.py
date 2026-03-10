from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    db_host: str = "localhost"
    db_user: str = "hydropi_user"
    db_password: str = "change_me"
    db_name: str = "hydropidb"

    # Email
    email_from: str = ""
    email_password: str = ""
    email_server: str = "smtp.gmail.com"
    email_port: int = 587
    email_to: str = ""

    # Logging
    log_file: str = "/var/log/hydropi/daemon.log"
    log_level: str = "INFO"

    # Development
    use_mock: bool = True


settings = Settings()
