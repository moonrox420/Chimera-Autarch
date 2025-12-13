from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CHIMERA"
    debug: bool = True
    server: 'ServerSettings' = None
    metacognitive: 'MetacognitiveSettings' = None
    persistence: 'PersistenceSettings' = None
    node: 'NodeSettings' = None
    federated_learning: 'FederatedLearningSettings' = None
    logging: 'LoggingSettings' = None
    llm: 'LLMSettings' = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server = ServerSettings()
        self.metacognitive = MetacognitiveSettings()
        self.persistence = PersistenceSettings()
        self.node = NodeSettings()
        self.federated_learning = FederatedLearningSettings()
        self.logging = LoggingSettings()
        self.llm = LLMSettings()

class ServerSettings(BaseSettings):
    host: str = "localhost"
    port: int = 3000
    http_host: str = "localhost"
    http_port: int = 3000
    ssl_enabled: bool = False
    ssl_cert_path: str = "ssl/cert.pem"
    ssl_key_path: str = "ssl/key.pem"

class MetacognitiveSettings(BaseSettings):
    enabled: bool = True

class PersistenceSettings(BaseSettings):
    db_path: str = "chimera_memory.db"

class NodeSettings(BaseSettings):
    node_id: str = "default"

class FederatedLearningSettings(BaseSettings):
    enabled: bool = False

class LoggingSettings(BaseSettings):
    level: str = "INFO"
    format: str = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_enabled: bool = False
    file_path: str = "logs/chimera.log"
    file_max_bytes: int = 1048576
    file_backup_count: int = 3

class LLMSettings(BaseSettings):
    provider: str = "openai"

def get_settings():
    return Settings()

def save_default_config():
    pass
