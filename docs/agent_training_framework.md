# Agent Training Framework

This document provides a comprehensive guide to the Agent Training Framework in the TORONTO AI Team Agent Team AI system. The framework enables specialized training of agent roles using professional certification content, such as the Google Project Manager and IBM Product Manager certification courses.

## Overview

The Agent Training Framework is designed to enhance agent capabilities by incorporating specialized knowledge from professional certification content. The framework consists of four main components:

1. **Knowledge Integration Layer** - Processes certification content into a structured knowledge base
2. **Model Training Layer** - Trains agent models using the processed content
3. **Agent Adaptation Layer** - Integrates trained models into agent roles
4. **Training Orchestration Layer** - Coordinates the entire training process

![Agent Training Framework Architecture](../assets/agent_training_framework.png)

## Framework Components

### Knowledge Integration Layer

The Knowledge Integration Layer processes various types of certification content (PDF, Markdown, JSON, CSV) and integrates it into a structured knowledge base. This layer handles:

- Content type detection and processing
- Content chunking and structuring
- Metadata extraction and organization
- Content registry management

```python
from app.training.knowledge_integration import KnowledgeIntegrationLayer

# Initialize the layer
knowledge_layer = KnowledgeIntegrationLayer()

# Process certification content
result = knowledge_layer.process_certification_content({
    "content_path": "/path/to/google_pm_certification",
    "certification_name": "Google Project Manager Certification",
    "role": "project_manager"
})

# Get the content ID for further processing
content_id = result["content_id"]
```

### Model Training Layer

The Model Training Layer trains agent models using the processed certification content from the knowledge base. This layer handles:

- Content chunk collection and preparation
- Model training and evaluation
- Model storage and versioning
- Capability extraction and documentation

```python
from app.training.model_training import ModelTrainingLayer

# Initialize the layer
model_layer = ModelTrainingLayer()

# Train an agent model
result = model_layer.train_agent_model({
    "role": "project_manager",
    "content_ids": [content_id],
    "training_config": {
        "model_type": "specialized",
        "training_method": "fine_tuning"
    }
})

# Get the training ID for further processing
training_id = result["training_id"]
```

### Agent Adaptation Layer

The Agent Adaptation Layer integrates trained models into agent roles to enhance their capabilities with certification knowledge. This layer handles:

- Agent class identification and loading
- Model integration and adaptation
- Capability enhancement and extension
- Adaptation registry management

```python
from app.training.agent_adaptation import AgentAdaptationLayer

# Initialize the layer
adaptation_layer = AgentAdaptationLayer()

# Adapt an agent role
result = adaptation_layer.adapt_agent_role({
    "role": "project_manager",
    "training_id": training_id,
    "adaptation_config": {
        "method": "knowledge_integration",
        "integration_points": ["decision_making", "task_planning"]
    }
})

# Get the adaptation ID
adaptation_id = result["adaptation_id"]
```

### Training Orchestration Layer

The Training Orchestration Layer coordinates the entire agent training process, from content integration to model training and agent adaptation. This layer provides:

- End-to-end training orchestration
- Status tracking and monitoring
- Error handling and recovery
- Training registry management

```python
from app.training.orchestration import TrainingOrchestrationLayer

# Initialize the layer
orchestration_layer = TrainingOrchestrationLayer()

# Train an agent from certification content
result = orchestration_layer.train_agent_from_certification({
    "role": "project_manager",
    "content_path": "/path/to/google_pm_certification",
    "certification_name": "Google Project Manager Certification",
    "training_config": {
        "model_type": "specialized",
        "training_method": "fine_tuning"
    },
    "adaptation_config": {
        "method": "knowledge_integration",
        "integration_points": ["decision_making", "task_planning"]
    }
})

# Get the training ID
training_id = result["training_id"]

# Check training status
status_result = orchestration_layer.get_training_status({
    "training_id": training_id
})
```

## Training Project Manager and Product Manager Roles

### Project Manager Training

The Project Manager role can be enhanced with the Google Project Manager Certification content to improve capabilities in:

- Project planning and scheduling
- Resource allocation and management
- Risk assessment and mitigation
- Stakeholder communication
- Team coordination
- Progress tracking and reporting

#### Training Process

1. Organize the Google Project Manager Certification content in a structured directory
2. Use the Training Orchestration Layer to process the content and train the Project Manager role
3. Verify the enhanced capabilities through testing and evaluation

