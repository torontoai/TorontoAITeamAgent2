# Coursera API Integration for Agent Training

## Overview

The Coursera API Integration module provides a sophisticated knowledge pipeline for training agent roles using specialized content from Coursera. This integration allows the TORONTO AI TEAM AGENT system to access high-quality educational content to enhance agent capabilities across various roles.

## Key Features

- **OAuth 2.0 Authentication**: Secure access to Coursera APIs with token management and caching
- **Robust API Client**: Handles rate limiting, error recovery, and connection management
- **Content Extraction**: Processes course materials, lectures, readings, and quizzes into structured knowledge
- **Role-Specific Knowledge**: Targeted queries for different agent roles (Project Manager, Business Analyst, Data Scientist, etc.)
- **Vector Database Integration**: Seamless connection with the existing vector-based knowledge system
- **Training Pipeline**: Complete workflow from course discovery to agent knowledge integration

## Architecture

The Coursera API integration consists of several components:

1. **CourseraConfig**: Configuration management for API access
2. **CourseraTokenManager**: Handles OAuth token acquisition and caching
3. **CourseraAPIClient**: Core client for interacting with Coursera APIs
4. **CourseraContentExtractor**: Extracts and processes content from courses
5. **CourseraKnowledgePipeline**: Processes content for agent training
6. **CourseraTrainingIntegration**: Integrates with the existing training system

## Usage

### Basic Setup

```python
from app.training.coursera_integration import initialize_coursera_integration

# Initialize the knowledge pipeline
knowledge_pipeline = initialize_coursera_integration(
    api_key="your_api_key",
    api_secret="your_api_secret",
    business_id="your_business_id",  # Optional
    token_cache_path="/path/to/token/cache.json"  # Optional
)
```

### Training an Agent Role

```python
from app.training.coursera_training import CourseraTrainingIntegration
from app.training.config import TrainingConfig
from app.training.vector_db import VectorDBManager
from app.training.knowledge_integration import KnowledgeIntegrator

# Initialize components
training_config = TrainingConfig()
vector_db_manager = VectorDBManager(training_config)
knowledge_integrator = KnowledgeIntegrator(training_config, vector_db_manager)

# Create training integration
coursera_training = CourseraTrainingIntegration(
    training_config=training_config,
    vector_db_manager=vector_db_manager,
    knowledge_integrator=knowledge_integrator,
    coursera_api_key="your_api_key",
    coursera_api_secret="your_api_secret",
    coursera_business_id="your_business_id"  # Optional
)

# Train a specific role
training_summary = coursera_training.train_agent_role(
    role="project_manager",
    limit_per_query=3
)

# Train multiple roles
overall_summary = coursera_training.train_all_agent_roles(
    roles=["project_manager", "business_analyst", "data_scientist"],
    limit_per_query=3
)
```

## Supported Agent Roles

The system includes pre-defined queries for the following roles:

- **Project Manager**: Project planning, agile methodologies, risk management, etc.
- **Business Analyst**: Requirements gathering, process modeling, stakeholder analysis, etc.
- **Data Scientist**: Machine learning, statistical analysis, data visualization, etc.
- **Software Engineer**: Software development, architecture, testing, DevOps, etc.
- **UX Designer**: User experience, interface design, usability testing, etc.
- **Product Manager**: Product strategy, roadmap planning, market research, etc.

Custom roles can be defined by providing specific queries during the training process.

## Integration with Existing Systems

The Coursera API integration connects with:

1. **Vector Database**: Stores processed knowledge chunks for efficient retrieval
2. **Knowledge Integration Framework**: Combines Coursera content with existing knowledge
3. **Agent Adaptation Layer**: Applies role-specific knowledge to agent behavior
4. **Human-AI Collaboration Framework**: Enables knowledge sharing between humans and AI agents

## Error Handling

The system includes comprehensive error handling for:

- Authentication failures
- Rate limiting
- Network issues
- Content processing errors
- Integration failures

All errors are logged with appropriate context for troubleshooting.

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `api_key` | Coursera API key | Required |
| `api_secret` | Coursera API secret | Required |
| `business_id` | Coursera Business ID | Optional |
| `base_url` | Base URL for API requests | https://api.coursera.com |
| `token_url` | URL for token requests | https://api.coursera.com/oauth2/client_credentials/token |
| `max_retries` | Maximum number of retries for failed requests | 3 |
| `timeout` | Request timeout in seconds | 30 |
| `token_cache_path` | Path to cache access tokens | None |

## Limitations

- Requires a valid Coursera Business/Campus/Government account
- API access is subject to Coursera's rate limits and terms of service
- Some course content may not be available through the API
- Processing large courses may require significant computational resources

## Future Enhancements

- Support for additional content types (videos, assignments, etc.)
- Enhanced metadata extraction for better knowledge integration
- Real-time content updates based on course changes
- Personalized learning paths for agent roles
- Integration with additional learning platforms
