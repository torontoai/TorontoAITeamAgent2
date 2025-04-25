# Security Features Documentation

This document provides comprehensive documentation for the security features in the TORONTO AI TEAM AGENT system.

## Overview

The security features module provides robust security capabilities for the TORONTO AI TEAM AGENT system, including security scanning tools integration and a comprehensive audit trail system. These features help ensure secure development practices and maintain accountability for all agent actions.

## Security Scanning Tools Integration

### Key Components

#### SecurityScannerType

An enumeration of supported security scanner types:

- `SNYK`: Snyk vulnerability scanner
- `SONARQUBE`: SonarQube code quality and security scanner
- `SEMGREP`: Semgrep static analysis tool
- `OWASP_ZAP`: OWASP ZAP dynamic application security testing tool
- `TRIVY`: Trivy container vulnerability scanner

#### VulnerabilitySeverity

An enumeration of vulnerability severity levels:

- `CRITICAL`: Critical severity vulnerabilities that must be addressed immediately
- `HIGH`: High severity vulnerabilities that should be addressed as soon as possible
- `MEDIUM`: Medium severity vulnerabilities that should be addressed in the near future
- `LOW`: Low severity vulnerabilities that should be addressed when convenient
- `INFO`: Informational findings that may not require action

#### Vulnerability

A class representing a security vulnerability with the following key attributes:

- `id`: The unique identifier of the vulnerability
- `title`: The title of the vulnerability
- `description`: The description of the vulnerability
- `severity`: The severity of the vulnerability
- `file_path`: The file path where the vulnerability was found
- `line_number`: The line number where the vulnerability was found
- `scanner_type`: The type of scanner that found the vulnerability
- `cve_id`: The CVE ID of the vulnerability (if applicable)
- `fix_recommendation`: Recommended fix for the vulnerability

#### ScanResult

A class representing the result of a security scan with the following key attributes:

- `scanner_type`: The type of scanner used
- `vulnerabilities`: The list of vulnerabilities found
- `scan_time`: The timestamp of the scan
- `scan_duration`: The duration of the scan in seconds
- `target`: The target of the scan (e.g., file path, URL)
- `success`: Whether the scan was successful
- `critical_count`: The number of critical vulnerabilities
- `high_count`: The number of high severity vulnerabilities
- `medium_count`: The number of medium severity vulnerabilities
- `low_count`: The number of low severity vulnerabilities
- `info_count`: The number of informational findings

#### SecurityScanner

A base class for security scanners with the following key methods:

- `scan(target, options=None)`: Scan a target for vulnerabilities
- `get_scanner_type()`: Get the type of the scanner
- `get_scanner_name()`: Get the name of the scanner
- `get_scanner_version()`: Get the version of the scanner

#### SnykScanner

A class for integrating with Snyk with the following key methods:

- `scan(target, options=None)`: Scan a target for vulnerabilities using Snyk
- `authenticate()`: Authenticate with Snyk
- `get_organization_projects()`: Get projects in the Snyk organization
- `import_project(name, repo_url)`: Import a project into Snyk
- `get_project_issues(project_id)`: Get issues for a project

#### SonarQubeScanner

A class for integrating with SonarQube with the following key methods:

- `scan(target, options=None)`: Scan a target for vulnerabilities using SonarQube
- `authenticate()`: Authenticate with SonarQube
- `create_project(key, name)`: Create a project in SonarQube
- `analyze_project(project_key)`: Analyze a project
- `get_project_issues(project_key)`: Get issues for a project

#### SemgrepScanner

A class for integrating with Semgrep with the following key methods:

- `scan(target, options=None)`: Scan a target for vulnerabilities using Semgrep
- `get_rules()`: Get available Semgrep rules
- `create_custom_rule(rule_yaml)`: Create a custom Semgrep rule
- `scan_with_rules(target, rules)`: Scan a target with specific rules

#### SecurityScanningManager

A class for managing security scanners with the following key methods:

- `register_scanner(scanner)`: Register a security scanner
- `unregister_scanner(scanner_type)`: Unregister a security scanner
- `get_scanner(scanner_type)`: Get a scanner by type
- `list_scanners()`: List all registered scanners
- `scan(target, scanner_type=None, options=None)`: Scan a target for vulnerabilities
- `scan_all(target, options=None)`: Scan a target with all registered scanners
- `get_scan_history(target)`: Get scan history for a target
- `get_latest_scan(target, scanner_type=None)`: Get the latest scan for a target

