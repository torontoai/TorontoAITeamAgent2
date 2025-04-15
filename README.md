# Toronto AI Team Agent

A multi-agent system for collaborative AI teamwork, featuring specialized agent roles and advanced orchestration capabilities.

## Agent Roles

The system includes specialized agent roles for different aspects of project management and development:

- Business Analyst: Analyzes requirements and creates specifications
- Data Scientist: Performs data analysis and creates models
- Project Manager: Coordinates team activities and tracks progress
- Developer: Implements features and fixes bugs
- QA Engineer: Tests functionality and ensures quality

All agent roles are now organized in the `app/agent` directory for better consistency.

## Multi-agent Architecture Search (MaAS) Integration

This repository includes Multi-agent Architecture Search (MaAS) integration, which enables:

- Dynamic discovery and optimization of agent team architectures based on task requirements
- Visualization of agent architectures, performance metrics, and search progress
- Integration with existing orchestration systems (AutoGen and A2A)
- Agentic Supernet for dynamic architecture sampling and optimization

For more information, see the documentation in the `docs/maas_integration_guide.md` and `docs/maas_implementation.md` files.
