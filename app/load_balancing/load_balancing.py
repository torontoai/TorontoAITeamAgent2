"""
Load Balancing System for TORONTO AI TEAM AGENT.

This module provides functionality to automatically distribute work across multiple agents
of the same role, ensuring efficient workload distribution and optimal resource utilization.
"""

import os
import json
import time
import uuid
import logging
import threading
import queue
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from enum import Enum
from dataclasses import dataclass, field
import heapq
import random
import math
from concurrent.futures import ThreadPoolExecutor, Future


class AgentRole(Enum):
    """Enum representing different agent roles in the system."""
    PROJECT_MANAGER = "project_manager"
    PRODUCT_MANAGER = "product_manager"
    DEVELOPER = "developer"
    QA_ENGINEER = "qa_engineer"
    DEVOPS_ENGINEER = "devops_engineer"
    SECURITY_ENGINEER = "security_engineer"
    DATA_SCIENTIST = "data_scientist"
    UI_DESIGNER = "ui_designer"


class TaskPriority(Enum):
    """Enum representing task priority levels."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


class TaskStatus(Enum):
    """Enum representing task status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Agent:
    """Class representing an agent in the system."""
    id: str
    role: AgentRole
    capabilities: List[str]
    max_concurrent_tasks: int = 1
    current_tasks: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    status: str = "available"
    last_heartbeat: float = field(default_factory=time.time)
    
    @property
    def is_available(self) -> bool:
        """Check if the agent is available to take on new tasks."""
        return (
            self.status == "available" and 
            len(self.current_tasks) < self.max_concurrent_tasks and
            (time.time() - self.last_heartbeat) < 60  # Consider agent alive if heartbeat within last minute
        )
    
    @property
    def load_percentage(self) -> float:
        """Calculate the current load percentage of the agent."""
        return (len(self.current_tasks) / self.max_concurrent_tasks) * 100 if self.max_concurrent_tasks > 0 else 100
    
    def update_heartbeat(self):
        """Update the agent's heartbeat timestamp."""
        self.last_heartbeat = time.time()
    
    def add_task(self, task_id: str) -> bool:
        """
        Add a task to the agent's current tasks.
        
        Args:
            task_id: ID of the task to add
            
        Returns:
            True if the task was added successfully, False otherwise
        """
        if not self.is_available:
            return False
        
        self.current_tasks.append(task_id)
        if len(self.current_tasks) >= self.max_concurrent_tasks:
            self.status = "busy"
        
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a task from the agent's current tasks.
        
        Args:
            task_id: ID of the task to remove
            
        Returns:
            True if the task was removed successfully, False otherwise
        """
        if task_id not in self.current_tasks:
            return False
        
        self.current_tasks.remove(task_id)
        if len(self.current_tasks) < self.max_concurrent_tasks:
            self.status = "available"
        
        return True
    
    def update_performance_metrics(self, task_type: str, execution_time: float, success: bool):
        """
        Update the agent's performance metrics based on task execution.
        
        Args:
            task_type: Type of task executed
            execution_time: Time taken to execute the task (in seconds)
            success: Whether the task was executed successfully
        """
        if task_type not in self.performance_metrics:
            self.performance_metrics[task_type] = {
                "avg_execution_time": execution_time,
                "success_rate": 1.0 if success else 0.0,
                "task_count": 1
            }
        else:
            metrics = self.performance_metrics[task_type]
            task_count = metrics["task_count"]
            
            # Update average execution time
            metrics["avg_execution_time"] = (
                (metrics["avg_execution_time"] * task_count + execution_time) / (task_count + 1)
            )
            
            # Update success rate
            metrics["success_rate"] = (
                (metrics["success_rate"] * task_count + (1.0 if success else 0.0)) / (task_count + 1)
            )
            
            # Update task count
            metrics["task_count"] += 1


@dataclass
class Task:
    """Class representing a task in the system."""
    id: str
    type: str
    description: str
    priority: TaskPriority
    required_role: AgentRole
    required_capabilities: List[str]
    estimated_duration: float  # in seconds
    dependencies: List[str] = field(default_factory=list)
    assigned_agent_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    
    @property
    def is_ready(self) -> bool:
        """Check if the task is ready to be executed (all dependencies are completed)."""
        # This would need to check with the task manager to verify dependency status
        return True  # Simplified for now
    
    @property
    def execution_time(self) -> Optional[float]:
        """Calculate the actual execution time of the task."""
        if self.started_at is None or self.completed_at is None:
            return None
        
        return self.completed_at - self.started_at
    
    @property
    def waiting_time(self) -> Optional[float]:
        """Calculate the waiting time of the task."""
        if self.started_at is None:
            return time.time() - self.created_at
        
        return self.started_at - self.created_at
    
    def start(self, agent_id: str):
        """
        Mark the task as started.
        
        Args:
            agent_id: ID of the agent that started the task
        """
        self.assigned_agent_id = agent_id
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = time.time()
    
    def complete(self, result: Any = None):
        """
        Mark the task as completed.
        
        Args:
            result: Result of the task execution
        """
        self.status = TaskStatus.COMPLETED
        self.completed_at = time.time()
        self.result = result
    
    def fail(self, error: str):
        """
        Mark the task as failed.
        
        Args:
            error: Error message explaining the failure
        """
        self.status = TaskStatus.FAILED
        self.completed_at = time.time()
        self.error = error


class LoadBalancingStrategy(Enum):
    """Enum representing different load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    PERFORMANCE_BASED = "performance_based"
    CAPABILITY_BASED = "capability_based"
    ADAPTIVE = "adaptive"