### Usage Examples

#### Basic Security Scanning

```python
from app.security.security_scanning import (
    SecurityScanningManager, SnykScanner, SonarQubeScanner, SemgrepScanner,
    SecurityScannerType
)

# Initialize the security scanning manager
security_scanning_manager = SecurityScanningManager()

# Register scanners
snyk_scanner = SnykScanner(api_token="your_snyk_api_token")
sonarqube_scanner = SonarQubeScanner(
    server_url="http://localhost:9000",
    token="your_sonarqube_token"
)
semgrep_scanner = SemgrepScanner()

security_scanning_manager.register_scanner(snyk_scanner)
security_scanning_manager.register_scanner(sonarqube_scanner)
security_scanning_manager.register_scanner(semgrep_scanner)

# Scan a project with Snyk
snyk_result = security_scanning_manager.scan(
    target="/path/to/project",
    scanner_type=SecurityScannerType.SNYK
)

# Print scan results
print(f"Scan completed in {snyk_result.scan_duration:.2f} seconds")
print(f"Found {len(snyk_result.vulnerabilities)} vulnerabilities:")
print(f"  Critical: {snyk_result.critical_count}")
print(f"  High: {snyk_result.high_count}")
print(f"  Medium: {snyk_result.medium_count}")
print(f"  Low: {snyk_result.low_count}")
print(f"  Info: {snyk_result.info_count}")

# Print vulnerability details
for vulnerability in snyk_result.vulnerabilities:
    print(f"\nVulnerability: {vulnerability.title}")
    print(f"Severity: {vulnerability.severity.name}")
    print(f"Description: {vulnerability.description}")
    print(f"File: {vulnerability.file_path}")
    if vulnerability.fix_recommendation:
        print(f"Fix: {vulnerability.fix_recommendation}")
```

#### Scanning with Multiple Scanners

```python
from app.security.security_scanning import SecurityScanningManager, SnykScanner, SemgrepScanner

# Initialize the security scanning manager
security_scanning_manager = SecurityScanningManager()

# Register scanners
security_scanning_manager.register_scanner(SnykScanner(api_token="your_snyk_api_token"))
security_scanning_manager.register_scanner(SemgrepScanner())

# Scan a project with all registered scanners
results = security_scanning_manager.scan_all(target="/path/to/project")

# Process results from each scanner
for scanner_type, result in results.items():
    print(f"\nResults from {scanner_type.name}:")
    print(f"Found {len(result.vulnerabilities)} vulnerabilities")
    
    # Count vulnerabilities by severity
    severity_counts = {}
    for vulnerability in result.vulnerabilities:
        severity = vulnerability.severity.name
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    for severity, count in severity_counts.items():
        print(f"  {severity}: {count}")
```

#### Continuous Security Scanning

```python
import time
from app.security.security_scanning import SecurityScanningManager, SemgrepScanner

# Initialize the security scanning manager
security_scanning_manager = SecurityScanningManager()

# Register scanner
security_scanning_manager.register_scanner(SemgrepScanner())

# Function to monitor a project for security issues
def monitor_project(project_path, interval=3600):  # Check every hour
    while True:
        print(f"Scanning {project_path}...")
        result = security_scanning_manager.scan_all(target=project_path)
        
        # Process results
        total_vulnerabilities = sum(len(r.vulnerabilities) for r in result.values())
        if total_vulnerabilities > 0:
            print(f"Found {total_vulnerabilities} vulnerabilities!")
            # Send notification or trigger alert
        else:
            print("No vulnerabilities found.")
        
        # Wait for the next scan
        print(f"Next scan in {interval // 60} minutes")
        time.sleep(interval)

# Start monitoring
monitor_project("/path/to/project")
```

## Audit Trail System

### Key Components

#### AuditEventType

An enumeration of audit event types:

- `AGENT_ACTION`: Actions performed by agents
- `USER_ACTION`: Actions performed by users
- `SYSTEM_EVENT`: System-level events
- `SECURITY_EVENT`: Security-related events
- `DATA_ACCESS`: Data access events

#### AuditEventSeverity

