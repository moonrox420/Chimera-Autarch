# 🗼 Tower API Key Integration Guide

**Integrate your custom API key generating tower with CHIMERA AUTARCH**

## Overview

The `tower_integration.py` module bridges your existing API key tower with CHIMERA's security system. It:

- ✅ Validates keys against your tower API
- ✅ Maps tower roles to CHIMERA roles
- ✅ Syncs permissions and capabilities
- ✅ Caches validated keys for performance
- ✅ Provides HTTP middleware for protected endpoints

## Quick Start

### 1. Environment Setup

```bash
# Configure your tower connection
export TOWER_URL="https://your-tower.example.com"
export TOWER_API_KEY="your_tower_admin_key"
export TOWER_SECRET="your_tower_secret"
```

### 2. Basic Usage

```python
from security import SecurityManager
from tower_integration import TowerAdapter

# Initialize
security = SecurityManager()
tower = TowerAdapter(
    tower_url="https://your-tower.example.com",
    tower_api_key="your_admin_key",
    tower_secret="your_secret",
    security_manager=security
)

# Authenticate with tower key
jwt_token = await tower.authenticate_with_tower("tower_key_abc123")

if jwt_token:
    print(f"✅ Authenticated: {jwt_token.user_id}")
    print(f"   Role: {jwt_token.role.value}")
    print(f"   Capabilities: {jwt_token.capabilities}")
```

### 3. HTTP Middleware

```python
from tower_integration import TowerMiddleware

middleware = TowerMiddleware(tower)

# In your HTTP handler
async def handle_request(headers):
    jwt_token = await middleware.authenticate_request(headers)
    
    if not jwt_token:
        return {"error": "Unauthorized"}, 401
    
    # Request is authenticated
    # ... handle request ...
```

## Implementation Steps

### Step 1: Implement Tower API Validation

Edit `tower_integration.py` line ~95, replace the mock validation with your actual tower API:

```python
async def validate_key_with_tower(self, api_key: str) -> Optional[TowerAPIKey]:
    """Validate API key against your tower"""
    
    # Check cache first
    if api_key in self._key_cache:
        tower_key, validated_at = self._key_cache[api_key]
        if time.time() - validated_at < self.cache_ttl:
            return tower_key
    
    # Call YOUR tower API
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{self.tower_url}/api/v1/validate",  # YOUR endpoint
            headers={
                "Authorization": f"Bearer {self.tower_api_key}",
                "X-Tower-Secret": self.tower_secret
            },
            json={"api_key": api_key}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            tower_key = TowerAPIKey(
                key_id=data["key_id"],           # YOUR field names
                key_value=api_key,
                user_id=data["user_id"],         # YOUR field names
                role=data["role"],               # YOUR field names
                scopes=set(data.get("scopes", [])),
                created_at=data.get("created_at", time.time()),
                expires_at=data.get("expires_at"),
                metadata=data.get("metadata", {})
            )
            
            # Cache the validated key
            self._key_cache[api_key] = (tower_key, time.time())
            return tower_key
    
    return None
```

### Step 2: Configure Role Mapping

Edit the `role_mapping` dict to match your tower's role names:

```python
self.role_mapping = {
    # Tower role -> CHIMERA role
    "admin": Role.ADMIN,
    "operator": Role.OPERATOR,
    "observer": Role.OBSERVER,
    "node": Role.NODE,
    "api_client": Role.API_CLIENT,
    
    # YOUR custom tower roles
    "superuser": Role.ADMIN,
    "engineer": Role.OPERATOR,
    "developer": Role.OPERATOR,
    "readonly": Role.OBSERVER,
    "service_account": Role.API_CLIENT,
}
```

### Step 3: Map Tower Scopes to CHIMERA Capabilities

Edit `map_tower_scopes_to_capabilities()` to match your tower's scope format:

```python
def map_tower_scopes_to_capabilities(self, scopes: Set[str]) -> Set[str]:
    """Convert tower scopes to CHIMERA capabilities"""
    capabilities = set()
    
    for scope in scopes:
        # YOUR tower's scope format
        if scope == "admin:full":
            capabilities.add("*")
        elif scope == "tools:execute":
            capabilities.add("execute:*")
        elif scope == "tools:read_only":
            capabilities.add("execute:get_system_stats")
            capabilities.add("execute:get_node_status")
        elif scope.startswith("file:"):
            action = scope.split(":")[-1]
            if action == "read":
                capabilities.add("execute:read_file")
            elif action == "write":
                capabilities.add("execute:write_file")
        
        # Keep original scope
        capabilities.add(scope)
    
    return capabilities
```

## Integration with CHIMERA

### Option 1: Integrate with chimera_autarch.py

Add tower authentication to the WebSocket handler:

```python
# In chimera_autarch.py, add at top:
from tower_integration import TowerAdapter, TowerMiddleware

class HeartNode:
    def __init__(self, ...):
        # ... existing init ...
        
        # Add tower adapter
        self.tower = TowerAdapter(security_manager=self.security)
        self.tower_middleware = TowerMiddleware(self.tower)
    
    async def _handle_websocket_client(self, websocket, path):
        """Handle WebSocket client with tower auth"""
        
        try:
            # First message should be authentication
            auth_msg = await asyncio.wait_for(
                websocket.recv(), timeout=10.0
            )
            auth_data = json.loads(auth_msg)
            
            # Support tower API key auth
            if auth_data.get("type") == "auth" and auth_data.get("api_key"):
                api_key = auth_data["api_key"]
                jwt_token = await self.tower.authenticate_with_tower(api_key)
                
                if not jwt_token:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid API key"
                    }))
                    return
                
                # Store token for this connection
                # ... continue with authenticated connection ...
```

### Option 2: Protect HTTP Endpoints

```python
# In APIRequestHandler class
async def do_POST(self):
    """POST handler with tower auth"""
    
    if self.path == "/api/protected":
        # Extract headers
        headers = dict(self.headers)
        
        # Authenticate with tower
        jwt_token = await self.tower_middleware.authenticate_request(headers)
        
        if not jwt_token:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Unauthorized"
            }).encode())
            return
        
        # Check permissions
        if not security.check_permission(jwt_token.role, Permission.EXECUTE_TOOL):
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Forbidden"
            }).encode())
            return
        
        # Request is authorized
        # ... handle request ...
```

## Tower API Requirements

Your tower should provide an endpoint that:

**Request:**
```json
POST /api/v1/validate
Headers:
  Authorization: Bearer <tower_admin_key>
  X-Tower-Secret: <secret>
Body:
{
  "api_key": "tower_abc123..."
}
```

**Response (Success):**
```json
{
  "valid": true,
  "key_id": "key_12345",
  "user_id": "user_alice",
  "role": "operator",
  "scopes": ["tools:execute", "files:read"],
  "created_at": 1699999999.0,
  "expires_at": 1702591999.0,
  "metadata": {
    "team": "backend",
    "rate_limit": 200
  }
}
```

**Response (Invalid):**
```json
{
  "valid": false,
  "error": "Key not found"
}
```

## Local Development (Without Tower)

For testing without connecting to your tower:

```python
# Create local tower-style keys
tower = TowerAdapter(security_manager=security)

# Generate a key
dev_key = tower.create_tower_key_locally(
    user_id="alice",
    role="developer",
    scopes={"tools:execute", "files:read", "files:write"},
    expires_in_days=30
)

print(f"Generated key: {dev_key}")

# Use the key
jwt_token = await tower.authenticate_with_tower(dev_key)
```

## Authentication Flow

```
1. Client sends request with API key
   ↓
2. TowerMiddleware extracts key from headers
   ↓
3. TowerAdapter.authenticate_with_tower(api_key)
   ↓
4. Check cache (if exists and valid, return cached)
   ↓
5. Call tower API to validate key
   ↓
6. Tower returns user_id, role, scopes
   ↓
7. Map tower role → CHIMERA role
8. Map tower scopes → CHIMERA capabilities
   ↓
9. Create CHIMERA APIKey object
   ↓
10. Generate JWT token
    ↓
11. Cache validated key
    ↓
12. Return JWT token to client
```

## Security Features

### Cache Management
- **TTL**: 5 minutes default (configurable)
- **Invalidation**: Manual via `tower.clear_cache()`
- **Stats**: `tower.get_cache_stats()` for monitoring