class LoadBalancer:
    """
    Load balancer for distributing tasks among agents.
    
    This class provides functionality to distribute tasks among agents based on
    various load balancing strategies, ensuring optimal resource utilization.
    """
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ADAPTIVE):
        """
        Initialize the load balancer.
        
        Args:
            strategy: Load balancing strategy to use
        """
        self.strategy = strategy
        self.agents: Dict[str, Agent] = {}
        self.agent_indices: Dict[AgentRole, int] = {}  # For round-robin strategy
        self.logger = logging.getLogger(__name__)
    
    def register_agent(self, agent: Agent):
        """
        Register an agent with the load balancer.
        
        Args:
            agent: Agent to register
        """
        self.agents[agent.id] = agent
        self.logger.info(f"Registered agent {agent.id} with role {agent.role}")
    
    def unregister_agent(self, agent_id: str):
        """
        Unregister an agent from the load balancer.
        
        Args:
            agent_id: ID of the agent to unregister
        """
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            self.logger.info(f"Unregistered agent {agent_id} with role {agent.role}")
    
    def get_available_agents(self, role: AgentRole = None, capabilities: List[str] = None) -> List[Agent]:
        """
        Get a list of available agents, optionally filtered by role and capabilities.
        
        Args:
            role: Role to filter by
            capabilities: Capabilities to filter by
            
        Returns:
            List of available agents
        """
        available_agents = [
            agent for agent in self.agents.values() 
            if agent.is_available and 
               (role is None or agent.role == role) and
               (capabilities is None or all(cap in agent.capabilities for cap in capabilities))
        ]
        
        return available_agents
    
    def select_agent_for_task(self, task: Task) -> Optional[Agent]:
        """
        Select an agent for a task based on the current load balancing strategy.
        
        Args:
            task: Task to assign
            
        Returns:
            Selected agent, or None if no suitable agent is available
        """
        available_agents = self.get_available_agents(
            role=task.required_role,
            capabilities=task.required_capabilities
        )
        
        if not available_agents:
            self.logger.warning(f"No available agents for task {task.id} with role {task.required_role}")
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._select_agent_round_robin(available_agents, task.required_role)
        
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._select_agent_least_connections(available_agents)
        
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._select_agent_weighted_round_robin(available_agents, task.required_role)
        
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_LEAST_CONNECTIONS:
            return self._select_agent_weighted_least_connections(available_agents)
        
        elif self.strategy == LoadBalancingStrategy.PERFORMANCE_BASED:
            return self._select_agent_performance_based(available_agents, task.type)
        
        elif self.strategy == LoadBalancingStrategy.CAPABILITY_BASED:
            return self._select_agent_capability_based(available_agents, task.required_capabilities)
        
        elif self.strategy == LoadBalancingStrategy.ADAPTIVE:
            return self._select_agent_adaptive(available_agents, task)
        
        else:
            # Default to least connections
            return self._select_agent_least_connections(available_agents)
    
    def _select_agent_round_robin(self, available_agents: List[Agent], role: AgentRole) -> Agent:
        """
        Select an agent using round-robin strategy.
        
        Args:
            available_agents: List of available agents
            role: Role of the agents
            
        Returns:
            Selected agent
        """
        if role not in self.agent_indices:
            self.agent_indices[role] = 0
        
        index = self.agent_indices[role] % len(available_agents)
        selected_agent = available_agents[index]
        
        # Update index for next selection
        self.agent_indices[role] = (self.agent_indices[role] + 1) % len(available_agents)
        
        return selected_agent
    
    def _select_agent_least_connections(self, available_agents: List[Agent]) -> Agent:
        """
        Select an agent using least connections strategy.
        
        Args:
            available_agents: List of available agents
            
        Returns:
            Selected agent
        """
        return min(available_agents, key=lambda agent: len(agent.current_tasks))
    
    def _select_agent_weighted_round_robin(self, available_agents: List[Agent], role: AgentRole) -> Agent:
        """
        Select an agent using weighted round-robin strategy.
        
        Args:
            available_agents: List of available agents
            role: Role of the agents
            
        Returns:
            Selected agent
        """
        # For simplicity, use max_concurrent_tasks as weight
        weights = [agent.max_concurrent_tasks for agent in available_agents]
        total_weight = sum(weights)
        
        if role not in self.agent_indices:
            self.agent_indices[role] = 0
        
        # Find the agent based on weighted distribution
        index = self.agent_indices[role] % total_weight
        
        for i, agent in enumerate(available_agents):
            index -= agent.max_concurrent_tasks
            if index < 0:
                # Update index for next selection
                self.agent_indices[role] = (self.agent_indices[role] + 1) % total_weight
                return agent
        
        # Fallback to first agent (should not happen)
        return available_agents[0]
    
    def _select_agent_weighted_least_connections(self, available_agents: List[Agent]) -> Agent:
        """
        Select an agent using weighted least connections strategy.
        
        Args:
            available_agents: List of available agents
            
        Returns:
            Selected agent
        """
        # Calculate load percentage for each agent
        return min(available_agents, key=lambda agent: agent.load_percentage)
    
    def _select_agent_performance_based(self, available_agents: List[Agent], task_type: str) -> Agent:
        """
        Select an agent based on past performance for similar tasks.
        
        Args:
            available_agents: List of available agents
            task_type: Type of task to assign
            
        Returns:
            Selected agent
        """
        # Calculate performance score for each agent
        def performance_score(agent: Agent) -> float:
            if task_type not in agent.performance_metrics:
                return 0.0
            
            metrics = agent.performance_metrics[task_type]
            # Lower execution time and higher success rate are better
            return (1.0 / (metrics["avg_execution_time"] + 1.0)) * metrics["success_rate"]
        
        # Select agent with highest performance score
        best_agent = max(available_agents, key=performance_score)
        
        # If best agent has no performance data, fall back to least connections
        if task_type not in best_agent.performance_metrics:
            return self._select_agent_least_connections(available_agents)
        
        return best_agent
    
    def _select_agent_capability_based(self, available_agents: List[Agent], required_capabilities: List[str]) -> Agent:
        """
        Select an agent based on capability match.
        
        Args:
            available_agents: List of available agents
            required_capabilities: Capabilities required for the task
            
        Returns:
            Selected agent
        """
        # Calculate capability match score for each agent
        def capability_match_score(agent: Agent) -> float:
            # Count how many capabilities the agent has beyond the required ones
            extra_capabilities = len(set(agent.capabilities) - set(required_capabilities))
            # Prefer agents with more specialized capabilities
            return extra_capabilities
        
        # Select agent with best capability match
        return max(available_agents, key=capability_match_score)
    
    def _select_agent_adaptive(self, available_agents: List[Agent], task: Task) -> Agent:
        """
        Select an agent using an adaptive strategy that considers multiple factors.
        
        Args:
            available_agents: List of available agents
            task: Task to assign
            
        Returns:
            Selected agent
        """
        # Calculate adaptive score for each agent
        def adaptive_score(agent: Agent) -> float:
            # Start with base score
            score = 0.0
            
            # Factor 1: Current load (lower is better)
            load_factor = 1.0 - (agent.load_percentage / 100.0)
            score += load_factor * 0.3  # 30% weight
            
            # Factor 2: Performance on similar tasks (higher is better)
            if task.type in agent.performance_metrics:
                metrics = agent.performance_metrics[task.type]
                perf_factor = (1.0 / (metrics["avg_execution_time"] + 1.0)) * metrics["success_rate"]
                score += perf_factor * 0.4  # 40% weight
            
            # Factor 3: Capability match (higher is better)
            extra_capabilities = len(set(agent.capabilities) - set(task.required_capabilities))
            cap_factor = min(extra_capabilities / 5.0, 1.0)  # Normalize to [0, 1]
            score += cap_factor * 0.2  # 20% weight
            
            # Factor 4: Random factor to prevent starvation
            random_factor = random.random()
            score += random_factor * 0.1  # 10% weight
            
            return score
        
        # Select agent with highest adaptive score
        return max(available_agents, key=adaptive_score)


