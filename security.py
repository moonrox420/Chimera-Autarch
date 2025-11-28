#!/usr/bin/env python3
"""
CHIMERA AUTARCH - Zero-Trust Security Module
JWT authentication, capability tokens, rate limiting, audit logging
"""
import os
import asyncio
import time
import secrets
import hashlib
import json
from typing import Dict, Set, Optional, List, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import logging

logger = logging.getLogger("chimera.security")


class Role(Enum):
    """User roles with hierarchical permissions"""
    ADMIN = "admin"           # Full access
    OPERATOR = "operator"     # Can execute tools and view metrics
    OBSERVER = "observer"     # Read-only access
    NODE = "node"            # Distributed node (limited tool access)
    API_CLIENT = "api_client"  # External API access


class Permission(Enum):
    """Granular permissions"""
    EXECUTE_TOOL = "execute_tool"
    VIEW_METRICS = "view_metrics"
    MANAGE_NODES = "manage_nodes"
    TRIGGER_LEARNING = "trigger_learning"
    MODIFY_CONFIG = "modify_config"
    VIEW_AUDIT_LOG = "view_audit_log"
    MANAGE_USERS = "manage_users"


# Role -> Permission mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.EXECUTE_TOOL,
        Permission.VIEW_METRICS,
        Permission.MANAGE_NODES,
        Permission.TRIGGER_LEARNING,
        Permission.MODIFY_CONFIG,
        Permission.VIEW_AUDIT_LOG,
        Permission.MANAGE_USERS,
    },
    Role.OPERATOR: {
        Permission.EXECUTE_TOOL,
        Permission.VIEW_METRICS,
        Permission.TRIGGER_LEARNING,
    },
    Role.OBSERVER: {
        Permission.VIEW_METRICS,
    },
    Role.NODE: {
        Permission.EXECUTE_TOOL,
        Permission.VIEW_METRICS,
    },
    Role.API_CLIENT: {
        Permission.EXECUTE_TOOL,
        Permission.VIEW_METRICS,
    },
}


@dataclass
class User:
    """User account with credentials and permissions"""
    user_id: str
    username: str
    password_hash: str
    role: Role
    api_key: Optional[str] = None
    # Specific tool capabilities
    capabilities: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=lambda: time.time())
    last_login: Optional[float] = None
    enabled: bool = True


@dataclass
class APIKey:
    """API key for external integrations"""
    key_id: str
    key_hash: str
    user_id: str
    role: Role
    capabilities: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=lambda: time.time())
    expires_at: Optional[float] = None
    enabled: bool = True
    rate_limit: int = 100  # requests per minute


@dataclass
class CapabilityToken:
    """Fine-grained capability token for specific operations"""
    token_id: str
    user_id: str
    capability: str  # e.g., "execute:read_file", "trigger:federated_learning"
    expires_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JWTToken:
    """JWT token structure"""
    token: str
    user_id: str
    role: Role
    issued_at: float
    expires_at: float
    capabilities: Set[str] = field(default_factory=set)


@dataclass
class AuditLogEntry:
    """Audit log entry for security events"""
    timestamp: float
    event_type: str  # login, logout, execute_tool, access_denied, etc.
    user_id: str
    ip_address: Optional[str]
    action: str
    resource: Optional[str]
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.tokens = requests_per_minute
        self.last_update = time.time()
        self.bucket_size = requests_per_minute
        self.refill_rate = requests_per_minute / 60.0  # per second

    def allow_request(self) -> bool:
        """Check if request is allowed under rate limit"""
        current_time = time.time()
        time_passed = current_time - self.last_update

        # Refill tokens
        self.tokens = min(
            self.bucket_size,
            self.tokens + time_passed * self.refill_rate
        )
        self.last_update = current_time

        # Check if request allowed
        if self.tokens >= 1:
            self.tokens -= 1
            return True

        return False

    def get_wait_time(self) -> float:
        """Get time to wait until next request allowed"""
        if self.tokens >= 1:
            return 0.0

        tokens_needed = 1 - self.tokens
        return tokens_needed / self.refill_rate


class ClientRateLimiter:
    """Per-client rate limiting"""

    def __init__(self, default_limit: int = 100):
        self.default_limit = default_limit
        self.limiters: Dict[str, RateLimiter] = {}

    def check_limit(self, client_id: str, custom_limit: Optional[int] = None) -> bool:
        """Check rate limit for specific client"""
        if client_id not in self.limiters:
            limit = custom_limit or self.default_limit
            self.limiters[client_id] = RateLimiter(requests_per_minute=limit)

        return self.limiters[client_id].allow_request()

    def get_wait_time(self, client_id: str) -> float:
        """Get wait time for client"""
        if client_id not in self.limiters:
            return 0.0

        return self.limiters[client_id].get_wait_time()


