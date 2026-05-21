from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Real-Time Surveillance Backend"
    app_env: str = "development"
    log_level: str = "INFO"

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_origin: str = "http://localhost:5173"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/surveillance"

    camera_index: int = 0
    target_fps: int = 12

    base_jpeg_quality: int = 75
    min_jpeg_quality: int = 40
    max_jpeg_quality: int = 90

    motion_threshold: float = 0.03
    motion_blur_kernel: int = 21

    enable_yolo: bool = False
    yolo_model: str = "yolov8n.pt"
    person_confidence: float = 0.4

    event_cooldown_seconds: int = 2
    max_events: int = 200

    snapshot_dir: str = "snapshots"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
