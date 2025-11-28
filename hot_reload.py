#!/usr/bin/env python3
"""
CHIMERA AUTARCH - Hot Code Reload Module
Dynamic module reloading without restart, versioned tool registry
"""
import asyncio
import importlib
import sys
import time
import hashlib
from pathlib import Path
from typing import Dict, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import logging

logger = logging.getLogger("chimera.hotreload")


@dataclass
class ModuleVersion:
    """Tracks module versions"""
    module_name: str
    version: int
    checksum: str
    loaded_at: float
    file_path: Path


@dataclass
class ToolVersion:
    """Version of a tool in the registry"""
    name: str
    version: str
    func: Callable
    loaded_at: float
    module: str
    deprecated: bool = False


class CodeWatcher(FileSystemEventHandler):
    """Watches code files for changes"""

    def __init__(self, reload_callback: Callable):
        self.reload_callback = reload_callback
        self.cooldown = 1.0  # seconds
        self.last_reload: Dict[str, float] = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        if not event.src_path.endswith('.py'):
            return

        # Skip __pycache__ and other generated files
        if '__pycache__' in event.src_path or event.src_path.endswith('.pyc'):
            return

        # Cooldown check
        current_time = time.time()
        if event.src_path in self.last_reload:
            if current_time - self.last_reload[event.src_path] < self.cooldown:
                return

        self.last_reload[event.src_path] = current_time

        logger.info(f"File modified: {event.src_path}")

        # Trigger reload
        asyncio.create_task(self.reload_callback(Path(event.src_path)))


class ModuleReloader:
    """Handles dynamic module reloading"""

    def __init__(self):
        self.modules: Dict[str, ModuleVersion] = {}
        self.reload_history: list = []
        self.protected_modules = {
            'sys', 'os', 'asyncio', 'logging', 'importlib'
        }

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum"""
        if not file_path.exists():
            return ""

        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()

    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name"""
        # Assuming all modules are in current directory or subdirectories
        relative_path = file_path.relative_to(Path.cwd())
        module_name = str(relative_path).replace('/', '.').replace('\\', '.')

        if module_name.endswith('.py'):
            module_name = module_name[:-3]

        return module_name

    async def reload_module(self, file_path: Path) -> bool:
        """Reload a Python module"""
        try:
            module_name = self._get_module_name(file_path)

            # Check if module is protected
            if any(protected in module_name for protected in self.protected_modules):
                logger.warning(
                    f"Module {module_name} is protected, skipping reload")
                return False

            # Calculate new checksum
            new_checksum = self._calculate_checksum(file_path)

            # Check if actually changed
            if module_name in self.modules:
                if self.modules[module_name].checksum == new_checksum:
                    logger.debug(
                        f"Module {module_name} unchanged, skipping reload")
                    return False

            # Reload module
            if module_name in sys.modules:
                logger.info(f"Reloading module: {module_name}")
                module = importlib.reload(sys.modules[module_name])
            else:
                logger.info(f"Loading new module: {module_name}")
                module = importlib.import_module(module_name)

            # Update version
            version = self.modules[module_name].version + \
                1 if module_name in self.modules else 1

            self.modules[module_name] = ModuleVersion(
                module_name=module_name,
                version=version,
                checksum=new_checksum,
                loaded_at=time.time(),
                file_path=file_path
            )

            # Record in history
            self.reload_history.append({
                "module": module_name,
                "version": version,
                "timestamp": time.time(),
                "checksum": new_checksum
            })

            logger.info(f"Successfully reloaded {module_name} (v{version})")
            return True

        except Exception as e:
            logger.error(f"Failed to reload {file_path}: {e}")
            return False

    def get_module_version(self, module_name: str) -> Optional[ModuleVersion]:
        """Get current version of module"""
        return self.modules.get(module_name)

    def get_reload_stats(self) -> Dict[str, Any]:
        """Get reload statistics"""
        return {
            "modules_tracked": len(self.modules),
            "total_reloads": len(self.reload_history),
            "recent_reloads": self.reload_history[-10:] if self.reload_history else []
        }


