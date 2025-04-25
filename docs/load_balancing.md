# Load Balancing System Documentation

This document provides comprehensive documentation for the Load Balancing System in the TORONTO AI TEAM AGENT system.

## Overview

The Load Balancing System enables automatic distribution of work across multiple agents of the same role, optimizing resource utilization and improving overall system performance. It intelligently assigns tasks based on agent capabilities, current workload, and task requirements, ensuring efficient execution of complex projects.

## Key Components

### LoadBalancingSystem

The central class that manages the load balancing system with the following key methods:

- `register_agent(agent)`: Register an agent with the load balancing system
- `unregister_agent(agent_id)`: Unregister an agent from the load balancing system
- `get_agents()`: Get all registered agents
- `get_agents_by_role(role)`: Get agents by role
- `assign_task(task)`: Assign a task to the most suitable agent
- `assign_task_to_agent(task, agent)`: Assign a task to a specific agent
- `complete_task(task_id)`: Mark a task as completed
- `get_task(task_id)`: Get a task by ID
- `get_agent_workload(agent_id)`: Get the workload of an agent
- `set_strategy(strategy)`: Set the load balancing strategy
- `reset()`: Reset the load balancing system

### LoadBalancer

A class that implements different load balancing algorithms with the following key methods:

- `select_agent(agents, task)`: Select the most suitable agent for a task
- `update_agent_workload(agent_id, task)`: Update the workload of an agent
- `get_agent_workload(agent_id)`: Get the workload of an agent

### TaskQueue

A class that manages the task queue with the following key methods:

- `add_task(task)`: Add a task to the queue
- `remove_task(task_id)`: Remove a task from the queue
- `get_task(task_id)`: Get a task by ID
- `get_tasks_by_status(status)`: Get tasks by status
- `get_tasks_by_priority(priority)`: Get tasks by priority
- `get_tasks_by_agent(agent_id)`: Get tasks assigned to an agent

### Agent

A class representing an agent in the system with the following key attributes:

- `id`: The unique identifier of the agent
- `name`: The name of the agent
- `role`: The role of the agent (e.g., DEVELOPER, PROJECT_MANAGER)
- `capabilities`: The capabilities of the agent (e.g., programming languages, skills)
- `status`: The current status of the agent (e.g., AVAILABLE, BUSY)

### Task

A class representing a task in the system with the following key attributes:

- `id`: The unique identifier of the task
- `name`: The name of the task
- `description`: The description of the task
- `required_capabilities`: The capabilities required to complete the task
- `priority`: The priority of the task (e.g., HIGH, MEDIUM, LOW)
- `status`: The current status of the task (e.g., PENDING, ASSIGNED, COMPLETED)
- `assigned_agent_id`: The ID of the agent assigned to the task
- `estimated_duration`: The estimated duration of the task in minutes
- `actual_duration`: The actual duration of the task in minutes
- `dependencies`: The IDs of tasks that must be completed before this task

### AgentRole

An enumeration of agent roles:

- `DEVELOPER`: Developer agent role
- `PROJECT_MANAGER`: Project manager agent role
- `PRODUCT_MANAGER`: Product manager agent role
- `DESIGNER`: Designer agent role
- `TESTER`: Tester agent role
- `DEVOPS`: DevOps agent role

### TaskPriority

An enumeration of task priorities:

- `CRITICAL`: Critical priority
- `HIGH`: High priority
- `MEDIUM`: Medium priority
- `LOW`: Low priority

### TaskStatus

An enumeration of task statuses:

- `PENDING`: Task is pending assignment
- `ASSIGNED`: Task is assigned to an agent
- `IN_PROGRESS`: Task is in progress
- `COMPLETED`: Task is completed
- `FAILED`: Task has failed
- `BLOCKED`: Task is blocked by dependencies

### LoadBalancingStrategy

An enumeration of load balancing strategies:

