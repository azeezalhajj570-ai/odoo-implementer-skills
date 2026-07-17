#!/usr/bin/env python3
"""
Plugin Manager — Extends the Skill Platform with Custom Plugins

Supports:
- Pre-processing plugins (before skill loading)
- Post-processing plugins (after skill loading)
- Custom skill generators
- Custom validators
- Custom RAG chunkers

Usage:
    from plugins.manager import PluginManager
    
    mgr = PluginManager()
    mgr.discover()
    plugins = mgr.get_plugins_of_type("validator")
    for plugin in plugins:
        plugin.execute(skill_data)
"""

import importlib
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


class Plugin:
    """A single plugin instance."""

    def __init__(self, name: str, plugin_type: str, module_path: str, config: dict = None):
        self.name = name
        self.plugin_type = plugin_type
        self.module_path = module_path
        self.config = config or {}
        self._module = None
        self._loaded = False

    def load(self):
        """Import the plugin module."""
        try:
            self._module = importlib.import_module(self.module_path)
            self._loaded = True
            logger.info(f"Loaded plugin: {self.name} ({self.plugin_type})")
        except ImportError as e:
            logger.error(f"Failed to load plugin {self.name}: {e}")

    def execute(self, *args, **kwargs) -> Any:
        """Execute the plugin's main function."""
        if not self._loaded:
            self.load()
        if self._module and hasattr(self._module, "execute"):
            return self._module.execute(*args, **kwargs)
        return None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.plugin_type,
            "module_path": self.module_path,
            "loaded": self._loaded,
            "config_keys": list(self.config.keys()),
        }


class PluginManager:
    """Discovers, loads, and manages plugins."""

    def __init__(self, plugin_dirs: Optional[List[Path]] = None):
        self.plugin_dirs = plugin_dirs or [ROOT / "plugins"]
        self._plugins: Dict[str, Plugin] = {}
        self._type_index: Dict[str, List[str]] = {}

    def discover(self) -> int:
        """Scan plugin directories and load plugin manifests."""
        count = 0
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
            for plugin_file in plugin_dir.glob("*.json"):
                try:
                    with open(plugin_file) as f:
                        manifest = json.load(f)
                    plugin = Plugin(
                        name=manifest["name"],
                        plugin_type=manifest["type"],
                        module_path=manifest.get("module", f"plugins.{plugin_file.stem}"),
                        config=manifest.get("config", {}),
                    )
                    self._plugins[plugin.name] = plugin
                    self._type_index.setdefault(plugin.plugin_type, []).append(plugin.name)
                    count += 1
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Invalid plugin manifest: {plugin_file}: {e}")

        logger.info(f"Discovered {count} plugins")
        return count

    def get_plugin(self, name: str) -> Optional[Plugin]:
        return self._plugins.get(name)

    def get_plugins_of_type(self, plugin_type: str) -> List[Plugin]:
        return [self._plugins[name] for name in self._type_index.get(plugin_type, []) if name in self._plugins]

    def execute_all(self, plugin_type: str, *args, **kwargs) -> List[Any]:
        """Execute all plugins of a given type."""
        results = []
        for plugin in self.get_plugins_of_type(plugin_type):
            try:
                result = plugin.execute(*args, **kwargs)
                results.append((plugin.name, result))
            except Exception as e:
                logger.error(f"Plugin {plugin.name} failed: {e}")
                results.append((plugin.name, None))
        return results

    def load_all(self):
        """Pre-load all discovered plugins."""
        for plugin in self._plugins.values():
            plugin.load()

    def all_plugins(self) -> List[dict]:
        return [p.to_dict() for p in self._plugins.values()]


# Sample plugin manifests for reference
SAMPLE_PLUGINS = {
    "custom_validator.json": {
        "name": "custom_knowledge_validator",
        "type": "validator",
        "module": "plugins.custom_validator",
        "config": {"strict_mode": True}
    },
    "ai_enhancer.json": {
        "name": "ai_content_enhancer",
        "type": "post_processor",
        "module": "plugins.ai_enhancer",
        "config": {"model": "gpt-4o"}
    }
}
