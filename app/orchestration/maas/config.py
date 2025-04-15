"""
Configuration module for Multi-agent Architecture Search (MaAS).

This module provides configuration settings for the MaAS system, including
search parameters, evaluation metrics, and integration settings.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class SearchParameters(BaseModel):
    """Parameters for the architecture search process."""
    
    population_size: int = Field(
        default=50,
        description="Size of the population for evolutionary algorithms"
    )
    generations: int = Field(
        default=100,
        description="Number of generations for evolutionary algorithms"
    )
    mutation_rate: float = Field(
        default=0.1,
        description="Probability of mutation for evolutionary algorithms"
    )
    crossover_rate: float = Field(
        default=0.7,
        description="Probability of crossover for evolutionary algorithms"
    )
    tournament_size: int = Field(
        default=5,
        description="Size of tournament for selection in evolutionary algorithms"
    )
    elitism_count: int = Field(
        default=2,
        description="Number of top individuals to preserve in each generation"
    )
    early_stopping_patience: int = Field(
        default=10,
        description="Number of generations without improvement before early stopping"
    )
    parallel_evaluations: int = Field(
        default=8,
        description="Number of parallel evaluations to run"
    )


class EvaluationMetrics(BaseModel):
    """Configuration for evaluation metrics used in architecture search."""
    
    performance_weight: float = Field(
        default=0.4,
        description="Weight for performance metrics in fitness calculation"
    )
    efficiency_weight: float = Field(
        default=0.3,
        description="Weight for efficiency metrics in fitness calculation"
    )
    adaptability_weight: float = Field(
        default=0.2,
        description="Weight for adaptability metrics in fitness calculation"
    )
    complexity_weight: float = Field(
        default=0.1,
        description="Weight for complexity metrics in fitness calculation"
    )
    performance_metrics: List[str] = Field(
        default=["success_rate", "completion_time", "quality_score"],
        description="List of performance metrics to evaluate"
    )
    efficiency_metrics: List[str] = Field(
        default=["resource_usage", "message_count", "computation_time"],
        description="List of efficiency metrics to evaluate"
    )
    adaptability_metrics: List[str] = Field(
        default=["task_diversity", "error_recovery", "learning_rate"],
        description="List of adaptability metrics to evaluate"
    )
    complexity_metrics: List[str] = Field(
        default=["agent_count", "connection_density", "hierarchy_depth"],
        description="List of complexity metrics to evaluate"
    )


class ArchitectureConstraints(BaseModel):
    """Constraints for valid agent architectures."""
    
    min_agents: int = Field(
        default=2,
        description="Minimum number of agents in an architecture"
    )
    max_agents: int = Field(
        default=20,
        description="Maximum number of agents in an architecture"
    )
    required_roles: List[str] = Field(
        default=["coordinator"],
        description="Roles that must be present in any architecture"
    )
    max_hierarchy_depth: int = Field(
        default=3,
        description="Maximum depth of agent hierarchy"
    )
    max_connections_per_agent: int = Field(
        default=5,
        description="Maximum number of connections per agent"
    )
    allowed_communication_patterns: List[str] = Field(
        default=["hierarchical", "mesh", "star", "ring", "hybrid"],
        description="Allowed communication patterns between agents"
    )


class IntegrationSettings(BaseModel):
    """Settings for integrating MaAS with other system components."""
    
    autogen_integration: bool = Field(
        default=True,
        description="Whether to integrate with Microsoft AutoGen Framework"
    )
    a2a_integration: bool = Field(
        default=True,
        description="Whether to integrate with Google's A2A Protocol"
    )
    mcp_integration: bool = Field(
        default=True,
        description="Whether to integrate with MCP Framework"
    )
    orchestration_service_integration: bool = Field(
        default=True,
        description="Whether to integrate with the Orchestration Service"
    )
    team_formation_integration: bool = Field(
        default=True,
        description="Whether to integrate with the Team Formation System"
    )
    workflow_engine_integration: bool = Field(
        default=True,
        description="Whether to integrate with the Workflow Engine"
    )
    cache_architectures: bool = Field(
        default=True,
        description="Whether to cache discovered architectures for reuse"
    )
    cache_expiration: int = Field(
        default=86400,  # 24 hours in seconds
        description="Expiration time for cached architectures in seconds"
    )


class VisualizationSettings(BaseModel):
    """Settings for visualizing architecture search results."""
    
    generate_visualizations: bool = Field(
        default=True,
        description="Whether to generate visualizations of architectures"
    )
    visualization_format: str = Field(
        default="svg",
        description="Format for architecture visualizations"
    )
    include_metrics: bool = Field(
        default=True,
        description="Whether to include metrics in visualizations"
    )
    include_evolution_history: bool = Field(
        default=True,
        description="Whether to include evolution history in visualizations"
    )
    max_visualizations: int = Field(
        default=10,
        description="Maximum number of architectures to visualize"
    )


class MaaSConfig(BaseModel):
    """Main configuration for the Multi-agent Architecture Search (MaAS) system."""
    
    enabled: bool = Field(
        default=True,
        description="Whether the MaAS system is enabled"
    )
    search_parameters: SearchParameters = Field(
        default_factory=SearchParameters,
        description="Parameters for the architecture search process"
    )
    evaluation_metrics: EvaluationMetrics = Field(
        default_factory=EvaluationMetrics,
        description="Configuration for evaluation metrics"
    )
    architecture_constraints: ArchitectureConstraints = Field(
        default_factory=ArchitectureConstraints,
        description="Constraints for valid agent architectures"
    )
    integration_settings: IntegrationSettings = Field(
        default_factory=IntegrationSettings,
        description="Settings for integrating with other system components"
    )
    visualization_settings: VisualizationSettings = Field(
        default_factory=VisualizationSettings,
        description="Settings for visualizing architecture search results"
    )
    log_level: str = Field(
        default="info",
        description="Logging level for the MaAS system"
    )
    search_algorithm: str = Field(
        default="evolutionary",
        description="Algorithm to use for architecture search"
    )
    search_space: str = Field(
        default="default",
        description="Search space definition to use"
    )
    template_directory: str = Field(
        default="templates",
        description="Directory containing architecture templates"
    )
    result_directory: str = Field(
        default="results",
        description="Directory to store search results"
    )


# Default configuration
DEFAULT_CONFIG = MaaSConfig()


def get_config() -> MaaSConfig:
    """Get the MaAS configuration."""
    return DEFAULT_CONFIG


def update_config(config_dict: Dict[str, Any]) -> MaaSConfig:
    """Update the MaAS configuration with values from a dictionary."""
    global DEFAULT_CONFIG
    DEFAULT_CONFIG = MaaSConfig.parse_obj({**DEFAULT_CONFIG.dict(), **config_dict})
    return DEFAULT_CONFIG


def load_config_from_file(file_path: str) -> MaaSConfig:
    """Load the MaAS configuration from a file."""
    import json
    import yaml
    import os
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    if file_path.endswith(".json"):
        with open(file_path, "r") as f:
            config_dict = json.load(f)
    elif file_path.endswith((".yaml", ".yml")):
        with open(file_path, "r") as f:
            config_dict = yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported configuration file format: {file_path}")
    
    return update_config(config_dict)


def save_config_to_file(file_path: str, config: Optional[MaaSConfig] = None) -> None:
    """Save the MaAS configuration to a file."""
    import json
    import yaml
    import os
    
    if config is None:
        config = DEFAULT_CONFIG
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    if file_path.endswith(".json"):
        with open(file_path, "w") as f:
            json.dump(config.dict(), f, indent=2)
    elif file_path.endswith((".yaml", ".yml")):
        with open(file_path, "w") as f:
            yaml.dump(config.dict(), f, default_flow_style=False)
    else:
        raise ValueError(f"Unsupported configuration file format: {file_path}")
