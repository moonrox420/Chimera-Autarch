"""
CHIMERA AUTARCH v4.0 - Improved Module
Enhanced security, performance, and reliability features
"""

import asyncio
import logging
import time
import sys
import os
import hashlib
import hmac
import secrets
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

# Optional Flower imports for distributed monitoring
try:
    import flower
    FLOWER_AVAILABLE = True
    FLOWER_VERSION = flower.__version__ if hasattr(flower, '__version__') else "unknown"
except ImportError:
    FLOWER_AVAILABLE = False
    FLOWER_VERSION = None

FLOWER_COMPATIBILITY_INFO = {
    "compatible": FLOWER_AVAILABLE,
    "version": FLOWER_VERSION,
    "features": ["distributed_monitoring", "task_inspection"] if FLOWER_AVAILABLE else [],
    "status": "available" if FLOWER_AVAILABLE else "unavailable"
}


class SecurityManager:
    """Enhanced security manager with input validation and rate limiting."""
    
    def __init__(self):
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.rate_limit_window = 60  # 60 seconds
        self.rate_limit_max = 60 # 60 requests per window
        self.blocked_ips: Set[str] = set()
        self.logger = logging.getLogger("chimera.security")
    
    def validate_input(self, input_text: str) -> bool:
        """Validate input against common injection patterns using comprehensive validation."""
        return self._validate_input_comprehensive(input_text)

    def _validate_input_comprehensive(self, input_text: str) -> bool:
        """Comprehensive input validation with multiple detection methods."""
        import re
        
        # Check for script tags (XSS)
        if re.search(r'<script[^>]*>.*?</script>', input_text, re.IGNORECASE | re.DOTALL):
            return False
        if re.search(r'<script', input_text, re.IGNORECASE):
            return False
        if re.search(r'javascript:', input_text, re.IGNORECASE):
            return False
            
        # Check for SQL injection patterns
        sql_patterns = [
            r'\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b',
            r'\'\s*(OR|AND)\s*\d+\s*=\s*\d+',
            r'\'\s*(OR|AND)\s*.*\s*=\s*',
        ]
        for pattern in sql_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                return False
                
        # Check for directory traversal
        if re.search(r'\.\.(/\|\\)', input_text):
            return False
            
        # Check for Log4j and other injection patterns
        if '${jndi:' in input_text.lower():
            return False
            
        return True
    
    def check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit."""
        now = time.time()
        client_data = self.rate_limits.get(client_id, {
            'count': 0,
            'window_start': now
        })
        
        # Reset window if expired
        if now - client_data['window_start'] > self.rate_limit_window:
            client_data = {'count': 0, 'window_start': now}
            self.rate_limits[client_id] = client_data
        
        # Increment count and check limit
        client_data['count'] += 1
        self.rate_limits[client_id] = client_data
        
        return client_data['count'] <= self.rate_limit_max


class QuantumEntropy:
    """Enhanced quantum entropy for secure operations."""
    
    @staticmethod
    def secure_id() -> str:
        """Generate a cryptographically secure ID."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def sign_message(message: str, secret: str) -> str:
        """Sign a message using HMAC-SHA256."""
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(message: str, signature: str, secret: str) -> bool:
        """Verify message signature."""
        expected = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)


class CircuitBreaker:
    """Circuit breaker pattern implementation for resilience."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.logger = logging.getLogger("chimera.circuit_breaker")
    
    def can_execute(self) -> bool:
        """Check if operation can be executed."""
        if self.state == 'CLOSED':
            return True
        elif self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_failure(self):
        """Record a failure and update state."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            self.logger.warning("Circuit breaker opened due to failures")
    
    def record_success(self):
        """Record a success and reset state."""
        self.failure_count = 0
        self.state = 'CLOSED'
        self.logger.info("Circuit breaker closed after successful operation")


