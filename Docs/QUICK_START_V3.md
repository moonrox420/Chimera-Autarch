# 🔥 CHIMERA v3.0 - QUICK REFERENCE

## Installation

```bash
# Clone and setup
git clone <your-repo>
cd Drox_AI

# Install base dependencies
pip install -r requirements.txt

# Optional: AI Code Generation
export OPENAI_API_KEY="sk-..."  # or ANTHROPIC_API_KEY

# Start CHIMERA
python chimera_autarch.py
```

## 5 Wickedly Badass Features

### 1️⃣ AI Code Generation

```python
from llm_integration import CodeGenerator

gen = CodeGenerator()  # Auto-detects OpenAI/Claude/Ollama
patch = await gen.generate_patch(
    "Create async API client with retry logic",
    context={"base_url": "https://api.example.com"}
)
result = await gen.apply_with_rollback(patch, Path("client.py"))
```

### 2️⃣ Anomaly Detection

```python
from anomaly_detection import AnomalyDetectionEngine

engine = AnomalyDetectionEngine()
await engine.add_metric("cpu_usage", 0.85)  # Auto-detects anomalies
will_fail, conf, forecast = await engine.predict_future_anomalies("cpu_usage", 10)
```

### 3️⃣ Security

```python
from security import SecurityManager, Role

sec = SecurityManager()
token = sec.authenticate("user", "pass", "192.168.1.1")
if sec.check_permission(token.role, Permission.EXECUTE_TOOL):
    if sec.check_rate_limit(token.user_id):
        # Execute tool
```

### 4️⃣ Swarm Coordination

```python
from swarm_coordination import SwarmCoordinator, AgentSpec, Task

swarm = SwarmCoordinator(max_agents=10)
agent = await swarm.spawn_agent(AgentSpec(
    agent_id="worker_1",
    role="executor",
    capabilities={"analyze", "optimize"}
))
await swarm.submit_task(Task(
    task_id="optimize_code",
    description="Analyze and optimize performance"
))
```

### 5️⃣ Hot Reload

```python
from hot_reload import HotReloadManager

reload = HotReloadManager(watch_paths=[Path(".")])
await reload.start()  # Watches for file changes

# Execute versioned tools
result = await reload.execute_tool_versioned(
    "read_file", 
    version="2.0",  # Specific version
    path="data.txt"
)
```

## API Endpoints

```bash
# Core
GET  http://localhost:3000              # Dashboard
GET  http://localhost:3000/metrics      # All metrics
WS   ws://localhost:3001                # WebSocket

# v3.0 Endpoints
POST /api/auth/login                    # JWT authentication
POST /api/llm/generate                  # Generate code patch
GET  /api/anomaly/detect                # Anomaly detection
POST /api/swarm/spawn                   # Spawn agent
POST /api/reload/module                 # Hot reload module

# v2.2 Endpoints  
GET  /api/events                        # Event statistics
GET  /graphql                           # GraphQL playground
POST /graphql                           # GraphQL queries
```

## Environment Variables

```bash
# LLM Providers
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export OLLAMA_BASE_URL="http://localhost:11434"

# Security
export CHIMERA_ADMIN_PASSWORD="secure123"
export CHIMERA_SECRET_KEY="your-jwt-secret"

# Swarm
export CHIMERA_MAX_AGENTS="10"
export CHIMERA_BASE_PORT="9000"

# Features
export CHIMERA_AUTO_RELOAD="true"
export CHIMERA_ENABLE_SWARM="true"
```

## Metrics

```bash
curl http://localhost:3000/metrics | jq

{
  "llm": {
    "success_rate": 0.92,
    "avg_time": 3.2,
    "provider": "OpenAIProvider"
  },
  "anomaly": {
    "total": 15,
    "last_hour": 3,
    "by_type": {"spike": 8, "drop": 4}
  },
  "security": {
    "active_tokens": 12,
    "failed_logins": 2
  },
  "swarm": {
    "active_agents": 7,
    "completed_tasks": 143
  },
  "hot_reload": {
    "total_reloads": 23,
    "tool_versions": 15
  }
}
```

## Dependencies

```bash
# Core (required)
pip install websockets aiosqlite numpy flwr grpcio

# AI Generation (optional)
pip install openai anthropic httpx

# Security (required for auth)
pip install PyJWT

# Anomaly Detection (optional)
pip install scikit-learn

# Hot Reload (required for auto-reload)
pip install watchdog
```

## Quick Tips

✅ **Start simple**: Run `python chimera_autarch.py` - all features have graceful degradation  
✅ **Add features incrementally**: Install optional deps as needed  
✅ **Use environment variables**: Configure without code changes  
✅ **Check metrics**: Monitor at `/metrics` endpoint  
✅ **Enable what you need**: Features can be toggled independently  

## File Structure

```
Drox_AI/
├── chimera_autarch.py        # Main system
├── llm_integration.py        # AI code gen
├── anomaly_detection.py      # Predictive alerts
├── security.py               # Auth & RBAC
├── swarm_coordination.py     # Multi-agent
├── hot_reload.py             # Zero-downtime
├── event_broker.py           # Real-time events
├── graphql_api.py            # GraphQL
├── requirements.txt          # Dependencies
└── WICKEDLY_BADASS_v3.md    # Full docs
```

## Performance

| Feature | Latency | Notes |
|---------|---------|-------|
| AI Code Gen | 2-5s | OpenAI/Claude |
| Anomaly Detect | <10ms | Real-time |
| Auth Check | <1ms | JWT verify |
| Rate Limit | <0.1ms | Token bucket |
| Agent Spawn | 2-5s | Subprocess |
| Hot Reload | 50-200ms | Module reload |

## Support

📖 Full docs: [WICKEDLY_BADASS_v3.md](./WICKEDLY_BADASS_v3.md)  
🏗️ Architecture: [README.md](./README.md)  
🔓 Independence: [INDEPENDENCE_GUIDE.md](./INDEPENDENCE_GUIDE.md)  
🎮 Quick start: This file!

---

**CHIMERA v3.0 - Power Level: 9000+** 🔥
