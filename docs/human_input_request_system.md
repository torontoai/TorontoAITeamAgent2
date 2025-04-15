# Human Input Request System Documentation

## Overview

The Human Input Request System is a new feature added to the TORONTO AI Team Agent Team AI platform that enhances collaboration between AI agents and human stakeholders. This system provides a structured way for agents to request information, decisions, feedback, or approvals from humans, with the Project Manager agent acting as the central coordinator.

## Key Features

1. **Collapsible Request Panel**: A dedicated panel that displays all human input requests, which can be minimized when not in use.

2. **Request Prioritization**: Requests are automatically prioritized based on urgency, impact, agent role, request age, and complexity.

3. **Status Tracking**: Each request has a clear status (pending, in progress, completed) that is visually indicated.

4. **Filtering Capabilities**: Requests can be filtered by status, priority, and category to help focus on the most important items.

5. **Project Manager Coordination**: All requests from agents are routed through the Project Manager, who reformulates and prioritizes them before presenting to the human.

6. **Detailed Request View**: Each request includes comprehensive information including the original agent query, reformulated description, priority, category, and time constraints.

## Using the Human Input Request System

### Viewing Requests

The Human Input Request panel appears at the top of the Project Manager interface. It shows a count of pending requests and can be expanded or collapsed by clicking on the header.

Each request in the list shows:
- Title
- Status (pending, in progress, completed)
- Category (decision, feedback, approval, information)
- Priority (high, medium, low)
- Requesting agent
- Creation time
- Time remaining or overdue status

### Responding to Requests

1. Click on any request in the list to view its details.
2. Review the full description, which includes context added by the Project Manager.
3. For pending requests, you can:
   - Click "Mark In Progress" to indicate you're working on it
   - Click "Mark Completed" when you've provided the requested input
4. Your response will be automatically routed back to the requesting agent through the Project Manager.

### Filtering Requests

1. Click the filter icon in the Human Input Request panel header.
2. Select filters for status, priority, and/or category.
3. Click "Apply Filters" to update the list.
4. Click "Reset" to clear all filters.

### Editing Requests

As a human stakeholder, you can edit requests to clarify or adjust them:

1. Open a request's details.
2. Click the edit icon in the top-right corner.
3. Modify any fields as needed.
4. Click "Save Changes" to update the request.

## How It Works Behind the Scenes

1. **Agent Request Generation**: When an agent needs human input, it sends a request to the Project Manager.

2. **Request Reformulation**: The Project Manager reviews the request, adds context, adjusts priority if needed, and reformulates it for clarity.

3. **Prioritization**: The system uses a sophisticated algorithm to prioritize requests based on multiple factors:
   - Urgency (time sensitivity)
   - Impact (importance to project progress)
   - Agent role (some roles may have higher priority)
   - Request age (older requests get gradually higher priority)
   - Complexity (estimated complexity of the response needed)

4. **Human Notification**: The request appears in the Human Input Request panel with appropriate visual indicators.

5. **Response Routing**: When you respond, the Project Manager ensures your input is properly formatted and delivered to the requesting agent.

6. **Status Tracking**: The system maintains a complete history of all requests and responses for project documentation.

## Benefits

- **Reduced Interruptions**: Instead of multiple agents asking for input at random times, requests are organized and prioritized.

- **Better Context**: The Project Manager adds context to requests, making them easier to understand and respond to.

- **Prioritized Workflow**: Focus on the most important requests first, with clear visual indicators of priority and urgency.

- **Comprehensive Tracking**: All requests and responses are tracked, creating a record of human input throughout the project.

- **Streamlined Communication**: The Project Manager handles routing of information, reducing communication overhead.

## Best Practices

1. **Regular Check-ins**: Review the Human Input Request panel regularly to avoid delays in project progress.

2. **Prioritize High-Impact Requests**: Pay special attention to "decision" and "approval" categories, as these often block further progress.

3. **Provide Complete Responses**: Include all necessary details in your responses to avoid follow-up requests.

4. **Use Status Indicators**: Mark requests as "In Progress" when you start working on them to inform the team.

5. **Filter Effectively**: Use the filtering system to focus on specific types of requests when needed.

## Troubleshooting

- **Too Many Requests**: If you're overwhelmed with requests, use the filtering system to focus on high-priority items first.

- **Unclear Requests**: Use the edit function to clarify the request or add notes for future reference.

- **Missing Context**: If a request lacks sufficient context, mark it as "In Progress" and ask the Project Manager for clarification.

- **Request Overdue**: Overdue requests are highlighted in red. Prioritize these to unblock team progress.

## Future Enhancements

The Human Input Request System will continue to evolve with planned enhancements including:

- Integration with external notification systems (email, messaging platforms)
- Advanced analytics on request patterns and response times
- Custom request templates for common input needs
- Batch response capabilities for related requests