An enumeration of audit event severity levels:

- `CRITICAL`: Critical severity events that require immediate attention
- `HIGH`: High severity events that should be reviewed soon
- `MEDIUM`: Medium severity events that should be reviewed
- `LOW`: Low severity events that may not require review
- `INFO`: Informational events

#### AuditEvent

A class representing an audit event with the following key attributes:

- `id`: The unique identifier of the event
- `timestamp`: The timestamp of the event
- `event_type`: The type of the event
- `severity`: The severity of the event
- `actor`: The actor who performed the action (user, agent, or system)
- `action`: The action that was performed
- `resource`: The resource that was affected
- `status`: The status of the action (success, failure, etc.)
- `details`: Additional details about the event
- `source_ip`: The source IP address (for user actions)
- `user_agent`: The user agent (for user actions)
- `session_id`: The session ID (for user actions)

#### AuditEventBuilder

A builder class for creating audit events with the following key methods:

- `set_event_type(event_type)`: Set the event type
- `set_severity(severity)`: Set the severity
- `set_actor(actor)`: Set the actor
- `set_action(action)`: Set the action
- `set_resource(resource)`: Set the resource
- `set_status(status)`: Set the status
- `set_details(details)`: Set the details
- `set_source_ip(source_ip)`: Set the source IP address
- `set_user_agent(user_agent)`: Set the user agent
- `set_session_id(session_id)`: Set the session ID
- `build()`: Build the audit event

#### AuditEventStorage

A base class for audit event storage with the following key methods:

- `store_event(event)`: Store an audit event
- `get_event(event_id)`: Get an audit event by ID
- `query_events(filters=None, start_time=None, end_time=None, limit=None, offset=None)`: Query audit events
- `delete_event(event_id)`: Delete an audit event
- `delete_events_before(timestamp)`: Delete events before a timestamp

#### FileAuditEventStorage

A class for storing audit events in a file with the following key methods:

- `store_event(event)`: Store an audit event in the file
- `get_event(event_id)`: Get an audit event by ID from the file
- `query_events(filters=None, start_time=None, end_time=None, limit=None, offset=None)`: Query audit events from the file
- `delete_event(event_id)`: Delete an audit event from the file
- `delete_events_before(timestamp)`: Delete events before a timestamp from the file

#### SQLiteAuditEventStorage

A class for storing audit events in a SQLite database with the following key methods:

- `store_event(event)`: Store an audit event in the database
- `get_event(event_id)`: Get an audit event by ID from the database
- `query_events(filters=None, start_time=None, end_time=None, limit=None, offset=None)`: Query audit events from the database
- `delete_event(event_id)`: Delete an audit event from the database
- `delete_events_before(timestamp)`: Delete events before a timestamp from the database

#### AuditTrailSystem

A class for managing the audit trail with the following key methods:

- `log_event(event)`: Log an audit event
- `log_agent_action(agent_id, action, resource, status="success", severity=AuditEventSeverity.INFO, details=None)`: Log an agent action
- `log_user_action(user_id, action, resource, status="success", severity=AuditEventSeverity.INFO, details=None, source_ip=None, user_agent=None, session_id=None)`: Log a user action
- `log_system_event(action, resource, status="success", severity=AuditEventSeverity.INFO, details=None)`: Log a system event
- `log_security_event(actor, action, resource, status="success", severity=AuditEventSeverity.INFO, details=None, source_ip=None)`: Log a security event
- `log_data_access(actor, action, resource, status="success", severity=AuditEventSeverity.INFO, details=None)`: Log a data access event
- `get_event(event_id)`: Get an audit event by ID
- `query_events(filters=None, start_time=None, end_time=None, limit=None, offset=None)`: Query audit events
- `delete_event(event_id)`: Delete an audit event
- `delete_events_before(timestamp)`: Delete events before a timestamp

### Usage Examples

#### Basic Audit Logging