- `ROUND_ROBIN`: Distribute tasks in a circular order
- `LEAST_CONNECTIONS`: Assign tasks to the agent with the fewest active tasks
- `WEIGHTED`: Assign tasks based on agent weights
- `CAPABILITY_BASED`: Assign tasks based on agent capabilities
- `RESPONSE_TIME`: Assign tasks based on agent response time
- `ADAPTIVE`: Dynamically adjust strategy based on system performance

## Usage Examples

### Basic Load Balancing

```python
from app.load_balancing.load_balancing import (
    LoadBalancingSystem, Agent, Task, AgentRole, 
    TaskPriority, TaskStatus, LoadBalancingStrategy
)

# Initialize the load balancing system
load_balancing_system = LoadBalancingSystem()

# Register agents
developer1 = Agent(
    id="dev1",
    name="Developer 1",
    role=AgentRole.DEVELOPER,
    capabilities=["python", "javascript"]
)

developer2 = Agent(
    id="dev2",
    name="Developer 2",
    role=AgentRole.DEVELOPER,
    capabilities=["java", "python"]
)

project_manager = Agent(
    id="pm1",
    name="Project Manager 1",
    role=AgentRole.PROJECT_MANAGER,
    capabilities=["planning", "coordination"]
)

load_balancing_system.register_agent(developer1)
load_balancing_system.register_agent(developer2)
load_balancing_system.register_agent(project_manager)

# Create tasks
task1 = Task(
    id="task1",
    name="Implement Feature X",
    description="Implement Feature X using Python",
    required_capabilities=["python"],
    priority=TaskPriority.HIGH,
    estimated_duration=120  # minutes
)

task2 = Task(
    id="task2",
    name="Implement Feature Y",
    description="Implement Feature Y using Java",
    required_capabilities=["java"],
    priority=TaskPriority.MEDIUM,
    estimated_duration=90  # minutes
)

task3 = Task(
    id="task3",
    name="Create Project Plan",
    description="Create a project plan for the next sprint",
    required_capabilities=["planning"],
    priority=TaskPriority.HIGH,
    estimated_duration=60  # minutes
)

# Assign tasks
assigned_agent1 = load_balancing_system.assign_task(task1)
assigned_agent2 = load_balancing_system.assign_task(task2)
assigned_agent3 = load_balancing_system.assign_task(task3)

print(f"Task 1 assigned to: {assigned_agent1.name}")
print(f"Task 2 assigned to: {assigned_agent2.name}")
print(f"Task 3 assigned to: {assigned_agent3.name}")

# Complete a task
load_balancing_system.complete_task(task1.id)

# Get agent workload
dev1_workload = load_balancing_system.get_agent_workload(developer1.id)
print(f"Developer 1 active tasks: {dev1_workload.active_tasks}")
print(f"Developer 1 completed tasks: {dev1_workload.completed_tasks}")
```

### Advanced Load Balancing with Different Strategies

