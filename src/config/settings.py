"""
Configuration management using Pydantic settings.

Supports YAML config files with environment variable overrides.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from fastapi import FastAPI


class ServerSettings(BaseSettings):
    """Server configuration settings."""

    websocket_host: str = Field(default="localhost")
    websocket_port: int = Field(default=3001)
    http_host: str = Field(default="localhost")
    http_port: int = Field(default=3000)
    ssl_enabled: bool = Field(default=False)
    ssl_cert_path: Optional[str] = Field(default=None)
    ssl_key_path: Optional[str] = Field(default=None)

    model_config = ConfigDict(env_prefix="APP_SERVER_")


class MetacognitiveSettings(BaseSettings):
    """Metacognitive engine settings."""

    confidence_threshold: float = Field(default=0.6)
    learning_cooldown: int = Field(default=300)
    failure_history_size: int = Field(default=100)
    predictive_check_interval: int = Field(default=15)

    model_config = ConfigDict(env_prefix="APP_METACOGNITIVE_")


class PersistenceSettings(BaseSettings):
    """Database and backup settings."""

    database_path: str = Field(default="memory.db")
    backup_interval: int = Field(default=3600)
    backup_retention: int = Field(default=24)
    backup_dir: str = Field(default="backups")

    model_config = ConfigDict(env_prefix="APP_PERSISTENCE_")


class NodeSettings(BaseSettings):
    """Node communication settings."""

    heartbeat_interval: float = Field(default=30.0)
    node_timeout: float = Field(default=90.0)

    model_config = ConfigDict(env_prefix="APP_NODE_")


class FederatedLearningSettings(BaseSettings):
    """Federated learning settings."""

    server_address: str = Field(default="127.0.0.1:8080")
    default_rounds: int = Field(default=3)
    min_rounds: int = Field(default=3)
    max_rounds: int = Field(default=10)

    model_config = ConfigDict(env_prefix="APP_FL_")


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    level: str = Field(default="INFO")
    format: str = Field(default="[%(asctime)s][%(levelname)s][%(name)s] %(message)s")
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S")
    file_enabled: bool = Field(default=False)
    file_path: str = Field(default="logs/app.log")
    file_max_bytes: int = Field(default=10_485_760)  # 10MB
    file_backup_count: int = Field(default=5)

    model_config = ConfigDict(env_prefix="APP_LOGGING_")


class LLMSettings(BaseSettings):
    """LLM integration settings."""

    enabled: bool = Field(default=True)
    provider: str = Field(default="ollama")  # ollama, openai, anthropic
    model: str = Field(default="codellama")
    api_key: Optional[str] = Field(default=None)
    base_url: Optional[str] = Field(default=None)
    timeout: int = Field(default=30)

    model_config = ConfigDict(env_prefix="APP_LLM_")


class Settings(BaseSettings):
    """Main configuration container."""

    server: ServerSettings = Field(default_factory=ServerSettings)
    metacognitive: MetacognitiveSettings = Field(default_factory=MetacognitiveSettings)
    persistence: PersistenceSettings = Field(default_factory=PersistenceSettings)
    node: NodeSettings = Field(default_factory=NodeSettings)
    federated_learning: FederatedLearningSettings = Field(default_factory=FederatedLearningSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)

    model_config = ConfigDict(env_prefix="APP_", extra="ignore")


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Load settings from YAML config file."""
    try:
        import yaml
    except ImportError:
        print("Warning: PyYAML not installed. Using default settings.")
        return {}
    
    path = Path(config_path)

    if not path.exists():
        return {}
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f) or {}
        return config_data
    except Exception as e:
        print(f"Warning: Failed to load config from {path}: {e}")
        return {}


def get_settings(config_path: Optional[str] = None) -> Settings:
    """Get application settings with optional config path override."""
    if config_path is None:
        config_path = os.getenv("APP_CONFIG_PATH", "config.yaml")
    
    try:
        config_data = load_yaml_config(config_path)
        if config_data:
            return Settings(**config_data)
    except Exception as e:
        print(f"Warning: Failed to initialize settings from {config_path}: {e}")

    return Settings()


def save_default_config(config_path: str = "config.yaml") -> None:
    """Save default configuration to YAML file."""
    import yaml

    defaults = {
        "server": {
            "websocket_host": "localhost",
            "websocket_port": 3001,
            "http_host": "localhost",
            "http_port": 3000,
            "ssl_enabled": False,
        },
        "metacognitive": {
            "confidence_threshold": 0.6,
            "learning_cooldown": 300,
            "failure_history_size": 100,
            "predictive_check_interval": 15,
        },
        "persistence": {
            "database_path": "data/memory.db",
            "backup_interval": 3600,
            "backup_retention": 24,
            "backup_dir": "data/backups",
        },
        "node": {
            "heartbeat_interval": 30.0,
            "node_timeout": 90.0,
        },
        "federated_learning": {
            "server_address": "127.0.0.1:8080",
            "default_rounds": 3,
            "min_rounds": 3,
            "max_rounds": 10,
        },
        "logging": {
            "level": "INFO",
            "file_enabled": False,
            "file_path": "logs/app.log",
        },
        "llm": {
            "enabled": True,
            "provider": "ollama",
            "model": "codellama",
        },
    }

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(defaults, f, default_flow_style=False, sort_keys=False)