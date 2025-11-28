#!/usr/bin/env python3
"""
CHIMERA AUTARCH - Tower API Key Integration
Integrates your custom API key generating tower with CHIMERA security
"""
import os
import asyncio
import time
import hashlib
import secrets
import logging
from typing import Dict, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

try:
    from security import SecurityManager, Role, Permission, APIKey, JWTToken
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

logger = logging.getLogger("chimera.tower")


@dataclass
class TowerCredentials:
    """Credentials for your Tower API"""
    tower_url: str
    tower_api_key: str
    tower_secret: str
    verify_ssl: bool = True


@dataclass
class TowerAPIKey:
    """API key from your Tower system"""
    key_id: str
    key_value: str
    user_id: str
    role: str
    scopes: Set[str]
    created_at: float
    expires_at: Optional[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


class TowerAdapter:
    """
    Adapter for integrating your API key generating tower with CHIMERA

    This bridges your existing tower with CHIMERA's security system:
    - Validates keys against your tower
    - Maps tower roles to CHIMERA roles
    - Syncs permissions and capabilities
    - Caches validated keys for performance
    """

    def __init__(
        self,
        tower_url: Optional[str] = None,
        tower_api_key: Optional[str] = None,
        tower_secret: Optional[str] = None,
        security_manager: Optional['SecurityManager'] = None,
        cache_ttl: int = 300  # 5 minutes
    ):
        # Load from environment if not provided
        self.tower_url = tower_url or os.getenv("TOWER_URL")
        self.tower_api_key = tower_api_key or os.getenv("TOWER_API_KEY")
        self.tower_secret = tower_secret or os.getenv("TOWER_SECRET")

        self.security_manager = security_manager
        self.cache_ttl = cache_ttl

        # Cache for validated keys (key_value -> (TowerAPIKey, validated_at))
        self._key_cache: Dict[str, tuple[TowerAPIKey, float]] = {}

        # Role mapping: Tower roles -> CHIMERA roles
        self.role_mapping = {
            "admin": Role.ADMIN,
            "operator": Role.OPERATOR,
            "observer": Role.OBSERVER,
            "node": Role.NODE,
            "api_client": Role.API_CLIENT,
            # Add your tower-specific roles
            "superuser": Role.ADMIN,
            "developer": Role.OPERATOR,
            "readonly": Role.OBSERVER,
        }

        logger.info(
            f"Tower adapter initialized: {self.tower_url or 'local mode'}")

    async def validate_key_with_tower(self, api_key: str) -> Optional[TowerAPIKey]:
        """
        Validate API key against your tower

        IMPLEMENT THIS based on your tower's API:
        - Make HTTP request to tower validation endpoint
        - Parse tower response
        - Return TowerAPIKey or None
        """
        # Check cache first
        if api_key in self._key_cache:
            tower_key, validated_at = self._key_cache[api_key]
            if time.time() - validated_at < self.cache_ttl:
                logger.debug(f"Using cached tower key: {tower_key.key_id}")
                return tower_key

        # TODO: Replace with actual tower API call
        # Example implementation:
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.tower_url}/api/validate",
                headers={
                    "Authorization": f"Bearer {self.tower_api_key}",
                    "X-Tower-Secret": self.tower_secret
                },
                json={"api_key": api_key}
            )
            
            if response.status_code == 200:
                data = response.json()
                tower_key = TowerAPIKey(
                    key_id=data["key_id"],
                    key_value=api_key,
                    user_id=data["user_id"],
                    role=data["role"],
                    scopes=set(data.get("scopes", [])),
                    created_at=data.get("created_at", time.time()),
                    expires_at=data.get("expires_at"),
                    metadata=data.get("metadata", {})
                )
                
                # Cache the validated key
                self._key_cache[api_key] = (tower_key, time.time())
                return tower_key
        
        return None
        """

        # For now, log that this needs implementation
        logger.warning(
            "validate_key_with_tower not implemented - using mock validation")

        # Mock validation (REMOVE THIS once you implement real tower API)
        if api_key.startswith("tower_"):
            tower_key = TowerAPIKey(
                key_id=hashlib.sha256(api_key.encode()).hexdigest()[:16],
                key_value=api_key,
                user_id="tower_user",
                role="operator",
                scopes={"execute:*", "view:*"},
                created_at=time.time(),
                expires_at=None
            )
            self._key_cache[api_key] = (tower_key, time.time())
            return tower_key

        return None

    def map_tower_role_to_chimera(self, tower_role: str) -> Role:
        """Map tower role to CHIMERA role"""
        return self.role_mapping.get(tower_role.lower(), Role.API_CLIENT)

    def map_tower_scopes_to_capabilities(self, scopes: Set[str]) -> Set[str]:
        """
        Convert tower scopes to CHIMERA capabilities

        Examples:
        - "tools:execute" -> "execute:*"
        - "files:read" -> "execute:read_file"
        - "admin:*" -> "*"
        """
        capabilities = set()

        for scope in scopes:
            # Direct mapping
            if scope == "admin:*" or scope == "*":
                capabilities.add("*")
            elif scope.startswith("tools:"):
                action = scope.split(":")[-1]
                if action == "execute":
                    capabilities.add("execute:*")
                else:
                    capabilities.add(f"execute:{action}")
            elif scope.startswith("files:"):
                action = scope.split(":")[-1]
                if action == "read":
                    capabilities.add("execute:read_file")
                elif action == "write":
                    capabilities.add("execute:write_file")
                elif action == "list":
                    capabilities.add("execute:list_directory")
            elif scope.startswith("system:"):
                action = scope.split(":")[-1]
                if action == "view":
                    capabilities.add("execute:get_system_stats")
                elif action == "manage":
                    capabilities.add("execute:*")

            # Keep original scope as well
            capabilities.add(scope)

        return capabilities

    async def sync_tower_key_to_chimera(
        self,
        api_key: str,
        force_refresh: bool = False
    ) -> Optional[APIKey]:
        """
        Validate key with tower and sync to CHIMERA security manager

        Returns CHIMERA APIKey object if valid
        """
        if not SECURITY_AVAILABLE or not self.security_manager:
            logger.error("Security manager not available")
            return None

        # Validate with tower
        tower_key = await self.validate_key_with_tower(api_key)
        if not tower_key:
            logger.warning(f"Tower key validation failed")
            return None

        # Map to CHIMERA role
        chimera_role = self.map_tower_role_to_chimera(tower_key.role)

        # Map scopes to capabilities
        capabilities = self.map_tower_scopes_to_capabilities(tower_key.scopes)

        # Check if key already exists in CHIMERA
        chimera_key = self.security_manager.verify_api_key(api_key)

        if chimera_key and not force_refresh:
            logger.debug(f"Using existing CHIMERA key: {chimera_key.key_id}")
            return chimera_key

        # Create new CHIMERA API key
        # Calculate expiry in days if tower key has expiry
        expires_in_days = None
        if tower_key.expires_at:
            days_remaining = (tower_key.expires_at - time.time()) / 86400
            expires_in_days = max(1, int(days_remaining))

        # Create the key in CHIMERA
        _, chimera_key_obj = self.security_manager.create_api_key(
            user_id=tower_key.user_id,
            role=chimera_role,
            capabilities=capabilities,
            expires_in_days=expires_in_days,
            rate_limit=tower_key.metadata.get("rate_limit", 100)
        )

        logger.info(
            f"Synced tower key to CHIMERA: "
            f"user={tower_key.user_id}, role={chimera_role.value}"
        )

        return chimera_key_obj

    async def authenticate_with_tower(
        self,
        api_key: str
    ) -> Optional[JWTToken]:
        """
        Authenticate using tower API key and return CHIMERA JWT token

        This is the main entry point for tower-based authentication
        """
        # Sync key from tower to CHIMERA
        chimera_key = await self.sync_tower_key_to_chimera(api_key)
        if not chimera_key:
            return None

        # Create JWT token using CHIMERA security manager
        jwt_token = self.security_manager.jwt_manager.create_token(
            user_id=chimera_key.user_id,
            role=chimera_key.role,
            capabilities=chimera_key.capabilities
        )

        logger.info(f"Created JWT token for tower user: {chimera_key.user_id}")
        return jwt_token

    def create_tower_key_locally(
        self,
        user_id: str,
        role: str,
        scopes: Set[str],
        expires_in_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a tower-style API key locally (without calling tower)

        Use this for development/testing or if your tower supports local generation
        """
        # Generate tower-style key
        api_key = f"tower_{secrets.token_urlsafe(32)}"

        expires_at = None
        if expires_in_days:
            expires_at = time.time() + (expires_in_days * 86400)

        tower_key = TowerAPIKey(
            key_id=hashlib.sha256(api_key.encode()).hexdigest()[:16],
            key_value=api_key,
            user_id=user_id,
            role=role,
            scopes=scopes,
            created_at=time.time(),
            expires_at=expires_at,
            metadata=metadata or {}
        )

        # Cache it
        self._key_cache[api_key] = (tower_key, time.time())

        logger.info(
            f"Created local tower key: {tower_key.key_id} for {user_id}")
        return api_key

    def clear_cache(self):
        """Clear the validation cache"""
        self._key_cache.clear()
        logger.info("Tower key cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = time.time()
        valid_entries = sum(
            1 for _, validated_at in self._key_cache.values()
            if now - validated_at < self.cache_ttl
        )

        return {
            "total_cached_keys": len(self._key_cache),
            "valid_cached_keys": valid_entries,
            "cache_ttl_seconds": self.cache_ttl,
            "cache_hit_ratio": valid_entries / max(1, len(self._key_cache))
        }


class TowerMiddleware:
    """
    Middleware for HTTP requests that checks tower API keys

    Use this to protect HTTP endpoints with tower authentication
    """

    def __init__(self, tower_adapter: TowerAdapter):
        self.tower = tower_adapter

    async def authenticate_request(
        self,
        headers: Dict[str, str]
    ) -> Optional[JWTToken]:
        """
        Extract and validate API key from request headers

        Supports:
        - Authorization: Bearer <api_key>
        - X-API-Key: <api_key>
        - X-Tower-Key: <api_key>
        """
        # Try Bearer token
        auth_header = headers.get(
            "authorization") or headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            api_key = auth_header[7:].strip()
            return await self.tower.authenticate_with_tower(api_key)

        # Try X-API-Key
        api_key = headers.get("x-api-key") or headers.get("X-API-Key")
        if api_key:
            return await self.tower.authenticate_with_tower(api_key)

        # Try X-Tower-Key (your custom header)
        tower_key = headers.get("x-tower-key") or headers.get("X-Tower-Key")
        if tower_key:
            return await self.tower.authenticate_with_tower(tower_key)

        return None


# Example usage functions

async def example_basic_usage():
    """Example: Basic tower integration"""
    from security import SecurityManager

    # Initialize security manager
    security = SecurityManager()

    # Initialize tower adapter
    tower = TowerAdapter(
        tower_url="https://your-tower.example.com",
        tower_api_key="your_tower_admin_key",
        tower_secret="your_tower_secret",
        security_manager=security
    )

    # Authenticate with tower key
    api_key = "tower_abc123..."
    jwt_token = await tower.authenticate_with_tower(api_key)

    if jwt_token:
        print(f"âœ… Authenticated! JWT: {jwt_token.token[:20]}...")
        print(f"   User: {jwt_token.user_id}")
        print(f"   Role: {jwt_token.role.value}")
        print(f"   Capabilities: {jwt_token.capabilities}")
    else:
        print("âŒ Authentication failed")


async def example_http_middleware():
    """Example: Protecting HTTP endpoints with tower middleware"""
    from security import SecurityManager

    security = SecurityManager()
    tower = TowerAdapter(security_manager=security)
    middleware = TowerMiddleware(tower)

    # Simulate HTTP request
    headers = {
        "Authorization": "Bearer tower_abc123...",
        "X-Real-IP": "192.168.1.100"
    }

    jwt_token = await middleware.authenticate_request(headers)

    if jwt_token:
        print(f"âœ… Request authorized: {jwt_token.user_id}")

        # Check specific permission
        if security.check_permission(jwt_token.role, Permission.EXECUTE_TOOL):
            print("   Can execute tools")

        # Check rate limit
        if security.check_rate_limit(jwt_token.user_id):
            print("   Rate limit OK")
        else:
            print("   âš ï¸  Rate limit exceeded")
    else:
        print("âŒ Request unauthorized")


async def example_create_local_keys():
    """Example: Create tower-style keys locally"""
    from security import SecurityManager

    security = SecurityManager()
    tower = TowerAdapter(security_manager=security)

    # Create a tower key for a developer
    dev_key = tower.create_tower_key_locally(
        user_id="developer_alice",
        role="developer",
        scopes={"tools:execute", "files:read", "files:write", "system:view"},
        expires_in_days=30,
        metadata={"team": "backend", "rate_limit": 200}
    )

    print(f"âœ… Created developer key: {dev_key}")

    # Create a readonly key for monitoring
    monitor_key = tower.create_tower_key_locally(
        user_id="monitoring_system",
        role="readonly",
        scopes={"system:view"},
        expires_in_days=365,
        metadata={"purpose": "metrics_collection", "rate_limit": 1000}
    )

    print(f"âœ… Created monitoring key: {monitor_key}")

    # Authenticate with the key
    jwt_token = await tower.authenticate_with_tower(dev_key)
    print(f"âœ… Developer authenticated: {jwt_token.user_id}")


async def example_cache_management():
    """Example: Manage validation cache"""
    from security import SecurityManager

    security = SecurityManager()
    tower = TowerAdapter(security_manager=security, cache_ttl=60)

    # First validation (hits tower API)
    jwt1 = await tower.authenticate_with_tower("tower_key123")
    print(f"First validation: {jwt1.user_id if jwt1 else 'Failed'}")

    # Second validation (from cache)
    jwt2 = await tower.authenticate_with_tower("tower_key123")
    print(f"Second validation (cached): {jwt2.user_id if jwt2 else 'Failed'}")

    # Check cache stats
    stats = tower.get_cache_stats()
    print(f"Cache stats: {stats}")

    # Clear cache
    tower.clear_cache()
    print("Cache cleared")


if __name__ == "__main__":
    """
    Run examples to test tower integration
    """
    import sys

    if not SECURITY_AVAILABLE:
        print("âŒ Security module not available. Install CHIMERA first.")
        sys.exit(1)

    print("="*60)
    print("CHIMERA Tower Integration - Examples")
    print("="*60)

    # Run examples
    asyncio.run(example_create_local_keys())
    print("\n" + "-"*60 + "\n")

    asyncio.run(example_http_middleware())
    print("\n" + "-"*60 + "\n")

    asyncio.run(example_cache_management())

    print("\n" + "="*60)
    print("âœ… Examples complete!")
    print("="*60)
    print("\nðŸ“ Next Steps:")
    print("1. Set environment variables:")
    print("   export TOWER_URL='https://your-tower.example.com'")
    print("   export TOWER_API_KEY='your_tower_admin_key'")
    print("   export TOWER_SECRET='your_tower_secret'")
    print("\n2. Implement validate_key_with_tower() with your tower's API")
    print("\n3. Integrate with chimera_autarch.py WebSocket/HTTP handlers")
    print("\n4. Update role_mapping for your tower's role names")
    print()

