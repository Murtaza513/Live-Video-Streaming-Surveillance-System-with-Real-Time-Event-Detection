from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Live Surveillance API'
    log_level: str = 'INFO'
    database_url: str = 'postgresql+asyncpg://<username>:<password>@localhost:5432/surveillance'
    websocket_fps: int = 10
    webcam_index: int = 0
    frame_width: int = 960
    frame_height: int = 540
    min_jpeg_quality: int = 45
    max_jpeg_quality: int = 85
    motion_threshold: float = 20.0
    enable_yolo: bool = False
    yolo_model: str = 'yolov8n.pt'
    allowed_origins: list[str] = Field(default_factory=lambda: ['http://localhost:5173'])


settings = Settings()