### Rate Limiting
- Uses tower's `rate_limit` from metadata
- Falls back to CHIMERA's default (100 req/min)
- Per-user tracking in SecurityManager

### Audit Logging
- All authentications logged
- Failed attempts tracked
- Can query via `security.get_audit_log()`

## Performance

- **First auth**: Tower API call (~50-200ms)
- **Cached auth**: <1ms lookup
- **JWT creation**: ~2ms
- **Cache hit ratio**: Typically >90% with 5min TTL

## Monitoring

```python
# Cache statistics
stats = tower.get_cache_stats()
print(f"Cached keys: {stats['total_cached_keys']}")
print(f"Valid keys: {stats['valid_cached_keys']}")
print(f"Hit ratio: {stats['cache_hit_ratio']:.2%}")

# Security statistics
sec_stats = security.get_security_stats()
print(f"Active tokens: {sec_stats['active_tokens']}")
print(f"Failed logins: {sec_stats['failed_logins_recent']}")
print(f"Rate limits: {sec_stats['rate_limit_hits']}")
```

## Example: Complete Integration

```python
import asyncio
from security import SecurityManager
from tower_integration import TowerAdapter, TowerMiddleware

async def main():
    # Initialize security
    security = SecurityManager()
    
    # Initialize tower adapter
    tower = TowerAdapter(
        tower_url="https://tower.example.com",
        tower_api_key="admin_key_123",
        tower_secret="secret_456",
        security_manager=security,
        cache_ttl=300  # 5 minutes
    )
    
    # Create middleware
    middleware = TowerMiddleware(tower)
    
    # Simulate authentication
    headers = {
        "Authorization": "Bearer tower_abc123...",
        "X-Real-IP": "192.168.1.100"
    }
    
    jwt_token = await middleware.authenticate_request(headers)
    
    if jwt_token:
        print(f"✅ Authenticated: {jwt_token.user_id}")
        
        # Check permissions
        from security import Permission
        
        if security.check_permission(jwt_token.role, Permission.EXECUTE_TOOL):
            print("✅ Can execute tools")
        
        if security.check_permission(jwt_token.role, Permission.MANAGE_NODES):
            print("✅ Can manage nodes")
        
        # Check rate limit
        if security.check_rate_limit(jwt_token.user_id):
            print("✅ Rate limit OK")
        
        # Execute protected action
        print("\n🔧 Executing protected tool...")
        # ... your protected code ...
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Issue: "validate_key_with_tower not implemented"
**Solution**: Replace the mock validation with your tower API call (see Step 1)

### Issue: "Tower key validation failed"
**Check**:
- Tower URL is correct
- Tower API key has admin permissions
- Tower secret matches
- API key format is valid
- Tower API endpoint is accessible

### Issue: Role mapping not working
**Solution**: Update `role_mapping` dict to match your tower's role names

### Issue: Capabilities not syncing
**Solution**: Update `map_tower_scopes_to_capabilities()` to match your scope format

### Issue: Cache not clearing
**Solution**: Call `tower.clear_cache()` or reduce `cache_ttl`

## Testing

Run the examples:

```bash
# Test basic functionality
python tower_integration.py

# Test with custom tower
python -c "
import asyncio
from tower_integration import TowerAdapter
from security import SecurityManager

async def test():
    security = SecurityManager()
    tower = TowerAdapter(
        tower_url='http://localhost:9999',
        security_manager=security
    )
    
    # Create local key for testing
    key = tower.create_tower_key_locally(
        user_id='test_user',
        role='operator',
        scopes={'tools:execute', 'files:read'}
    )
    
    print(f'Test key: {key}')
    
    # Authenticate
    jwt = await tower.authenticate_with_tower(key)
    print(f'JWT: {jwt.token[:40]}...')
    
asyncio.run(test())
"
```

## Next Steps

1. ✅ Configure environment variables
2. ✅ Implement `validate_key_with_tower()` with your tower's API
3. ✅ Update role mapping
4. ✅ Update scope mapping
5. ✅ Integrate with chimera_autarch.py
6. ✅ Test authentication flow
7. ✅ Deploy to production

---

**Questions?** Check the inline comments in `tower_integration.py` or run the examples.