class TaskQueue:
    """
    Priority queue for tasks.
    
    This class provides a priority queue implementation for tasks, ensuring that
    high-priority tasks are processed before low-priority ones.
    """
    
    def __init__(self):
        """Initialize the task queue."""
        self._queue = []  # Priority queue using heapq
        self._task_map = {}  # Map of task ID to task
        self._lock = threading.Lock()
        self._counter = 0  # For breaking ties in priority
    
    def push(self, task: Task):
        """
        Push a task to the queue.
        
        Args:
            task: Task to push
        """
        with self._lock:
            # Priority tuple: (priority value, counter, task ID)
            # Lower priority value = higher priority
            priority = (
                -task.priority.value,  # Negative because heapq is a min-heap
                self._counter,
                task.id
            )
            heapq.heappush(self._queue, priority)
            self._task_map[task.id] = task
            self._counter += 1
    
    def pop(self) -> Optional[Task]:
        """
        Pop the highest-priority task from the queue.
        
        Returns:
            Highest-priority task, or None if the queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            
            _, _, task_id = heapq.heappop(self._queue)
            task = self._task_map.pop(task_id)
            return task
    
    def peek(self) -> Optional[Task]:
        """
        Peek at the highest-priority task without removing it.
        
        Returns:
            Highest-priority task, or None if the queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            
            _, _, task_id = self._queue[0]
            return self._task_map[task_id]
    
    def remove(self, task_id: str) -> bool:
        """
        Remove a task from the queue.
        
        Args:
            task_id: ID of the task to remove
            
        Returns:
            True if the task was removed, False otherwise
        """
        with self._lock:
            if task_id not in self._task_map:
                return False
            
            # Remove from task map
            task = self._task_map.pop(task_id)
            
            # Rebuild queue without the removed task
            self._queue = [p for p in self._queue if p[2] != task_id]
            heapq.heapify(self._queue)
            
            return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            Task with the given ID, or None if not found
        """
        with self._lock:
            return self._task_map.get(task_id)
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if the queue is empty, False otherwise
        """
        with self._lock:
            return len(self._queue) == 0
    
    def size(self) -> int:
        """
        Get the size of the queue.
        
        Returns:
            Number of tasks in the queue
        """
        with self._lock:
            return len(self._queue)
    
    def clear(self):
        """Clear the queue."""
        with self._lock:
            self._queue = []
            self._task_map = {}
            self._counter = 0