class JWTManager:
    """JWT token management"""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.token_expiry = 3600  # 1 hour default
        self.active_tokens: Dict[str, JWTToken] = {}

        # Try to use PyJWT if available
        try:
            import jwt
            self.jwt_lib = jwt
            self.jwt_available = True
        except ImportError:
            logger.warning("PyJWT not installed. Using simple token signing.")
            self.jwt_available = False

    def create_token(
        self,
        user_id: str,
        role: Role,
        capabilities: Set[str],
        expires_in: Optional[int] = None
    ) -> JWTToken:
        """Create new JWT token"""
        issued_at = time.time()
        expires_at = issued_at + (expires_in or self.token_expiry)

        payload = {
            "user_id": user_id,
            "role": role.value,
            "capabilities": list(capabilities),
            "iat": issued_at,
            "exp": expires_at
        }

        if self.jwt_available:
            token = self.jwt_lib.encode(
                payload, self.secret_key, algorithm="HS256")
        else:
            # Simple token: base64(payload + signature)
            import base64
            payload_str = json.dumps(payload)
            signature = hashlib.sha256(
                (payload_str + self.secret_key).encode()
            ).hexdigest()
            token = base64.b64encode(
                f"{payload_str}:{signature}".encode()
            ).decode()

        jwt_token = JWTToken(
            token=token,
            user_id=user_id,
            role=role,
            issued_at=issued_at,
            expires_at=expires_at,
            capabilities=capabilities
        )

        self.active_tokens[token] = jwt_token
        return jwt_token

    def verify_token(self, token: str) -> Optional[JWTToken]:
        """Verify and decode JWT token"""
        # Check active tokens cache
        if token in self.active_tokens:
            jwt_token = self.active_tokens[token]
            if time.time() < jwt_token.expires_at:
                return jwt_token
            else:
                del self.active_tokens[token]
                return None

        try:
            if self.jwt_available:
                payload = self.jwt_lib.decode(
                    token, self.secret_key, algorithms=["HS256"])
            else:
                # Decode simple token
                import base64
                decoded = base64.b64decode(token.encode()).decode()
                payload_str, signature = decoded.rsplit(':', 1)

                # Verify signature
                expected_sig = hashlib.sha256(
                    (payload_str + self.secret_key).encode()
                ).hexdigest()

                if signature != expected_sig:
                    return None

                payload = json.loads(payload_str)

            # Check expiry
            if time.time() >= payload["exp"]:
                return None

            jwt_token = JWTToken(
                token=token,
                user_id=payload["user_id"],
                role=Role(payload["role"]),
                issued_at=payload["iat"],
                expires_at=payload["exp"],
                capabilities=set(payload.get("capabilities", []))
            )

            self.active_tokens[token] = jwt_token
            return jwt_token

        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    def revoke_token(self, token: str):
        """Revoke a token"""
        if token in self.active_tokens:
            del self.active_tokens[token]