```python
from app.security.audit_trail import (
    AuditTrailSystem, FileAuditEventStorage, AuditEventType, AuditEventSeverity
)

# Initialize the audit trail system with file storage
audit_storage = FileAuditEventStorage("/path/to/audit.log")
audit_trail_system = AuditTrailSystem(audit_storage)

# Log an agent action
audit_trail_system.log_agent_action(
    agent_id="agent1",
    action="code_generation",
    resource="project/file.py",
    status="success",
    severity=AuditEventSeverity.INFO,
    details={"language": "python", "tokens": 150}
)

# Log a user action
audit_trail_system.log_user_action(
    user_id="user1",
    action="login",
    resource="system",
    status="success",
    severity=AuditEventSeverity.INFO,
    source_ip="192.168.1.1",
    user_agent="Mozilla/5.0",
    session_id="session123"
)

# Log a system event
audit_trail_system.log_system_event(
    action="backup",
    resource="database",
    status="success",
    severity=AuditEventSeverity.INFO,
    details={"backup_size": "1.2GB", "duration": "5m"}
)

# Log a security event
audit_trail_system.log_security_event(
    actor="user2",
    action="permission_change",
    resource="project/sensitive.py",
    status="success",
    severity=AuditEventSeverity.HIGH,
    details={"old_permissions": "rw-r--r--", "new_permissions": "rw-rw-r--"},
    source_ip="192.168.1.2"
)

# Query events
events = audit_trail_system.query_events()
print(f"Found {len(events)} events")

# Query events by type
agent_events = audit_trail_system.query_events(
    filters={"event_type": AuditEventType.AGENT_ACTION.value}
)
print(f"Found {len(agent_events)} agent events")

# Query events by severity
high_severity_events = audit_trail_system.query_events(
    filters={"severity": AuditEventSeverity.HIGH.value}
)
print(f"Found {len(high_severity_events)} high severity events")

# Query events by time range
import time
current_time = time.time()
recent_events = audit_trail_system.query_events(
    start_time=current_time - 3600,  # Last hour
    end_time=current_time
)
print(f"Found {len(recent_events)} events in the last hour")
```

#### Advanced Audit Trail Usage

```python
import time
from app.security.audit_trail import (
    AuditTrailSystem, SQLiteAuditEventStorage, AuditEvent, AuditEventBuilder,
    AuditEventType, AuditEventSeverity
)

# Initialize the audit trail system with SQLite storage
audit_storage = SQLiteAuditEventStorage("/path/to/audit.db")
audit_trail_system = AuditTrailSystem(audit_storage, async_mode=True)

# Create a custom audit event using the builder
event_builder = AuditEventBuilder()
event = (event_builder
    .set_event_type(AuditEventType.SECURITY_EVENT)
    .set_severity(AuditEventSeverity.CRITICAL)
    .set_actor("system")
    .set_action("intrusion_detection")
    .set_resource("network")
    .set_status("alert")
    .set_details({
        "source_ip": "203.0.113.1",
        "destination_ip": "192.168.1.10",
        "protocol": "TCP",
        "port": 22,
        "attempts": 5,
        "signature": "SSH brute force attempt"
    })
    .set_source_ip("203.0.113.1")
    .build())

# Log the custom event
audit_trail_system.log_event(event)

# Function to monitor security events
def monitor_security_events(interval=60):  # Check every minute
    while True:
        # Query critical security events
        critical_events = audit_trail_system.query_events(
            filters={
                "event_type": AuditEventType.SECURITY_EVENT.value,
                "severity": AuditEventSeverity.CRITICAL.value
            },
            start_time=time.time() - interval
        )
        
        if critical_events:
            print(f"ALERT: Found {len(critical_events)} critical security events!")
            for event in critical_events:
                print(f"  {event.timestamp}: {event.action} on {event.resource}")
                print(f"  Details: {event.details}")
                print()
            
            # Send notification or trigger alert
        
        # Wait for the next check
        time.sleep(interval)

# Start monitoring
monitor_security_events()
```

#### Compliance Reporting