class LoadBalancingSystem:
    """
    Load balancing system for distributing work across multiple agents.
    
    This class provides functionality to automatically distribute work across multiple
    agents of the same role, ensuring efficient workload distribution and optimal
    resource utilization.
    """
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ADAPTIVE,
               max_workers: int = 10):
        """
        Initialize the load balancing system.
        
        Args:
            strategy: Load balancing strategy to use
            max_workers: Maximum number of worker threads
        """
        self.load_balancer = LoadBalancer(strategy)
        self.task_queues: Dict[AgentRole, TaskQueue] = {role: TaskQueue() for role in AgentRole}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures: Dict[str, Future] = {}
        self.running = False
        self.scheduler_thread = None
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def register_agent(self, agent: Agent):
        """
        Register an agent with the load balancing system.
        
        Args:
            agent: Agent to register
        """
        self.load_balancer.register_agent(agent)
    
    def unregister_agent(self, agent_id: str):
        """
        Unregister an agent from the load balancing system.
        
        Args:
            agent_id: ID of the agent to unregister
        """
        self.load_balancer.unregister_agent(agent_id)
    
    def submit_task(self, task: Task) -> str:
        """
        Submit a task to the load balancing system.
        
        Args:
            task: Task to submit
            
        Returns:
            ID of the submitted task
        """
        # Add task to the appropriate queue
        self.task_queues[task.required_role].push(task)
        self.logger.info(f"Submitted task {task.id} with priority {task.priority}")
        
        return task.id
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        Get the status of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Status of the task, or None if the task is not found
        """
        # Check all queues for the task
        for queue in self.task_queues.values():
            task = queue.get_task(task_id)
            if task:
                return task.status
        
        # Task not found in queues, check if it's running
        with self.lock:
            if task_id in self.futures:
                # Task is running
                future = self.futures[task_id]
                if future.done():
                    try:
                        # Task completed
                        future.result()
                        return TaskStatus.COMPLETED
                    except Exception:
                        # Task failed
                        return TaskStatus.FAILED
                else:
                    # Task is still running
                    return TaskStatus.IN_PROGRESS
        
        # Task not found
        return None
    
    def get_task_result(self, task_id: str) -> Tuple[Optional[Any], Optional[str]]:
        """
        Get the result of a completed task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Tuple of (result, error), where result is the task result (or None if failed)
            and error is the error message (or None if succeeded)
        """
        # Check all queues for the task
        for queue in self.task_queues.values():
            task = queue.get_task(task_id)
            if task and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return task.result, task.error
        
        # Task not found in queues, check if it's running
        with self.lock:
            if task_id in self.futures:
                # Task is running
                future = self.futures[task_id]
                if future.done():
                    try:
                        # Task completed
                        result = future.result()
                        return result, None
                    except Exception as e:
                        # Task failed
                        return None, str(e)
        
        # Task not found or not completed
        return None, "Task not found or not completed"
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            True if the task was cancelled, False otherwise
        """
        # Check all queues for the task
        for queue in self.task_queues.values():
            if queue.remove(task_id):
                self.logger.info(f"Cancelled task {task_id} (removed from queue)")
                return True
        
        # Task not found in queues, check if it's running
        with self.lock:
            if task_id in self.futures:
                # Task is running, try to cancel it
                future = self.futures[task_id]
                cancelled = future.cancel()
                if cancelled:
                    self.logger.info(f"Cancelled task {task_id} (cancelled future)")
                    self.futures.pop(task_id)
                    return True
                else:
                    self.logger.warning(f"Failed to cancel task {task_id} (future could not be cancelled)")
                    return False
        
        # Task not found
        self.logger.warning(f"Failed to cancel task {task_id} (task not found)")
        return False
    
    def start(self):
        """Start the load balancing system."""
        with self.lock:
            if self.running:
                return
            
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            
            self.logger.info("Load balancing system started")
    
    def stop(self):
        """Stop the load balancing system."""
        with self.lock:
            if not self.running:
                return
            
            self.running = False
            
            # Wait for scheduler thread to terminate
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5.0)
            
            # Cancel all running tasks
            for future in self.futures.values():
                future.cancel()
            
            # Shutdown executor
            self.executor.shutdown(wait=False)
            
            self.logger.info("Load balancing system stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                # Process each role's task queue
                for role, queue in self.task_queues.items():
                    if queue.is_empty():
                        continue
                    
                    # Get the highest-priority task
                    task = queue.peek()
                    if not task:
                        continue
                    
                    # Check if the task is ready to be executed
                    if not task.is_ready:
                        continue
                    
                    # Try to assign the task to an agent
                    agent = self.load_balancer.select_agent_for_task(task)
                    if not agent:
                        # No available agent, try again later
                        continue
                    
                    # Remove the task from the queue
                    queue.pop()
                    
                    # Assign the task to the agent
                    if not agent.add_task(task.id):
                        # Agent couldn't accept the task, put it back in the queue
                        queue.push(task)
                        continue
                    
                    # Mark the task as assigned
                    task.status = TaskStatus.ASSIGNED
                    task.assigned_agent_id = agent.id
                    
                    # Submit the task for execution
                    future = self.executor.submit(self._execute_task, task, agent)
                    
                    with self.lock:
                        self.futures[task.id] = future
                    
                    self.logger.info(f"Assigned task {task.id} to agent {agent.id}")
            
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
            
            # Sleep for a short time to avoid busy-waiting
            time.sleep(0.1)
    
    def _execute_task(self, task: Task, agent: Agent) -> Any:
        """
        Execute a task on an agent.
        
        Args:
            task: Task to execute
            agent: Agent to execute the task on
            
        Returns:
            Result of the task execution
        """
        try:
            # Mark the task as started
            task.start(agent.id)
            self.logger.info(f"Started task {task.id} on agent {agent.id}")
            
            # Simulate task execution
            # In a real implementation, this would call the agent's API to execute the task
            start_time = time.time()
            
            # Simulate task execution time
            execution_time = task.estimated_duration * (0.8 + 0.4 * random.random())  # 80% to 120% of estimated time
            time.sleep(min(execution_time, 0.5))  # Cap at 0.5 seconds for simulation
            
            # Generate a result
            result = f"Task {task.id} executed successfully by agent {agent.id}"
            
            # Mark the task as completed
            task.complete(result)
            
            # Update agent performance metrics
            agent.update_performance_metrics(
                task_type=task.type,
                execution_time=time.time() - start_time,
                success=True
            )
            
            # Remove the task from the agent's current tasks
            agent.remove_task(task.id)
            
            self.logger.info(f"Completed task {task.id} on agent {agent.id}")
            
            # Clean up
            with self.lock:
                if task.id in self.futures:
                    self.futures.pop(task.id)
            
            return result
        
        except Exception as e:
            # Mark the task as failed
            task.fail(str(e))
            
            # Update agent performance metrics
            agent.update_performance_metrics(
                task_type=task.type,
                execution_time=time.time() - (task.started_at or time.time()),
                success=False
            )
            
            # Remove the task from the agent's current tasks
            agent.remove_task(task.id)
            
            self.logger.error(f"Failed to execute task {task.id} on agent {agent.id}: {e}")
            
            # Clean up
            with self.lock:
                if task.id in self.futures:
                    self.futures.pop(task.id)
            
            # Re-raise the exception
            raise