class SecurityManager:
    """Main security management system"""

    def __init__(self, secret_key: Optional[str] = None):
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.capability_tokens: Dict[str, CapabilityToken] = {}
        self.jwt_manager = JWTManager(secret_key)
        self.rate_limiter = ClientRateLimiter(default_limit=100)
        self.audit_log: deque = deque(maxlen=10000)

        # Create default admin user
        self._create_default_admin()

    def _create_default_admin(self):
        """Create default admin user"""
        admin_password = os.getenv(
            "CHIMERA_ADMIN_PASSWORD", secrets.token_urlsafe(16))

        admin_user = User(
            user_id="admin",
            username="admin",
            password_hash=self._hash_password(admin_password),
            role=Role.ADMIN
        )

        self.users["admin"] = admin_user

        logger.info(f"Default admin user created. Password: {admin_password}")
        logger.warning("Change admin password in production!")

    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_hex = password_hash.split('$')
            pwd_hash = hashlib.pbkdf2_hmac(
                'sha256', password.encode(), salt.encode(), 100000)
            return pwd_hash.hex() == hash_hex
        except:
            return False

    def create_user(
        self,
        username: str,
        password: str,
        role: Role,
        capabilities: Optional[Set[str]] = None
    ) -> User:
        """Create new user"""
        user_id = secrets.token_urlsafe(16)

        user = User(
            user_id=user_id,
            username=username,
            password_hash=self._hash_password(password),
            role=role,
            capabilities=capabilities or set()
        )

        self.users[user_id] = user

        self._audit_log("user_created", user_id, "system", None, True, {
            "username": username,
            "role": role.value
        })

        return user

    def authenticate(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Optional[JWTToken]:
        """Authenticate user and return JWT token"""
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break

        if not user or not user.enabled:
            self._audit_log("login_failed", username, "auth", ip_address, False, {
                "reason": "user_not_found"
            })
            return None

        # Verify password
        if not self._verify_password(password, user.password_hash):
            self._audit_log("login_failed", user.user_id, "auth", ip_address, False, {
                "reason": "invalid_password"
            })
            return None

        # Create JWT token
        token = self.jwt_manager.create_token(
            user_id=user.user_id,
            role=user.role,
            capabilities=user.capabilities
        )

        user.last_login = time.time()

        self._audit_log("login_success", user.user_id,
                        "auth", ip_address, True, {})

        return token

    def verify_api_key(self, api_key: str) -> Optional[APIKey]:
        """Verify API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        for key_obj in self.api_keys.values():
            if key_obj.key_hash == key_hash and key_obj.enabled:
                # Check expiry
                if key_obj.expires_at and time.time() >= key_obj.expires_at:
                    return None

                return key_obj

        return None

    def create_api_key(
        self,
        user_id: str,
        role: Role,
        capabilities: Optional[Set[str]] = None,
        expires_in_days: Optional[int] = None,
        rate_limit: int = 100
    ) -> tuple[str, APIKey]:
        """Create new API key

        Returns:
            (api_key_string, APIKey object)
        """
        key_id = secrets.token_urlsafe(16)
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        expires_at = None
        if expires_in_days:
            expires_at = time.time() + (expires_in_days * 86400)

        key_obj = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            user_id=user_id,
            role=role,
            capabilities=capabilities or set(),
            expires_at=expires_at,
            rate_limit=rate_limit
        )

        self.api_keys[key_id] = key_obj

        self._audit_log("api_key_created", user_id, "system", None, True, {
            "key_id": key_id,
            "role": role.value
        })

        return api_key, key_obj

    def create_capability_token(
        self,
        user_id: str,
        capability: str,
        expires_in_minutes: int = 60,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CapabilityToken:
        """Create capability token for specific operation"""
        token_id = secrets.token_urlsafe(24)
        expires_at = time.time() + (expires_in_minutes * 60)

        token = CapabilityToken(
            token_id=token_id,
            user_id=user_id,
            capability=capability,
            expires_at=expires_at,
            metadata=metadata or {}
        )

        self.capability_tokens[token_id] = token
        return token

    def verify_capability(self, token_id: str, required_capability: str) -> bool:
        """Verify capability token"""
        if token_id not in self.capability_tokens:
            return False

        token = self.capability_tokens[token_id]

        # Check expiry
        if time.time() >= token.expires_at:
            del self.capability_tokens[token_id]
            return False

        # Check capability match
        return token.capability == required_capability

    def check_permission(self, user_or_role: User | Role, permission: Permission) -> bool:
        """Check if user/role has permission"""
        role = user_or_role.role if isinstance(
            user_or_role, User) else user_or_role
        return permission in ROLE_PERMISSIONS.get(role, set())

    def check_rate_limit(self, client_id: str, custom_limit: Optional[int] = None) -> bool:
        """Check rate limit for client"""
        allowed = self.rate_limiter.check_limit(client_id, custom_limit)

        if not allowed:
            self._audit_log("rate_limit_exceeded", client_id,
                            "rate_limit", None, False, {})

        return allowed

    def authorize_tool_execution(
        self,
        token: JWTToken,
        tool_name: str
    ) -> bool:
        """Authorize tool execution"""
        # Check if user has EXECUTE_TOOL permission
        if not self.check_permission(token.role, Permission.EXECUTE_TOOL):
            return False

        # Check specific tool capability if defined
        if token.capabilities:
            tool_capability = f"execute:{tool_name}"
            return tool_capability in token.capabilities or "*" in token.capabilities

        return True

    def _audit_log(
        self,
        event_type: str,
        user_id: str,
        action: str,
        ip_address: Optional[str],
        success: bool,
        details: Dict[str, Any]
    ):
        """Add audit log entry"""
        entry = AuditLogEntry(
            timestamp=time.time(),
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            action=action,
            resource=None,
            success=success,
            details=details
        )

        self.audit_log.append(entry)

        if not success:
            logger.warning(
                f"Security event: {event_type} - {user_id} - {action}")

    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        last_n: int = 100
    ) -> List[AuditLogEntry]:
        """Get audit log entries"""
        entries = list(self.audit_log)[-last_n:]

        if user_id:
            entries = [e for e in entries if e.user_id == user_id]

        if event_type:
            entries = [e for e in entries if e.event_type == event_type]

        return entries

    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        recent_entries = list(self.audit_log)[-1000:]

        failed_logins = sum(
            1 for e in recent_entries if e.event_type == "login_failed")
        successful_logins = sum(
            1 for e in recent_entries if e.event_type == "login_success")
        rate_limit_hits = sum(
            1 for e in recent_entries if e.event_type == "rate_limit_exceeded")

        return {
            "total_users": len(self.users),
            "active_api_keys": sum(1 for k in self.api_keys.values() if k.enabled),
            "active_tokens": len(self.jwt_manager.active_tokens),
            "audit_log_entries": len(self.audit_log),
            "failed_logins_recent": failed_logins,
            "successful_logins_recent": successful_logins,
            "rate_limit_hits": rate_limit_hits
        }


# Import for environment variable

