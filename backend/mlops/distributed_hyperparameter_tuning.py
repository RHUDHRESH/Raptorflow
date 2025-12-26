"""
S.W.A.R.M. Phase 2: Distributed Hyperparameter Tuning
Production-ready distributed hyperparameter optimization with multiple search strategies
"""

import asyncio
import json
import logging
import os
import pickle
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Hyperparameter optimization imports
# Import ML dependencies with dependency management
from core.dependencies import get_ml_dependencies

ml_deps = get_ml_dependencies()

# Optuna imports
optuna = ml_deps.import_optuna()
if optuna:
    from optuna import Study, Trial, create_study
    from optuna.pruners import HyperbandPruner, MedianPruner
    from optuna.samplers import GridSampler, RandomSampler, TPESampler

    OPTUNA_AVAILABLE = True
else:
    OPTUNA_AVAILABLE = False

# Ray imports
ray = ml_deps.import_ray()
if ray:
    from ray import tune
    from ray.tune import RunConfig, TuneConfig
    from ray.tune.schedulers import ASHAScheduler, PopulationBasedTraining
    from ray.tune.search.optuna import OptunaSearch

    RAY_AVAILABLE = True
else:
    RAY_AVAILABLE = False

# Hyperopt imports
hyperopt = ml_deps.import_hyperopt()
if hyperopt:
    from hyperopt import STATUS_OK, Trials, fmin, hp, tpe

    HYPEROPT_AVAILABLE = True
else:
    HYPEROPT_AVAILABLE = False

# MLflow imports
mlflow = ml_deps.import_mlflow()
if mlflow:
    import mlflow.pytorch

    MLFLOW_AVAILABLE = True
else:
    MLFLOW_AVAILABLE = False

# PyTorch imports
torch = ml_deps.import_torch()
if torch:
    import torch.nn as nn
    import torch.optim as optim

    PYTORCH_AVAILABLE = True
else:
    PYTORCH_AVAILABLE = False

logger = logging.getLogger("raptorflow.distributed_hyperparameter_tuning")


class SearchStrategy(Enum):
    """Hyperparameter search strategies."""

    RANDOM = "random"
    GRID = "grid"
    BAYESIAN = "bayesian"
    TPE = "tpe"
    HYPERBAND = "hyperband"
    PBT = "pbt"  # Population Based Training
    OPTUNA_TPE = "optuna_tpe"
    OPTUNA_RANDOM = "optuna_random"


class PruningStrategy(Enum):
    """Early pruning strategies."""

    MEDIAN = "median"
    HYPERBAND = "hyperband"
    NONE = "none"


class OptimizationDirection(Enum):
    """Optimization direction."""

    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


@dataclass
class HyperparameterSpace:
    """Hyperparameter search space definition."""

    name: str
    parameter_type: str  # categorical, uniform, loguniform, int, choice
    low: Optional[float] = None
    high: Optional[float] = None
    choices: Optional[List[Any]] = None
    step: Optional[float] = None
    log: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "parameter_type": self.parameter_type,
            "low": self.low,
            "high": self.high,
            "choices": self.choices,
            "step": self.step,
            "log": self.log,
        }


@dataclass
class TuningConfig:
    """Hyperparameter tuning configuration."""

    study_name: str = field(default_factory=lambda: str(uuid.uuid4()))
    search_strategy: SearchStrategy = SearchStrategy.TPE
    pruning_strategy: PruningStrategy = PruningStrategy.MEDIAN
    direction: OptimizationDirection = OptimizationDirection.MINIMIZE
    max_trials: int = 100
    timeout_seconds: Optional[int] = None
    n_parallel_trials: int = 4
    early_stopping_patience: int = 10
    metric_name: str = "val_loss"
    hyperparameter_spaces: List[HyperparameterSpace] = field(default_factory=list)
    fixed_hyperparameters: Dict[str, Any] = field(default_factory=dict)
    storage_url: Optional[str] = None  # For distributed Optuna studies

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "study_name": self.study_name,
            "search_strategy": self.search_strategy.value,
            "pruning_strategy": self.pruning_strategy.value,
            "direction": self.direction.value,
            "max_trials": self.max_trials,
            "timeout_seconds": self.timeout_seconds,
            "n_parallel_trials": self.n_parallel_trials,
            "early_stopping_patience": self.early_stopping_patience,
            "metric_name": self.metric_name,
            "hyperparameter_spaces": [
                space.to_dict() for space in self.hyperparameter_spaces
            ],
            "fixed_hyperparameters": self.fixed_hyperparameters,
            "storage_url": self.storage_url,
        }