```python
# Train Project Manager with Google PM Certification
result = orchestration_layer.train_agent_from_certification({
    "role": "project_manager",
    "content_path": "/path/to/google_pm_certification",
    "certification_name": "Google Project Manager Certification",
    "training_config": {
        "model_type": "specialized",
        "training_method": "fine_tuning"
    },
    "adaptation_config": {
        "method": "knowledge_integration",
        "integration_points": ["decision_making", "task_planning", "communication", "artifact_generation"]
    }
})
```

### Product Manager Training

The Product Manager role can be enhanced with the IBM Product Manager Certification content to improve capabilities in:

- Market research and analysis
- Product strategy development
- Feature prioritization
- Roadmap planning
- User story creation
- Product lifecycle management

#### Training Process

1. Organize the IBM Product Manager Certification content in a structured directory
2. Use the Training Orchestration Layer to process the content and train the Product Manager role
3. Verify the enhanced capabilities through testing and evaluation

```python
# Train Product Manager with IBM PM Certification
result = orchestration_layer.train_agent_from_certification({
    "role": "product_manager",
    "content_path": "/path/to/ibm_pm_certification",
    "certification_name": "IBM Product Manager Certification",
    "training_config": {
        "model_type": "specialized",
        "training_method": "fine_tuning"
    },
    "adaptation_config": {
        "method": "knowledge_integration",
        "integration_points": ["decision_making", "market_analysis", "feature_prioritization", "roadmap_planning"]
    }
})
```

## Content Organization

To effectively train agent roles, certification content should be organized in a structured format:

### Directory Structure

```
/path/to/certification/
├── module_1/
│   ├── lesson_1.md
│   ├── lesson_2.md
│   └── resources/
│       ├── resource_1.pdf
│       └── resource_2.json
├── module_2/
│   ├── lesson_1.md
│   └── lesson_2.md
└── metadata.json
```

### Metadata Format

The `metadata.json` file should contain information about the certification:

```json
{
  "name": "Google Project Manager Certification",
  "provider": "Google",
  "description": "Comprehensive project management certification covering all aspects of project planning, execution, and monitoring.",
  "modules": [
    {
      "name": "Module 1: Project Initiation",
      "lessons": [
        "Lesson 1: Project Charter",
        "Lesson 2: Stakeholder Analysis"
      ]
    },
    {
      "name": "Module 2: Project Planning",
      "lessons": [
        "Lesson 1: Work Breakdown Structure",
        "Lesson 2: Risk Management"
      ]
    }
  ]
}
```

## Extending the Framework

The Agent Training Framework is designed to be extensible, allowing for training of additional agent roles beyond Project Manager and Product Manager. To extend the framework:

1. Organize certification content for the new role
2. Use the Training Orchestration Layer to process the content and train the role
3. Implement any role-specific adaptation methods if needed

```python
# Train a new role
result = orchestration_layer.train_agent_from_certification({
    "role": "new_role",
    "content_path": "/path/to/new_role_certification",
    "certification_name": "New Role Certification",
    "training_config": {
        "model_type": "specialized",
        "training_method": "fine_tuning"
    },
    "adaptation_config": {
        "method": "knowledge_integration",
        "integration_points": ["decision_making", "specialized_task"]
    }
})
```

## API Requirements

The Agent Training Framework requires API access to language models for training and adaptation. The following API keys should be configured:

- OpenAI API Key (for GPT models)
- Anthropic API Key (for Claude models)
- DeepSeek API Key (for DeepSeek models)
- Google API Key (for Gemini models)

See the [API Integration Guide](api_integration_guide.md) for detailed instructions on configuring API keys.

## Best Practices

### Content Preparation

- Break certification content into modular, focused lessons
- Include practical examples and exercises
- Provide clear metadata for each content piece
- Use a consistent format for similar content types

### Training Configuration

- Start with default training configurations
- Adjust parameters based on evaluation results
- Use specialized training methods for complex capabilities
- Document successful configurations for future reference

### Evaluation

- Test enhanced agent roles with realistic scenarios
- Compare performance before and after training
- Gather feedback from human users
- Iterate on training based on evaluation results

## Troubleshooting

### Common Issues

- **Content Processing Failures**: Ensure content is in a supported format and properly structured
- **Training Failures**: Check API configurations and ensure sufficient resources
- **Adaptation Failures**: Verify that the agent role class exists and is properly implemented
- **Performance Issues**: Adjust training parameters and content organization

### Logging

The framework includes comprehensive logging to help diagnose issues:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Conclusion

The Agent Training Framework provides a powerful system for enhancing agent roles with specialized knowledge from professional certification content. By following this guide, you can train the Project Manager and Product Manager roles using Google and IBM certification content, and extend the framework to train additional roles in the future.
