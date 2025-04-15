"""
Models for Multi-agent Architecture Search (MaAS).

This module defines the data models used in the MaAS system, including
architecture representations, search spaces, and evaluation results.
"""

from typing import Dict, List, Any, Optional, Set, Tuple, Union
from enum import Enum
from pydantic import BaseModel, Field
import uuid
import datetime


class MetricType(str, Enum):
    """Enumeration of metric types for evaluation."""
    
    ACCURACY = "accuracy"
    RESOURCE = "resource"
    LATENCY = "latency"
    OTHER = "other"


class AgentRole(str, Enum):
    """Enumeration of possible agent roles in an architecture."""
    
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    PLANNER = "planner"
    RESEARCHER = "researcher"
    CRITIC = "critic"
    MEMORY = "memory"
    REASONER = "reasoner"
    GENERATOR = "generator"
    EVALUATOR = "evaluator"
    COMMUNICATOR = "communicator"
    SPECIALIST = "specialist"
    CUSTOM = "custom"
    MANAGER = "manager"
    WORKER = "worker"
    CODER = "coder"
    WRITER = "writer"


class CommunicationPattern(str, Enum):
    """Enumeration of possible communication patterns between agents."""
    
    HIERARCHICAL = "hierarchical"
    MESH = "mesh"
    STAR = "star"
    RING = "ring"
    HYBRID = "hybrid"


class AgentCapability(str, Enum):
    """Enumeration of possible agent capabilities."""
    
    TEXT_PROCESSING = "text_processing"
    IMAGE_PROCESSING = "image_processing"
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_PROCESSING = "video_processing"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    PLANNING = "planning"
    MEMORY_MANAGEMENT = "memory_management"
    INFORMATION_RETRIEVAL = "information_retrieval"
    DECISION_MAKING = "decision_making"
    CREATIVITY = "creativity"
    COORDINATION = "coordination"
    COMMUNICATION = "communication"
    LEARNING = "learning"
    ADAPTATION = "adaptation"
    DELEGATION = "delegation"
    MONITORING = "monitoring"
    REPORTING = "reporting"
    TOOL_USE = "tool_use"
    CODE_EXECUTION = "code_execution"
    ACTION_EXECUTION = "action_execution"
    GOAL_DECOMPOSITION = "goal_decomposition"
    STRATEGY_FORMULATION = "strategy_formulation"
    KNOWLEDGE_INTEGRATION = "knowledge_integration"
    FACT_CHECKING = "fact_checking"
    FEEDBACK = "feedback"
    ERROR_DETECTION = "error_detection"
    INFORMATION_STORAGE = "information_storage"
    CONTEXT_MANAGEMENT = "context_management"
    LOGICAL_REASONING = "logical_reasoning"
    PROBLEM_SOLVING = "problem_solving"
    CONTENT_GENERATION = "content_generation"
    SUMMARIZATION = "summarization"
    QUALITY_ASSESSMENT = "quality_assessment"
    PERFORMANCE_MONITORING = "performance_monitoring"
    NATURAL_LANGUAGE_PROCESSING = "natural_language_processing"
    DIALOGUE_MANAGEMENT = "dialogue_management"
    EXPLANATION = "explanation"
    DOMAIN_EXPERTISE = "domain_expertise"
    SPECIALIZED_KNOWLEDGE = "specialized_knowledge"
    TECHNICAL_SKILLS = "technical_skills"
    REQUIREMENTS_ANALYSIS = "requirements_analysis"
    RESEARCH = "research"
    DEBUGGING = "debugging"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    UI_DESIGN = "ui_design"
    DATABASE = "database"