```python
from app.load_balancing.load_balancing import (
    LoadBalancingSystem, Agent, Task, AgentRole, 
    TaskPriority, TaskStatus, LoadBalancingStrategy
)

# Initialize the load balancing system
load_balancing_system = LoadBalancingSystem()

# Register multiple developer agents
developers = []
for i in range(1, 6):
    developer = Agent(
        id=f"dev{i}",
        name=f"Developer {i}",
        role=AgentRole.DEVELOPER,
        capabilities=["python", "javascript"] if i % 2 == 0 else ["java", "python"]
    )
    developers.append(developer)
    load_balancing_system.register_agent(developer)

# Create multiple tasks
tasks = []
for i in range(1, 11):
    task = Task(
        id=f"task{i}",
        name=f"Task {i}",
        description=f"Task {i} description",
        required_capabilities=["python"],
        priority=TaskPriority.MEDIUM,
        estimated_duration=60  # minutes
    )
    tasks.append(task)

# Test round-robin strategy
load_balancing_system.set_strategy(LoadBalancingStrategy.ROUND_ROBIN)
print("Using Round Robin strategy:")

assigned_agents = []
for task in tasks[:5]:
    agent = load_balancing_system.assign_task(task)
    assigned_agents.append(agent.id)
    print(f"Task {task.id} assigned to: {agent.name}")

# Reset tasks and agent workloads
for task in tasks[:5]:
    task.status = TaskStatus.PENDING
    task.assigned_agent_id = None

load_balancing_system.reset()

# Test least-connections strategy
load_balancing_system.set_strategy(LoadBalancingStrategy.LEAST_CONNECTIONS)
print("\nUsing Least Connections strategy:")

# Assign one task to the first developer
load_balancing_system.assign_task_to_agent(tasks[0], developers[0])
print(f"Task {tasks[0].id} assigned to: {developers[0].name}")

# Now assign the rest of the tasks
for task in tasks[1:5]:
    agent = load_balancing_system.assign_task(task)
    print(f"Task {task.id} assigned to: {agent.name}")

# Reset tasks and agent workloads
for task in tasks[:5]:
    task.status = TaskStatus.PENDING
    task.assigned_agent_id = None

load_balancing_system.reset()

# Test capability-based strategy
load_balancing_system.set_strategy(LoadBalancingStrategy.CAPABILITY_BASED)
print("\nUsing Capability Based strategy:")

# Create tasks with different capability requirements
java_task = Task(
    id="java_task",
    name="Java Task",
    description="Task requiring Java",
    required_capabilities=["java"],
    priority=TaskPriority.HIGH,
    estimated_duration=90  # minutes
)

javascript_task = Task(
    id="javascript_task",
    name="JavaScript Task",
    description="Task requiring JavaScript",
    required_capabilities=["javascript"],
    priority=TaskPriority.HIGH,
    estimated_duration=90  # minutes
)

# Assign tasks
java_agent = load_balancing_system.assign_task(java_task)
javascript_agent = load_balancing_system.assign_task(javascript_task)

print(f"Java task assigned to: {java_agent.name}")
print(f"JavaScript task assigned to: {javascript_agent.name}")
```

## Load Balancing Strategies

### Round Robin

The Round Robin strategy distributes tasks in a circular order, ensuring that each agent receives an equal number of tasks. This strategy is simple and works well when all agents have similar capabilities and performance characteristics.

### Least Connections

The Least Connections strategy assigns tasks to the agent with the fewest active tasks. This strategy helps balance the workload across agents and prevents any single agent from becoming overloaded.

### Weighted

The Weighted strategy assigns tasks based on agent weights, allowing more capable or higher-performing agents to receive more tasks. This strategy is useful when agents have different performance characteristics.

### Capability Based

The Capability Based strategy assigns tasks based on agent capabilities, ensuring that tasks are assigned to agents with the required skills. This strategy is useful when tasks require specific expertise.

### Response Time

The Response Time strategy assigns tasks based on agent response time, preferring agents that complete tasks more quickly. This strategy helps optimize overall system performance.

### Adaptive

The Adaptive strategy dynamically adjusts the load balancing approach based on system performance metrics. This strategy can combine elements of other strategies to optimize performance in changing conditions.

## Task Scheduling and Dependencies

The Load Balancing System supports task dependencies, allowing you to define tasks that must be completed before other tasks can start. This enables complex workflow management and ensures that tasks are executed in the correct order.