```python
import time
import csv
from datetime import datetime
from app.security.audit_trail import AuditTrailSystem, SQLiteAuditEventStorage

# Initialize the audit trail system
audit_storage = SQLiteAuditEventStorage("/path/to/audit.db")
audit_trail_system = AuditTrailSystem(audit_storage)

# Function to generate a compliance report
def generate_compliance_report(start_time, end_time, output_file):
    # Query events for the specified time period
    events = audit_trail_system.query_events(
        start_time=start_time,
        end_time=end_time
    )
    
    # Write events to CSV file
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = [
            'timestamp', 'event_type', 'severity', 'actor',
            'action', 'resource', 'status', 'source_ip'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for event in events:
            writer.writerow({
                'timestamp': datetime.fromtimestamp(event.timestamp).isoformat(),
                'event_type': event.event_type,
                'severity': event.severity,
                'actor': event.actor,
                'action': event.action,
                'resource': event.resource,
                'status': event.status,
                'source_ip': event.source_ip
            })
    
    print(f"Generated compliance report with {len(events)} events")

# Generate a monthly compliance report
def generate_monthly_report(year, month):
    import calendar
    
    # Calculate start and end timestamps for the month
    _, last_day = calendar.monthrange(year, month)
    start_time = datetime(year, month, 1).timestamp()
    end_time = datetime(year, month, last_day, 23, 59, 59).timestamp()
    
    # Generate the report
    output_file = f"compliance_report_{year}_{month:02d}.csv"
    generate_compliance_report(start_time, end_time, output_file)
    
    return output_file

# Generate report for the previous month
from datetime import datetime
now = datetime.now()
if now.month == 1:
    report_year = now.year - 1
    report_month = 12
else:
    report_year = now.year
    report_month = now.month - 1

report_file = generate_monthly_report(report_year, report_month)
print(f"Monthly compliance report saved to: {report_file}")
```

## Best Practices

### Security Scanning Best Practices

1. **Regular Scanning**: Implement regular security scanning as part of your CI/CD pipeline to catch vulnerabilities early.

2. **Multiple Scanners**: Use multiple security scanners to get comprehensive coverage of different types of vulnerabilities.

3. **Prioritize Vulnerabilities**: Focus on critical and high severity vulnerabilities first, then address medium and low severity issues.

4. **Automate Remediation**: Where possible, automate the remediation of common vulnerabilities.

5. **Track Vulnerability Trends**: Monitor vulnerability trends over time to identify recurring issues and improve development practices.

6. **Scan Dependencies**: Ensure that third-party dependencies are scanned for vulnerabilities.

7. **Custom Rules**: Develop custom scanning rules for organization-specific security requirements.

8. **Developer Education**: Use scanning results to educate developers about security best practices.

### Audit Trail Best Practices

1. **Comprehensive Logging**: Log all significant actions and events in the system.

2. **Structured Data**: Use structured data formats for audit events to facilitate analysis.

3. **Tamper-Proof Storage**: Ensure that audit logs cannot be modified or deleted by unauthorized users.

4. **Retention Policy**: Implement a retention policy for audit logs based on compliance requirements.

5. **Regular Review**: Regularly review audit logs for suspicious activities.

6. **Automated Alerting**: Set up automated alerts for critical security events.

7. **Performance Considerations**: Balance logging detail with performance impact.

8. **Privacy Compliance**: Ensure that audit logging complies with privacy regulations like GDPR.

## Troubleshooting

### Common Security Scanning Issues

1. **Scanner Configuration**: Ensure that security scanners are properly configured with the correct API tokens and settings.

2. **False Positives**: Review and validate reported vulnerabilities to identify false positives.

3. **Scan Performance**: If scans are taking too long, consider optimizing scan configurations or targeting specific parts of the codebase.

4. **Integration Issues**: If scanners are not integrating properly with your CI/CD pipeline, check API endpoints and authentication.

### Common Audit Trail Issues

1. **Missing Events**: If events are not being logged, check that the audit trail system is properly initialized and configured.

2. **Storage Issues**: If events are not being stored, verify that the storage backend is accessible and has sufficient space.

3. **Performance Impact**: If logging is impacting system performance, consider using async mode or optimizing the storage backend.

4. **Query Performance**: If queries are slow, consider adding indexes to the storage backend or optimizing query filters.

### Debugging Tips

1. **Enable Debug Logging**: Set the log level to DEBUG for more detailed information about security scanning and audit trail operations.

2. **Check Scanner Output**: Review the raw output from security scanners to identify issues.

3. **Validate Event Storage**: Verify that audit events are being properly stored by directly checking the storage backend.

4. **Test with Simplified Configurations**: When troubleshooting complex issues, test with simplified configurations to isolate the problem.

## API Reference

For a complete API reference, see the inline documentation in the source code:

- `app/security/security_scanning.py`
- `app/security/audit_trail.py`
