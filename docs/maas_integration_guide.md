# Multi-agent Architecture Search (MaAS) Integration Guide

## Overview

The Multi-agent Architecture Search (MaAS) module is a powerful addition to the TORONTO AI TEAM AGENT system that enables dynamic discovery and optimization of agent team architectures based on task requirements. This guide provides a comprehensive overview of the MaAS integration, its components, and how to use it effectively.

## Key Features

- **Dynamic Architecture Discovery**: Automatically discover optimal agent architectures for specific tasks
- **Agentic Supernet**: A neural architecture search inspired approach to sampling and optimizing agent architectures
- **Performance Evaluation**: Comprehensive metrics and evaluation mechanisms for comparing architectures
- **Visualization Tools**: Interactive and static visualizations for understanding agent architectures
- **Framework Integration**: Seamless integration with both AutoGen and A2A frameworks
- **Continuous Learning**: Feedback loop for improving architecture selection over time

## Architecture

The MaAS integration consists of several key components:

### Core Components

1. **Models**: Data models for representing architectures, agents, connections, and evaluation results
2. **Templates**: Predefined architecture templates that serve as starting points for architecture search
3. **Agentic Supernet**: The central component that samples and optimizes architectures
   - Architecture Sampler: Handles the sampling of architectures from templates or random generation
   - Supernet Controller: Learns to optimize architecture selection based on performance feedback

### Evaluation System

1. **Metrics Calculator**: Calculates and normalizes performance metrics from workflow execution results
2. **Fitness Function**: Converts normalized metrics into a single fitness score
3. **Architecture Evaluator**: Orchestrates the evaluation process and stores evaluation history

### Visualization Components

1. **Architecture Visualizer**: Creates interactive and static visualizations of agent architectures
2. **Performance Visualizer**: Generates visualizations of performance metrics for different architectures
3. **Search Progress Visualizer**: Tracks and visualizes the progress of architecture search over time

### Integration Layer

1. **AutoGen Integration**: Adapter for creating agent teams using the Microsoft AutoGen framework
2. **A2A Integration**: Adapter for creating agent teams using the A2A protocol
3. **Integration Manager**: Unified interface for working with both frameworks

## Usage Examples

### Basic Usage

```python
from app.orchestration.maas.models import TaskModel, AgentCapability
from app.orchestration.maas.integration import MaaSIntegrationManager

# Create a task
task = TaskModel(
    id="task_001",
    name="Research Task",
    description="Research the latest developments in AI",
    domain="research",
    required_capabilities=[
        AgentCapability.RESEARCH,
        AgentCapability.SUMMARIZATION,
        AgentCapability.PLANNING
    ],
    complexity_score=0.7
)

# Initialize the integration manager
integration_manager = MaaSIntegrationManager()

# Create an agent team using AutoGen
autogen_config = integration_manager.create_agent_team(
    task=task,
    framework="autogen"
)

# Execute the workflow with AutoGen
# ... (AutoGen-specific code to execute the workflow)

# Alternatively, create an agent team using A2A
a2a_config = integration_manager.create_agent_team(
    task=task,
    framework="a2a"
)

# Execute the workflow with A2A
# ... (A2A-specific code to execute the workflow)
```

### Advanced Usage with Feedback Loop

```python
from app.orchestration.maas.models import TaskModel, AgentCapability
from app.orchestration.maas.integration import MaaSIntegrationManager
from app.orchestration.maas.supernet.agentic_supernet import AgenticSupernet
from app.orchestration.maas.evaluation.evaluator import ArchitectureEvaluator

# Initialize components
supernet = AgenticSupernet()
evaluator = ArchitectureEvaluator()
integration_manager = MaaSIntegrationManager(supernet, evaluator)

# Create a task
task = TaskModel(
    id="task_002",
    name="Code Generation Task",
    description="Generate a Python script for data analysis",
    domain="coding",
    required_capabilities=[
        AgentCapability.CODE_GENERATION,
        AgentCapability.PLANNING,
        AgentCapability.QUALITY_ASSESSMENT
    ],
    complexity_score=0.8
)

# Sample multiple architectures and evaluate them
results = []
for i in range(5):
    # Sample an architecture
    architecture = supernet.sample_architecture(task)
    
    # Create agent team configuration
    config = integration_manager.create_agent_team(
        task=task,
        framework="autogen",
        architecture=architecture
    )
    
    # Execute the workflow and collect metrics
    # ... (code to execute workflow and collect metrics)
    metrics = {
        "execution_time": 120.5,
        "success": 1.0,
        "quality_score": 0.85,
        # ... other metrics
    }
    
    # Evaluate the architecture
    evaluation_result = evaluator.evaluate_architecture(
        architecture=architecture,
        task=task,
        metrics=metrics
    )
    
    results.append(evaluation_result)
    
    # Provide feedback to the supernet
    supernet.update_with_feedback(architecture, evaluation_result.fitness)

# Generate evaluation report
report = evaluator.generate_evaluation_report(results)

# Visualize the results
from app.orchestration.maas.visualization.performance_visualizer import PerformanceVisualizer
visualizer = PerformanceVisualizer(output_format="html")
visualization = visualizer.visualize_comparison(results, output_path="performance_comparison")
```