class AgentModel(BaseModel):
    """Model representing an agent in an architecture."""
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the agent"
    )
    name: str = Field(
        ...,
        description="Name of the agent"
    )
    role: AgentRole = Field(
        ...,
        description="Role of the agent in the architecture"
    )
    capabilities: List[AgentCapability] = Field(
        default_factory=list,
        description="Capabilities of the agent"
    )
    model_name: str = Field(
        default="gpt-4",
        description="Name of the underlying model used by the agent"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for the agent"
    )
    custom_role_name: Optional[str] = Field(
        default=None,
        description="Custom role name if role is CUSTOM"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the agent model to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "model_name": self.model_name,
            "parameters": self.parameters,
            "custom_role_name": self.custom_role_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentModel":
        """Create an agent model from a dictionary."""
        # Convert string role to enum
        if isinstance(data.get("role"), str):
            data["role"] = AgentRole(data["role"])
        
        # Convert string capabilities to enum
        if "capabilities" in data and isinstance(data["capabilities"], list):
            data["capabilities"] = [
                AgentCapability(cap) if isinstance(cap, str) else cap
                for cap in data["capabilities"]
            ]
        
        return cls(**data)


class ConnectionModel(BaseModel):
    """Model representing a connection between agents in an architecture."""
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the connection"
    )
    source_id: str = Field(
        ...,
        description="ID of the source agent"
    )
    target_id: str = Field(
        ...,
        description="ID of the target agent"
    )
    bidirectional: bool = Field(
        default=False,
        description="Whether the connection is bidirectional"
    )
    weight: float = Field(
        default=1.0,
        description="Weight of the connection"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for the connection"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the connection model to a dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "bidirectional": self.bidirectional,
            "weight": self.weight,
            "parameters": self.parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConnectionModel":
        """Create a connection model from a dictionary."""
        return cls(**data)


class ArchitectureModel(BaseModel):
    """Model representing an agent architecture."""
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the architecture"
    )
    name: str = Field(
        ...,
        description="Name of the architecture"
    )
    description: str = Field(
        default="",
        description="Description of the architecture"
    )
    agents: List[AgentModel] = Field(
        default_factory=list,
        description="Agents in the architecture"
    )
    connections: List[ConnectionModel] = Field(
        default_factory=list,
        description="Connections between agents in the architecture"
    )
    communication_pattern: CommunicationPattern = Field(
        default=CommunicationPattern.HIERARCHICAL,
        description="Overall communication pattern of the architecture"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for the architecture"
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Creation timestamp"
    )
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Last update timestamp"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the architecture model to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agents": [agent.to_dict() for agent in self.agents],
            "connections": [conn.to_dict() for conn in self.connections],
            "communication_pattern": self.communication_pattern.value,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArchitectureModel":
        """Create an architecture model from a dictionary."""
        # Convert string communication pattern to enum
        if isinstance(data.get("communication_pattern"), str):
            data["communication_pattern"] = CommunicationPattern(data["communication_pattern"])
        
        # Convert agent dictionaries to AgentModel objects
        if "agents" in data and isinstance(data["agents"], list):
            data["agents"] = [
                AgentModel.from_dict(agent) if isinstance(agent, dict) else agent
                for agent in data["agents"]
            ]
        
        # Convert connection dictionaries to ConnectionModel objects
        if "connections" in data and isinstance(data["connections"], list):
            data["connections"] = [
                ConnectionModel.from_dict(conn) if isinstance(conn, dict) else conn
                for conn in data["connections"]
            ]
        
        # Convert string timestamps to datetime objects
        for timestamp_field in ["created_at", "updated_at"]:
            if timestamp_field in data and isinstance(data[timestamp_field], str):
                data[timestamp_field] = datetime.datetime.fromisoformat(data[timestamp_field])
        
        return cls(**data)
    
    def get_agent_by_id(self, agent_id: str) -> Optional[AgentModel]:
        """Get an agent by its ID."""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def get_connections_for_agent(self, agent_id: str) -> List[ConnectionModel]:
        """Get all connections for an agent."""
        return [
            conn for conn in self.connections
            if conn.source_id == agent_id or (conn.bidirectional and conn.target_id == agent_id)
        ]
    
    def add_agent(self, agent: AgentModel) -> None:
        """Add an agent to the architecture."""
        self.agents.append(agent)
        self.updated_at = datetime.datetime.now()
    
    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the architecture."""
        self.agents = [agent for agent in self.agents if agent.id != agent_id]
        # Also remove connections involving this agent
        self.connections = [
            conn for conn in self.connections
            if conn.source_id != agent_id and conn.target_id != agent_id
        ]
        self.updated_at = datetime.datetime.now()
    
    def add_connection(self, connection: ConnectionModel) -> None:
        """Add a connection to the architecture."""
        self.connections.append(connection)
        self.updated_at = datetime.datetime.now()
    
    def remove_connection(self, connection_id: str) -> None:
        """Remove a connection from the architecture."""
        self.connections = [conn for conn in self.connections if conn.id != connection_id]
        self.updated_at = datetime.datetime.now()
    
    def get_agent_count(self) -> int:
        """Get the number of agents in the architecture."""
        return len(self.agents)
    
    def get_connection_count(self) -> int:
        """Get the number of connections in the architecture."""
        return len(self.connections)
    
    def get_connection_density(self) -> float:
        """Get the connection density of the architecture."""
        n = len(self.agents)
        if n <= 1:
            return 0.0
        max_connections = n * (n - 1)
        return len(self.connections) / max_connections
    
    def get_hierarchy_depth(self) -> int:
        """Get the depth of the agent hierarchy."""
        if not self.agents or not self.connections:
            return 0
        
        # Find root agents (those that have outgoing connections but no incoming)
        incoming_connections = {conn.target_id for conn in self.connections}
        outgoing_connections = {conn.source_id for conn in self.connections}
        root_agents = outgoing_connections - incoming_connections
        
        if not root_agents:
            # No clear root, use any agent as starting point
            root_agents = {self.agents[0].id}
        
        # Build adjacency list
        adjacency_list = {}
        for conn in self.connections:
            if conn.source_id not in adjacency_list:
                adjacency_list[conn.source_id] = []
            adjacency_list[conn.source_id].append(conn.target_id)
            if conn.bidirectional:
                if conn.target_id not in adjacency_list:
                    adjacency_list[conn.target_id] = []
                adjacency_list[conn.target_id].append(conn.source_id)
        
        # Find maximum depth using BFS
        max_depth = 0
        for root in root_agents:
            visited = set()
            queue = [(root, 0)]  # (agent_id, depth)
            
            while queue:
                agent_id, depth = queue.pop(0)
                if agent_id in visited:
                    continue
                
                visited.add(agent_id)
                max_depth = max(max_depth, depth)
                
                if agent_id in adjacency_list:
                    for neighbor in adjacency_list[agent_id]:
                        if neighbor not in visited:
                            queue.append((neighbor, depth + 1))
        
        return max_depth


class TaskModel(BaseModel):
    """Model representing a task for architecture evaluation."""
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the task"
    )
    name: str = Field(
        ...,
        description="Name of the task"
    )
    description: str = Field(
        default="",
        description="Description of the task"
    )
    domain: Optional[str] = Field(
        default=None,
        description="Domain of the task (e.g., research, coding, creative)"
    )
    complexity_score: Optional[float] = Field(
        default=None,
        description="Complexity score of the task (0.0 to 1.0)"
    )
    required_capabilities: List[AgentCapability] = Field(
        default_factory=list,
        description="Capabilities required for the task"
    )
    expected_steps: Optional[int] = Field(
        default=None,
        description="Expected number of steps to complete the task"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for the task"
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Creation timestamp"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task model to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "complexity_score": self.complexity_score,
            "required_capabilities": [cap.value for cap in self.required_capabilities],
            "expected_steps": self.expected_steps,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskModel":
        """Create a task model from a dictionary."""
        # Convert string capabilities to enum
        if "required_capabilities" in data and isinstance(data["required_capabilities"], list):
            data["required_capabilities"] = [
                AgentCapability(cap) if isinstance(cap, str) else cap
                for cap in data["required_capabilities"]
            ]
        
        # Convert string timestamp to datetime object
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.datetime.fromisoformat(data["created_at"])
        
        return cls(**data)


class EvaluationResult(BaseModel):
    """Model representing the evaluation result of an architecture."""
    
    architecture_id: Optional[str] = Field(
        default=None,
        description="ID of the evaluated architecture"
    )
    architecture_name: Optional[str] = Field(
        default=None,
        description="Name of the evaluated architecture"
    )
    task_id: Optional[str] = Field(
        default=None,
        description="ID of the task used for evaluation"
    )
    fitness: float = Field(
        default=0.0,
        description="Overall fitness score of the architecture"
    )
    metrics: Dict[str, float] = Field(
        default_factory=dict,
        description="Performance metrics of the architecture"
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="Timestamp of the evaluation"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the evaluation result to a dictionary."""
        return {
            "architecture_id": self.architecture_id,
            "architecture_name": self.architecture_name,
            "task_id": self.task_id,
            "fitness": self.fitness,
            "metrics": self.metrics,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationResult":
        """Create an evaluation result from a dictionary."""
        return cls(**data)


class SearchResult(BaseModel):
    """Model representing the result of an architecture search."""
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the search result"
    )
    task_id: str = Field(
        ...,
        description="ID of the task for which the search was performed"
    )
    best_architecture_id: str = Field(
        ...,
        description="ID of the best architecture found"
    )
    best_fitness: float = Field(
        ...,
        description="Fitness score of the best architecture"
    )
    search_iterations: int = Field(
        default=0,
        description="Number of search iterations performed"
    )
    architectures_evaluated: int = Field(
        default=0,
        description="Number of architectures evaluated during search"
    )
    search_time: float = Field(
        default=0.0,
        description="Time taken for the search in seconds"
    )
    search_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters used for the search"
    )
    fitness_history: List[float] = Field(
        default_factory=list,
        description="History of best fitness scores during search"
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Creation timestamp"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the search result to a dictionary."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "best_architecture_id": self.best_architecture_id,
            "best_fitness": self.best_fitness,
            "search_iterations": self.search_iterations,
            "architectures_evaluated": self.architectures_evaluated,
            "search_time": self.search_time,
            "search_parameters": self.search_parameters,
            "fitness_history": self.fitness_history,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create a search result from a dictionary."""
        # Convert string timestamp to datetime object
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.datetime.fromisoformat(data["created_at"])
        
        return cls(**data)


class SearchSpace(BaseModel):
    """Model representing a search space for architecture search."""
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the search space"
    )
    name: str = Field(
        ...,
        description="Name of the search space"
    )
    description: str = Field(
        default="",
        description="Description of the search space"
    )
    allowed_agent_roles: List[AgentRole] = Field(
        default_factory=lambda: list(AgentRole),
        description="Allowed agent roles in the search space"
    )
    allowed_communication_patterns: List[CommunicationPattern] = Field(
        default_factory=lambda: list(CommunicationPattern),
        description="Allowed communication patterns in the search space"
    )
    allowed_agent_capabilities: List[AgentCapability] = Field(
        default_factory=lambda: list(AgentCapability),
        description="Allowed agent capabilities in the search space"
    )
    min_agents: int = Field(
        default=2,
        description="Minimum number of agents in an architecture"
    )
    max_agents: int = Field(
        default=20,
        description="Maximum number of agents in an architecture"
    )
    min_connections: int = Field(
        default=1,
        description="Minimum number of connections in an architecture"
    )
    max_connections: Optional[int] = Field(
        default=None,
        description="Maximum number of connections in an architecture"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for the search space"
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Creation timestamp"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the search space to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "allowed_agent_roles": [role.value for role in self.allowed_agent_roles],
            "allowed_communication_patterns": [pattern.value for pattern in self.allowed_communication_patterns],
            "allowed_agent_capabilities": [cap.value for cap in self.allowed_agent_capabilities],
            "min_agents": self.min_agents,
            "max_agents": self.max_agents,
            "min_connections": self.min_connections,
            "max_connections": self.max_connections,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchSpace":
        """Create a search space from a dictionary."""
        # Convert string roles to enum
        if "allowed_agent_roles" in data and isinstance(data["allowed_agent_roles"], list):
            data["allowed_agent_roles"] = [
                AgentRole(role) if isinstance(role, str) else role
                for role in data["allowed_agent_roles"]
            ]
        
        # Convert string patterns to enum
        if "allowed_communication_patterns" in data and isinstance(data["allowed_communication_patterns"], list):
            data["allowed_communication_patterns"] = [
                CommunicationPattern(pattern) if isinstance(pattern, str) else pattern
                for pattern in data["allowed_communication_patterns"]
            ]
        
        # Convert string capabilities to enum
        if "allowed_agent_capabilities" in data and isinstance(data["allowed_agent_capabilities"], list):
            data["allowed_agent_capabilities"] = [
                AgentCapability(cap) if isinstance(cap, str) else cap
                for cap in data["allowed_agent_capabilities"]
            ]
        
        # Convert string timestamp to datetime object
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.datetime.fromisoformat(data["created_at"])
        
        return cls(**data)
