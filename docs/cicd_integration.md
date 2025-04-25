# CI/CD Integration Documentation

This document provides comprehensive documentation for the CI/CD integration features in the TORONTO AI TEAM AGENT system.

## Overview

The CI/CD integration module enables agents to create, manage, and optimize CI/CD pipelines for automated testing and deployment. It supports multiple CI/CD platforms, including GitHub Actions and GitLab CI, with a unified interface for working with both.

## Key Components

### CICDPlatform

An enumeration of supported CI/CD platforms:

- `GITHUB_ACTIONS`: GitHub Actions CI/CD platform
- `GITLAB_CI`: GitLab CI/CD platform

### WorkflowTemplate

A base class for CI/CD workflow templates with the following key methods:

- `add_stage(name, runs_on)`: Add a stage to the workflow
- `add_job(name, display_name, stage=None)`: Add a job to a specific stage
- `to_yaml()`: Convert the workflow to YAML format
- `to_json()`: Convert the workflow to JSON format
- `save(file_path)`: Save the workflow to a file

### PipelineStage

Represents a stage in a CI/CD pipeline with the following key methods:

- `add_job(name, display_name)`: Add a job to the stage
- `to_dict()`: Convert the stage to a dictionary

### PipelineJob

Represents a job in a CI/CD pipeline with the following key methods:

- `add_step(name, run=None, uses=None, with_args=None)`: Add a step to the job
- `to_dict()`: Convert the job to a dictionary

### JobStep

Represents a step in a CI/CD job with the following key methods:

- `to_dict()`: Convert the step to a dictionary

### GitHubActionsIntegration

A class for integrating with GitHub Actions with the following key methods:

- `create_workflow(name, trigger_events)`: Create a new GitHub Actions workflow
- `get_workflow(workflow_id)`: Get a workflow by ID
- `list_workflows()`: List all workflows in the repository
- `run_workflow(workflow_id, ref="main")`: Run a workflow
- `get_workflow_run(run_id)`: Get a workflow run by ID
- `list_workflow_runs(workflow_id)`: List all runs for a workflow
- `cancel_workflow_run(run_id)`: Cancel a workflow run
- `get_workflow_run_logs(run_id)`: Get logs for a workflow run

### GitLabCIIntegration

A class for integrating with GitLab CI with the following key methods:

- `create_pipeline(name)`: Create a new GitLab CI pipeline
- `get_pipeline(pipeline_id)`: Get a pipeline by ID
- `list_pipelines()`: List all pipelines in the project
- `run_pipeline(pipeline_id, ref="main")`: Run a pipeline
- `get_pipeline_run(run_id)`: Get a pipeline run by ID
- `list_pipeline_runs(pipeline_id)`: List all runs for a pipeline
- `cancel_pipeline_run(run_id)`: Cancel a pipeline run
- `get_pipeline_run_logs(run_id)`: Get logs for a pipeline run

## Usage Examples

### Creating a GitHub Actions Workflow

```python
from app.cicd.cicd_integration import GitHubActionsIntegration, CICDPlatform

# Initialize the GitHub Actions integration
github_integration = GitHubActionsIntegration(
    repository="torontoai/TorontoAITeamAgent2",
    token="your_github_token"
)

# Create a workflow
workflow = github_integration.create_workflow(
    name="Build and Test",
    trigger_events=["push", "pull_request"]
)

# Add a build stage
build_stage = workflow.add_stage(
    name="build",
    runs_on="ubuntu-latest"
)

# Add a build job
build_job = build_stage.add_job(
    name="build_app",
    display_name="Build Application"
)

# Add steps to the job
build_job.add_step(
    name="checkout",
    uses="actions/checkout@v2"
)

build_job.add_step(
    name="setup_node",
    uses="actions/setup-node@v2",
    with_args={"node-version": "16"}
)

build_job.add_step(
    name="install",
    run="npm install"
)

build_job.add_step(
    name="build",
    run="npm run build"
)

# Add a test stage
test_stage = workflow.add_stage(
    name="test",
    runs_on="ubuntu-latest"
)

# Add a test job
test_job = test_stage.add_job(
    name="test_app",
    display_name="Test Application"
)

# Add steps to the job
test_job.add_step(
    name="checkout",
    uses="actions/checkout@v2"
)

test_job.add_step(
    name="setup_node",
    uses="actions/setup-node@v2",
    with_args={"node-version": "16"}
)

test_job.add_step(
    name="install",
    run="npm install"
)

test_job.add_step(
    name="test",
    run="npm test"
)

# Save the workflow to a file
workflow.save(".github/workflows/build-and-test.yml")

# Run the workflow
github_integration.run_workflow(workflow.id)
```