@dataclass
class TrialResult:
    """Trial result."""

    trial_id: str
    trial_number: int
    hyperparameters: Dict[str, Any]
    objective_value: float
    intermediate_values: List[float]
    user_attrs: Dict[str, Any]
    datetime_complete: datetime
    state: str  # COMPLETE, PRUNED, FAIL
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trial_id": self.trial_id,
            "trial_number": self.trial_number,
            "hyperparameters": self.hyperparameters,
            "objective_value": self.objective_value,
            "intermediate_values": self.intermediate_values,
            "user_attrs": self.user_attrs,
            "datetime_complete": self.datetime_complete.isoformat(),
            "state": self.state,
            "error": self.error,
        }


class HyperparameterOptimizer(ABC):
    """Abstract base class for hyperparameter optimizers."""

    @abstractmethod
    async def optimize(
        self, config: TuningConfig, objective_function: Callable
    ) -> List[TrialResult]:
        """Run hyperparameter optimization."""
        pass

    @abstractmethod
    async def get_best_trial(self, study_name: str) -> Optional[TrialResult]:
        """Get the best trial."""
        pass

    @abstractmethod
    async def get_study_summary(self, study_name: str) -> Dict[str, Any]:
        """Get study summary."""
        pass


class OptunaOptimizer(HyperparameterOptimizer):
    """Optuna-based hyperparameter optimizer."""

    def __init__(self):
        self.studies: Dict[str, Study] = {}
        self.study_summaries: Dict[str, Dict[str, Any]] = {}

    async def optimize(
        self, config: TuningConfig, objective_function: Callable
    ) -> List[TrialResult]:
        """Run Optuna optimization."""
        if not OPTUNA_AVAILABLE:
            raise ImportError("Optuna is required")

        try:
            # Create sampler based on strategy
            if config.search_strategy == SearchStrategy.OPTUNA_TPE:
                sampler = TPESampler(seed=42)
            elif config.search_strategy == SearchStrategy.OPTUNA_RANDOM:
                sampler = RandomSampler(seed=42)
            else:
                sampler = TPESampler(seed=42)

            # Create pruner based on strategy
            if config.pruning_strategy == PruningStrategy.MEDIAN:
                pruner = MedianPruner()
            elif config.pruning_strategy == PruningStrategy.HYPERBAND:
                pruner = HyperbandPruner()
            else:
                pruner = MedianPruner()

            # Create study
            study = create_study(
                study_name=config.study_name,
                direction=config.direction.value,
                sampler=sampler,
                pruner=pruner,
                storage=config.storage_url,
                load_if_exists=True,
            )

            self.studies[config.study_name] = study

            # Define objective wrapper
            def objective_wrapper(trial: Trial):
                try:
                    # Suggest hyperparameters
                    hyperparams = self._suggest_hyperparameters(trial, config)

                    # Add fixed hyperparameters
                    hyperparams.update(config.fixed_hyperparameters)

                    # Call objective function
                    result = objective_function(trial, hyperparams)

                    return result

                except Exception as e:
                    logger.error(f"Trial {trial.number} failed: {str(e)}")
                    raise

            # Run optimization
            study.optimize(
                objective_wrapper,
                n_trials=config.max_trials,
                timeout=config.timeout_seconds,
                n_jobs=config.n_parallel_trials,
            )

            # Convert trials to results
            results = []
            for trial in study.trials:
                result = TrialResult(
                    trial_id=str(trial._trial_id),
                    trial_number=trial.number,
                    hyperparameters=trial.params,
                    objective_value=(
                        trial.value if trial.value is not None else float("inf")
                    ),
                    intermediate_values=list(trial.intermediate_values.values()),
                    user_attrs=trial.user_attrs,
                    datetime_complete=trial.datetime_complete,
                    state=trial.state.name,
                    error=(
                        str(trial.system_attrs.get("error", ""))
                        if trial.system_attrs.get("error")
                        else None
                    ),
                )
                results.append(result)

            # Store study summary
            self.study_summaries[config.study_name] = {
                "study_name": config.study_name,
                "direction": config.direction.value,
                "n_trials": len(study.trials),
                "best_trial": study.best_trial.number if study.best_trial else None,
                "best_value": (
                    study.best_value if study.best_value is not None else float("inf")
                ),
                "best_params": study.best_params if study.best_params else {},
            }

            return results

        except Exception as e:
            logger.error(f"Optuna optimization failed: {str(e)}")
            raise

    async def get_best_trial(self, study_name: str) -> Optional[TrialResult]:
        """Get the best trial."""
        if study_name not in self.studies:
            return None

        study = self.studies[study_name]
        if not study.best_trial:
            return None

        trial = study.best_trial
        return TrialResult(
            trial_id=str(trial._trial_id),
            trial_number=trial.number,
            hyperparameters=trial.params,
            objective_value=trial.value,
            intermediate_values=list(trial.intermediate_values.values()),
            user_attrs=trial.user_attrs,
            datetime_complete=trial.datetime_complete,
            state=trial.state.name,
        )

    async def get_study_summary(self, study_name: str) -> Dict[str, Any]:
        """Get study summary."""
        return self.study_summaries.get(study_name, {})

    def _suggest_hyperparameters(
        self, trial: Trial, config: TuningConfig
    ) -> Dict[str, Any]:
        """Suggest hyperparameters based on search space."""
        hyperparams = {}

        for space in config.hyperparameter_spaces:
            if space.parameter_type == "uniform":
                if space.log:
                    hyperparams[space.name] = trial.suggest_float(
                        space.name, space.low, space.high, log=True
                    )
                else:
                    hyperparams[space.name] = trial.suggest_float(
                        space.name, space.low, space.high, step=space.step
                    )

            elif space.parameter_type == "int":
                if space.log:
                    hyperparams[space.name] = trial.suggest_int(
                        space.name, int(space.low), int(space.high), log=True
                    )
                else:
                    hyperparams[space.name] = trial.suggest_int(
                        space.name,
                        int(space.low),
                        int(space.high),
                        step=int(space.step) if space.step else 1,
                    )

            elif space.parameter_type == "categorical":
                hyperparams[space.name] = trial.suggest_categorical(
                    space.name, space.choices
                )

            elif space.parameter_type == "choice":
                hyperparams[space.name] = trial.suggest_categorical(
                    space.name, space.choices
                )

        return hyperparams


