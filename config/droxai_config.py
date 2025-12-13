#!/usr/bin/env python3
"""
Consumer-friendly configuration management for DroxAI
Supports JSON config files with environment variable overrides and dynamic path resolution
"""
import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class AppInfo:
    """Application information settings"""
    name: str = "DroxAI"
    version: str = "1.0.0"
    description: str = "Advanced AI Orchestration System"
    environment: str = "Production"

@dataclass
class ServerConfig:
    """Server configuration settings"""
    websocket_host: str = "localhost"
    websocket_port: int = 3001
    http_host: str = "localhost"
    http_port: int = 3000
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None

@dataclass
class MetacognitiveConfig:
    """Metacognitive engine settings"""
    confidence_threshold: float = 0.6
    learning_cooldown: int = 300
    failure_history_size: int = 100
    predictive_check_interval: int = 15

@dataclass
class PersistenceConfig:
    """Database and backup settings - using dynamic paths"""
    def __init__(self, home_dir: str):
        self.home_dir = Path(home_dir)
        self.data_dir = self.home_dir / "data"
        self.logs_dir = self.home_dir / "logs"
        self.temp_dir = self.home_dir / "temp"
        self.backup_dir = self.data_dir / "backups"
        self.database_path = str(self.data_dir / "droxai_memory.db")
        self.backup_interval = 3600
        self.backup_retention = 24

@dataclass
class NodeConfig:
    """Node communication settings"""
    heartbeat_interval: float = 30.0
    node_timeout: float = 90.0

@dataclass
class FederatedLearningConfig:
    """Federated learning settings"""
    server_address: str = "127.0.0.1:8080"
    default_rounds: int = 3
    min_rounds: int = 3
    max_rounds: int = 10

@dataclass
class LoggingConfig:
    """Logging configuration - using dynamic paths"""
    def __init__(self, home_dir: str):
        self.home_dir = Path(home_dir)
        self.logs_dir = self.home_dir / "logs"
        self.level: str = "INFO"
        self.format: str = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
        self.date_format: str = "%Y-%m-%d %H:%M:%S"
        self.file_enabled: bool = True
        self.file_path: str = str(self.logs_dir / "droxai.log")
        self.file_max_bytes: int = 10485760
        self.file_backup_count: int = 5

@dataclass
class RuntimeConfig:
    """Runtime paths and directories - using dynamic paths"""
    def __init__(self, home_dir: str):
        self.home_dir = Path(home_dir)
        self.runtime_dir = self.home_dir / "runtime"
        self.models_dir = self.runtime_dir / "models"
        self.plugins_dir = self.home_dir / "plugins"
        self.certificates_dir = self.runtime_dir / "certificates"
        self.temp_dir = self.home_dir / "temp"

@dataclass
class DroxAIConfig:
    """Main configuration container with dynamic path resolution"""
    app: AppInfo
    server: ServerConfig
    metacognitive: MetacognitiveConfig
    persistence: PersistenceConfig
    node: NodeConfig
    federated_learning: FederatedLearningConfig
    logging: LoggingConfig
    runtime: RuntimeConfig