## Customization

### Creating Custom Architecture Templates

You can create custom architecture templates by extending the `architecture_templates.py` file:

```python
from app.orchestration.maas.models import ArchitectureTemplate, AgentRole, AgentCapability

# Define a custom template
custom_template = ArchitectureTemplate(
    name="Custom Hierarchical Architecture",
    description="A custom hierarchical architecture with specialized agents",
    agent_roles=[
        AgentRole.COORDINATOR,
        AgentRole.PLANNER,
        AgentRole.EXECUTOR,
        AgentRole.RESEARCHER,
        AgentRole.EVALUATOR
    ],
    connection_pattern="hierarchical",
    min_agents=5,
    max_agents=10,
    default_capabilities={
        AgentRole.COORDINATOR: [AgentCapability.PLANNING, AgentCapability.COORDINATION],
        AgentRole.PLANNER: [AgentCapability.PLANNING, AgentCapability.REASONING],
        AgentRole.EXECUTOR: [AgentCapability.CODE_EXECUTION, AgentCapability.TOOL_USE],
        AgentRole.RESEARCHER: [AgentCapability.RESEARCH, AgentCapability.INFORMATION_RETRIEVAL],
        AgentRole.EVALUATOR: [AgentCapability.QUALITY_ASSESSMENT, AgentCapability.EVALUATION]
    }
)

# Register the template
from app.orchestration.maas.templates.architecture_templates import register_template
register_template(custom_template)
```

### Customizing Evaluation Metrics

You can customize the evaluation metrics by modifying the `metrics.py` file or by providing custom metrics when evaluating architectures:

```python
from app.orchestration.maas.evaluation.metrics import MetricsCalculator

# Create a custom metrics calculator
class CustomMetricsCalculator(MetricsCalculator):
    def calculate_metrics(self, results, task, architecture):
        # Get base metrics
        metrics = super().calculate_metrics(results, task, architecture)
        
        # Add custom metrics
        metrics["custom_metric_1"] = self._calculate_custom_metric_1(results)
        metrics["custom_metric_2"] = self._calculate_custom_metric_2(results, architecture)
        
        return metrics
    
    def _calculate_custom_metric_1(self, results):
        # Custom metric calculation logic
        return 0.75
    
    def _calculate_custom_metric_2(self, results, architecture):
        # Another custom metric calculation logic
        return 0.92

# Use the custom metrics calculator
custom_calculator = CustomMetricsCalculator()
metrics = custom_calculator.calculate_metrics(results, task, architecture)
```

## Integration with Existing Systems

The MaAS integration is designed to work seamlessly with the existing TORONTO AI TEAM AGENT system. It integrates with:

1. **AutoGen Framework**: Through the `autogen_adapter.py` module
2. **A2A Protocol**: Through the `a2a_adapter.py` module
3. **Orchestration System**: Through the `orchestration_service.py` module

## Performance Considerations

- **Architecture Sampling**: The architecture sampling process is computationally efficient and can be performed in real-time
- **Evaluation**: The evaluation process requires executing workflows, which can be time-consuming
- **Visualization**: Interactive visualizations may be resource-intensive for very large architectures

## Best Practices

1. **Start with Templates**: Use predefined templates as starting points for architecture search
2. **Iterative Refinement**: Use the feedback loop to iteratively refine architectures
3. **Task-Specific Optimization**: Optimize architectures for specific task domains
4. **Balanced Metrics**: Use a balanced set of metrics that capture different aspects of performance
5. **Visualization**: Use visualizations to understand and compare architectures

## Troubleshooting

### Common Issues

1. **Architecture Sampling Failures**: Ensure that the task has valid required capabilities and that the search space is properly configured
2. **Integration Errors**: Check that the framework adapters are properly configured and that the required dependencies are installed
3. **Visualization Errors**: Ensure that all visualization dependencies (matplotlib, plotly, networkx) are installed

### Debugging

The MaAS integration includes comprehensive logging that can help with debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app.orchestration.maas")
```

## Future Directions

The MaAS integration is designed to be extensible and can be enhanced in several ways:

1. **Advanced Search Algorithms**: Implementing more sophisticated architecture search algorithms
2. **Meta-Learning**: Learning from past tasks to improve architecture selection for new tasks
3. **Distributed Evaluation**: Parallelizing the evaluation of architectures for faster search
4. **Interactive Design**: Adding tools for interactive architecture design and refinement
5. **Integration with More Frameworks**: Supporting additional agent frameworks beyond AutoGen and A2A

## Conclusion

The Multi-agent Architecture Search (MaAS) integration provides a powerful mechanism for discovering and optimizing agent team architectures. By leveraging the principles of neural architecture search and applying them to multi-agent systems, MaAS enables the TORONTO AI TEAM AGENT system to dynamically adapt to different tasks and continuously improve its performance over time.