class RayTuneOptimizer(HyperparameterOptimizer):
    """Ray Tune-based hyperparameter optimizer."""

    def __init__(self):
        self.experiment_results: Dict[str, List[Dict[str, Any]]] = {}

    async def optimize(
        self, config: TuningConfig, objective_function: Callable
    ) -> List[TrialResult]:
        """Run Ray Tune optimization."""
        if not RAY_AVAILABLE:
            raise ImportError("Ray Tune is required")

        try:
            # Initialize Ray if not already running
            if not ray.is_initialized():
                ray.init()

            # Define search space
            search_space = self._create_search_space(config)

            # Create search algorithm
            if config.search_strategy == SearchStrategy.BAYESIAN:
                search_alg = OptunaSearch()
            elif config.search_strategy == SearchStrategy.TPE:
                search_alg = OptunaSearch(sampler=TPESampler())
            else:
                search_alg = None

            # Create scheduler
            if config.pruning_strategy == PruningStrategy.HYPERBAND:
                scheduler = ASHAScheduler(
                    max_t=config.max_trials, grace_period=config.early_stopping_patience
                )
            else:
                scheduler = None

            # Define trainable function
            def trainable_function(config_dict):
                # Call objective function
                result = objective_function(None, config_dict)

                # Report metrics
                tune.report({config.metric_name: result})

            # Configure tune
            tune_config = TuneConfig(
                metric=config.metric_name,
                mode=config.direction.value,
                num_samples=config.max_trials,
            )

            run_config = RunConfig(
                name=config.study_name, stop={"training_iteration": config.max_trials}
            )

            # Run optimization
            analysis = tune.run(
                trainable_function,
                config=search_space,
                tune_config=tune_config,
                run_config=run_config,
                search_alg=search_alg,
                scheduler=scheduler,
                resources_per_trial={"cpu": 1, "gpu": 0.5},
            )

            # Convert results to TrialResult format
            results = []
            for trial in analysis.trials:
                result = TrialResult(
                    trial_id=str(trial.trial_id),
                    trial_number=trial.trial_id,
                    hyperparameters=trial.config,
                    objective_value=trial.last_result.get(
                        config.metric_name, float("inf")
                    ),
                    intermediate_values=[],
                    user_attrs={},
                    datetime_complete=datetime.now(),
                    state="COMPLETE" if trial.status == "COMPLETED" else "FAILED",
                )
                results.append(result)

            # Store results
            self.experiment_results[config.study_name] = analysis.results

            return results

        except Exception as e:
            logger.error(f"Ray Tune optimization failed: {str(e)}")
            raise

        finally:
            # Shutdown Ray
            if ray.is_initialized():
                ray.shutdown()

    async def get_best_trial(self, study_name: str) -> Optional[TrialResult]:
        """Get the best trial."""
        if study_name not in self.experiment_results:
            return None

        # Find best trial from results
        results = self.experiment_results[study_name]
        if not results:
            return None

        # This is simplified - in practice, you'd need to parse the actual results
        best_result = min(results, key=lambda x: x.get("metric", float("inf")))

        return TrialResult(
            trial_id=str(best_result.get("trial_id", "")),
            trial_number=best_result.get("trial_id", 0),
            hyperparameters=best_result.get("config", {}),
            objective_value=best_result.get("metric", float("inf")),
            intermediate_values=[],
            user_attrs={},
            datetime_complete=datetime.now(),
            state="COMPLETE",
        )

    async def get_study_summary(self, study_name: str) -> Dict[str, Any]:
        """Get study summary."""
        if study_name not in self.experiment_results:
            return {}

        results = self.experiment_results[study_name]

        return {
            "study_name": study_name,
            "n_trials": len(results),
            "best_trial": None,  # Would need to calculate from results
            "best_value": None,  # Would need to calculate from results
            "best_params": {},  # Would need to calculate from results
        }

    def _create_search_space(self, config: TuningConfig) -> Dict[str, Any]:
        """Create Ray Tune search space."""
        search_space = {}

        for space in config.hyperparameter_spaces:
            if space.parameter_type == "uniform":
                if space.log:
                    search_space[space.name] = tune.loguniform(space.low, space.high)
                else:
                    search_space[space.name] = tune.uniform(space.low, space.high)

            elif space.parameter_type == "int":
                if space.log:
                    search_space[space.name] = tune.lograndint(
                        int(space.low), int(space.high)
                    )
                else:
                    search_space[space.name] = tune.randint(
                        int(space.low), int(space.high)
                    )

            elif (
                space.parameter_type == "categorical"
                or space.parameter_type == "choice"
            ):
                search_space[space.name] = tune.choice(space.choices)

        return search_space


