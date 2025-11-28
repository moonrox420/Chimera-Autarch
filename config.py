
# Renamed to avoid shadowing config package. See config/settings.py for settings classes.

# (This file is intentionally left as a stub or can be deleted if not needed.)

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
    learning_cooldown: int = 300  # seconds
    failure_history_size: int = 100
    predictive_check_interval: int = 15  # seconds

@dataclass
class PersistenceConfig:
    """Database and backup settings"""
    database_path: str = "chimera_memory.db"
    backup_interval: int = 3600  # seconds
    backup_retention: int = 24  # number of backups to keep
    backup_dir: str = "backups"

@dataclass
class NodeConfig:
    """Node communication settings"""
    heartbeat_interval: float = 30.0  # seconds
    node_timeout: float = 90.0  # seconds

@dataclass
class FederatedLearningConfig:
    """Federated learning settings"""
    server_address: str = "127.0.0.1:8080"
    default_rounds: int = 3
    min_rounds: int = 3
    max_rounds: int = 10

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_enabled: bool = False
    file_path: str = "logs/chimera.log"
    file_max_bytes: int = 10485760  # 10MB
    file_backup_count: int = 5

@dataclass
class ChimeraConfig:
    """Main configuration container"""
    server: ServerConfig
    metacognitive: MetacognitiveConfig
    persistence: PersistenceConfig
    node: NodeConfig
    federated_learning: FederatedLearningConfig
    logging: LoggingConfig

def load_config(config_path: str = "config.yaml") -> ChimeraConfig:
    """
    Load configuration from YAML file with environment variable overrides
    
    Environment variables override YAML settings using pattern:
    CHIMERA_SECTION_SETTING (e.g., CHIMERA_SERVER_WEBSOCKET_PORT=3000)
    """
    # Default configuration
    config_dict = {
        "server": {},
        "metacognitive": {},
        "persistence": {},
        "node": {},
        "federated_learning": {},
        "logging": {}
    }
    
    # Load from YAML if exists
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            loaded = yaml.safe_load(f)
            if loaded:
                config_dict.update(loaded)
    
    # Apply environment variable overrides
    env_prefix = "CHIMERA_"
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
    
    # Build config objects
    return ChimeraConfig(
        server=ServerConfig(**config_dict.get("server", {})),
        metacognitive=MetacognitiveConfig(**config_dict.get("metacognitive", {})),
        persistence=PersistenceConfig(**config_dict.get("persistence", {})),
        node=NodeConfig(**config_dict.get("node", {})),
        federated_learning=FederatedLearningConfig(**config_dict.get("federated_learning", {})),
        logging=LoggingConfig(**config_dict.get("logging", {}))
    )

def save_default_config(config_path: str = "config.yaml"):
    """Save default configuration to YAML file"""
    default_config = {
        "server": {
            "websocket_host": "localhost",
            "websocket_port": 3001,
            "http_host": "localhost",
            "http_port": 3000,
            "ssl_enabled": False,
            "ssl_cert_path": None,
            "ssl_key_path": None
        },
        "metacognitive": {
            "confidence_threshold": 0.6,
            "learning_cooldown": 300,
            "failure_history_size": 100,
            "predictive_check_interval": 15
        },
        "persistence": {
            "database_path": "chimera_memory.db",
            "backup_interval": 3600,
            "backup_retention": 24,
            "backup_dir": "backups"
        },
        "node": {
            "heartbeat_interval": 30.0,
            "node_timeout": 90.0
        },
        "federated_learning": {
            "server_address": "127.0.0.1:8080",
            "default_rounds": 3,
            "min_rounds": 3,
            "max_rounds": 10
        },
        "logging": {
            "level": "INFO",
            "format": "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "file_enabled": False,
            "file_path": "logs/chimera.log",
            "file_max_bytes": 10485760,
            "file_backup_count": 5
        }
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

if __name__ == "__main__":
    # Generate default config file
    save_default_config("config.example.yaml")
    print("Generated config.example.yaml")

