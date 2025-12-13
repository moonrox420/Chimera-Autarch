#!/usr/bin/env python3
"""
Consumer-friendly configuration management for DroxAI
Supports JSON config files with environment variable overrides and dynamic path resolution
"""
import os
import sys
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

# Configure logging for file operations
logger = logging.getLogger("chimera.config")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("chimera.config")

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
    web_socket_host: str = "0.0.0.0"
    web_socket_port: int = 3001
    http_host: str = "0.0.0.0"
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
        # Add attributes expected by JSON (but derived dynamically)
        self.database_name = "droxai_memory.db"
        self.backup_directory = "backups"

@dataclass
class NodeConfig:
    """Node communication settings"""
    heartbeat_interval: float = 30.0
    node_timeout: float = 90.0

@dataclass
class FederatedLearningConfig:
    """Federated learning settings"""
    server_address: str = "0.0.0.0:8080"
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
        # Add attributes expected by JSON (but derived dynamically)
        self.file_name = "droxai.log"

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
        # Add attributes expected by JSON (but derived dynamically)
        self.models_directory = "runtime/models"
        self.plugins_directory = "plugins"
        self.certificates_directory = "runtime/certificates"
        self.temp_directory = "temp"

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
                "web_socket_host": "0.0.0.0",
                "web_socket_port": 3001,
                "http_host": "0.0.0.0",
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
                "server_address": "0.0.0.0:8080",
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
            config_file = app_home / "appsettings.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded = json.load(f)
                    if loaded:
                        # Deep merge loaded config
                        cls._deep_merge(config_dict, loaded)
            except Exception as e:
                logger.info(f"Warning: Could not load config file {config_file}: {e}")
        
        # Apply environment variable overrides (e.g., DROXAI_SERVER_WEBSOCKET_PORT=3001)
        env_prefix = "DROXAI_"
        for key in os.environ:
            if key.startswith(env_prefix):
                parts = key[len(env_prefix):].lower().split('_', 1)
                if len(parts) == 2:
                    section, setting = parts
                    
                    # Convert section key back to title case for matching config_dict
                    section_title = section.title()
                    
                    if section_title in config_dict:
                        
                        value = os.environ[key]
                        
                        # Attempt type conversion
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        elif value.isdigit():
                            value = int(value)
                        elif value.replace('.', '', 1).isdigit(): # Allows for one decimal point
                            value = float(value)
                        
                        # Find the actual key in the target dictionary (case-insensitive approach)
                        found_setting = None
                        for k in config_dict[section_title]:
                             if k.lower() == setting.lower():
                                 found_setting = k
                                 break
                                 
                        if found_setting:
                            config_dict[section_title][found_setting] = value
        
        # Ensure all required directories exist
        home_dir = str(app_home)
        cls._ensure_directories(app_home)
        
        # --- FIX: Convert keys to snake_case for dataclass instantiation ---
        # This resolves the issue where JSON uses "HttpPort" and Python expects "http_port"
        def convert_keys_to_snake(data: Dict[str, Any]) -> Dict[str, Any]:
            import re
            new_data = {}
            for k, v in data.items():
                # Convert TitleCase/camelCase to snake_case
                # Handle sequences of capitals (e.g., "SSLEnabled" -> "ssl_enabled")
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', k)
                new_key = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
                new_data[new_key] = v
            return new_data

        
        app_data = convert_keys_to_snake(config_dict.get("App", {}))
        server_data = convert_keys_to_snake(config_dict.get("Server", {}))
        metacognitive_data = convert_keys_to_snake(config_dict.get("Metacognitive", {}))
        node_data = convert_keys_to_snake(config_dict.get("Node", {}))
        federated_learning_data = convert_keys_to_snake(config_dict.get("FederatedLearning", {}))
        logging_data = convert_keys_to_snake(config_dict.get("Logging", {}))
        runtime_data = convert_keys_to_snake(config_dict.get("Runtime", {}))


        # Build config objects
        return DroxAIConfig(
            app=AppInfo(**app_data),
            server=ServerConfig(**server_data),
            metacognitive=MetacognitiveConfig(**metacognitive_data),
            persistence=PersistenceConfig(home_dir),
            node=NodeConfig(**node_data),
            federated_learning=FederatedLearningConfig(**federated_learning_data),
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
                "Name": "DroxAI",
                "Version": "1.0.0",
                "Description": "Advanced AI Orchestration System",
                "Environment": "Production"
            },
            "Server": {
                "WebSocketHost": "0.0.0.0",
                "WebSocketPort": 3001,
                "HttpHost": "0.0.0.0", 
                "HttpPort": 3000,
                "SSLEnabled": False,
                "SSLCertPath": None,
                "SSLKeyPath": None
            },
            "Metacognitive": {
                "ConfidenceThreshold": 0.6,
                "LearningCooldown": 300,
                "FailureHistorySize": 100,
                "PredictiveCheckInterval": 15
            },
            "Persistence": {
                "DatabaseName": "droxai_memory.db",
                "BackupInterval": 3600,
                "BackupRetention": 24,
                "BackupDirectory": "backups"
            },
            "Node": {
                "HeartbeatInterval": 30.0,
                "NodeTimeout": 90.0
            },
            "FederatedLearning": {
                "ServerAddress": "0.0.0.0:8080",
                "DefaultRounds": 3,
                "MinRounds": 3,
                "MaxRounds": 10
            },
            "Logging": {
                "Level": "INFO",
                "Format": "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
                "DateFormat": "%Y-%m-%d %H:%M:%S",
                "FileEnabled": True,
                "FileName": "droxai.log",
                "FileMaxBytes": 10485760,
                "FileBackupCount": 5
            },
            "Runtime": {
                "ModelsDirectory": "runtime/models",
                "PluginsDirectory": "plugins",
                "CertificatesDirectory": "runtime/certificates",
                "TempDirectory": "temp"
            }
        }
        
        if config_path:
            config_file = Path(config_path)
        else:
            app_home = cls.get_application_home()
            config_file = app_home / "appsettings.json"
        
        # Ensure config directory exists
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)

if __name__ == "__main__":
    # Generate default config file in release structure
    ConfigManager.save_default_config()
    logger.info("Generated appsettings.json")
