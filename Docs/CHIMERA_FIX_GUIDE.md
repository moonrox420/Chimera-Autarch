# CHIMERA System Fix and Deployment Guide

## Issues Identified

1. **Missing config.yaml** - Docker build fails
2. **PowerShell Scripts** - Run as batch files (incorrect)
3. **Dependencies** - Missing dataclass, version conflicts
4. **Core Files** - Missing sanctuary functions
5. **Service Installation** - Requires admin privileges

## Quick Fix Solutions

### 1. Create Missing config.yaml
```yaml
server:
  websocket_host: localhost
  websocket_port: 3001
  http_host: localhost
  http_port: 3000
  ssl_enabled: false

metacognitive:
  confidence_threshold: 0.6
  learning_cooldown: 300
  failure_history_size: 100

persistence:
  database_path: chimera_memory.db
  backup_interval: 3600
  backup_retention: 24

logging:
  level: INFO
  file_enabled: false
```

### 2. Run Commands Correctly
```bash
# PowerShell (as admin)
.\install-service.ps1

# Python
python chimera_autarch.py

# Docker (after config.yaml exists)
docker compose up -d --build
```

### 3. Fix Dependencies
```bash
# Install core dependencies
pip install dataclasses typing-extensions pydantic websockets aiosqlite

# Or use virtual environment
python -m venv chimera-env
.\chimera-env\Scripts\Activate
pip install -r requirements-core.txt
```

## Status
- Port changes: ✅ COMPLETED (8765 → 3000/3001)
- droxai_tower: ✅ MOVED to C:\Users\droxaitower
- chimera_web_cli.html: ✅ REMOVED
- CLI System: ✅ ACTIVE with fortress commands
