#!/usr/bin/env python3
"""
DroxAI Consumer Launcher
Single entry point for end users - handles environment setup and service orchestration
"""
import os
import sys
import json
import time
import subprocess
import webbrowser
import threading
from pathlib import Path
from typing import Optional

class DroxAILauncher:
    """Consumer-friendly launcher for DroxAI system"""
    
    def __init__(self):
        self.app_home = self._get_app_home()
        self.config_manager = None
        self.backend_process = None
        self.frontend_process = None
        
    def _get_app_home(self) -> Path:
        """Get application home directory"""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        else:
            return Path(__file__).parent
    
    def _load_config(self) -> dict:
        """Load configuration from appsettings.json"""
        config_file = self.app_home / "config" / "appsettings.json"
        
        if not config_file.exists():
            print(f"[DroxAI] Creating default configuration at {config_file}")
            self._create_default_config()
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[DroxAI] Error loading config: {e}")
            return self._get_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration file"""
        config_dir = self.app_home / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        default_config = self._get_default_config()
        
        with open(config_dir / "appsettings.json", 'w') as f:
            json.dump(default_config, f, indent=2)
    
    def _get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            "App": {
                "Name": "DroxAI",
                "Version": "1.0.0",
                "Description": "Advanced AI Orchestration System",
                "Environment": "Production"
            },
            "Server": {
                "WebSocketHost": "localhost",
                "WebSocketPort": 3001,
                "HttpHost": "localhost",
                "HttpPort": 3000,
                "SSLEnabled": False,
                "SSLCertPath": "",
                "SSLKeyPath": ""
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
                "ServerAddress": "127.0.0.1:8080",
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
            }
        }
    
    def _setup_directories(self) -> None:
        """Ensure all required directories exist"""
        dirs = [
            "data",
            "logs", 
            "temp",
            "plugins",
            "runtime/models",
            "runtime/certificates"
        ]
        
        for dir_name in dirs:
            dir_path = self.app_home / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _find_python_executable(self) -> Optional[str]:
        """Find Python executable"""
        # Check for embedded Python in frozen executable
        if getattr(sys, 'frozen', False):
            # Try to find Python in the same directory
            python_paths = [
                sys.executable,  # Use current executable
                self.app_home / "python.exe",
                self.app_home / "bin" / "python.exe",
                "python.exe",
                "py"
            ]
            
            for python_path in python_paths:
                try:
                    if subprocess.run([python_path, "--version"], 
                                    capture_output=True, text=True).returncode == 0:
                        return python_path
                except (FileNotFoundError, OSError):
                    continue
        else:
            # Running as script, use current Python
            return sys.executable
        
        return None
    
    def _check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("[DroxAI] Checking prerequisites...")
        
        # Check Python
        python_exe = self._find_python_executable()
        if not python_exe:
            print("[DroxAI] ERROR: Python executable not found")
            return False
        
        print(f"[DroxAI] Using Python: {python_exe}")
        
        # Check backend executable
        backend_exe = self._find_backend_executable()
        if not backend_exe:
            print("[DroxAI] ERROR: Backend executable not found")
            return False
        
        print(f"[DroxAI] Backend: {backend_exe}")
        
        return True
    
    def _find_backend_executable(self) -> Optional[Path]:
        """Find the backend executable"""
        possible_backends = [
            self.app_home / "bin" / "DroxAI_Core.exe",
            self.app_home / "bin" / "DroxAI_Core.py",
            self.app_home / "droxai_core.exe",
            self.app_home / "droxai_core.py"
        ]
        
        for backend_path in possible_backends:
            if backend_path.exists():
                return backend_path
        
        return None
    
    def start_backend(self, config: dict) -> bool:
        """Start the backend service"""
        print("[DroxAI] Starting backend service...")
        
        backend_path = self._find_backend_executable()
        if not backend_path:
            print("[DroxAI] ERROR: Backend executable not found")
            return False
        
        # Prepare environment
        env = os.environ.copy()
        env['DROXAI_HOME'] = str(self.app_home)
        env['DROXAI_CONFIG'] = str(self.app_home / "config" / "appsettings.json")
        
        try:
            # Start backend process
            if backend_path.suffix == '.exe':
                # Windows executable
                self.backend_process = subprocess.Popen(
                    [str(backend_path)],
                    cwd=str(self.app_home),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
            else:
                # Python script
                python_exe = self._find_python_executable()
                if not python_exe:
                    return False
                
                self.backend_process = subprocess.Popen(
                    [python_exe, str(backend_path)],
                    cwd=str(self.app_home),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            # Wait for backend to start
            print("[DroxAI] Waiting for backend to initialize...")
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("[DroxAI] Backend started successfully")
                return True
            else:
                print("[DroxAI] ERROR: Backend failed to start")
                stdout, stderr = self.backend_process.communicate()
                if stderr:
                    print(f"[DroxAI] Backend error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"[DroxAI] ERROR: Failed to start backend: {e}")
            return False
    
    def open_web_interface(self, config: dict) -> None:
        """Open web interface in default browser"""
        host = config.get("Server", {}).get("HttpHost", "localhost")
        port = config.get("Server", {}).get("HttpPort", 3000)
        
        # Wait a moment for server to be ready
        time.sleep(2)
        
        url = f"http://{host}:{port}"
        print(f"[DroxAI] Opening web interface: {url}")
        
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"[DroxAI] Warning: Could not open browser: {e}")
            print(f"[DroxAI] Please open {url} manually")
    
    def run(self) -> None:
        """Main launcher entry point"""
        print("=" * 60)
        print("    DroxAI v1.0.0 - Advanced AI Orchestration System")
        print("=" * 60)
        print()
        
        try:
            # Setup
            self._setup_directories()
            config = self._load_config()
            
            # Check prerequisites
            if not self._check_prerequisites():
                input("Press Enter to exit...")
                return
            
            # Start backend
            if not self.start_backend(config):
                input("Press Enter to exit...")
                return
            
            # Open web interface in background thread
            threading.Thread(target=self.open_web_interface, args=(config,), daemon=True).start()
            
            print()
            print("[DroxAI] ====================================================")
            print("[DroxAI]  DroxAI is now running!")
            print("[DroxAI] ====================================================")
            print()
            print(f"[DroxAI] Web Interface: http://localhost:{config.get('Server', {}).get('HttpPort', 3000)}")
            print(f"[DroxAI] WebSocket API: ws://localhost:{config.get('Server', {}).get('WebSocketPort', 3001)}")
            print()
            print("[DroxAI] Press Ctrl+C to stop the application")
            print()
            
            # Monitor backend process
            try:
                while True:
                    if self.backend_process.poll() is not None:
                        print("[DroxAI] Backend process terminated unexpectedly")
                        break
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[DroxAI] Shutting down...")
            
        except Exception as e:
            print(f"[DroxAI] ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up processes"""
        if self.backend_process and self.backend_process.poll() is None:
            print("[DroxAI] Stopping backend...")
            self.backend_process.terminate()
            
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                self.backend_process.wait()

def main():
    """Main entry point"""
    try:
        launcher = DroxAILauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n[DroxAI] Interrupted by user")
    except Exception as e:
        print(f"[DroxAI] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

