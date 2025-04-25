# Task Estimation Framework Documentation

This document provides comprehensive documentation for the Task Estimation Framework implemented in the TORONTO AI TEAM AGENT system, enabling agents to accurately estimate completion times for tasks.

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)
3. [Key Features](#key-features)
4. [Integration with Other Components](#integration-with-other-components)
5. [Usage Examples](#usage-examples)

## Overview

The Task Estimation Framework enables agents to accurately estimate completion times for tasks and communicate their estimated time of arrival (ETA) to project managers and stakeholders. The framework uses historical performance data, task complexity analysis, and dependency awareness to generate accurate estimates with confidence intervals.

## Core Components

### TaskEstimationFramework

The `TaskEstimationFramework` class is the main entry point for task estimation.

```python
from app.orchestration.task_estimation import TaskEstimationFramework, TaskType, TaskComplexity, TaskStatus

# Create a framework
framework = TaskEstimationFramework()

# Create a task
task = framework.create_task(
    title="Implement Login Feature",
    description="Create a login form with authentication",
    task_type=TaskType.CODING,
    complexity=TaskComplexity.MODERATE,
    assigned_agent_id="agent1"
)

# Estimate the task
estimate = framework.estimate_task(
    task_id=task.id,
    agent_id="agent1",
    confidence_level=0.8
)

# Schedule the task
framework.schedule_task(task_id=task.id)

# Update task status
framework.update_task_status(task_id=task.id, status=TaskStatus.IN_PROGRESS)

# Get task ETA
eta = framework.get_task_eta(task_id=task.id)
print(f"Task ETA: {eta}")
```

### Task

The `Task` class represents a task with estimation data.

**Properties:**
- `id`: Unique identifier for the task
- `title`: Title of the task
- `description`: Description of the task
- `type`: Type of task (e.g., coding, research, documentation)
- `complexity`: Complexity level of the task
- `status`: Current status of the task
- `assigned_agent_id`: ID of the assigned agent
- `parent_task_id`: ID of the parent task (if any)
- `dependencies`: List of task IDs that this task depends on
- `estimate`: Task estimate (if available)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### TaskType

The `TaskType` enum defines the types of tasks.

**Values:**
- `CODING`: Software development tasks
- `RESEARCH`: Research and investigation tasks
- `DOCUMENTATION`: Documentation and writing tasks
- `DESIGN`: Design and creative tasks
- `TESTING`: Testing and quality assurance tasks
- `REVIEW`: Code review and feedback tasks
- `PLANNING`: Planning and organization tasks
- `DEPLOYMENT`: Deployment and release tasks
- `MAINTENANCE`: Maintenance and support tasks
- `OTHER`: Other types of tasks

### TaskComplexity

The `TaskComplexity` enum defines the complexity levels of tasks.

**Values:**
- `TRIVIAL`: Very simple tasks (level 1)
- `SIMPLE`: Easy tasks (level 2)
- `MODERATE`: Average complexity tasks (level 3)
- `COMPLEX`: Difficult tasks (level 4)
- `VERY_COMPLEX`: Extremely challenging tasks (level 5)

### TaskStatus

The `TaskStatus` enum defines the status values for tasks.

**Values:**
- `NOT_STARTED`: Task has not been started
- `IN_PROGRESS`: Task is currently in progress
- `COMPLETED`: Task has been completed
- `BLOCKED`: Task is blocked by dependencies or issues
- `DELAYED`: Task is delayed beyond its estimated completion time

### TaskEstimate

The `TaskEstimate` class represents a task time estimate.

**Properties:**
- `task_id`: ID of the estimated task
- `agent_id`: ID of the agent providing the estimate
- `estimated_duration`: Estimated duration in hours
- `confidence_level`: Confidence level of the estimate (0.0 to 1.0)
- `lower_bound`: Lower bound of the confidence interval in hours
- `upper_bound`: Upper bound of the confidence interval in hours
- `estimated_start_time`: Estimated start time (Unix timestamp)
- `estimated_completion_time`: Estimated completion time (Unix timestamp)
- `actual_start_time`: Actual start time (Unix timestamp)
- `actual_completion_time`: Actual completion time (Unix timestamp)
- `created_at`: Creation timestamp

**Methods:**
- `get_eta()`: Get the estimated time of arrival as a formatted string
- `get_time_remaining()`: Get the estimated time remaining in hours
- `get_progress_percentage()`: Get the estimated progress percentage
- `get_accuracy()`: Calculate the accuracy of the estimate

### AgentPerformanceProfile

The `AgentPerformanceProfile` class represents an agent's performance profile for estimation.

**Properties:**
- `agent_id`: ID of the agent
- `task_type_performance`: Performance data by task type
- `complexity_performance`: Performance data by complexity level
- `overall_accuracy`: Overall estimation accuracy
- `total_tasks_completed`: Total number of completed tasks
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Methods:**
- `update_with_task(task)`: Update the profile with a completed task

## Key Features

### Task Complexity Analysis

The framework analyzes task complexity to generate more accurate estimates:

```python
# Create tasks with different complexity levels
simple_task = framework.create_task(
    title="Update Documentation",
    description="Update the API documentation with new endpoints",
    task_type=TaskType.DOCUMENTATION,
    complexity=TaskComplexity.SIMPLE,
    assigned_agent_id="agent1"
)

complex_task = framework.create_task(
    title="Implement Authentication System",
    description="Create a secure authentication system with OAuth and MFA",
    task_type=TaskType.CODING,
    complexity=TaskComplexity.COMPLEX,
    assigned_agent_id="agent1"
)

# Estimate tasks
simple_estimate = framework.estimate_task(task_id=simple_task.id, agent_id="agent1")
complex_estimate = framework.estimate_task(task_id=complex_task.id, agent_id="agent1")

print(f"Simple task estimate: {simple_estimate.estimated_duration} hours")
print(f"Complex task estimate: {complex_estimate.estimated_duration} hours")
```

### Historical Performance Tracking

The framework tracks historical performance to improve future estimates:

```python
# Create and complete multiple tasks
for i in range(5):
    # Create task
    task = framework.create_task(
        title=f"Task {i+1}",
        description=f"Description for Task {i+1}",
        task_type=TaskType.CODING,
        complexity=TaskComplexity.MODERATE,
        assigned_agent_id="agent1"
    )
    
    # Estimate task
    framework.estimate_task(task_id=task.id, agent_id="agent1")
    
    # Schedule task
    framework.schedule_task(task_id=task.id)
    
    # Start and complete task
    framework.update_task_status(task.id, TaskStatus.IN_PROGRESS)
    # Simulate work being done
    time.sleep(0.1)
    framework.update_task_status(task.id, TaskStatus.COMPLETED)

# Get agent profile
profile = framework.get_agent_profile("agent1")

print(f"Agent accuracy: {profile.overall_accuracy}%")
print(f"Tasks completed: {profile.total_tasks_completed}")
```

### Dependency-Aware Estimation

The framework considers task dependencies when generating estimates:

```python
# Create dependent tasks
task1 = framework.create_task(
    title="Database Schema Design",
    description="Design the database schema for the application",
    task_type=TaskType.DESIGN,
    complexity=TaskComplexity.MODERATE,
    assigned_agent_id="agent1"
)

task2 = framework.create_task(
    title="Database Implementation",
    description="Implement the database schema",
    task_type=TaskType.CODING,
    complexity=TaskComplexity.MODERATE,
    assigned_agent_id="agent2",
    dependencies=[task1.id]
)

# Estimate tasks
estimate1 = framework.estimate_task(task_id=task1.id, agent_id="agent1")
estimate2 = framework.estimate_task(task_id=task2.id, agent_id="agent2")

# Schedule tasks
framework.schedule_task(task_id=task1.id)
framework.schedule_task(task_id=task2.id)

# Get ETAs
eta1 = framework.get_task_eta(task1.id)
eta2 = framework.get_task_eta(task2.id)

print(f"Task 1 ETA: {eta1}")
print(f"Task 2 ETA: {eta2}")
```

### Confidence Intervals

The framework provides confidence intervals for estimates:

```python
# Create a task
task = framework.create_task(
    title="Implement Search Feature",
    description="Create a search feature with filters and pagination",
    task_type=TaskType.CODING,
    complexity=TaskComplexity.COMPLEX,
    assigned_agent_id="agent1"
)

# Estimate with different confidence levels
low_confidence = framework.estimate_task(
    task_id=task.id,
    agent_id="agent1",
    confidence_level=0.6
)

high_confidence = framework.estimate_task(
    task_id=task.id,
    agent_id="agent1",
    confidence_level=0.9
)

print(f"Low confidence (60%): {low_confidence.lower_bound} - {low_confidence.upper_bound} hours")
print(f"High confidence (90%): {high_confidence.lower_bound} - {high_confidence.upper_bound} hours")
```

### Automatic Adjustment

The framework automatically adjusts estimates based on actual performance:

```python
# Create a task
task = framework.create_task(
    title="Implement Feature",
    description="Implement a new feature",
    task_type=TaskType.CODING,
    complexity=TaskComplexity.MODERATE,
    assigned_agent_id="agent1"
)

# Estimate and schedule
framework.estimate_task(task_id=task.id, agent_id="agent1")
framework.schedule_task(task_id=task.id)

# Start task
framework.update_task_status(task.id, TaskStatus.IN_PROGRESS)

# Get initial progress
initial_progress = framework.get_task_progress(task.id)
print(f"Initial progress: {initial_progress}%")

# Simulate time passing (25% of estimated duration)
time.sleep(0.1)

# Get updated progress
updated_progress = framework.get_task_progress(task.id)
print(f"Updated progress: {updated_progress}%")

# Complete task
framework.update_task_status(task.id, TaskStatus.COMPLETED)

# Create a similar task
similar_task = framework.create_task(
    title="Implement Similar Feature",
    description="Implement another similar feature",
    task_type=TaskType.CODING,
    complexity=TaskComplexity.MODERATE,
    assigned_agent_id="agent1"
)

# Estimate should be adjusted based on previous performance
adjusted_estimate = framework.estimate_task(task_id=similar_task.id, agent_id="agent1")
print(f"Adjusted estimate: {adjusted_estimate.estimated_duration} hours")
```

## Integration with Other Components

The Task Estimation Framework integrates with other components of the TORONTO AI TEAM AGENT system:

### Integration with Project Management Features

The Task Estimation Framework can be integrated with the project management features:

```python
from app.orchestration.task_estimation import TaskEstimationFramework, TaskType, TaskComplexity
from app.project_management.gantt_chart import GanttChartGenerator, Task as GanttTask, Dependency
import datetime

# Create frameworks
estimation_framework = TaskEstimationFramework()
gantt_generator = GanttChartGenerator()

# Create and estimate tasks
task1 = estimation_framework.create_task(
    title="Research",
    description="Research technologies and approaches",
    task_type=TaskType.RESEARCH,
    complexity=TaskComplexity.MODERATE,
    assigned_agent_id="agent1"
)

task2 = estimation_framework.create_task(
    title="Design",
    description="Design the system architecture",
    task_type=TaskType.DESIGN,
    complexity=TaskComplexity.COMPLEX,
    assigned_agent_id="agent2",
    dependencies=[task1.id]
)

task3 = estimation_framework.create_task(
    title="Implementation",
    description="Implement the system",
    task_type=TaskType.CODING,
    complexity=TaskComplexity.COMPLEX,
    assigned_agent_id="agent3",
    dependencies=[task2.id]
)

# Estimate all tasks
for task_id in [task1.id, task2.id, task3.id]:
    agent_id = estimation_framework.get_task(task_id).assigned_agent_id
    estimation_framework.estimate_task(task_id=task_id, agent_id=agent_id)
    estimation_framework.schedule_task(task_id=task_id)

# Convert to Gantt chart tasks
gantt_tasks = []
dependencies = []

for i, task_id in enumerate([task1.id, task2.id, task3.id]):
    task = estimation_framework.get_task(task_id)
    
    if task.estimate and task.estimate.estimated_start_time and task.estimate.estimated_completion_time:
        start_date = datetime.datetime.fromtimestamp(task.estimate.estimated_start_time).strftime("%Y-%m-%d")
        end_date = datetime.datetime.fromtimestamp(task.estimate.estimated_completion_time).strftime("%Y-%m-%d")
        
        gantt_tasks.append(GanttTask(
            id=task.id,
            name=task.title,
            start_date=start_date,
            end_date=end_date,
            progress=0,
            assignee=task.assigned_agent_id
        ))
        
        # Add dependencies
        for dep_id in task.dependencies:
            dependencies.append(Dependency(
                from_task_id=dep_id,
                to_task_id=task.id
            ))

# Create Gantt chart
gantt = gantt_generator.create_gantt_chart(
    title="Project Timeline",
    tasks=gantt_tasks,
    dependencies=dependencies
)

# Export to HTML
html = gantt_generator.export_to_html(gantt)
```

### Integration with AI Model Integrations

The Task Estimation Framework can be enhanced with AI models:

```python
from app.orchestration.task_estimation import TaskEstimationFramework, TaskType, TaskComplexity
from app.models.adapters.claude_adapter import ClaudeAdapter

# Create frameworks
estimation_framework = TaskEstimationFramework()
claude_adapter = ClaudeAdapter(api_key="your_api_key")

# Use Claude to analyze task description
task_description = "Implement a secure authentication system with OAuth 2.0, multi-factor authentication, and password recovery"

analysis = claude_adapter.generate_response(
    prompt=f"""
    Analyze the following task description and provide:
    1. Task type (coding, research, documentation, design, testing, review, planning, deployment, maintenance, other)
    2. Complexity level (1-5, where 1 is trivial and 5 is very complex)
    3. Estimated hours to complete
    4. Required skills
    
    Task: {task_description}
    
    Format your response as JSON:
    {{
        "task_type": "...",
        "complexity": X,
        "estimated_hours": X,
        "required_skills": ["skill1", "skill2", ...]
    }}
    """,
    max_tokens=500
)

# Parse the analysis (in a real implementation, use proper JSON parsing)
# This is a simplified example
task_type = TaskType.CODING
complexity = TaskComplexity.COMPLEX
estimated_hours = 20
required_skills = ["oauth", "security", "authentication"]

# Create and estimate task
task = estimation_framework.create_task(
    title="Implement Authentication System",
    description=task_description,
    task_type=task_type,
    complexity=complexity,
    assigned_agent_id="agent1"
)

estimate = estimation_framework.estimate_task(
    task_id=task.id,
    agent_id="agent1"
)

# Compare AI estimate with framework estimate
print(f"AI estimated hours: {estimated_hours}")
print(f"Framework estimated hours: {estimate.estimated_duration}")
```

### Integration with Multi-Agent Teams

The Task Estimation Framework supports multi-agent teams:

```python
from app.orchestration.task_estimation import TaskEstimationFramework, TaskType, TaskComplexity

# Create framework
framework = TaskEstimationFramework()

# Define team
team = ["agent1", "agent2", "agent3", "agent4", "agent5"]

# Create tasks for the team
tasks = []
for i in range(10):
    task = framework.create_task(
        title=f"Task {i+1}",
        description=f"Description for Task {i+1}",
        task_type=TaskType.CODING,
        complexity=TaskComplexity.MODERATE,
        assigned_agent_id=team[i % len(team)]  # Round-robin assignment
    )
    tasks.append(task)

# Estimate all tasks
for task in tasks:
    framework.estimate_task(
        task_id=task.id,
        agent_id=task.assigned_agent_id
    )
    framework.schedule_task(task_id=task.id)

# Get team workload
workload = framework.get_team_workload(team)

# Print workload summary
for agent_id, agent_workload in workload.items():
    print(f"Agent: {agent_id}")
    print(f"  Total tasks: {agent_workload['total_tasks']}")
    print(f"  Estimated hours: {agent_workload['total_estimated_hours']}")
    print(f"  In-progress tasks: {len(agent_workload['in_progress_tasks'])}")
    print()

# Find critical path
critical_path = framework.get_critical_path([task.id for task in tasks])
print(f"Critical path: {critical_path}")
```

## Usage Examples

### Example 1: Basic Task Estimation

```python
from app.orchestration.task_estimation import TaskEstimationFramework, TaskType, TaskComplexity, TaskStatus

# Create framework
framework = TaskEstimationFramework()

# Create a task
task = framework.create_task(
    title="Implement User Registration",
    description="Create a user registration form with validation and database integration",
    task_type=TaskType.CODING,
    complexity=TaskComplexity.MODERATE,
    assigned_agent_id="developer1"
)

# Estimate the task
estimate = framework.estimate_task(
    task_id=task.id,
    agent_id="developer1",
    confidence_level=0.8
)

# Print estimate details
print(f"Task: {task.title}")
print(f"Estimated duration: {estimate.estimated_duration} hours")
print(f"Confidence interval: {estimate.lower_bound} - {estimate.upper_bound} hours")

# Schedule the task
framework.schedule_task(task_id=task.id)

# Get ETA
eta = framework.get_task_eta(task.id)
print(f"Estimated completion: {eta}")

# Update task status
framework.update_task_status(task.id, TaskStatus.IN_PROGRESS)

# Get progress
progress = framework.get_task_progress(task.id)
print(f"Progress: {progress}%")

# Complete the task
framework.update_task_status(task.id, TaskStatus.COMPLETED)

# Get accuracy
task = framework.get_task(task.id)
accuracy = task.estimate.get_accuracy()
print(f"Estimation accuracy: {accuracy}%")
```

### Example 2: Managing a Project with Dependencies

```python
from app.orchestration.task_estimation import TaskEstimationFramework, TaskType, TaskComplexity, TaskStatus

# Create framework
framework = TaskEstimationFramework()

# Create project tasks with dependencies
tasks = {
    "requirements": framework.create_task(
        title="Requirements Analysis",
        description="Analyze and document project requirements",
        task_type=TaskType.PLANNING,
        complexity=TaskComplexity.MODERATE,
        assigned_agent_id="analyst1"
    ),
    "design": framework.create_task(
        title="System Design",
        description="Design the system architecture",
        task_type=TaskType.DESIGN,
        complexity=TaskComplexity.COMPLEX,
        assigned_agent_id="architect1"
    ),
    "frontend": framework.create_task(
        title="Frontend Development",
        description="Develop the user interface",
        task_type=TaskType.CODING,
        complexity=TaskComplexity.MODERATE,
        assigned_agent_id="developer1"
    ),
    "backend": framework.create_task(
        title="Backend Development",
        description="Develop the server-side logic",
        task_type=TaskType.CODING,
        complexity=TaskComplexity.COMPLEX,
        assigned_agent_id="developer2"
    ),
    "testing": framework.create_task(
        title="Testing",
        description="Test the application",
        task_type=TaskType.TESTING,
        complexity=TaskComplexity.MODERATE,
        assigned_agent_id="tester1"
    ),
    "deployment": framework.create_task(
        title="Deployment",
        description="Deploy the application to production",
        task_type=TaskType.DEPLOYMENT,
        complexity=TaskComplexity.SIMPLE,
        assigned_agent_id="devops1"
    )
}

# Set up dependencies
framework.get_task(tasks["design"].id).dependencies = [tasks["requirements"].id]
framework.get_task(tasks["frontend"].id).dependencies = [tasks["design"].id]
framework.get_task(tasks["backend"].id).dependencies = [tasks["design"].id]
framework.get_task(tasks["testing"].id).dependencies = [tasks["frontend"].id, tasks["backend"].id]
framework.get_task(tasks["deployment"].id).dependencies = [tasks["testing"].id]

# Estimate all tasks
for task_id, task in tasks.items():
    framework.estimate_task(
        task_id=task.id,
        agent_id=task.assigned_agent_id
    )

# Schedule all tasks
for task_id, task in tasks.items():
    framework.schedule_task(task_id=task.id)

# Print project timeline
print("Project Timeline:")
for task_id, task in tasks.items():
    eta = framework.get_task_eta(task.id)
    print(f"  {task.title}: {eta}")

# Find critical path
critical_path = framework.get_critical_path([task.id for task in tasks.values()])
print(f"Critical path: {critical_path}")

# Simulate project execution
for task_id, task in tasks.items():
    print(f"Starting: {task.title}")
    framework.update_task_status(task.id, TaskStatus.IN_PROGRESS)
    
    # Simulate work being done
    time.sleep(0.1)
    
    print(f"Completing: {task.title}")
    framework.update_task_status(task.id, TaskStatus.COMPLETED)

# Get agent performance profiles
agents = ["analyst1", "architect1", "developer1", "developer2", "tester1", "devops1"]
for agent_id in agents:
    profile = framework.get_agent_profile(agent_id)
    if profile:
        print(f"Agent: {agent_id}")
        print(f"  Tasks completed: {profile.total_tasks_completed}")
        print(f"  Accuracy: {profile.overall_accuracy}%")
```

### Example 3: Team Workload Management

```python
from app.orchestration.task_estimation import TaskEstimationFramework, TaskType, TaskComplexity

# Create framework
framework = TaskEstimationFramework()

# Define development team
developers = [
    {"id": "dev1", "name": "Developer 1", "skills": ["frontend", "javascript", "react"]},
    {"id": "dev2", "name": "Developer 2", "skills": ["backend", "python", "django"]},
    {"id": "dev3", "name": "Developer 3", "skills": ["frontend", "backend", "fullstack"]},
    {"id": "dev4", "name": "Developer 4", "skills": ["mobile", "react-native", "ios"]},
    {"id": "dev5", "name": "Developer 5", "skills": ["backend", "database", "api"]}
]

# Create tasks for sprint
sprint_tasks = [
    {"title": "Implement Login UI", "type": TaskType.CODING, "complexity": TaskComplexity.SIMPLE, "skills": ["frontend", "react"]},
    {"title": "Create Authentication API", "type": TaskType.CODING, "complexity": TaskComplexity.MODERATE, "skills": ["backend", "api"]},
    {"title": "Design Database Schema", "type": TaskType.DESIGN, "complexity": TaskComplexity.MODERATE, "skills": ["database"]},
    {"title": "Implement User Profile", "type": TaskType.CODING, "complexity": TaskComplexity.MODERATE, "skills": ["frontend", "react"]},
    {"title": "Create Mobile Navigation", "type": TaskType.CODING, "complexity": TaskComplexity.COMPLEX, "skills": ["mobile", "react-native"]},
    {"title": "Implement Search Feature", "type": TaskType.CODING, "complexity": TaskComplexity.COMPLEX, "skills": ["backend", "frontend"]},
    {"title": "Add Payment Integration", "type": TaskType.CODING, "complexity": TaskComplexity.VERY_COMPLEX, "skills": ["backend", "api"]},
    {"title": "Create Admin Dashboard", "type": TaskType.CODING, "complexity": TaskComplexity.COMPLEX, "skills": ["frontend", "react"]},
    {"title": "Implement Notifications", "type": TaskType.CODING, "complexity": TaskComplexity.MODERATE, "skills": ["backend", "frontend"]},
    {"title": "Add Analytics Tracking", "type": TaskType.CODING, "complexity": TaskComplexity.SIMPLE, "skills": ["frontend", "javascript"]}
]

# Assign tasks to developers based on skills
tasks = []
for task_data in sprint_tasks:
    # Find best developer for task
    best_dev = None
    best_match = 0
    
    for dev in developers:
        # Count matching skills
        matches = sum(1 for skill in task_data["skills"] if skill in dev["skills"])
        if matches > best_match:
            best_match = matches
            best_dev = dev
    
    # Create task with assigned developer
    task = framework.create_task(
        title=task_data["title"],
        description=f"Task requiring skills: {', '.join(task_data['skills'])}",
        task_type=task_data["type"],
        complexity=task_data["complexity"],
        assigned_agent_id=best_dev["id"] if best_dev else None
    )
    tasks.append(task)

# Estimate all tasks
for task in tasks:
    if task.assigned_agent_id:
        framework.estimate_task(
            task_id=task.id,
            agent_id=task.assigned_agent_id
        )
        framework.schedule_task(task_id=task.id)

# Get team workload
workload = framework.get_team_workload([dev["id"] for dev in developers])

# Print workload summary
print("Team Workload Summary:")
for dev in developers:
    dev_id = dev["id"]
    if dev_id in workload:
        dev_workload = workload[dev_id]
        print(f"{dev['name']}:")
        print(f"  Tasks: {dev_workload['total_tasks']}")
        print(f"  Estimated hours: {dev_workload['total_estimated_hours']}")
        print()

# Balance workload if needed
max_hours = max(workload[dev["id"]]["total_estimated_hours"] for dev in developers if dev["id"] in workload)
min_hours = min(workload[dev["id"]]["total_estimated_hours"] for dev in developers if dev["id"] in workload)

if max_hours - min_hours > 10:  # More than 10 hours difference
    print("Workload is unbalanced. Reassigning tasks...")
    
    # Find overloaded and underloaded developers
    overloaded = [dev["id"] for dev in developers if dev["id"] in workload and workload[dev["id"]]["total_estimated_hours"] > max_hours - 5]
    underloaded = [dev["id"] for dev in developers if dev["id"] in workload and workload[dev["id"]]["total_estimated_hours"] < min_hours + 5]
    
    # Reassign some tasks
    for task in tasks:
        if task.assigned_agent_id in overloaded:
            # Find a suitable underloaded developer
            for dev_id in underloaded:
                dev = next(d for d in developers if d["id"] == dev_id)
                task_skills = task.description.replace("Task requiring skills: ", "").split(", ")
                
                # Check if developer has at least one required skill
                if any(skill in dev["skills"] for skill in task_skills):
                    # Reassign task
                    task.assigned_agent_id = dev_id
                    
                    # Re-estimate with new developer
                    framework.estimate_task(
                        task_id=task.id,
                        agent_id=dev_id
                    )
                    framework.schedule_task(task_id=task.id)
                    
                    print(f"Reassigned task '{task.title}' to {dev['name']}")
                    break
    
    # Get updated workload
    updated_workload = framework.get_team_workload([dev["id"] for dev in developers])
    
    # Print updated workload summary
    print("\nUpdated Team Workload Summary:")
    for dev in developers:
        dev_id = dev["id"]
        if dev_id in updated_workload:
            dev_workload = updated_workload[dev_id]
            print(f"{dev['name']}:")
            print(f"  Tasks: {dev_workload['total_tasks']}")
            print(f"  Estimated hours: {dev_workload['total_estimated_hours']}")
            print()
```
