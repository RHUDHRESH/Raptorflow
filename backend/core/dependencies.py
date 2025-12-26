"""
RaptorFlow Backend Dependency Management
Handles optional dependencies and graceful fallbacks for production environments.
"""

import logging
import importlib
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger("raptorflow.dependencies")


@dataclass
class DependencyStatus:
    """Status of a dependency."""
    name: str
    available: bool
    version: Optional[str] = None
    error: Optional[str] = None


class DependencyManager:
    """
    Manages optional dependencies with graceful fallbacks.
    """
    
    def __init__(self):
        self._dependencies: Dict[str, DependencyStatus] = {}
        self._check_core_dependencies()
    
    def _check_core_dependencies(self):
        """Check core required dependencies."""
        core_deps = [
            "fastapi",
            "uvicorn", 
            "pydantic",
            "asyncpg",
            "redis",
            "httpx",
            "python-jose",
            "passlib"
        ]
        
        for dep in core_deps:
            self._check_dependency(dep)
    
    def _check_dependency(self, name: str) -> DependencyStatus:
        """Check if a dependency is available."""
        if name in self._dependencies:
            return self._dependencies[name]
        
        try:
            module = importlib.import_module(name)
            version = getattr(module, "__version__", "unknown")
            status = DependencyStatus(name=name, available=True, version=version)
            logger.debug(f"Dependency {name} available (v{version})")
        except ImportError as e:
            status = DependencyStatus(name=name, available=False, error=str(e))
            logger.warning(f"Dependency {name} not available: {e}")
        
        self._dependencies[name] = status
        return status
    
    def is_available(self, name: str) -> bool:
        """Check if a dependency is available."""
        status = self._check_dependency(name)
        return status.available
    
    def get_version(self, name: str) -> Optional[str]:
        """Get version of a dependency."""
        status = self._check_dependency(name)
        return status.version
    
    def require_dependency(self, name: str, error_message: Optional[str] = None) -> bool:
        """
        Require a dependency to be available.
        Raises ImportError if not available.
        """
        if not self.is_available(name):
            message = error_message or f"Required dependency '{name}' is not installed"
            raise ImportError(message)
        return True
    
    def get_dependency_status(self) -> Dict[str, DependencyStatus]:
        """Get status of all checked dependencies."""
        return self._dependencies.copy()
    
    def import_optional(self, name: str, fallback: Any = None):
        """
        Import an optional dependency with fallback.
        """
        if self.is_available(name):
            try:
                return importlib.import_module(name)
            except ImportError as e:
                logger.warning(f"Failed to import {name}: {e}")
                return fallback
        else:
            logger.debug(f"Optional dependency {name} not available, using fallback")
            return fallback


# ML/MLops Dependencies
class MLDependencies:
    """Handle ML-related optional dependencies."""
    
    def __init__(self, dep_manager: DependencyManager):
        self.dep_manager = dep_manager
        self._check_ml_deps()
    
    def _check_ml_deps(self):
        """Check ML dependencies."""
        ml_deps = [
            "torch",
            "transformers", 
            "sklearn",
            "optuna",
            "ray",
            "hyperopt",
            "mlflow"
        ]
        
        for dep in ml_deps:
            self.dep_manager._check_dependency(dep)
    
    def is_ml_available(self) -> bool:
        """Check if basic ML stack is available."""
        return (self.dep_manager.is_available("torch") and 
                self.dep_manager.is_available("sklearn"))
    
    def is_advanced_ml_available(self) -> bool:
        """Check if advanced ML features are available."""
        return (self.is_ml_available() and
                self.dep_manager.is_available("transformers"))
    
    def is_optimization_available(self) -> bool:
        """Check if hyperparameter optimization is available."""
        return (self.dep_manager.is_available("optuna") or
                self.dep_manager.is_available("ray") or
                self.dep_manager.is_available("hyperopt"))
    
    def import_torch(self, fallback=None):
        """Import PyTorch with fallback."""
        return self.dep_manager.import_optional("torch", fallback)
    
    def import_transformers(self, fallback=None):
        """Import transformers with fallback."""
        return self.dep_manager.import_optional("transformers", fallback)
    
    def import_optuna(self, fallback=None):
        """Import Optuna with fallback."""
        return self.dep_manager.import_optional("optuna", fallback)
    
    def import_ray(self, fallback=None):
        """Import Ray with fallback."""
        return self.dep_manager.import_optional("ray", fallback)
    
    def import_hyperopt(self, fallback=None):
        """Import Hyperopt with fallback."""
        return self.dep_manager.import_optional("hyperopt", fallback)
    
    def import_mlflow(self, fallback=None):
        """Import MLflow with fallback."""
        return self.dep_manager.import_optional("mlflow", fallback)


# Data Processing Dependencies
class DataDependencies:
    """Handle data processing optional dependencies."""
    
    def __init__(self, dep_manager: DependencyManager):
        self.dep_manager = dep_manager
        self._check_data_deps()
    
    def _check_data_deps(self):
        """Check data processing dependencies."""
        data_deps = [
            "pandas",
            "numpy",
            "pyarrow",
            "polars"
        ]
        
        for dep in data_deps:
            self.dep_manager._check_dependency(dep)
    
    def is_pandas_available(self) -> bool:
        """Check if pandas is available."""
        return self.dep_manager.is_available("pandas")
    
    def is_pyarrow_available(self) -> bool:
        """Check if PyArrow is available."""
        return self.dep_manager.is_available("pyarrow")
    
    def import_pandas(self, fallback=None):
        """Import pandas with fallback."""
        return self.dep_manager.import_optional("pandas", fallback)
    
    def import_numpy(self, fallback=None):
        """Import numpy with fallback."""
        return self.dep_manager.import_optional("numpy", fallback)
    
    def import_pyarrow(self, fallback=None):
        """Import PyArrow with fallback."""
        return self.dep_manager.import_optional("pyarrow", fallback)
    
    def import_polars(self, fallback=None):
        """Import Polars with fallback."""
        return self.dep_manager.import_optional("polars", fallback)