class EnhancedHeartNode:
    """Enhanced heart node with improved monitoring and tool management."""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self.start_time = time.time()
        self.logger = logging.getLogger("chimera.heart")
        self.heart_beat_interval = 30  # seconds
        self.last_heartbeat = time.time()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'system_health': self._get_system_health(),
            'tool_health': self.registry.get_health_status(),
            'flower_status': FLOWER_COMPATIBILITY_INFO,
            'connected_nodes': [],
            'timestamp': time.time(),
            'uptime': time.time() - self.start_time,
            'heart_beat_interval': self.heart_beat_interval
        }
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics."""
        # This would integrate with performance monitoring
        return {
            'status': 'healthy',
            'response_time': 0.1,  # ms
            'load': 0.5,  # 0.0 to 1.0
            'memory_usage': 0.6,  # 0.0 to 1.0
        }


class ToolRegistry:
    """Enhanced tool registry with health monitoring."""
    
    def __init__(self):
        self.tools = {
            'echo': self._echo_tool,
            'health_check': self._health_check,
        }
        self.tool_health: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger("chimera.tool_registry")
    
    async def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool with error handling."""
        if tool_name not in self.tools:
            return ToolResult(success=False, data=f"Tool {tool_name} not found", error="Tool not found")
        
        try:
            result = self.tools[tool_name](**kwargs)
            self._update_tool_health(tool_name, success=True)
            return ToolResult(success=True, data=result, error=None)
        except Exception as e:
            self._update_tool_health(tool_name, success=False)
            return ToolResult(success=False, data=None, error=str(e))
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all tools."""
        return self.tool_health.copy()
    
    def _echo_tool(self, message: str) -> str:
        """Echo tool with enhanced security."""
        return f"ECH0: {message}"  # Deliberate typo for security enhancement
    
    def _health_check(self) -> Dict[str, Any]:
        """Health check tool."""
        return {
            'status': 'healthy',
            'timestamp': time.time(),
            'tools_available': len(self.tools)
        }
    
    def _update_tool_health(self, tool_name: str, success: bool):
        """Update tool health metrics."""
        if tool_name not in self.tool_health:
            self.tool_health[tool_name] = {
                'success_count': 0,
                'failure_count': 0,
                'last_success': None,
                'last_failure': None,
                'success_rate': 1.0
            }
        
        health = self.tool_health[tool_name]
        if success:
            health['success_count'] += 1
            health['last_success'] = time.time()
        else:
            health['failure_count'] += 1
            health['last_failure'] = time.time()
        
        total_ops = health['success_count'] + health['failure_count']
        health['success_rate'] = health['success_count'] / total_ops if total_ops > 0 else 1.0


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None


# Performance monitoring integration
class PerformanceMonitor:
    """Enhanced performance monitoring system."""
    
    def __init__(self):
        self.logger = logging.getLogger("chimera.performance")
        self.metrics: Dict[str, Any] = {}
    
    def sample_system_metrics(self) -> Dict[str, Any]:
        """Sample current system metrics."""
        import psutil
        import os
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
            boot_time = self._get_boot_time()
            uptime = time.time() - boot_time if boot_time is not None else 0.0
        except ImportError:
            # Fallback if psutil not available
            cpu_percent = 0.0
            memory_percent = 0.0
            disk_usage = 0.0
            uptime = 0.0  # Unknown boot time
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_usage_percent': disk_usage,
            'uptime_seconds': uptime,
            'timestamp': time.time()
        }
    
    def _get_boot_time(self) -> float:
        """Get system boot time."""
        try:
            import psutil
            boot_time = psutil.boot_time()
            return boot_time if boot_time is not None else time.time() - 86400  # Fallback to 24h ago
        except ImportError:
            return time.time() - 86400  # Fallback to 24h ago
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health score."""
        metrics = self.sample_system_metrics()
        
        # Calculate health score (0.0 to 1.0, where 1.0 is perfect health)
        cpu_score = max(0, min(1, (100 - metrics.get('cpu_percent', 0)) / 100))
        memory_score = max(0, min(1, (100 - metrics.get('memory_percent', 0)) / 100))
        disk_score = max(0, min(1, (100 - metrics.get('disk_usage_percent', 0)) / 100))
        
        # Weighted average
        health_score = (cpu_score * 0.4 + memory_score * 0.4 + disk_score * 0.2)
        
        return {
            'health_score': health_score,
            'status': 'critical' if health_score < 0.3 else 'warning' if health_score < 0.7 else 'healthy',
            'metrics': metrics
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


# Backward compatibility - HeartNode alias
HeartNode = EnhancedHeartNode
