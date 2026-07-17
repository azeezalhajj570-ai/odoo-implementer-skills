#!/usr/bin/env python3
"""
Project Context Engine — Analyzes an Odoo project repository and builds a live
project model with all architecture, modules, models, security, views, etc.

This is the core intelligence that makes skills project-aware.

Usage:
    from project.engine import ProjectContextEngine
    
    engine = ProjectContextEngine("/path/to/odoo/project")
    engine.scan()
    model = engine.get_model()
    print(model.modules_count, model.custom_modules_count)
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

logger = logging.getLogger(__name__)


@dataclass
class ModuleInfo:
    """Information about a discovered Odoo module."""
    path: str
    name: str
    version: str = ""
    category: str = ""
    license: str = ""
    depends: List[str] = field(default_factory=list)
    models: List[str] = field(default_factory=list)
    security_groups: List[str] = field(default_factory=list)
    crons: List[dict] = field(default_factory=list)
    controllers: List[str] = field(default_factory=list)
    is_custom: bool = False
    is_installable: bool = True
    manifest_summary: str = ""


@dataclass
class ProjectModel:
    """Complete model of an Odoo project."""
    root_path: str
    project_name: str = ""
    odoo_version: str = ""
    modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    custom_modules: List[str] = field(default_factory=list)
    addons_paths: List[str] = field(default_factory=list)
    dependency_graph: List[tuple] = field(default_factory=list)
    has_docker: bool = False
    has_helm: bool = False
    has_ci_cd: bool = False
    has_custom_theme: bool = False
    scanned_at: str = ""

    @property
    def modules_count(self) -> int:
        return len(self.modules)

    @property
    def custom_modules_count(self) -> int:
        return len(self.custom_modules)

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "odoo_version": self.odoo_version,
            "root_path": self.root_path,
            "modules_count": self.modules_count,
            "custom_modules_count": self.custom_modules_count,
            "custom_modules": self.custom_modules,
            "addons_paths": self.addons_paths,
            "has_docker": self.has_docker,
            "has_helm": self.has_helm,
            "has_ci_cd": self.has_ci_cd,
            "dependency_edges": len(self.dependency_graph),
            "scanned_at": self.scanned_at,
            "modules": {
                name: {
                    "path": info.path,
                    "version": info.version,
                    "category": info.category,
                    "depends": info.depends,
                    "models_count": len(info.models),
                    "is_custom": info.is_custom,
                }
                for name, info in self.modules.items()
            },
        }


class ProjectContextEngine:
    """Scans an Odoo project directory and builds a live ProjectModel."""

    MANIFEST_FILES = ["__manifest__.py", "__openerp__.py"]

    def __init__(self, root_path: Optional[str] = None):
        self.root_path = Path(root_path).resolve() if root_path else Path.cwd()
        self.model = ProjectModel(root_path=str(self.root_path))
        self.model.project_name = self.root_path.name
        self.model.scanned_at = datetime.now(timezone.utc).isoformat()

    def scan(self, addons_paths: Optional[List[str]] = None) -> ProjectModel:
        """Scan the project directory and build the project model."""
        logger.info(f"Scanning Odoo project: {self.root_path}")

        # Detect Odoo version
        self._detect_odoo_version()

        # Discover addons paths
        if addons_paths:
            self.model.addons_paths = addons_paths
        else:
            self._discover_addons_paths()

        # Scan each addons path for modules
        for ap in self.model.addons_paths:
            ap_path = Path(ap)
            if not ap_path.exists():
                continue
            self._scan_addons_path(ap_path)

        # Build dependency graph
        self._build_dependency_graph()

        # Detect infrastructure
        self._detect_infrastructure()

        logger.info(f"Scan complete: {self.model.modules_count} modules "
                     f"({self.model.custom_modules_count} custom)")
        return self.model

    def _detect_odoo_version(self):
        """Detect Odoo version from common sources."""
        manifest = self.root_path / "__manifest__.py"
        if manifest.exists():
            try:
                content = manifest.read_text()
                import re
                m = re.search(r"'version'\s*:\s*'(\d+)\.(\d+)", content)
                if m:
                    self.model.odoo_version = f"{m.group(1)}.{m.group(2)}"
            except IOError:
                pass

    def _discover_addons_paths(self):
        """Discover addons paths from config files and common conventions."""
        candidates = []

        # Check odoo.conf
        for conf_file in ["odoo.conf", ".odoorc", "odoorc"]:
            conf_path = self.root_path / "config" / conf_file
            if not conf_path.exists():
                conf_path = self.root_path / conf_file
            if conf_path.exists():
                try:
                    for line in conf_path.read_text().splitlines():
                        if "addons_path" in line:
                            paths = line.split("=")[1].strip().split(",")
                            candidates.extend(p.strip() for p in paths)
                except IOError:
                    pass

        # Check docker-compose volume mounts
        docker_file = self.root_path / "docker-compose.yml"
        if docker_file.exists():
            try:
                content = docker_file.read_text()
                for m in re.finditer(r'["\']([^"\']*addons[^"\']*)["\']', content):
                    candidates.append(m.group(1))
            except IOError:
                pass

        # Common conventions
        candidates.extend([
            str(self.root_path / "addons"),
            str(self.root_path / "addons" / "custom"),
            str(self.root_path / "odoo" / "addons"),
            str(self.root_path / "custom-addons"),
            str(self.root_path / "custom"),
            str(self.root_path / "src"),
        ])

        # Deduplicate and resolve
        seen = set()
        for c in candidates:
            resolved = str(Path(c).resolve()) if Path(c).exists() else c
            if resolved not in seen:
                seen.add(resolved)
                self.model.addons_paths.append(resolved)
                logger.info(f"Addons path: {resolved}")

    def _scan_addons_path(self, path: Path):
        """Scan a single addons path for Odoo modules."""
        if not path.exists():
            return

        for item in sorted(path.iterdir()):
            if not item.is_dir():
                continue
            self._scan_module(item)

    def _scan_module(self, module_path: Path):
        """Scan a single module directory."""
        manifest = self._find_manifest(module_path)
        if not manifest:
            return

        try:
            content = manifest.read_text()
        except IOError:
            return

        try:
            # Parse manifest using ast for safety
            import ast
            tree = ast.parse(content)
            manifest_data = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    for key, value in zip(node.keys, node.values):
                        if isinstance(key, ast.Str):
                            if isinstance(value, ast.Str):
                                manifest_data[key.s] = value.s
                            elif isinstance(value, ast.List):
                                manifest_data[key.s] = [
                                    e.s for e in value.elts if isinstance(e, ast.Str)
                                ]

            name = manifest_data.get("name", module_path.name)
            module_name = module_path.name

            info = ModuleInfo(
                path=str(module_path),
                name=module_name,
                version=manifest_data.get("version", ""),
                category=manifest_data.get("category", ""),
                license=manifest_data.get("license", ""),
                depends=manifest_data.get("depends", []),
                is_custom=self._is_custom(module_path),
                is_installable=manifest_data.get("installable", True),
            )

            # Scan models
            models_dir = module_path / "models"
            if models_dir.exists():
                for model_file in models_dir.glob("*.py"):
                    if model_file.name.startswith("_"):
                        continue
                    try:
                        content = model_file.read_text()
                        for m in re.finditer(
                            r"_name\s*=\s*['\"]([^'\"]+)['\"]", content
                        ):
                            info.models.append(m.group(1))
                    except IOError:
                        pass

            # Scan security
            security_dir = module_path / "security"
            if security_dir.exists():
                for sec_file in security_dir.glob("*.xml"):
                    try:
                        sec_content = sec_file.read_text()
                        for m in re.finditer(
                            r"id\s*=\s*['\"]([^'\"]+)_group['\"]", sec_content
                        ):
                            info.security_groups.append(m.group(1))
                    except IOError:
                        pass

            # Scan controllers
            controllers_dir = module_path / "controllers"
            if controllers_dir.exists():
                for ctrl_file in controllers_dir.glob("*.py"):
                    if ctrl_file.name.startswith("_"):
                        continue
                    try:
                        ctrl_content = ctrl_file.read_text()
                        for m in re.finditer(
                            r"@http\.route\(['\"]([^'\"]+)", ctrl_content
                        ):
                            info.controllers.append(m.group(1))
                    except IOError:
                        pass

            self.model.modules[module_name] = info

        except Exception as e:
            logger.warning(f"Error scanning module {module_path.name}: {e}")

    def _find_manifest(self, module_path: Path) -> Optional[Path]:
        for mf in self.MANIFEST_FILES:
            p = module_path / mf
            if p.exists():
                return p
        return None

    def _is_custom(self, module_path: Path) -> bool:
        path_str = str(module_path)
        custom_indicators = ["custom", "third-party", "extra-addons"]
        return any(ind in path_str.lower() for ind in custom_indicators)

    def _build_dependency_graph(self):
        """Build the module dependency graph."""
        for name, info in self.model.modules.items():
            for dep in info.depends:
                if dep in self.model.modules:
                    self.model.dependency_graph.append((name, dep))

    def _detect_infrastructure(self):
        """Detect Docker, Helm, CI/CD configurations."""
        self.model.has_docker = (self.root_path / "docker-compose.yml").exists()
        self.model.has_helm = any(
            self.root_path.glob("**/Chart.yaml")
        )
        self.model.has_ci_cd = any(
            (self.root_path / p).exists()
            for p in [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile"]
        )

    def get_model(self) -> ProjectModel:
        return self.model

    def get_module(self, name: str) -> Optional[ModuleInfo]:
        return self.model.modules.get(name)

    def get_custom_modules(self) -> List[ModuleInfo]:
        return [m for m in self.model.modules.values() if m.is_custom]

    def get_dependency_graph_mermaid(self) -> str:
        """Generate a Mermaid dependency graph."""
        lines = ["graph LR"]
        for src, tgt in self.model.dependency_graph:
            lines.append(f"    {src}-->{tgt}")
        return "\n".join(lines)
