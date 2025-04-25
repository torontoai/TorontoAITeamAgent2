"""
Resource Allocation Optimization Module for TORONTO AI TEAM AGENT

This module provides algorithms for optimal assignment of tasks to human and AI team members.
It supports workload balancing, skill matching, priority-based allocation, and dynamic
resource reallocation based on changing project requirements.

Features:
- Optimal task assignment based on skills, availability, and priorities
- Workload balancing across team members
- Resource utilization tracking and optimization
- Constraint-based resource allocation
- Dynamic reallocation based on changing conditions
- Integration with project management and task estimation systems
"""

import datetime
import json
import os
import random
from typing import Dict, List, Optional, Set, Tuple, Union, Any
import numpy as np
from dataclasses import dataclass, field
from enum import Enum, auto

class ResourceType(Enum):
    """Types of resources that can be allocated to tasks."""
    HUMAN = auto()
    AI_AGENT = auto()
    COMPUTE = auto()
    EXTERNAL = auto()

class SkillLevel(Enum):
    """Skill proficiency levels."""
    NOVICE = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    MASTER = 5

@dataclass
class Skill:
    """Represents a skill with a proficiency level."""
    name: str
    level: SkillLevel = SkillLevel.INTERMEDIATE
    
    def __hash__(self):
        return hash((self.name, self.level))
    
    def to_dict(self) -> Dict:
        """Convert skill to dictionary for serialization."""
        return {
            "name": self.name,
            "level": self.level.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Skill':
        """Create skill from dictionary."""
        return cls(
            name=data["name"],
            level=SkillLevel[data["level"]]
        )

@dataclass
class Resource:
    """Represents a resource (human or AI) that can be assigned to tasks."""
    id: str
    name: str
    type: ResourceType
    skills: Set[Skill] = field(default_factory=set)
    cost_per_hour: float = 0.0
    availability: Dict[str, List[Tuple[datetime.time, datetime.time]]] = field(default_factory=dict)
    max_hours_per_day: float = 8.0
    max_hours_per_week: float = 40.0
    current_allocation: Dict[str, float] = field(default_factory=dict)  # task_id -> hours
    
    def __post_init__(self):
        """Initialize default availability if not provided."""
        if not self.availability:
            # Default to 9 AM - 5 PM, Monday to Friday
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            work_hours = [(datetime.time(9, 0), datetime.time(17, 0))]
            self.availability = {day: work_hours for day in weekdays}
    
    def add_skill(self, skill: Skill) -> None:
        """Add a skill to the resource."""
        self.skills.add(skill)
    
    def has_skill(self, skill_name: str, min_level: SkillLevel = SkillLevel.NOVICE) -> bool:
        """Check if resource has a skill at or above the specified level."""
        for skill in self.skills:
            if skill.name == skill_name and skill.level.value >= min_level.value:
                return True
        return False
    
    def get_skill_level(self, skill_name: str) -> Optional[SkillLevel]:
        """Get the level of a specific skill."""
        for skill in self.skills:
            if skill.name == skill_name:
                return skill.level
        return None
    
    def is_available(self, date: datetime.date, start_time: datetime.time, end_time: datetime.time) -> bool:
        """Check if resource is available during the specified time period."""
        day_name = date.strftime("%A")
        
        if day_name not in self.availability:
            return False
        
        for avail_start, avail_end in self.availability[day_name]:
            if avail_start <= start_time and avail_end >= end_time:
                return True
        
        return False
    
    def get_daily_allocation(self, date: datetime.date) -> float:
        """Get total hours allocated on a specific date."""
        return sum(hours for task_id, hours in self.current_allocation.items() 
                  if task_id.startswith(date.isoformat()))
    
    def get_weekly_allocation(self, week_start: datetime.date) -> float:
        """Get total hours allocated in a specific week."""
        week_dates = [week_start + datetime.timedelta(days=i) for i in range(7)]
        return sum(self.get_daily_allocation(date) for date in week_dates)
    
    def can_allocate(self, date: datetime.date, hours: float) -> bool:
        """Check if resource can be allocated additional hours on a specific date."""
        current_daily = self.get_daily_allocation(date)
        
        # Check daily limit
        if current_daily + hours > self.max_hours_per_day:
            return False
        
        # Check weekly limit
        week_start = date - datetime.timedelta(days=date.weekday())
        current_weekly = self.get_weekly_allocation(week_start)
        
        return current_weekly + hours <= self.max_hours_per_week
    
    def allocate(self, task_id: str, hours: float) -> bool:
        """Allocate hours to a task."""
        if task_id in self.current_allocation:
            self.current_allocation[task_id] += hours
        else:
            self.current_allocation[task_id] = hours
        return True
    
    def deallocate(self, task_id: str) -> float:
        """Remove allocation for a task and return the hours that were allocated."""
        if task_id not in self.current_allocation:
            return 0.0
        
        hours = self.current_allocation[task_id]
        del self.current_allocation[task_id]
        return hours
    
    def to_dict(self) -> Dict:
        """Convert resource to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.name,
            "skills": [skill.to_dict() for skill in self.skills],
            "cost_per_hour": self.cost_per_hour,
            "availability": {
                day: [
                    (start.strftime("%H:%M"), end.strftime("%H:%M"))
                    for start, end in times
                ]
                for day, times in self.availability.items()
            },
            "max_hours_per_day": self.max_hours_per_day,
            "max_hours_per_week": self.max_hours_per_week,
            "current_allocation": self.current_allocation
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Resource':
        """Create resource from dictionary."""
        resource = cls(
            id=data["id"],
            name=data["name"],
            type=ResourceType[data["type"]],
            cost_per_hour=data.get("cost_per_hour", 0.0),
            max_hours_per_day=data.get("max_hours_per_day", 8.0),
            max_hours_per_week=data.get("max_hours_per_week", 40.0),
            current_allocation=data.get("current_allocation", {})
        )
        
        # Add skills
        for skill_data in data.get("skills", []):
            resource.add_skill(Skill.from_dict(skill_data))
        
        # Parse availability
        availability = {}
        for day, times in data.get("availability", {}).items():
            availability[day] = [
                (
                    datetime.datetime.strptime(start, "%H:%M").time(),
                    datetime.datetime.strptime(end, "%H:%M").time()
                )
                for start, end in times
            ]
        resource.availability = availability
        
        return resource

@dataclass
class Task:
    """Represents a task that requires resources."""
    id: str
    name: str
    description: str = ""
    required_skills: List[Tuple[str, SkillLevel]] = field(default_factory=list)
    estimated_hours: float = 0.0
    priority: int = 1  # 1 (lowest) to 10 (highest)
    deadline: Optional[datetime.datetime] = None
    dependencies: List[str] = field(default_factory=list)
    assigned_resources: Dict[str, float] = field(default_factory=dict)  # resource_id -> hours
    
    def is_assigned(self) -> bool:
        """Check if task has resources assigned."""
        return len(self.assigned_resources) > 0
    
    def get_total_assigned_hours(self) -> float:
        """Get total hours assigned to the task."""
        return sum(self.assigned_resources.values())
    
    def is_fully_assigned(self) -> bool:
        """Check if task has all required hours assigned."""
        return self.get_total_assigned_hours() >= self.estimated_hours
    
    def assign_resource(self, resource_id: str, hours: float) -> None:
        """Assign a resource to the task."""
        if resource_id in self.assigned_resources:
            self.assigned_resources[resource_id] += hours
        else:
            self.assigned_resources[resource_id] = hours
    
    def unassign_resource(self, resource_id: str) -> float:
        """Unassign a resource from the task and return the hours that were assigned."""
        if resource_id not in self.assigned_resources:
            return 0.0
        
        hours = self.assigned_resources[resource_id]
        del self.assigned_resources[resource_id]
        return hours
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "required_skills": [
                {"name": name, "level": level.name}
                for name, level in self.required_skills
            ],
            "estimated_hours": self.estimated_hours,
            "priority": self.priority,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "dependencies": self.dependencies,
            "assigned_resources": self.assigned_resources
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create task from dictionary."""
        task = cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            estimated_hours=data.get("estimated_hours", 0.0),
            priority=data.get("priority", 1),
            deadline=datetime.datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            dependencies=data.get("dependencies", []),
            assigned_resources=data.get("assigned_resources", {})
        )
        
        # Parse required skills
        for skill_data in data.get("required_skills", []):
            task.required_skills.append(
                (skill_data["name"], SkillLevel[skill_data["level"]])
            )
        
        return task

