class ServerConfig:
    http_host = "127.0.0.1"
    http_port = 3000
    websocket_host = "127.0.0.1"
    websocket_port = 3000

class AppConfig:
    name = "CHIMERA AUTARCH v3"
    version = "3.0.0"

class Config:
    server = ServerConfig()
    app = AppConfig()

class ConfigManager:
    @staticmethod
    def load_config():
        return Config()