class HyperoptOptimizer(HyperparameterOptimizer):
    """Hyperopt-based hyperparameter optimizer."""

    def __init__(self):
        self.trials: Dict[str, Trials] = {}
        self.best_results: Dict[str, Dict[str, Any]] = {}

    async def optimize(
        self, config: TuningConfig, objective_function: Callable
    ) -> List[TrialResult]:
        """Run Hyperopt optimization."""
        if not HYPEROPT_AVAILABLE:
            raise ImportError("Hyperopt is required")

        try:
            # Create search space
            search_space = self._create_search_space(config)

            # Initialize trials
            trials_obj = Trials()
            self.trials[config.study_name] = trials_obj

            # Define objective wrapper
            def objective_wrapper(hyperparams):
                try:
                    # Add fixed hyperparameters
                    hyperparams.update(config.fixed_hyperparameters)

                    # Call objective function
                    result = objective_function(None, hyperparams)

                    return {
                        "loss": result,
                        "status": STATUS_OK,
                        "eval_time": time.time(),
                    }

                except Exception as e:
                    logger.error(f"Hyperopt trial failed: {str(e)}")
                    return {
                        "loss": float("inf"),
                        "status": STATUS_FAIL,
                        "eval_time": time.time(),
                    }

            # Run optimization
            best = fmin(
                fn=objective_wrapper,
                space=search_space,
                algo=tpe.suggest,
                max_evals=config.max_trials,
                trials=trials_obj,
                verbose=1,
            )

            # Store best result
            self.best_results[config.study_name] = best

            # Convert trials to results
            results = []
            for i, trial in enumerate(trials_obj.trials):
                result = TrialResult(
                    trial_id=str(i),
                    trial_number=i,
                    hyperparameters=trial["misc"]["vals"],
                    objective_value=trial["result"]["loss"],
                    intermediate_values=[],
                    user_attrs={},
                    datetime_complete=datetime.now(),
                    state=(
                        "COMPLETE" if trial["result"]["status"] == STATUS_OK else "FAIL"
                    ),
                )
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Hyperopt optimization failed: {str(e)}")
            raise

    async def get_best_trial(self, study_name: str) -> Optional[TrialResult]:
        """Get the best trial."""
        if study_name not in self.best_results:
            return None

        best_params = self.best_results[study_name]

        return TrialResult(
            trial_id="best",
            trial_number=0,
            hyperparameters=best_params,
            objective_value=0.0,  # Would need to track actual best value
            intermediate_values=[],
            user_attrs={},
            datetime_complete=datetime.now(),
            state="COMPLETE",
        )

    async def get_study_summary(self, study_name: str) -> Dict[str, Any]:
        """Get study summary."""
        if study_name not in self.trials:
            return {}

        trials_obj = self.trials[study_name]

        return {
            "study_name": study_name,
            "n_trials": len(trials_obj.trials),
            "best_trial": self.best_results.get(study_name, {}),
            "best_value": None,  # Would need to calculate from trials
            "best_params": self.best_results.get(study_name, {}),
        }

    def _create_search_space(self, config: TuningConfig) -> Dict[str, Any]:
        """Create Hyperopt search space."""
        search_space = {}

        for space in config.hyperparameter_spaces:
            if space.parameter_type == "uniform":
                if space.log:
                    search_space[space.name] = hp.loguniform(
                        space.name, space.low, space.high
                    )
                else:
                    search_space[space.name] = hp.uniform(
                        space.name, space.low, space.high
                    )

            elif space.parameter_type == "int":
                search_space[space.name] = hp.quniform(
                    space.name, space.low, space.high, space.step or 1
                )

            elif (
                space.parameter_type == "categorical"
                or space.parameter_type == "choice"
            ):
                search_space[space.name] = hp.choice(space.name, space.choices)

        return search_space