class AllocationStrategy(Enum):
    """Resource allocation strategies."""
    PRIORITY_BASED = auto()  # Allocate resources to high-priority tasks first
    DEADLINE_BASED = auto()  # Allocate resources to tasks with nearest deadlines first
    SKILL_MATCH = auto()     # Allocate resources based on best skill match
    COST_OPTIMIZED = auto()  # Allocate resources to minimize cost
    BALANCED = auto()        # Balance workload across resources
    CUSTOM = auto()          # Custom allocation strategy

class ResourceAllocator:
    """
    Handles optimal allocation of resources to tasks based on various strategies.
    """
    
    def __init__(self, strategy: AllocationStrategy = AllocationStrategy.BALANCED):
        """
        Initialize a new resource allocator.
        
        Args:
            strategy: Allocation strategy to use
        """
        self.strategy = strategy
        self.resources: Dict[str, Resource] = {}
        self.tasks: Dict[str, Task] = {}
    
    def add_resource(self, resource: Resource) -> None:
        """
        Add a resource to the allocator.
        
        Args:
            resource: Resource to add
        """
        self.resources[resource.id] = resource
    
    def add_task(self, task: Task) -> None:
        """
        Add a task to the allocator.
        
        Args:
            task: Task to add
        """
        self.tasks[task.id] = task
    
    def remove_resource(self, resource_id: str) -> None:
        """
        Remove a resource from the allocator.
        
        Args:
            resource_id: ID of the resource to remove
        """
        if resource_id not in self.resources:
            raise ValueError(f"Resource with ID {resource_id} not found")
        
        # Unassign resource from all tasks
        for task in self.tasks.values():
            task.unassign_resource(resource_id)
        
        del self.resources[resource_id]
    
    def remove_task(self, task_id: str) -> None:
        """
        Remove a task from the allocator.
        
        Args:
            task_id: ID of the task to remove
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        
        task = self.tasks[task_id]
        
        # Deallocate resources assigned to this task
        for resource_id, hours in list(task.assigned_resources.items()):
            if resource_id in self.resources:
                self.resources[resource_id].deallocate(task_id)
        
        del self.tasks[task_id]
    
    def get_resource(self, resource_id: str) -> Resource:
        """
        Get a resource by ID.
        
        Args:
            resource_id: ID of the resource to retrieve
            
        Returns:
            Resource object
        """
        if resource_id not in self.resources:
            raise ValueError(f"Resource with ID {resource_id} not found")
        
        return self.resources[resource_id]
    
    def get_task(self, task_id: str) -> Task:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Task object
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        
        return self.tasks[task_id]
    
    def get_all_resources(self) -> List[Resource]:
        """
        Get all resources in the allocator.
        
        Returns:
            List of all Resource objects
        """
        return list(self.resources.values())
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks in the allocator.
        
        Returns:
            List of all Task objects
        """
        return list(self.tasks.values())
    
    def get_unassigned_tasks(self) -> List[Task]:
        """
        Get all tasks that have not been fully assigned.
        
        Returns:
            List of Task objects that are not fully assigned
        """
        return [task for task in self.tasks.values() if not task.is_fully_assigned()]
    
    def get_available_resources(self, date: datetime.date, 
                               start_time: datetime.time, 
                               end_time: datetime.time) -> List[Resource]:
        """
        Get resources available during a specific time period.
        
        Args:
            date: Date to check availability for
            start_time: Start time of the period
            end_time: End time of the period
            
        Returns:
            List of available Resource objects
        """
        return [
            resource for resource in self.resources.values()
            if resource.is_available(date, start_time, end_time)
        ]
    
    def get_resources_with_skill(self, skill_name: str, 
                                min_level: SkillLevel = SkillLevel.NOVICE) -> List[Resource]:
        """
        Get resources with a specific skill at or above the specified level.
        
        Args:
            skill_name: Name of the skill to check for
            min_level: Minimum skill level required
            
        Returns:
            List of Resource objects with the required skill
        """
        return [
            resource for resource in self.resources.values()
            if resource.has_skill(skill_name, min_level)
        ]
    
    def calculate_skill_match_score(self, resource: Resource, task: Task) -> float:
        """
        Calculate how well a resource's skills match a task's requirements.
        
        Args:
            resource: Resource to evaluate
            task: Task to match against
            
        Returns:
            Match score (0.0 to 1.0, higher is better)
        """
        if not task.required_skills:
            return 1.0  # No skills required, perfect match
        
        total_score = 0.0
        
        for skill_name, required_level in task.required_skills:
            resource_level = resource.get_skill_level(skill_name)
            
            if resource_level is None:
                continue  # Resource doesn't have this skill
            
            # Calculate score based on skill level match
            level_diff = resource_level.value - required_level.value
            
            if level_diff < 0:
                # Resource's skill level is below required
                skill_score = 0.5 + (level_diff / (2 * required_level.value))  # Partial credit
            else:
                # Resource's skill level meets or exceeds required
                skill_score = 1.0 + (level_diff / 10)  # Bonus for exceeding requirements
            
            total_score += skill_score
        
        # Normalize score
        max_possible_score = len(task.required_skills)
        
        return total_score / max_possible_score if max_possible_score > 0 else 0.0
    
    def allocate_task(self, task_id: str, resource_id: str, hours: float) -> bool:
        """
        Manually allocate a specific resource to a task.
        
        Args:
            task_id: ID of the task to allocate
            resource_id: ID of the resource to allocate
            hours: Number of hours to allocate
            
        Returns:
            True if allocation was successful, False otherwise
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        
        if resource_id not in self.resources:
            raise ValueError(f"Resource with ID {resource_id} not found")
        
        task = self.tasks[task_id]
        resource = self.resources[resource_id]
        
        # Check if task is already fully allocated
        if task.is_fully_assigned():
            return False
        
        # Check if resource has the required skills
        for skill_name, required_level in task.required_skills:
            if not resource.has_skill(skill_name, required_level):
                return False
        
        # Allocate the resource
        task.assign_resource(resource_id, hours)
        resource.allocate(task_id, hours)
        
        return True
    
    def deallocate_task(self, task_id: str, resource_id: str) -> float:
        """
        Remove a resource allocation from a task.
        
        Args:
            task_id: ID of the task to deallocate
            resource_id: ID of the resource to deallocate
            
        Returns:
            Number of hours that were deallocated
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        
        if resource_id not in self.resources:
            raise ValueError(f"Resource with ID {resource_id} not found")
        
        task = self.tasks[task_id]
        resource = self.resources[resource_id]
        
        # Deallocate the resource
        hours = task.unassign_resource(resource_id)
        resource.deallocate(task_id)
        
        return hours
    
    def _sort_tasks_by_priority(self) -> List[Task]:
        """Sort tasks by priority (highest first)."""
        return sorted(self.tasks.values(), key=lambda t: t.priority, reverse=True)
    
    def _sort_tasks_by_deadline(self) -> List[Task]:
        """Sort tasks by deadline (earliest first)."""
        # Tasks with no deadline go last
        return sorted(
            self.tasks.values(),
            key=lambda t: t.deadline or datetime.datetime.max
        )
    
    def _sort_resources_by_skill_match(self, task: Task) -> List[Tuple[Resource, float]]:
        """Sort resources by skill match score for a specific task."""
        scored_resources = [
            (resource, self.calculate_skill_match_score(resource, task))
            for resource in self.resources.values()
        ]
        
        return sorted(scored_resources, key=lambda r: r[1], reverse=True)
    
    def _sort_resources_by_cost(self) -> List[Resource]:
        """Sort resources by cost (lowest first)."""
        return sorted(self.resources.values(), key=lambda r: r.cost_per_hour)
    
    def _sort_resources_by_availability(self) -> List[Resource]:
        """Sort resources by availability (most available first)."""
        return sorted(
            self.resources.values(),
            key=lambda r: sum(
                1 for day, times in r.availability.items()
                for _ in times
            ),
            reverse=True
        )
    
    def allocate_resources(self, date: Optional[datetime.date] = None) -> Dict[str, List[str]]:
        """
        Automatically allocate resources to tasks based on the selected strategy.
        
        Args:
            date: Specific date to allocate for (defaults to today)
            
        Returns:
            Dictionary mapping task IDs to lists of allocated resource IDs
        """
        date = date or datetime.date.today()
        allocations = {}
        
        if self.strategy == AllocationStrategy.PRIORITY_BASED:
            return self._allocate_priority_based(date)
        elif self.strategy == AllocationStrategy.DEADLINE_BASED:
            return self._allocate_deadline_based(date)
        elif self.strategy == AllocationStrategy.SKILL_MATCH:
            return self._allocate_skill_match(date)
        elif self.strategy == AllocationStrategy.COST_OPTIMIZED:
            return self._allocate_cost_optimized(date)
        elif self.strategy == AllocationStrategy.BALANCED:
            return self._allocate_balanced(date)
        else:
            raise ValueError(f"Unsupported allocation strategy: {self.strategy}")
    
    def _allocate_priority_based(self, date: datetime.date) -> Dict[str, List[str]]:
        """Allocate resources based on task priority."""
        allocations = {}
        
        # Sort tasks by priority (highest first)
        sorted_tasks = self._sort_tasks_by_priority()
        
        for task in sorted_tasks:
            if task.is_fully_assigned():
                continue
            
            # Find resources with matching skills
            matching_resources = []
            for skill_name, required_level in task.required_skills:
                resources = self.get_resources_with_skill(skill_name, required_level)
                matching_resources.extend(resources)
            
            # Count occurrences to find resources with most matching skills
            resource_counts = {}
            for resource in matching_resources:
                resource_counts[resource.id] = resource_counts.get(resource.id, 0) + 1
            
            # Sort resources by number of matching skills
            sorted_resources = sorted(
                resource_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Allocate resources
            task_allocations = []
            remaining_hours = task.estimated_hours - task.get_total_assigned_hours()
            
            for resource_id, _ in sorted_resources:
                resource = self.resources[resource_id]
                
                # Check if resource can be allocated
                if resource.can_allocate(date, remaining_hours):
                    # Allocate the resource
                    self.allocate_task(task.id, resource_id, remaining_hours)
                    task_allocations.append(resource_id)
                    remaining_hours = 0
                    break
                else:
                    # Allocate what we can
                    available_hours = min(
                        resource.max_hours_per_day - resource.get_daily_allocation(date),
                        remaining_hours
                    )
                    
                    if available_hours > 0:
                        self.allocate_task(task.id, resource_id, available_hours)
                        task_allocations.append(resource_id)
                        remaining_hours -= available_hours
                
                if remaining_hours <= 0:
                    break
            
            if task_allocations:
                allocations[task.id] = task_allocations
        
        return allocations
    
    def _allocate_deadline_based(self, date: datetime.date) -> Dict[str, List[str]]:
        """Allocate resources based on task deadlines."""
        allocations = {}
        
        # Sort tasks by deadline (earliest first)
        sorted_tasks = self._sort_tasks_by_deadline()
        
        for task in sorted_tasks:
            if task.is_fully_assigned():
                continue
            
            # Skip tasks with no deadline
            if task.deadline is None:
                continue
            
            # Find resources with matching skills
            matching_resources = []
            for skill_name, required_level in task.required_skills:
                resources = self.get_resources_with_skill(skill_name, required_level)
                matching_resources.extend(resources)
            
            # Count occurrences to find resources with most matching skills
            resource_counts = {}
            for resource in matching_resources:
                resource_counts[resource.id] = resource_counts.get(resource.id, 0) + 1
            
            # Sort resources by number of matching skills
            sorted_resources = sorted(
                resource_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Allocate resources
            task_allocations = []
            remaining_hours = task.estimated_hours - task.get_total_assigned_hours()
            
            for resource_id, _ in sorted_resources:
                resource = self.resources[resource_id]
                
                # Check if resource can be allocated
                if resource.can_allocate(date, remaining_hours):
                    # Allocate the resource
                    self.allocate_task(task.id, resource_id, remaining_hours)
                    task_allocations.append(resource_id)
                    remaining_hours = 0
                    break
                else:
                    # Allocate what we can
                    available_hours = min(
                        resource.max_hours_per_day - resource.get_daily_allocation(date),
                        remaining_hours
                    )
                    
                    if available_hours > 0:
                        self.allocate_task(task.id, resource_id, available_hours)
                        task_allocations.append(resource_id)
                        remaining_hours -= available_hours
                
                if remaining_hours <= 0:
                    break
            
            if task_allocations:
                allocations[task.id] = task_allocations
        
        return allocations
    
    def _allocate_skill_match(self, date: datetime.date) -> Dict[str, List[str]]:
        """Allocate resources based on skill match."""
        allocations = {}
        
        # Process each task
        for task in self.tasks.values():
            if task.is_fully_assigned():
                continue
            
            # Sort resources by skill match score
            sorted_resources = self._sort_resources_by_skill_match(task)
            
            # Allocate resources
            task_allocations = []
            remaining_hours = task.estimated_hours - task.get_total_assigned_hours()
            
            for resource, score in sorted_resources:
                # Skip resources with poor skill match
                if score < 0.5:
                    continue
                
                # Check if resource can be allocated
                if resource.can_allocate(date, remaining_hours):
                    # Allocate the resource
                    self.allocate_task(task.id, resource.id, remaining_hours)
                    task_allocations.append(resource.id)
                    remaining_hours = 0
                    break
                else:
                    # Allocate what we can
                    available_hours = min(
                        resource.max_hours_per_day - resource.get_daily_allocation(date),
                        remaining_hours
                    )
                    
                    if available_hours > 0:
                        self.allocate_task(task.id, resource.id, available_hours)
                        task_allocations.append(resource.id)
                        remaining_hours -= available_hours
                
                if remaining_hours <= 0:
                    break
            
            if task_allocations:
                allocations[task.id] = task_allocations
        
        return allocations
    
    def _allocate_cost_optimized(self, date: datetime.date) -> Dict[str, List[str]]:
        """Allocate resources to minimize cost."""
        allocations = {}
        
        # Sort tasks by priority (highest first)
        sorted_tasks = self._sort_tasks_by_priority()
        
        # Sort resources by cost (lowest first)
        sorted_resources = self._sort_resources_by_cost()
        
        for task in sorted_tasks:
            if task.is_fully_assigned():
                continue
            
            # Allocate resources
            task_allocations = []
            remaining_hours = task.estimated_hours - task.get_total_assigned_hours()
            
            for resource in sorted_resources:
                # Check if resource has required skills
                has_skills = True
                for skill_name, required_level in task.required_skills:
                    if not resource.has_skill(skill_name, required_level):
                        has_skills = False
                        break
                
                if not has_skills:
                    continue
                
                # Check if resource can be allocated
                if resource.can_allocate(date, remaining_hours):
                    # Allocate the resource
                    self.allocate_task(task.id, resource.id, remaining_hours)
                    task_allocations.append(resource.id)
                    remaining_hours = 0
                    break
                else:
                    # Allocate what we can
                    available_hours = min(
                        resource.max_hours_per_day - resource.get_daily_allocation(date),
                        remaining_hours
                    )
                    
                    if available_hours > 0:
                        self.allocate_task(task.id, resource.id, available_hours)
                        task_allocations.append(resource.id)
                        remaining_hours -= available_hours
                
                if remaining_hours <= 0:
                    break
            
            if task_allocations:
                allocations[task.id] = task_allocations
        
        return allocations
    
    def _allocate_balanced(self, date: datetime.date) -> Dict[str, List[str]]:
        """Allocate resources to balance workload."""
        allocations = {}
        
        # Sort tasks by priority (highest first)
        sorted_tasks = self._sort_tasks_by_priority()
        
        for task in sorted_tasks:
            if task.is_fully_assigned():
                continue
            
            # Find resources with matching skills
            matching_resources = []
            for skill_name, required_level in task.required_skills:
                resources = self.get_resources_with_skill(skill_name, required_level)
                matching_resources.extend(resources)
            
            # Count occurrences to find resources with most matching skills
            resource_counts = {}
            for resource in matching_resources:
                resource_counts[resource.id] = resource_counts.get(resource.id, 0) + 1
            
            # Filter resources with all required skills
            qualified_resources = [
                resource_id for resource_id, count in resource_counts.items()
                if count == len(task.required_skills)
            ]
            
            # Sort qualified resources by current workload (least busy first)
            sorted_resources = sorted(
                qualified_resources,
                key=lambda r_id: sum(self.resources[r_id].current_allocation.values())
            )
            
            # Allocate resources
            task_allocations = []
            remaining_hours = task.estimated_hours - task.get_total_assigned_hours()
            
            for resource_id in sorted_resources:
                resource = self.resources[resource_id]
                
                # Check if resource can be allocated
                if resource.can_allocate(date, remaining_hours):
                    # Allocate the resource
                    self.allocate_task(task.id, resource_id, remaining_hours)
                    task_allocations.append(resource_id)
                    remaining_hours = 0
                    break
                else:
                    # Allocate what we can
                    available_hours = min(
                        resource.max_hours_per_day - resource.get_daily_allocation(date),
                        remaining_hours
                    )
                    
                    if available_hours > 0:
                        self.allocate_task(task.id, resource_id, available_hours)
                        task_allocations.append(resource_id)
                        remaining_hours -= available_hours
                
                if remaining_hours <= 0:
                    break
            
            if task_allocations:
                allocations[task.id] = task_allocations
        
        return allocations
    
    def optimize_allocations(self) -> Dict[str, List[str]]:
        """
        Optimize existing resource allocations to improve efficiency.
        
        Returns:
            Dictionary mapping task IDs to lists of allocated resource IDs
        """
        # Clear all existing allocations
        for task in self.tasks.values():
            for resource_id in list(task.assigned_resources.keys()):
                self.deallocate_task(task.id, resource_id)
        
        # Reallocate using the current strategy
        return self.allocate_resources()
    
    def calculate_allocation_metrics(self) -> Dict[str, Any]:
        """
        Calculate metrics for the current resource allocation.
        
        Returns:
            Dictionary of allocation metrics
        """
        metrics = {
            "total_tasks": len(self.tasks),
            "assigned_tasks": sum(1 for task in self.tasks.values() if task.is_assigned()),
            "fully_assigned_tasks": sum(1 for task in self.tasks.values() if task.is_fully_assigned()),
            "total_resources": len(self.resources),
            "utilized_resources": sum(1 for resource in self.resources.values() if resource.current_allocation),
            "total_allocated_hours": sum(
                sum(hours for hours in task.assigned_resources.values())
                for task in self.tasks.values()
            ),
            "total_estimated_hours": sum(task.estimated_hours for task in self.tasks.values()),
            "allocation_percentage": 0.0,
            "resource_utilization": {},
            "skill_coverage": {}
        }
        
        # Calculate allocation percentage
        if metrics["total_estimated_hours"] > 0:
            metrics["allocation_percentage"] = (
                metrics["total_allocated_hours"] / metrics["total_estimated_hours"] * 100
            )
        
        # Calculate resource utilization
        for resource in self.resources.values():
            total_allocated = sum(resource.current_allocation.values())
            max_capacity = resource.max_hours_per_day * 5  # Assuming 5-day work week
            
            utilization = (total_allocated / max_capacity * 100) if max_capacity > 0 else 0
            metrics["resource_utilization"][resource.id] = utilization
        
        # Calculate skill coverage
        all_required_skills = set()
        for task in self.tasks.values():
            for skill_name, _ in task.required_skills:
                all_required_skills.add(skill_name)
        
        for skill_name in all_required_skills:
            # Count resources with this skill
            resources_with_skill = sum(
                1 for resource in self.resources.values()
                if resource.has_skill(skill_name)
            )
            
            metrics["skill_coverage"][skill_name] = resources_with_skill
        
        return metrics
    
    def save(self, filename: str) -> str:
        """
        Save resource allocator data to a JSON file.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to the saved file
        """
        data = {
            "strategy": self.strategy.name,
            "resources": {r_id: resource.to_dict() for r_id, resource in self.resources.items()},
            "tasks": {t_id: task.to_dict() for t_id, task in self.tasks.items()}
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        return filename
    
    @classmethod
    def load(cls, filename: str) -> 'ResourceAllocator':
        """
        Load resource allocator data from a JSON file.
        
        Args:
            filename: Input filename
            
        Returns:
            ResourceAllocator object
        """
        with open(filename, "r") as f:
            data = json.load(f)
        
        allocator = cls(AllocationStrategy[data["strategy"]])
        
        # Load resources
        for resource_data in data["resources"].values():
            allocator.add_resource(Resource.from_dict(resource_data))
        
        # Load tasks
        for task_data in data["tasks"].values():
            allocator.add_task(Task.from_dict(task_data))
        
        return allocator


class ResourceAllocationManager:
    """
    Manager for creating and maintaining multiple resource allocation plans.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize a new resource allocation manager.
        
        Args:
            storage_dir: Directory for storing allocation data
        """
        self.storage_dir = storage_dir or os.path.join(os.getcwd(), "resource_allocations")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.allocators: Dict[str, ResourceAllocator] = {}
    
    def create_allocator(self, project_id: str, 
                        strategy: AllocationStrategy = AllocationStrategy.BALANCED) -> ResourceAllocator:
        """
        Create a new resource allocator.
        
        Args:
            project_id: Unique project identifier
            strategy: Allocation strategy to use
            
        Returns:
            New ResourceAllocator object
        """
        if project_id in self.allocators:
            raise ValueError(f"Project with ID {project_id} already exists")
        
        allocator = ResourceAllocator(strategy)
        self.allocators[project_id] = allocator
        
        return allocator
    
    def get_allocator(self, project_id: str) -> ResourceAllocator:
        """
        Get a resource allocator by project ID.
        
        Args:
            project_id: Project identifier
            
        Returns:
            ResourceAllocator object
        """
        if project_id not in self.allocators:
            raise ValueError(f"Project with ID {project_id} not found")
        
        return self.allocators[project_id]
    
    def list_allocators(self) -> List[Tuple[str, AllocationStrategy]]:
        """
        List all available resource allocators.
        
        Returns:
            List of (project_id, strategy) tuples
        """
        return [(project_id, allocator.strategy) for project_id, allocator in self.allocators.items()]
    
    def save_allocator(self, project_id: str) -> str:
        """
        Save a resource allocator to disk.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Path to the saved file
        """
        if project_id not in self.allocators:
            raise ValueError(f"Project with ID {project_id} not found")
        
        allocator = self.allocators[project_id]
        filename = os.path.join(self.storage_dir, f"{project_id}.json")
        
        return allocator.save(filename)
    
    def load_allocator(self, project_id: str) -> ResourceAllocator:
        """
        Load a resource allocator from disk.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Loaded ResourceAllocator object
        """
        filename = os.path.join(self.storage_dir, f"{project_id}.json")
        
        if not os.path.exists(filename):
            raise ValueError(f"No saved allocator found for project ID {project_id}")
        
        allocator = ResourceAllocator.load(filename)
        self.allocators[project_id] = allocator
        
        return allocator
    
    def delete_allocator(self, project_id: str) -> None:
        """
        Delete a resource allocator.
        
        Args:
            project_id: Project identifier
        """
        if project_id not in self.allocators:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Remove from memory
        del self.allocators[project_id]
        
        # Remove from disk if exists
        filename = os.path.join(self.storage_dir, f"{project_id}.json")
        if os.path.exists(filename):
            os.remove(filename)
    
    def save_all(self) -> List[str]:
        """
        Save all resource allocators to disk.
        
        Returns:
            List of saved file paths
        """
        return [self.save_allocator(project_id) for project_id in self.allocators]
    
    def load_all(self) -> List[str]:
        """
        Load all resource allocators from disk.
        
        Returns:
            List of loaded project IDs
        """
        loaded = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                project_id = os.path.splitext(filename)[0]
                self.load_allocator(project_id)
                loaded.append(project_id)
        
        return loaded