```python
# Create tasks with dependencies
task1 = Task(
    id="task1",
    name="Setup Database",
    description="Set up the database schema",
    required_capabilities=["database"],
    priority=TaskPriority.HIGH,
    estimated_duration=60  # minutes
)

task2 = Task(
    id="task2",
    name="Implement API",
    description="Implement the REST API",
    required_capabilities=["python"],
    priority=TaskPriority.HIGH,
    estimated_duration=120,  # minutes
    dependencies=["task1"]  # This task depends on task1
)

task3 = Task(
    id="task3",
    name="Implement Frontend",
    description="Implement the frontend UI",
    required_capabilities=["javascript"],
    priority=TaskPriority.MEDIUM,
    estimated_duration=180,  # minutes
    dependencies=["task2"]  # This task depends on task2
)

# Assign tasks
# task1 will be assigned immediately since it has no dependencies
assigned_agent1 = load_balancing_system.assign_task(task1)

# task2 will be blocked until task1 is completed
assigned_agent2 = load_balancing_system.assign_task(task2)
if assigned_agent2:
    print(f"Task 2 assigned to: {assigned_agent2.name}")
else:
    print("Task 2 is blocked by dependencies")

# Complete task1
load_balancing_system.complete_task(task1.id)

# Now task2 can be assigned
assigned_agent2 = load_balancing_system.assign_task(task2)
print(f"Task 2 assigned to: {assigned_agent2.name}")
```

## Performance Monitoring and Optimization

The Load Balancing System includes performance monitoring capabilities to track agent performance and optimize task assignment. You can use these metrics to identify bottlenecks and improve system efficiency.

```python
# Get performance metrics for all agents
for agent in load_balancing_system.get_agents():
    workload = load_balancing_system.get_agent_workload(agent.id)
    
    print(f"Agent: {agent.name}")
    print(f"  Active Tasks: {workload.active_tasks}")
    print(f"  Completed Tasks: {workload.completed_tasks}")
    print(f"  Average Task Duration: {workload.average_task_duration} minutes")
    print(f"  Task Completion Rate: {workload.task_completion_rate} tasks/hour")

# Get system-wide performance metrics
system_metrics = load_balancing_system.get_system_metrics()
print(f"Total Tasks: {system_metrics.total_tasks}")
print(f"Completed Tasks: {system_metrics.completed_tasks}")
print(f"Average Task Duration: {system_metrics.average_task_duration} minutes")
print(f"System Throughput: {system_metrics.throughput} tasks/hour")
```

## Best Practices

1. **Choose the Right Strategy**: Select a load balancing strategy that matches your workload characteristics and agent capabilities.

2. **Monitor Performance**: Regularly monitor agent and system performance metrics to identify bottlenecks and optimize task assignment.

3. **Balance Specialization and Flexibility**: While specializing agents for specific tasks can improve efficiency, maintaining some flexibility ensures the system can handle varying workloads.

4. **Implement Proper Error Handling**: Ensure that the system can handle agent failures and task execution errors gracefully.

5. **Consider Task Dependencies**: When designing workflows, carefully consider task dependencies to minimize blocking and maximize parallelism.

6. **Optimize Task Granularity**: Break down large tasks into smaller, more manageable units to improve load balancing and reduce the impact of individual task failures.

7. **Implement Timeout Handling**: Set appropriate timeouts for tasks to prevent stuck tasks from blocking the system.

8. **Scale Horizontally**: Add more agents of the same role to handle increased workload rather than overloading existing agents.

## Troubleshooting

### Common Issues

1. **Unbalanced Workload**: If some agents are consistently overloaded while others are underutilized, consider changing the load balancing strategy or adjusting agent capabilities.

2. **Blocked Tasks**: If tasks are frequently blocked by dependencies, review your workflow design to minimize dependencies and maximize parallelism.

3. **Slow Task Execution**: If tasks are taking longer than expected to complete, investigate agent performance issues or consider optimizing task implementation.

4. **Resource Contention**: If agents are competing for shared resources, consider implementing resource allocation mechanisms or adjusting the load balancing strategy.

### Debugging Tips

1. **Enable Detailed Logging**: Set the log level to DEBUG for more detailed information about task assignment and execution.

2. **Monitor Agent Metrics**: Regularly review agent performance metrics to identify issues early.

3. **Test with Simplified Workflows**: When troubleshooting complex issues, test with simplified workflows to isolate the problem.

4. **Validate Task Dependencies**: Ensure that task dependencies are correctly defined and that there are no circular dependencies.

## API Reference

For a complete API reference, see the inline documentation in the source code:

- `app/load_balancing/load_balancing.py`