class ConfigManager:
    """Manages configuration loading and path resolution"""
    
    @staticmethod
    def get_application_home() -> Path:
        """
        Get the application home directory
        Resolves to the directory containing the executable
        """
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return Path(sys.executable).parent
        else:
            # Running as Python script
            return Path(__file__).parent
    
    @classmethod
    def load_config(cls, config_path: Optional[str] = None) -> DroxAIConfig:
        """
        Load configuration from JSON file with environment variable overrides
        Uses dynamic path resolution based on executable location
        """
        app_home = cls.get_application_home()
        
        # Default configuration
        config_dict = {
            "App": {
                "name": "DroxAI",
                "version": "1.0.0",
                "description": "Advanced AI Orchestration System",
                "environment": "Production"
            },
            "Server": {
                "websocket_host": "localhost",
                "websocket_port": 3001,
                "http_host": "localhost",
                "http_port": 3000,
                "ssl_enabled": False,
                "ssl_cert_path": None,
                "ssl_key_path": None
            },
            "Metacognitive": {
                "confidence_threshold": 0.6,
                "learning_cooldown": 300,
                "failure_history_size": 100,
                "predictive_check_interval": 15
            },
            "Persistence": {},
            "Node": {
                "heartbeat_interval": 30.0,
                "node_timeout": 90.0
            },
            "FederatedLearning": {
                "server_address": "127.0.0.1:8080",
                "default_rounds": 3,
                "min_rounds": 3,
                "max_rounds": 10
            },
            "Logging": {},
            "Runtime": {}
        }
        
        # Load from JSON config if provided
        if config_path:
            config_file = Path(config_path)
        else:
            # Look for config in application home
            config_file = app_home / "config" / "appsettings.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded = json.load(f)
                    if loaded:
                        # Deep merge loaded config
                        cls._deep_merge(config_dict, loaded)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
        
        # Apply environment variable overrides
        env_prefix = "DROXAI_"
        for key in os.environ:
            if key.startswith(env_prefix):
                parts = key[len(env_prefix):].lower().split('_', 1)
                if len(parts) == 2:
                    section, setting = parts
                    if section in config_dict:
                        # Convert value types
                        value = os.environ[key]
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        elif value.isdigit():
                            value = int(value)
                        elif value.replace('.', '').isdigit():
                            value = float(value)
                        
                        config_dict[section][setting] = value
        
        # Ensure all required directories exist
        home_dir = str(app_home)
        cls._ensure_directories(app_home)
        
        # Build config objects
        return DroxAIConfig(
            app=AppInfo(**config_dict.get("App", {})),
            server=ServerConfig(**config_dict.get("Server", {})),
            metacognitive=MetacognitiveConfig(**config_dict.get("Metacognitive", {})),
            persistence=PersistenceConfig(home_dir),
            node=NodeConfig(**config_dict.get("Node", {})),
            federated_learning=FederatedLearningConfig(**config_dict.get("FederatedLearning", {})),
            logging=LoggingConfig(home_dir),
            runtime=RuntimeConfig(home_dir)
        )
    
    @staticmethod
    def _deep_merge(base: Dict, update: Dict) -> None:
        """Deep merge two dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ConfigManager._deep_merge(base[key], value)
            else:
                base[key] = value
    
    @staticmethod
    def _ensure_directories(app_home: Path) -> None:
        """Ensure all required directories exist"""
        dirs = [
            app_home / "data",
            app_home / "logs", 
            app_home / "temp",
            app_home / "plugins",
            app_home / "runtime" / "models",
            app_home / "runtime" / "certificates"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def save_default_config(cls, config_path: Optional[str] = None) -> None:
        """Save default configuration to JSON file"""
        default_config = {
            "App": {
                "name": "DroxAI",
                "version": "1.0.0",
                "description": "Advanced AI Orchestration System",
                "environment": "Production"
            },
            "Server": {
                "websocket_host": "localhost",
                "websocket_port": 3001,
                "http_host": "localhost", 
                "http_port": 3000,
                "ssl_enabled": False,
                "ssl_cert_path": None,
                "ssl_key_path": None
            },
            "Metacognitive": {
                "confidence_threshold": 0.6,
                "learning_cooldown": 300,
                "failure_history_size": 100,
                "predictive_check_interval": 15
            },
            "Persistence": {
                "database_name": "droxai_memory.db",
                "backup_interval": 3600,
                "backup_retention": 24,
                "backup_directory": "backups"
            },
            "Node": {
                "heartbeat_interval": 30.0,
                "node_timeout": 90.0
            },
            "FederatedLearning": {
                "server_address": "127.0.0.1:8080",
                "default_rounds": 3,
                "min_rounds": 3,
                "max_rounds": 10
            },
            "Logging": {
                "level": "INFO",
                "format": "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
                "date_format": "%Y-%m-%d %H:%M:%S",
                "file_enabled": True,
                "file_name": "droxai.log",
                "file_max_bytes": 10485760,
                "file_backup_count": 5
            },
            "Runtime": {
                "models_directory": "runtime/models",
                "plugins_directory": "plugins",
                "certificates_directory": "runtime/certificates",
                "temp_directory": "temp"
            }
        }
        
        if config_path:
            config_file = Path(config_path)
        else:
            app_home = cls.get_application_home()
            config_file = app_home / "config" / "appsettings.json"
        
        # Ensure config directory exists
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2, default_flow_style=False)

if __name__ == "__main__":
    # Generate default config file in release structure
    ConfigManager.save_default_config()
    print("Generated appsettings.json")

