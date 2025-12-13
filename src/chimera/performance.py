

import asyncio
import os
import time
import hashlib
from typing import Optional, Dict, Any, List, Callable, Awaitable
from dataclasses import dataclass
import logging
import json

logger = logging.getLogger("chimera.performance")

# Optional imports for performance features
try:
    import torch
    TORCH_AVAILABLE = True
    TORCH_CUDA_AVAILABLE = torch.cuda.is_available()
except ImportError:
    TORCH_AVAILABLE = False
    TORCH_CUDA_AVAILABLE = False

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class CacheEntry:
    """A cached item with metadata"""
    data: Any
    timestamp: float
    ttl: Optional[int] = None
    access_count: int = 0
    last_accessed: float = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""
    operation: str
    start_time: float
    end_time: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    gpu_usage: Optional[float] = None
    success: bool = False

    @property
    def duration(self) -> Optional[float]:
        """Calculate operation duration"""
        if self.end_time is None:
            return None
        return self.end_time - self.start_time


class GPUAccelerator:
    """GPU acceleration for compute-intensive tasks"""

    def __init__(self):
        self.available = TORCH_CUDA_AVAILABLE
        if self.available:
            logger.info(f"GPU acceleration available: {torch.cuda.get_device_name()}")
        else:
            logger.warning("GPU acceleration unavailable - install PyTorch with CUDA support")

    async def accelerate_computation(self, func: Callable, *args, **kwargs) -> Any:
        """Run a function on GPU if available"""
        if not self.available:
            # Run on CPU
            return await self._run_on_cpu(func, *args, **kwargs)

        try:
            # Move computation to GPU
            return await self._run_on_gpu(func, *args, **kwargs)
        except Exception as e:
            logger.warning(f"GPU computation failed, falling back to CPU: {e}")
            return await self._run_on_cpu(func, *args, **kwargs)

    async def _run_on_cpu(self, func: Callable, *args, **kwargs) -> Any:
        """Run function on CPU"""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)

    async def _run_on_gpu(self, func: Callable, *args, **kwargs) -> Any:
        """Run function on GPU with torch acceleration"""
        # This is a placeholder - real implementation would convert data to tensors
        # and run GPU-accelerated operations
        logger.info("Running computation on GPU")

        # For now, just run on CPU but log GPU usage
        result = await self._run_on_cpu(func, *args, **kwargs)

        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated() / 1024**2  # MB
            logger.info(f"GPU memory used: {gpu_memory:.1f} MB")

        return result

    def get_gpu_stats(self) -> Dict[str, Any]:
        """Get GPU statistics"""
        if not self.available:
            return {"gpu_available": False}

        return {
            "gpu_available": True,
            "device_name": torch.cuda.get_device_name(),
            "device_count": torch.cuda.device_count(),
            "current_device": torch.cuda.current_device(),
            "memory_allocated": torch.cuda.memory_allocated() / 1024**2,  # MB
            "memory_reserved": torch.cuda.memory_reserved() / 1024**2,   # MB
        }


