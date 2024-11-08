from datetime import timedelta
from pathlib import Path

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    rcon_host: str
    rcon_port: int = 25575
    rcon_password: str

    server_path: Path

    backup_destination: Path
    backup_interval: timedelta
    backup_count: int
