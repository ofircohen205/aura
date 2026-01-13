
import yaml
from pathlib import Path
from pydantic import BaseModel
import os

class AuraConfig(BaseModel):
    version: str = "0.1.0"
    api_url: str = "http://localhost:8000"
    api_key: str | None = None

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".aura"
        self.config_file = self.config_dir / "config.yaml"
        self._ensure_config()

    def _ensure_config(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
        if not self.config_file.exists():
            default_config = AuraConfig()
            self.save(default_config)

    def load(self) -> AuraConfig:
        if not self.config_file.exists():
            return AuraConfig()
        with open(self.config_file, "r") as f:
            data = yaml.safe_load(f) or {}
            return AuraConfig(**data)

    def save(self, config: AuraConfig):
        with open(self.config_file, "w") as f:
            yaml.dump(config.model_dump(), f)

config_manager = ConfigManager()