# External Service Dependencies
class ExternalServiceDependencies:
    """Handle external service dependencies."""
    
    def __init__(self, dep_manager: DependencyManager):
        self.dep_manager = dep_manager
        self._check_external_deps()
    
    def _check_external_deps(self):
        """Check external service dependencies."""
        external_deps = [
            "openai",
            "anthropic",
            "tavily",
            "perplexity",
            "google.cloud.storage",
            "google.cloud.secret_manager",
            "google.cloud.bigquery",
            "supabase",
            "sendgrid"
        ]
        
        for dep in external_deps:
            self.dep_manager._check_dependency(dep)
    
    def is_openai_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.dep_manager.is_available("openai")
    
    def is_anthropic_available(self) -> bool:
        """Check if Anthropic is available."""
        return self.dep_manager.is_available("anthropic")
    
    def is_tavily_available(self) -> bool:
        """Check if Tavily is available."""
        return self.dep_manager.is_available("tavily")
    
    def is_perplexity_available(self) -> bool:
        """Check if Perplexity is available."""
        return self.dep_manager.is_available("perplexity")
    
    def is_gcp_available(self) -> bool:
        """Check if GCP services are available."""
        gcp_deps = ["google.cloud.storage", "google.cloud.secret_manager"]
        return all(self.dep_manager.is_available(dep) for dep in gcp_deps)
    
    def is_supabase_available(self) -> bool:
        """Check if Supabase is available."""
        return self.dep_manager.is_available("supabase")
    
    def import_openai(self, fallback=None):
        """Import OpenAI with fallback."""
        return self.dep_manager.import_optional("openai", fallback)
    
    def import_anthropic(self, fallback=None):
        """Import Anthropic with fallback."""
        return self.dep_manager.import_optional("anthropic", fallback)
    
    def import_tavily(self, fallback=None):
        """Import Tavily with fallback."""
        return self.dep_manager.import_optional("tavily", fallback)
    
    def import_perplexity(self, fallback=None):
        """Import Perplexity with fallback."""
        return self.dep_manager.import_optional("perplexity", fallback)
    
    def import_gcp_storage(self, fallback=None):
        """Import GCP Storage with fallback."""
        return self.dep_manager.import_optional("google.cloud.storage", fallback)
    
    def import_gcp_secrets(self, fallback=None):
        """Import GCP Secret Manager with fallback."""
        return self.dep_manager.import_optional("google.cloud.secret_manager", fallback)
    
    def import_supabase(self, fallback=None):
        """Import Supabase with fallback."""
        return self.dep_manager.import_optional("supabase", fallback)


# Global dependency manager instance
_dependency_manager: Optional[DependencyManager] = None
_ml_deps: Optional[MLDependencies] = None
_data_deps: Optional[DataDependencies] = None
_external_deps: Optional[ExternalServiceDependencies] = None


def get_dependency_manager() -> DependencyManager:
    """Get the global dependency manager instance."""
    global _dependency_manager
    if _dependency_manager is None:
        _dependency_manager = DependencyManager()
    return _dependency_manager


def get_ml_dependencies() -> MLDependencies:
    """Get ML dependencies manager."""
    global _ml_deps
    if _ml_deps is None:
        _ml_deps = MLDependencies(get_dependency_manager())
    return _ml_deps


def get_data_dependencies() -> DataDependencies:
    """Get data dependencies manager."""
    global _data_deps
    if _data_deps is None:
        _data_deps = DataDependencies(get_dependency_manager())
    return _data_deps


def get_external_dependencies() -> ExternalServiceDependencies:
    """Get external service dependencies manager."""
    global _external_deps
    if _external_deps is None:
        _external_deps = ExternalServiceDependencies(get_dependency_manager())
    return _external_deps


# Utility functions
def check_all_dependencies() -> Dict[str, Any]:
    """Check status of all dependencies."""
    dep_manager = get_dependency_manager()
    ml_deps = get_ml_dependencies()
    data_deps = get_data_dependencies()
    external_deps = get_external_dependencies()
    
    return {
        "core": dep_manager.get_dependency_status(),
        "ml_available": ml_deps.is_ml_available(),
        "advanced_ml_available": ml_deps.is_advanced_ml_available(),
        "optimization_available": ml_deps.is_optimization_available(),
        "pandas_available": data_deps.is_pandas_available(),
        "pyarrow_available": data_deps.is_pyarrow_available(),
        "openai_available": external_deps.is_openai_available(),
        "anthropic_available": external_deps.is_anthropic_available(),
        "tavily_available": external_deps.is_tavily_available(),
        "perplexity_available": external_deps.is_perplexity_available(),
        "gcp_available": external_deps.is_gcp_available(),
        "supabase_available": external_deps.is_supabase_available()
    }


def require_core_dependencies():
    """Require all core dependencies to be available."""
    dep_manager = get_dependency_manager()
    
    core_deps = [
        "fastapi",
        "uvicorn",
        "pydantic", 
        "asyncpg",
        "redis",
        "httpx"
    ]
    
    missing_deps = []
    for dep in core_deps:
        if not dep_manager.is_available(dep):
            missing_deps.append(dep)
    
    if missing_deps:
        raise ImportError(f"Missing core dependencies: {missing_deps}")


if __name__ == "__main__":
    # Test dependency management
    status = check_all_dependencies()
    print("Dependency Status:")
    for category, info in status.items():
        print(f"  {category}: {info}")