class DistributedHyperparameterTuner:
    """Main distributed hyperparameter tuning orchestrator."""

    def __init__(self):
        self.optimizers: Dict[SearchStrategy, HyperparameterOptimizer] = {
            SearchStrategy.OPTUNA_TPE: OptunaOptimizer(),
            SearchStrategy.OPTUNA_RANDOM: OptunaOptimizer(),
            SearchStrategy.BAYESIAN: RayTuneOptimizer(),
            SearchStrategy.TPE: HyperoptOptimizer(),
        }
        self.active_studies: Dict[str, TuningConfig] = {}
        self.study_results: Dict[str, List[TrialResult]] = {}
        self.study_history: List[Dict[str, Any]] = []

    async def create_study(self, config: TuningConfig) -> str:
        """Create a new hyperparameter study."""
        self.active_studies[config.study_name] = config

        # Initialize study results
        self.study_results[config.study_name] = []

        logger.info(f"Created study: {config.study_name}")
        return config.study_name

    async def run_optimization(
        self, study_name: str, objective_function: Callable
    ) -> List[TrialResult]:
        """Run hyperparameter optimization."""
        if study_name not in self.active_studies:
            raise ValueError(f"Study {study_name} not found")

        config = self.active_studies[study_name]
        optimizer = self.optimizers.get(config.search_strategy)

        if not optimizer:
            raise ValueError(f"Unsupported search strategy: {config.search_strategy}")

        try:
            # Log study start with MLflow
            if MLFLOW_AVAILABLE:
                mlflow.start_run(run_name=f"hyperopt_{study_name}")
                mlflow.log_params(config.to_dict())

            # Run optimization
            results = await optimizer.optimize(config, objective_function)

            # Store results
            self.study_results[study_name] = results

            # Record study completion
            self.study_history.append(
                {
                    "study_name": study_name,
                    "config": config.to_dict(),
                    "n_trials": len(results),
                    "best_trial": (
                        min(results, key=lambda x: x.objective_value).to_dict()
                        if results
                        else None
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info(
                f"Completed optimization for study {study_name} with {len(results)} trials"
            )

            return results

        except Exception as e:
            logger.error(f"Optimization failed for study {study_name}: {str(e)}")
            raise

        finally:
            if MLFLOW_AVAILABLE:
                mlflow.end_run()

    async def get_best_hyperparameters(
        self, study_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get best hyperparameters for a study."""
        if study_name not in self.study_results:
            return None

        results = self.study_results[study_name]
        if not results:
            return None

        # Find best trial
        best_trial = min(results, key=lambda x: x.objective_value)
        return best_trial.hyperparameters

    async def get_study_results(self, study_name: str) -> List[TrialResult]:
        """Get all results for a study."""
        return self.study_results.get(study_name, [])

    async def compare_studies(self, study_names: List[str]) -> Dict[str, Any]:
        """Compare multiple studies."""
        comparison = {
            "studies": {},
            "best_overall": None,
            "comparison_timestamp": datetime.now().isoformat(),
        }

        best_value = float("inf")
        best_study = None

        for study_name in study_names:
            if study_name in self.study_results:
                results = self.study_results[study_name]
                if results:
                    best_trial = min(results, key=lambda x: x.objective_value)

                    comparison["studies"][study_name] = {
                        "best_value": best_trial.objective_value,
                        "best_hyperparameters": best_trial.hyperparameters,
                        "n_trials": len(results),
                    }

                    if best_trial.objective_value < best_value:
                        best_value = best_trial.objective_value
                        best_study = study_name

        comparison["best_overall"] = {
            "study_name": best_study,
            "best_value": best_value,
        }

        return comparison

    def get_study_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get study history."""
        return self.study_history[-limit:]


# Example objective function
def create_pytorch_objective_function(train_dataset, val_dataset, model_class):
    """Create PyTorch objective function for hyperparameter tuning."""
    if not PYTORCH_AVAILABLE:
        raise ImportError("PyTorch is required")

    def objective_function(trial, hyperparams):
        try:
            # Extract hyperparameters
            learning_rate = hyperparams.get("learning_rate", 0.001)
            batch_size = hyperparams.get("batch_size", 32)
            hidden_size = hyperparams.get("hidden_size", 256)
            dropout_rate = hyperparams.get("dropout_rate", 0.2)
            weight_decay = hyperparams.get("weight_decay", 1e-4)

            # Create model
            model = model_class(
                input_size=784,
                hidden_size=hidden_size,
                num_classes=10,
                dropout_rate=dropout_rate,
            )

            # Create optimizer
            optimizer = optim.Adam(
                model.parameters(), lr=learning_rate, weight_decay=weight_decay
            )

            # Create data loaders
            train_loader = torch.utils.data.DataLoader(
                train_dataset, batch_size=batch_size, shuffle=True
            )
            val_loader = torch.utils.data.DataLoader(
                val_dataset, batch_size=batch_size, shuffle=False
            )

            # Training loop (simplified)
            model.train()
            total_loss = 0.0
            num_batches = 0

            for epoch in range(5):  # Quick training for tuning
                for batch_idx, (data, target) in enumerate(train_loader):
                    optimizer.zero_grad()
                    output = model(data)
                    loss = nn.functional.cross_entropy(output, target)
                    loss.backward()
                    optimizer.step()

                    total_loss += loss.item()
                    num_batches += 1

                    # Report intermediate value for pruning
                    if trial and batch_idx % 100 == 0:
                        intermediate_loss = total_loss / num_batches
                        if hasattr(trial, "report"):
                            trial.report(
                                intermediate_loss, epoch * len(train_loader) + batch_idx
                            )

                        # Check for pruning
                        if hasattr(trial, "should_prune") and trial.should_prune():
                            raise optuna.exceptions.TrialPruned()

            # Validation
            model.eval()
            val_loss = 0.0
            correct = 0
            total = 0

            with torch.no_grad():
                for data, target in val_loader:
                    output = model(data)
                    loss = nn.functional.cross_entropy(output, target)
                    val_loss += loss.item()

                    pred = output.argmax(dim=1)
                    correct += (pred == target).sum().item()
                    total += target.size(0)

            avg_val_loss = val_loss / len(val_loader)
            accuracy = correct / total

            # Return validation loss (to be minimized)
            return avg_val_loss

        except optuna.exceptions.TrialPruned:
            raise
        except Exception as e:
            logger.error(f"Trial failed: {str(e)}")
            return float("inf")

    return objective_function


# Predefined tuning templates
class HyperparameterTuningTemplates:
    """Predefined hyperparameter tuning templates."""

    @staticmethod
    def get_pytorch_mlp_template() -> TuningConfig:
        """Get PyTorch MLP hyperparameter tuning template."""
        return TuningConfig(
            study_name="pytorch_mlp_tuning",
            search_strategy=SearchStrategy.OPTUNA_TPE,
            pruning_strategy=PruningStrategy.MEDIAN,
            direction=OptimizationDirection.MINIMIZE,
            max_trials=50,
            n_parallel_trials=4,
            metric_name="val_loss",
            hyperparameter_spaces=[
                HyperparameterSpace(
                    name="learning_rate",
                    parameter_type="uniform",
                    low=1e-5,
                    high=1e-1,
                    log=True,
                ),
                HyperparameterSpace(
                    name="batch_size",
                    parameter_type="choice",
                    choices=[16, 32, 64, 128],
                ),
                HyperparameterSpace(
                    name="hidden_size",
                    parameter_type="choice",
                    choices=[128, 256, 512, 1024],
                ),
                HyperparameterSpace(
                    name="dropout_rate", parameter_type="uniform", low=0.0, high=0.5
                ),
                HyperparameterSpace(
                    name="weight_decay",
                    parameter_type="uniform",
                    low=1e-6,
                    high=1e-3,
                    log=True,
                ),
            ],
            fixed_hyperparameters={"epochs": 10, "input_size": 784, "num_classes": 10},
        )

    @staticmethod
    def get_xgboost_template() -> TuningConfig:
        """Get XGBoost hyperparameter tuning template."""
        return TuningConfig(
            study_name="xgboost_tuning",
            search_strategy=SearchStrategy.TPE,
            direction=OptimizationDirection.MINIMIZE,
            max_trials=100,
            metric_name="val_rmse",
            hyperparameter_spaces=[
                HyperparameterSpace(
                    name="learning_rate", parameter_type="uniform", low=0.01, high=0.3
                ),
                HyperparameterSpace(
                    name="max_depth", parameter_type="int", low=3, high=10
                ),
                HyperparameterSpace(
                    name="n_estimators",
                    parameter_type="choice",
                    choices=[50, 100, 200, 500],
                ),
                HyperparameterSpace(
                    name="subsample", parameter_type="uniform", low=0.6, high=1.0
                ),
                HyperparameterSpace(
                    name="colsample_bytree", parameter_type="uniform", low=0.6, high=1.0
                ),
                HyperparameterSpace(
                    name="reg_alpha", parameter_type="uniform", low=0.0, high=1.0
                ),
                HyperparameterSpace(
                    name="reg_lambda", parameter_type="uniform", low=0.0, high=1.0
                ),
            ],
        )


if __name__ == "__main__":
    # Example usage
    async def main():
        tuner = DistributedHyperparameterTuner()

        # Create study
        config = HyperparameterTuningTemplates.get_pytorch_mlp_template()
        study_name = await tuner.create_study(config)

        # Define dummy objective function
        def dummy_objective(trial, hyperparams):
            # Simulate training with some noise
            base_loss = 0.5
            lr_penalty = abs(hyperparams.get("learning_rate", 0.001) - 0.01) * 10
            noise = np.random.normal(0, 0.1)
            return base_loss + lr_penalty + noise

        # Run optimization
        results = await tuner.run_optimization(study_name, dummy_objective)
        print(f"Completed {len(results)} trials")

        # Get best hyperparameters
        best_params = await tuner.get_best_hyperparameters(study_name)
        print(f"Best hyperparameters: {best_params}")

    asyncio.run(main())