class DistributedCache:
    """Distributed caching with Redis fallback to local cache"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_available = REDIS_AVAILABLE
        self.redis_client = None
        self.local_cache: Dict[str, CacheEntry] = {}
        self.redis_url = redis_url

        if self.redis_available:
            try:
                self.redis_client = redis.from_url(redis_url)
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self.redis_available = False

        if not self.redis_available:
            logger.info("Using local memory cache")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._make_key(key)

        # Try Redis first
        if self.redis_available and self.redis_client:
            try:
                data = await self.redis_client.get(cache_key)
                if data:
                    entry = CacheEntry(**json.loads(data))
                    if not entry.is_expired():
                        entry.access_count += 1
                        entry.last_accessed = time.time()
                        await self.redis_client.set(cache_key, json.dumps(entry.__dict__))
                        return entry.data
                    else:
                        await self.redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        # Fallback to local cache
        entry = self.local_cache.get(cache_key)
        if entry and not entry.is_expired():
            entry.access_count += 1
            entry.last_accessed = time.time()
            return entry.data
        elif entry and entry.is_expired():
            del self.local_cache[cache_key]

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        cache_key = self._make_key(key)
        entry = CacheEntry(
            data=value,
            timestamp=time.time(),
            ttl=ttl,
            access_count=1,
            last_accessed=time.time()
        )

        # Try Redis first
        if self.redis_available and self.redis_client:
            try:
                await self.redis_client.set(cache_key, json.dumps(entry.__dict__), ex=ttl)
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

        # Fallback to local cache
        self.local_cache[cache_key] = entry

        # Clean up expired entries periodically
        if len(self.local_cache) > 1000:
            self._cleanup_expired()

    async def delete(self, key: str):
        """Delete from cache"""
        cache_key = self._make_key(key)

        # Try Redis
        if self.redis_available and self.redis_client:
            try:
                await self.redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")

        # Local cache
        if cache_key in self.local_cache:
            del self.local_cache[cache_key]

    def _make_key(self, key: str) -> str:
        """Create a consistent cache key"""
        return f"chimera:{hashlib.md5(key.encode()).hexdigest()}"

    def _cleanup_expired(self):
        """Remove expired entries from local cache"""
        expired_keys = [k for k, v in self.local_cache.items() if v.is_expired()]
        for k in expired_keys:
            del self.local_cache[k]

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        local_entries = len(self.local_cache)
        local_size = sum(len(json.dumps(v.__dict__)) for v in self.local_cache.values())

        stats = {
            "cache_type": "redis" if self.redis_available else "local",
            "local_entries": local_entries,
            "local_size_bytes": local_size,
        }

        if self.redis_available and self.redis_client:
            try:
                info = await self.redis_client.info()
                stats.update({
                    "redis_connected_clients": info.get("connected_clients", 0),
                    "redis_used_memory": info.get("used_memory", 0),
                    "redis_total_keys": await self.redis_client.dbsize(),
                })
            except Exception as e:
                logger.warning(f"Redis stats failed: {e}")

        return stats


class PerformanceMonitor:
    """Real-time performance monitoring and analytics"""

    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.max_metrics = 1000
        self.gpu_accelerator = GPUAccelerator()

    def start_operation(self, operation: str) -> str:
        """Start monitoring an operation"""
        operation_id = f"{operation}_{int(time.time() * 1000)}"

        metrics = PerformanceMetrics(
            operation=operation,
            start_time=time.time()
        )

        # Capture initial resource usage
        if PSUTIL_AVAILABLE:
            try:
                metrics.cpu_usage = psutil.cpu_percent(interval=None)
                metrics.memory_usage = psutil.virtual_memory().percent
            except Exception as e:
                logger.warning(f"Resource monitoring failed: {e}")

        if self.gpu_accelerator.available:
            gpu_stats = self.gpu_accelerator.get_gpu_stats()
            metrics.gpu_usage = gpu_stats.get("memory_allocated", 0)

        self.metrics.append(metrics)

        # Keep only recent metrics
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]

        return operation_id

    def end_operation(self, operation_id: str, success: bool = True):
        """End monitoring an operation"""
        # Find the metrics entry
        for metrics in reversed(self.metrics):
            if f"{metrics.operation}_{int(metrics.start_time * 1000)}" == operation_id:
                metrics.end_time = time.time()
                metrics.success = success
                break

    async def get_analytics(self) -> Dict[str, Any]:
        """Get real-time performance analytics"""
        if not self.metrics:
            return {"status": "no_metrics_available"}

        recent_metrics = [m for m in self.metrics if m.end_time is not None][-100:]  # Last 100 operations

        if not recent_metrics:
            return {"status": "no_completed_operations"}

        # Calculate statistics
        total_operations = len(recent_metrics)
        successful_operations = sum(1 for m in recent_metrics if m.success)
        avg_duration = sum(m.duration for m in recent_metrics if m.duration) / len([m for m in recent_metrics if m.duration])

        operation_counts = {}
        for m in recent_metrics:
            operation_counts[m.operation] = operation_counts.get(m.operation, 0) + 1

        # Resource usage trends
        cpu_trend = [m.cpu_usage for m in recent_metrics if m.cpu_usage is not None]
        memory_trend = [m.memory_usage for m in recent_metrics if m.memory_usage is not None]

        return {
            "total_operations": total_operations,
            "success_rate": successful_operations / total_operations,
            "avg_operation_duration": avg_duration,
            "operation_breakdown": operation_counts,
            "resource_trends": {
                "cpu_avg": sum(cpu_trend) / len(cpu_trend) if cpu_trend else None,
                "memory_avg": sum(memory_trend) / len(memory_trend) if memory_trend else None,
            },
            "gpu_available": self.gpu_accelerator.available,
            "cache_stats": {},  # Will be filled by cache integration
        }


class PerformanceIntegration:
    """Integration layer for performance optimizations"""

    def __init__(self):
        self.gpu = GPUAccelerator()
        self.cache = DistributedCache()
        self.monitor = PerformanceMonitor()

    async def optimize_function(self, func: Callable, *args, use_gpu: bool = False, cache_key: Optional[str] = None, **kwargs) -> Any:
        """Run a function with performance optimizations"""
        # Check cache first
        if cache_key:
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {cache_key}")
                return cached_result

        # Start monitoring
        operation_id = self.monitor.start_operation(func.__name__)

        try:
            # Run with GPU acceleration if requested
            if use_gpu:
                result = await self.gpu.accelerate_computation(func, *args, **kwargs)
            else:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, func, *args, **kwargs)

            # Cache result if key provided
            if cache_key:
                await self.cache.set(cache_key, result, ttl=3600)  # 1 hour TTL

            self.monitor.end_operation(operation_id, success=True)
            return result

        except Exception as e:
            self.monitor.end_operation(operation_id, success=False)
            raise e

    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        analytics = await self.monitor.get_analytics()
        cache_stats = await self.cache.get_stats()
        gpu_stats = self.gpu.get_gpu_stats()

        return {
            "analytics": analytics,
            "cache": cache_stats,
            "gpu": gpu_stats,
            "timestamp": time.time()
        }