### Creating a GitLab CI Pipeline

```python
from app.cicd.cicd_integration import GitLabCIIntegration, CICDPlatform

# Initialize the GitLab CI integration
gitlab_integration = GitLabCIIntegration(
    project_id="12345",
    token="your_gitlab_token"
)

# Create a pipeline
pipeline = gitlab_integration.create_pipeline(
    name="Build, Test, and Deploy"
)

# Add stages
pipeline.add_stage(name="build")
pipeline.add_stage(name="test")
pipeline.add_stage(name="deploy")

# Add a build job
build_job = pipeline.add_job(
    name="build_app",
    stage="build",
    image="node:16-alpine"
)

# Add steps to the job
build_job.add_step(
    name="install",
    script="npm install"
)

build_job.add_step(
    name="build",
    script="npm run build"
)

# Add a test job
test_job = pipeline.add_job(
    name="test_app",
    stage="test",
    image="node:16-alpine"
)

# Add steps to the job
test_job.add_step(
    name="test",
    script="npm test"
)

# Add a deploy job
deploy_job = pipeline.add_job(
    name="deploy_app",
    stage="deploy",
    image="alpine:latest"
)

# Add steps to the job
deploy_job.add_step(
    name="deploy",
    script="./deploy.sh"
)

# Save the pipeline to a file
pipeline.save(".gitlab-ci.yml")

# Run the pipeline
gitlab_integration.run_pipeline(pipeline.id)
```

## Best Practices

1. **Use Environment Variables for Secrets**: Never hardcode tokens or secrets in your CI/CD configuration. Use environment variables or secret management services.

2. **Minimize Build Times**: Keep your CI/CD pipelines fast by optimizing build steps, using caching, and parallelizing jobs when possible.

3. **Implement Proper Testing**: Include unit tests, integration tests, and end-to-end tests in your CI/CD pipelines to ensure code quality.

4. **Use Matrix Builds**: For projects that need to be tested across multiple environments or configurations, use matrix builds to run tests in parallel.

5. **Implement Deployment Gates**: Use approval gates or manual triggers for production deployments to ensure proper review.

6. **Monitor Pipeline Performance**: Regularly review pipeline performance metrics to identify bottlenecks and optimize accordingly.

7. **Version Control Your CI/CD Configuration**: Keep your CI/CD configuration files in version control alongside your code.

## Troubleshooting

### Common Issues

1. **Authentication Failures**: Ensure your API tokens have the necessary permissions and haven't expired.

2. **Missing Dependencies**: Verify that all required dependencies are installed in your CI/CD environment.

3. **Configuration Errors**: Validate your YAML or JSON configuration files for syntax errors.

4. **Resource Constraints**: Check if your CI/CD jobs are failing due to memory or CPU constraints.

### Debugging Tips

1. **Enable Verbose Logging**: Set the log level to DEBUG for more detailed information.

2. **Inspect Job Logs**: Review the complete job logs to identify the exact point of failure.

3. **Local Testing**: Test your CI/CD configuration locally before pushing to the repository.

4. **Incremental Changes**: Make small, incremental changes to your CI/CD configuration to isolate issues.

## API Reference

For a complete API reference, see the inline documentation in the source code:

- `app/cicd/cicd_integration.py`
- `app/cicd/examples.py`