class VersionedToolRegistry:
    """Tool registry with versioning support"""

    def __init__(self):
        # tool_name -> [versions]
        self.tools: Dict[str, List[ToolVersion]] = {}
        # tool_name -> active_version
        self.active_versions: Dict[str, str] = {}
        self.default_version = "latest"

    def register_tool(
        self,
        name: str,
        version: str,
        func: Callable,
        module: str,
        replace: bool = False
    ):
        """Register tool version"""
        if name not in self.tools:
            self.tools[name] = []

        # Check if version already exists
        existing = [t for t in self.tools[name] if t.version == version]
        if existing and not replace:
            logger.warning(f"Tool {name} v{version} already exists, skipping")
            return

        # Remove old version if replacing
        if existing and replace:
            self.tools[name] = [
                t for t in self.tools[name] if t.version != version]
            logger.info(f"Replaced tool {name} v{version}")

        # Add new version
        tool_version = ToolVersion(
            name=name,
            version=version,
            func=func,
            loaded_at=time.time(),
            module=module
        )

        self.tools[name].append(tool_version)

        # Set as active version if first or version is "latest"
        if name not in self.active_versions or version == "latest" or replace:
            self.active_versions[name] = version

        logger.info(f"Registered tool {name} v{version} from {module}")

    def get_tool(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[ToolVersion]:
        """Get tool by name and version"""
        if name not in self.tools:
            return None

        if version is None:
            version = self.active_versions.get(name, self.default_version)

        if version == "latest" or version == self.default_version:
            # Get most recent non-deprecated version
            active_tools = [t for t in self.tools[name] if not t.deprecated]
            if active_tools:
                return max(active_tools, key=lambda t: t.loaded_at)

        # Find specific version
        for tool in self.tools[name]:
            if tool.version == version and not tool.deprecated:
                return tool

        return None

    def deprecate_version(self, name: str, version: str):
        """Deprecate a tool version"""
        if name not in self.tools:
            return

        for tool in self.tools[name]:
            if tool.version == version:
                tool.deprecated = True
                logger.info(f"Deprecated tool {name} v{version}")

    def set_active_version(self, name: str, version: str):
        """Set active version for tool"""
        if name in self.tools:
            # Check if version exists
            if any(t.version == version for t in self.tools[name]):
                self.active_versions[name] = version
                logger.info(f"Set active version of {name} to {version}")

    def list_versions(self, name: str) -> List[str]:
        """List all versions of a tool"""
        if name not in self.tools:
            return []

        return [t.version for t in self.tools[name] if not t.deprecated]

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_tools": len(self.tools),
            "total_versions": sum(len(versions) for versions in self.tools.values()),
            "active_versions": len(self.active_versions),
            "deprecated_versions": sum(
                1 for versions in self.tools.values()
                for t in versions if t.deprecated
            )
        }


class HotReloadManager:
    """Main hot reload coordination"""

    def __init__(
        self,
        watch_paths: Optional[List[Path]] = None,
        enable_auto_reload: bool = True
    ):
        self.watch_paths = watch_paths or [Path.cwd()]
        self.enable_auto_reload = enable_auto_reload
        self.module_reloader = ModuleReloader()
        self.tool_registry = VersionedToolRegistry()
        self.observers: List[Observer] = []
        self.reload_callbacks: List[Callable] = []
        self.state_preservation: Dict[str, Any] = {}

    async def start(self):
        """Start hot reload system"""
        if not self.enable_auto_reload:
            logger.info("Hot reload disabled")
            return

        logger.info(f"Starting hot reload, watching: {self.watch_paths}")

        for watch_path in self.watch_paths:
            if not watch_path.exists():
                logger.warning(f"Watch path does not exist: {watch_path}")
                continue

            event_handler = CodeWatcher(self._handle_file_change)
            observer = Observer()
            observer.schedule(event_handler, str(watch_path), recursive=True)
            observer.start()
            self.observers.append(observer)

            logger.info(f"Watching {watch_path} for changes")

    async def stop(self):
        """Stop hot reload system"""
        for observer in self.observers:
            observer.stop()
            observer.join()

        self.observers.clear()
        logger.info("Hot reload stopped")

    async def _handle_file_change(self, file_path: Path):
        """Handle file change event"""
        logger.info(f"Detected change in {file_path}")

        # Preserve state before reload
        await self._preserve_state()

        # Reload module
        success = await self.module_reloader.reload_module(file_path)

        if success:
            # Restore state
            await self._restore_state()

            # Notify callbacks
            for callback in self.reload_callbacks:
                try:
                    await callback(file_path)
                except Exception as e:
                    logger.error(f"Reload callback error: {e}")

    async def _preserve_state(self):
        """Preserve critical state before reload"""
        # In real implementation, save:
        # - Active WebSocket connections
        # - In-flight tasks
        # - Database connections
        # - Metrics

        self.state_preservation["timestamp"] = time.time()
        logger.debug("State preserved")

    async def _restore_state(self):
        """Restore state after reload"""
        # In real implementation, restore preserved state

        logger.debug("State restored")

    def register_reload_callback(self, callback: Callable):
        """Register callback to be called after reload"""
        self.reload_callbacks.append(callback)

    async def reload_tool(
        self,
        tool_name: str,
        module_name: str,
        func_name: str,
        version: str = "latest"
    ):
        """Reload specific tool from module"""
        try:
            # Reload module
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)

            # Get function
            if not hasattr(module, func_name):
                logger.error(
                    f"Function {func_name} not found in {module_name}")
                return False

            func = getattr(module, func_name)

            # Register new version
            self.tool_registry.register_tool(
                name=tool_name,
                version=version,
                func=func,
                module=module_name,
                replace=True
            )

            logger.info(
                f"Reloaded tool {tool_name} from {module_name}.{func_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to reload tool {tool_name}: {e}")
            return False

    async def execute_tool_versioned(
        self,
        tool_name: str,
        version: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Execute tool with specific version"""
        tool = self.tool_registry.get_tool(tool_name, version)

        if not tool:
            raise ValueError(
                f"Tool {tool_name} v{version or 'latest'} not found")

        logger.debug(f"Executing {tool_name} v{tool.version}")

        # Execute
        if asyncio.iscoroutinefunction(tool.func):
            return await tool.func(**kwargs)
        else:
            return tool.func(**kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """Get hot reload statistics"""
        return {
            "auto_reload_enabled": self.enable_auto_reload,
            "watch_paths": [str(p) for p in self.watch_paths],
            "observers_active": len(self.observers),
            "module_stats": self.module_reloader.get_reload_stats(),
            "tool_stats": self.tool_registry.get_stats()
        }

