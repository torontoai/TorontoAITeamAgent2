# Project Management Features Documentation

This document provides comprehensive documentation for the project management features implemented in the TORONTO AI TEAM AGENT system, including Gantt Chart Generation, Resource Allocation Optimization, and Automated Progress Reporting.

## Table of Contents

1. [Gantt Chart Generation](#gantt-chart-generation)
2. [Resource Allocation Optimization](#resource-allocation-optimization)
3. [Automated Progress Reporting](#automated-progress-reporting)
4. [Integration with Other Components](#integration-with-other-components)
5. [Usage Examples](#usage-examples)

## Gantt Chart Generation

The Gantt Chart Generation feature enables agents to create and maintain detailed project timelines with dependencies, providing a visual representation of project schedules and progress.

### Core Components

#### GanttChartGenerator

The `GanttChartGenerator` class is the main entry point for creating and managing Gantt charts.

```python
from app.project_management.gantt_chart import GanttChartGenerator, Task, Dependency

# Create a generator
generator = GanttChartGenerator()

# Create tasks
tasks = [
    Task(id="1", name="Research", start_date="2025-04-25", end_date="2025-04-30", progress=0),
    Task(id="2", name="Design", start_date="2025-05-01", end_date="2025-05-05", progress=0),
    Task(id="3", name="Implementation", start_date="2025-05-06", end_date="2025-05-15", progress=0),
    Task(id="4", name="Testing", start_date="2025-05-16", end_date="2025-05-20", progress=0)
]

# Create dependencies
dependencies = [
    Dependency(from_task_id="1", to_task_id="2"),
    Dependency(from_task_id="2", to_task_id="3"),
    Dependency(from_task_id="3", to_task_id="4")
]

# Create a Gantt chart
gantt = generator.create_gantt_chart(
    title="Project Timeline",
    tasks=tasks,
    dependencies=dependencies
)

# Export to HTML
html = generator.export_to_html(gantt)
```

#### Task

The `Task` class represents a single task in a Gantt chart.

**Properties:**
- `id`: Unique identifier for the task
- `name`: Name of the task
- `start_date`: Start date in "YYYY-MM-DD" format
- `end_date`: End date in "YYYY-MM-DD" format
- `progress`: Progress percentage (0-100)
- `assignee`: (Optional) Name of the assignee
- `color`: (Optional) Color for the task bar
- `milestone`: (Optional) Whether the task is a milestone

#### Dependency

The `Dependency` class represents a dependency between two tasks.

**Properties:**
- `from_task_id`: ID of the predecessor task
- `to_task_id`: ID of the successor task
- `type`: (Optional) Type of dependency (e.g., "finish-to-start", "start-to-start")

#### GanttChart

The `GanttChart` class represents a complete Gantt chart.

**Properties:**
- `title`: Title of the Gantt chart
- `tasks`: List of tasks
- `dependencies`: List of dependencies
- `start_date`: (Optional) Start date of the chart
- `end_date`: (Optional) End date of the chart

### Key Features

- **Interactive Visualization**: Generate interactive HTML-based Gantt charts
- **Dependency Management**: Define and visualize task dependencies
- **Progress Tracking**: Update and visualize task progress
- **Critical Path Analysis**: Identify the critical path through the project
- **Timeline Adjustment**: Automatically adjust dependent task dates when predecessors change
- **Export Options**: Export to HTML, PNG, or PDF formats

## Resource Allocation Optimization

The Resource Allocation Optimization feature implements algorithms for optimal assignment of tasks to human and AI team members, ensuring efficient use of resources and balanced workloads.

### Core Components

#### ResourceAllocationOptimizer

The `ResourceAllocationOptimizer` class is the main entry point for optimizing resource allocation.

```python
from app.project_management.resource_allocation import ResourceAllocationOptimizer, Resource, Task, Assignment

# Create an optimizer
optimizer = ResourceAllocationOptimizer()

# Create resources
resources = [
    Resource(id="1", name="Developer 1", skills=["python", "javascript"], availability=1.0),
    Resource(id="2", name="Developer 2", skills=["python", "java"], availability=0.5),
    Resource(id="3", name="Designer", skills=["ui", "ux"], availability=1.0)
]

# Create tasks
tasks = [
    Task(id="1", name="Frontend Development", required_skills=["javascript"], estimated_hours=20),
    Task(id="2", name="Backend Development", required_skills=["python", "java"], estimated_hours=30),
    Task(id="3", name="UI Design", required_skills=["ui"], estimated_hours=15)
]

# Optimize allocation
assignments = optimizer.optimize_allocation(resources, tasks)

# Calculate workload
workload = optimizer.calculate_workload(resources, tasks, assignments)

# Balance workload
balanced_assignments = optimizer.balance_workload(resources, tasks, assignments)
```

#### Resource

The `Resource` class represents a resource (human or AI) that can be assigned to tasks.

**Properties:**
- `id`: Unique identifier for the resource
- `name`: Name of the resource
- `skills`: List of skills possessed by the resource
- `availability`: Availability factor (0.0-1.0)
- `cost`: (Optional) Cost per hour
- `type`: (Optional) Type of resource (e.g., "human", "ai")

#### Task

The `Task` class represents a task that needs to be assigned to resources.

**Properties:**
- `id`: Unique identifier for the task
- `name`: Name of the task
- `required_skills`: List of skills required for the task
- `estimated_hours`: Estimated hours to complete the task
- `priority`: (Optional) Priority of the task (1-10)
- `deadline`: (Optional) Deadline for the task

#### Assignment

The `Assignment` class represents an assignment of a resource to a task.

**Properties:**
- `resource_id`: ID of the assigned resource
- `task_id`: ID of the assigned task
- `allocation_percentage`: Percentage of the resource's time allocated to the task
- `start_date`: (Optional) Start date of the assignment
- `end_date`: (Optional) End date of the assignment

### Key Features

- **Skill-Based Matching**: Match resources to tasks based on required skills
- **Workload Balancing**: Distribute work evenly across resources
- **Priority-Based Allocation**: Prioritize high-priority tasks
- **Partial Allocation**: Assign resources partially to multiple tasks
- **Optimization Algorithms**: Use algorithms to find optimal allocations
- **Constraint Satisfaction**: Handle constraints like deadlines and availability

## Automated Progress Reporting

The Automated Progress Reporting feature generates customized reports for different stakeholders with appropriate detail levels, providing insights into project progress and resource utilization.

### Core Components

#### ProgressReportGenerator

The `ProgressReportGenerator` class is the main entry point for generating progress reports.

```python
from app.project_management.progress_reporting import ProgressReportGenerator, ReportType

# Create a generator
generator = ProgressReportGenerator()

# Generate a summary report
summary_report = generator.generate_report(
    title="Project Progress Summary",
    report_type=ReportType.SUMMARY,
    tasks=tasks,
    resources=resources,
    assignments=assignments
)

# Generate a detailed report
detailed_report = generator.generate_report(
    title="Detailed Project Progress",
    report_type=ReportType.DETAILED,
    tasks=tasks,
    resources=resources,
    assignments=assignments
)

# Export to PDF
pdf_data = generator.export_to_pdf(detailed_report)
```

#### ReportType

The `ReportType` enum defines the types of reports that can be generated.

**Values:**
- `SUMMARY`: High-level summary for executives
- `DETAILED`: Detailed report for project managers
- `TECHNICAL`: Technical report for developers
- `STAKEHOLDER`: Report for external stakeholders

#### Report

The `Report` class represents a generated report.

**Properties:**
- `title`: Title of the report
- `report_type`: Type of the report
- `content`: Content of the report
- `created_at`: Creation timestamp
- `charts`: (Optional) List of charts included in the report
- `metrics`: (Optional) Dictionary of metrics included in the report

### Key Features

- **Multiple Report Types**: Generate different types of reports for different audiences
- **Customizable Content**: Customize report content based on requirements
- **Visual Elements**: Include charts, graphs, and tables
- **Progress Metrics**: Calculate and include progress metrics
- **Export Options**: Export to PDF, HTML, or Markdown formats
- **Scheduled Reports**: Generate reports on a schedule

## Integration with Other Components

The project management features integrate with other components of the TORONTO AI TEAM AGENT system:

### Integration with Task Estimation Framework

The project management features integrate with the Task Estimation Framework to incorporate accurate task duration estimates into Gantt charts and resource allocation.

```python
from app.orchestration.task_estimation import TaskEstimationFramework
from app.project_management.gantt_chart import GanttChartGenerator, Task as GanttTask

# Get estimated tasks from the Task Estimation Framework
estimation_framework = TaskEstimationFramework()
estimated_tasks = estimation_framework.get_all_tasks()

# Convert to Gantt chart tasks
gantt_tasks = []
for task in estimated_tasks:
    if task.estimate and task.estimate.estimated_start_time and task.estimate.estimated_completion_time:
        start_date = datetime.fromtimestamp(task.estimate.estimated_start_time).strftime("%Y-%m-%d")
        end_date = datetime.fromtimestamp(task.estimate.estimated_completion_time).strftime("%Y-%m-%d")
        progress = task.estimate.get_progress_percentage() or 0
        
        gantt_tasks.append(GanttTask(
            id=task.id,
            name=task.title,
            start_date=start_date,
            end_date=end_date,
            progress=progress,
            assignee=task.assigned_agent_id
        ))

# Create Gantt chart
generator = GanttChartGenerator()
gantt = generator.create_gantt_chart(
    title="Project Timeline",
    tasks=gantt_tasks
)
```

### Integration with AI Model Integrations

The project management features can leverage AI models for advanced capabilities:

```python
from app.models.adapters.claude_adapter import ClaudeAdapter
from app.project_management.resource_allocation import ResourceAllocationOptimizer

# Use Claude to analyze task requirements
claude_adapter = ClaudeAdapter(api_key="your_api_key")
task_description = "Implement a user authentication system with OAuth support"

analysis = claude_adapter.generate_response(
    prompt=f"Analyze the following task and list the required skills and estimated hours: {task_description}",
    max_tokens=500
)

# Parse the analysis to extract skills and hours
# (This would require more sophisticated parsing in a real implementation)
required_skills = ["python", "oauth", "security"]
estimated_hours = 15

# Create a task with the analyzed requirements
task = Task(
    id="auth_task",
    name="Implement Authentication",
    required_skills=required_skills,
    estimated_hours=estimated_hours
)

# Optimize resource allocation
optimizer = ResourceAllocationOptimizer()
assignments = optimizer.optimize_allocation(resources, [task])
```

## Usage Examples

### Example 1: Creating a Project Timeline

```python
from app.project_management.gantt_chart import GanttChartGenerator, Task, Dependency
import datetime

# Create a generator
generator = GanttChartGenerator()

# Define project phases
phases = [
    {"name": "Planning", "duration": 5},
    {"name": "Design", "duration": 10},
    {"name": "Implementation", "duration": 15},
    {"name": "Testing", "duration": 7},
    {"name": "Deployment", "duration": 3}
]

# Create tasks
tasks = []
dependencies = []
start_date = datetime.datetime.now()

for i, phase in enumerate(phases):
    # Calculate dates
    phase_start = start_date + datetime.timedelta(days=sum(p["duration"] for p in phases[:i]))
    phase_end = phase_start + datetime.timedelta(days=phase["duration"])
    
    # Create task
    task = Task(
        id=str(i+1),
        name=phase["name"],
        start_date=phase_start.strftime("%Y-%m-%d"),
        end_date=phase_end.strftime("%Y-%m-%d"),
        progress=0
    )
    tasks.append(task)
    
    # Create dependency (except for the first phase)
    if i > 0:
        dependencies.append(Dependency(
            from_task_id=str(i),
            to_task_id=str(i+1)
        ))

# Create a Gantt chart
gantt = generator.create_gantt_chart(
    title="Project Timeline",
    tasks=tasks,
    dependencies=dependencies
)

# Export to HTML
html = generator.export_to_html(gantt)
```

### Example 2: Optimizing Team Allocation

```python
from app.project_management.resource_allocation import ResourceAllocationOptimizer, Resource, Task, Assignment

# Create an optimizer
optimizer = ResourceAllocationOptimizer()

# Define team members
team = [
    Resource(id="dev1", name="Developer 1", skills=["python", "javascript", "react"], availability=1.0),
    Resource(id="dev2", name="Developer 2", skills=["python", "java", "backend"], availability=0.8),
    Resource(id="dev3", name="Developer 3", skills=["javascript", "react", "frontend"], availability=1.0),
    Resource(id="designer", name="Designer", skills=["ui", "ux", "figma"], availability=0.5),
    Resource(id="pm", name="Project Manager", skills=["management", "planning"], availability=0.3)
]

# Define project tasks
project_tasks = [
    Task(id="task1", name="Backend API Development", required_skills=["python", "backend"], estimated_hours=40),
    Task(id="task2", name="Frontend UI Implementation", required_skills=["javascript", "react"], estimated_hours=30),
    Task(id="task3", name="Database Schema Design", required_skills=["backend"], estimated_hours=15),
    Task(id="task4", name="UI/UX Design", required_skills=["ui", "ux"], estimated_hours=20),
    Task(id="task5", name="Project Planning", required_skills=["management"], estimated_hours=10)
]

# Optimize allocation
assignments = optimizer.optimize_allocation(team, project_tasks)

# Calculate workload
workload = optimizer.calculate_workload(team, project_tasks, assignments)

# Print assignments
for assignment in assignments:
    resource = next(r for r in team if r.id == assignment.resource_id)
    task = next(t for t in project_tasks if t.id == assignment.task_id)
    print(f"{resource.name} assigned to {task.name} ({assignment.allocation_percentage}%)")

# Print workload
for resource_id, hours in workload.items():
    resource = next(r for r in team if r.id == resource_id)
    print(f"{resource.name} workload: {hours} hours")
```

### Example 3: Generating Progress Reports

```python
from app.project_management.progress_reporting import ProgressReportGenerator, ReportType
from app.project_management.gantt_chart import Task as GanttTask
from app.project_management.resource_allocation import Resource, Assignment

# Create a generator
generator = ProgressReportGenerator()

# Define tasks with progress
tasks = [
    GanttTask(id="1", name="Task 1", start_date="2025-04-25", end_date="2025-04-30", progress=100),
    GanttTask(id="2", name="Task 2", start_date="2025-05-01", end_date="2025-05-05", progress=50),
    GanttTask(id="3", name="Task 3", start_date="2025-05-06", end_date="2025-05-10", progress=0)
]

# Define resources
resources = [
    Resource(id="1", name="Developer 1", skills=["python", "javascript"], availability=1.0),
    Resource(id="2", name="Developer 2", skills=["python", "java"], availability=0.5)
]

# Define assignments
assignments = [
    Assignment(resource_id="1", task_id="1", allocation_percentage=100),
    Assignment(resource_id="1", task_id="2", allocation_percentage=50),
    Assignment(resource_id="2", task_id="2", allocation_percentage=50),
    Assignment(resource_id="2", task_id="3", allocation_percentage=100)
]

# Generate reports for different stakeholders
reports = {
    "executive": generator.generate_report(
        title="Executive Summary",
        report_type=ReportType.SUMMARY,
        tasks=tasks,
        resources=resources,
        assignments=assignments
    ),
    "manager": generator.generate_report(
        title="Project Manager Report",
        report_type=ReportType.DETAILED,
        tasks=tasks,
        resources=resources,
        assignments=assignments
    ),
    "technical": generator.generate_report(
        title="Technical Progress Report",
        report_type=ReportType.TECHNICAL,
        tasks=tasks,
        resources=resources,
        assignments=assignments
    )
}

# Export reports to PDF
for name, report in reports.items():
    pdf_data = generator.export_to_pdf(report)
    with open(f"{name}_report.pdf", "wb") as f:
        f.write(pdf_data)
```
