"""
Automated Progress Reporting Module for TORONTO AI TEAM AGENT

This module provides functionality for generating customized reports for different stakeholders
with appropriate detail levels. It supports various report formats, visualization options,
and delivery mechanisms to keep stakeholders informed about project progress.

Features:
- Customized reports for different stakeholder types
- Multiple detail levels (executive, manager, developer)
- Various report formats (text, HTML, PDF, dashboard)
- Automated report generation and delivery
- Integration with project management and resource allocation systems
"""

import datetime
import json
import os
import re
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Callable
import matplotlib.pyplot as plt
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum, auto
import jinja2

# Import project management modules if available
try:
    from .gantt_chart import GanttChart, Task as GanttTask
    from .resource_allocation import ResourceAllocator, Task as ResourceTask, Resource
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False


class StakeholderType(Enum):
    """Types of stakeholders for report customization."""
    EXECUTIVE = auto()
    MANAGER = auto()
    DEVELOPER = auto()
    CLIENT = auto()
    CUSTOM = auto()


class ReportFormat(Enum):
    """Available report formats."""
    TEXT = auto()
    HTML = auto()
    PDF = auto()
    MARKDOWN = auto()
    JSON = auto()
    DASHBOARD = auto()


class ReportSection(Enum):
    """Standard report sections."""
    SUMMARY = auto()
    TIMELINE = auto()
    RESOURCES = auto()
    TASKS = auto()
    RISKS = auto()
    ISSUES = auto()
    MILESTONES = auto()
    METRICS = auto()
    RECOMMENDATIONS = auto()
    CUSTOM = auto()


@dataclass
class ReportMetric:
    """Represents a metric to be included in a report."""
    name: str
    value: Any
    target: Optional[Any] = None
    unit: str = ""
    trend: Optional[float] = None  # Positive = improving, negative = worsening
    description: str = ""
    visualization: Optional[str] = None  # Type of visualization (bar, line, etc.)
    
    def to_dict(self) -> Dict:
        """Convert metric to dictionary for serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "target": self.target,
            "unit": self.unit,
            "trend": self.trend,
            "description": self.description,
            "visualization": self.visualization
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReportMetric':
        """Create metric from dictionary."""
        return cls(
            name=data["name"],
            value=data["value"],
            target=data.get("target"),
            unit=data.get("unit", ""),
            trend=data.get("trend"),
            description=data.get("description", ""),
            visualization=data.get("visualization")
        )


@dataclass
class ReportIssue:
    """Represents an issue to be included in a report."""
    id: str
    title: str
    description: str
    severity: str  # High, Medium, Low
    status: str  # Open, In Progress, Resolved
    assigned_to: Optional[str] = None
    created_date: datetime.datetime = field(default_factory=datetime.datetime.now)
    resolution_date: Optional[datetime.datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert issue to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "created_date": self.created_date.isoformat(),
            "resolution_date": self.resolution_date.isoformat() if self.resolution_date else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReportIssue':
        """Create issue from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            severity=data["severity"],
            status=data["status"],
            assigned_to=data.get("assigned_to"),
            created_date=datetime.datetime.fromisoformat(data["created_date"]),
            resolution_date=datetime.datetime.fromisoformat(data["resolution_date"]) if data.get("resolution_date") else None
        )


@dataclass
class ReportRisk:
    """Represents a risk to be included in a report."""
    id: str
    title: str
    description: str
    probability: float  # 0.0 to 1.0
    impact: float  # 0.0 to 1.0
    mitigation: str
    status: str  # Identified, Mitigated, Accepted, Closed
    owner: Optional[str] = None
    
    @property
    def risk_score(self) -> float:
        """Calculate risk score (probability * impact)."""
        return self.probability * self.impact
    
    def to_dict(self) -> Dict:
        """Convert risk to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "probability": self.probability,
            "impact": self.impact,
            "mitigation": self.mitigation,
            "status": self.status,
            "owner": self.owner
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReportRisk':
        """Create risk from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            probability=data["probability"],
            impact=data["impact"],
            mitigation=data["mitigation"],
            status=data["status"],
            owner=data.get("owner")
        )


@dataclass
class ReportMilestone:
    """Represents a milestone to be included in a report."""
    id: str
    title: str
    description: str
    due_date: datetime.datetime
    status: str  # Not Started, In Progress, Completed, Delayed
    completion_percentage: float = 0.0  # 0.0 to 1.0
    
    def to_dict(self) -> Dict:
        """Convert milestone to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat(),
            "status": self.status,
            "completion_percentage": self.completion_percentage
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReportMilestone':
        """Create milestone from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            due_date=datetime.datetime.fromisoformat(data["due_date"]),
            status=data["status"],
            completion_percentage=data.get("completion_percentage", 0.0)
        )


@dataclass
class ReportRecommendation:
    """Represents a recommendation to be included in a report."""
    id: str
    title: str
    description: str
    priority: str  # High, Medium, Low
    impact: str
    effort: str  # High, Medium, Low
    
    def to_dict(self) -> Dict:
        """Convert recommendation to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "impact": self.impact,
            "effort": self.effort
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReportRecommendation':
        """Create recommendation from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            priority=data["priority"],
            impact=data["impact"],
            effort=data["effort"]
        )


@dataclass
class ReportTemplate:
    """Template for generating reports."""
    name: str
    description: str
    stakeholder_type: StakeholderType
    format: ReportFormat
    sections: List[ReportSection]
    detail_level: int = 1  # 1 (minimal) to 5 (comprehensive)
    custom_sections: Dict[str, str] = field(default_factory=dict)
    template_path: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert template to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "stakeholder_type": self.stakeholder_type.name,
            "format": self.format.name,
            "sections": [section.name for section in self.sections],
            "detail_level": self.detail_level,
            "custom_sections": self.custom_sections,
            "template_path": self.template_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReportTemplate':
        """Create template from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            stakeholder_type=StakeholderType[data["stakeholder_type"]],
            format=ReportFormat[data["format"]],
            sections=[ReportSection[section] for section in data["sections"]],
            detail_level=data.get("detail_level", 1),
            custom_sections=data.get("custom_sections", {}),
            template_path=data.get("template_path")
        )


class ProgressReport:
    """
    Represents a progress report with customizable content and format.
    """
    
    def __init__(self, project_name: str, report_date: datetime.datetime = None):
        """
        Initialize a new progress report.
        
        Args:
            project_name: Name of the project
            report_date: Date of the report (defaults to current date/time)
        """
        self.project_name = project_name
        self.report_date = report_date or datetime.datetime.now()
        self.report_id = f"{project_name.lower().replace(' ', '_')}_{self.report_date.strftime('%Y%m%d_%H%M%S')}"
        
        # Report content
        self.summary = ""
        self.metrics: List[ReportMetric] = []
        self.issues: List[ReportIssue] = []
        self.risks: List[ReportRisk] = []
        self.milestones: List[ReportMilestone] = []
        self.recommendations: List[ReportRecommendation] = []
        self.custom_sections: Dict[str, str] = {}
        
        # Report metadata
        self.author = "TORONTO AI TEAM AGENT"
        self.stakeholder_type = StakeholderType.MANAGER
        self.detail_level = 3
        self.format = ReportFormat.HTML
        self.sections = [
            ReportSection.SUMMARY,
            ReportSection.METRICS,
            ReportSection.MILESTONES,
            ReportSection.ISSUES,
            ReportSection.RECOMMENDATIONS
        ]
    
    def set_summary(self, summary: str) -> None:
        """
        Set the report summary.
        
        Args:
            summary: Summary text
        """
        self.summary = summary
    
    def add_metric(self, metric: ReportMetric) -> None:
        """
        Add a metric to the report.
        
        Args:
            metric: Metric to add
        """
        self.metrics.append(metric)
    
    def add_issue(self, issue: ReportIssue) -> None:
        """
        Add an issue to the report.
        
        Args:
            issue: Issue to add
        """
        self.issues.append(issue)
    
    def add_risk(self, risk: ReportRisk) -> None:
        """
        Add a risk to the report.
        
        Args:
            risk: Risk to add
        """
        self.risks.append(risk)
    
    def add_milestone(self, milestone: ReportMilestone) -> None:
        """
        Add a milestone to the report.
        
        Args:
            milestone: Milestone to add
        """
        self.milestones.append(milestone)
    
    def add_recommendation(self, recommendation: ReportRecommendation) -> None:
        """
        Add a recommendation to the report.
        
        Args:
            recommendation: Recommendation to add
        """
        self.recommendations.append(recommendation)
    
    def add_custom_section(self, title: str, content: str) -> None:
        """
        Add a custom section to the report.
        
        Args:
            title: Section title
            content: Section content
        """
        self.custom_sections[title] = content
    
    def set_stakeholder_type(self, stakeholder_type: StakeholderType) -> None:
        """
        Set the stakeholder type for the report.
        
        Args:
            stakeholder_type: Type of stakeholder
        """
        self.stakeholder_type = stakeholder_type
    
    def set_detail_level(self, level: int) -> None:
        """
        Set the detail level for the report.
        
        Args:
            level: Detail level (1-5)
        """
        if level < 1 or level > 5:
            raise ValueError("Detail level must be between 1 and 5")
        
        self.detail_level = level
    
    def set_format(self, format: ReportFormat) -> None:
        """
        Set the report format.
        
        Args:
            format: Report format
        """
        self.format = format
    
    def set_sections(self, sections: List[ReportSection]) -> None:
        """
        Set the sections to include in the report.
        
        Args:
            sections: List of sections
        """
        self.sections = sections
    
    def generate_report(self, output_path: str = None) -> str:
        """
        Generate the report in the specified format.
        
        Args:
            output_path: Path to save the report (optional)
            
        Returns:
            Generated report content or file path
        """
        if self.format == ReportFormat.TEXT:
            return self._generate_text_report(output_path)
        elif self.format == ReportFormat.HTML:
            return self._generate_html_report(output_path)
        elif self.format == ReportFormat.MARKDOWN:
            return self._generate_markdown_report(output_path)
        elif self.format == ReportFormat.JSON:
            return self._generate_json_report(output_path)
        elif self.format == ReportFormat.PDF:
            return self._generate_pdf_report(output_path)
        elif self.format == ReportFormat.DASHBOARD:
            return self._generate_dashboard_report(output_path)
        else:
            raise ValueError(f"Unsupported report format: {self.format}")
    
    def _generate_text_report(self, output_path: str = None) -> str:
        """Generate a plain text report."""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append(f"{self.project_name} - Progress Report")
        lines.append(f"Date: {self.report_date.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Author: {self.author}")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        if ReportSection.SUMMARY in self.sections and self.summary:
            lines.append("SUMMARY")
            lines.append("-" * 80)
            lines.append(self.summary)
            lines.append("")
        
        # Metrics
        if ReportSection.METRICS in self.sections and self.metrics:
            lines.append("METRICS")
            lines.append("-" * 80)
            for metric in self.metrics:
                target_str = f" (Target: {metric.target}{metric.unit})" if metric.target is not None else ""
                trend_str = ""
                if metric.trend is not None:
                    trend_str = " ↑" if metric.trend > 0 else " ↓" if metric.trend < 0 else " →"
                
                lines.append(f"{metric.name}: {metric.value}{metric.unit}{target_str}{trend_str}")
                if self.detail_level >= 3 and metric.description:
                    lines.append(f"  {metric.description}")
            lines.append("")
        
        # Milestones
        if ReportSection.MILESTONES in self.sections and self.milestones:
            lines.append("MILESTONES")
            lines.append("-" * 80)
            for milestone in self.milestones:
                lines.append(f"{milestone.title} ({milestone.status})")
                lines.append(f"  Due: {milestone.due_date.strftime('%Y-%m-%d')}")
                lines.append(f"  Completion: {milestone.completion_percentage * 100:.1f}%")
                if self.detail_level >= 3:
                    lines.append(f"  {milestone.description}")
                lines.append("")
        
        # Issues
        if ReportSection.ISSUES in self.sections and self.issues:
            lines.append("ISSUES")
            lines.append("-" * 80)
            for issue in self.issues:
                lines.append(f"{issue.title} ({issue.severity}, {issue.status})")
                if issue.assigned_to:
                    lines.append(f"  Assigned to: {issue.assigned_to}")
                if self.detail_level >= 3:
                    lines.append(f"  {issue.description}")
                lines.append("")
        
        # Risks
        if ReportSection.RISKS in self.sections and self.risks:
            lines.append("RISKS")
            lines.append("-" * 80)
            for risk in self.risks:
                lines.append(f"{risk.title} (Score: {risk.risk_score:.2f}, {risk.status})")
                if self.detail_level >= 3:
                    lines.append(f"  {risk.description}")
                    lines.append(f"  Mitigation: {risk.mitigation}")
                lines.append("")
        
        # Recommendations
        if ReportSection.RECOMMENDATIONS in self.sections and self.recommendations:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 80)
            for recommendation in self.recommendations:
                lines.append(f"{recommendation.title} (Priority: {recommendation.priority})")
                if self.detail_level >= 3:
                    lines.append(f"  {recommendation.description}")
                    lines.append(f"  Impact: {recommendation.impact}")
                    lines.append(f"  Effort: {recommendation.effort}")
                lines.append("")
        
        # Custom sections
        if ReportSection.CUSTOM in self.sections and self.custom_sections:
            for title, content in self.custom_sections.items():
                lines.append(title.upper())
                lines.append("-" * 80)
                lines.append(content)
                lines.append("")
        
        # Footer
        lines.append("=" * 80)
        lines.append(f"End of Report - Generated on {self.report_date.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        
        report_content = "\n".join(lines)
        
        if output_path:
            with open(output_path, "w") as f:
                f.write(report_content)
            return output_path
        
        return report_content
    
    def _generate_html_report(self, output_path: str = None) -> str:
        """Generate an HTML report."""
        # Define HTML template
        template_str = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ project_name }} - Progress Report</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1, h2, h3 {
                    color: #2c3e50;
                }
                .header {
                    border-bottom: 2px solid #3498db;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                }
                .section {
                    margin-bottom: 30px;
                }
                .footer {
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px solid #ddd;
                    font-size: 0.9em;
                    color: #777;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                th, td {
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f8f9fa;
                }
                .metric-card {
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 15px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .metric-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                }
                .metric-name {
                    font-size: 16px;
                    color: #7f8c8d;
                }
                .trend-up {
                    color: #27ae60;
                }
                .trend-down {
                    color: #e74c3c;
                }
                .trend-neutral {
                    color: #f39c12;
                }
                .status-completed {
                    color: #27ae60;
                }
                .status-in-progress {
                    color: #f39c12;
                }
                .status-delayed {
                    color: #e74c3c;
                }
                .status-not-started {
                    color: #7f8c8d;
                }
                .severity-high {
                    color: #e74c3c;
                }
                .severity-medium {
                    color: #f39c12;
                }
                .severity-low {
                    color: #3498db;
                }
                .progress-bar {
                    background-color: #ecf0f1;
                    border-radius: 3px;
                    height: 20px;
                    width: 100%;
                    margin-top: 5px;
                }
                .progress-bar-fill {
                    background-color: #3498db;
                    height: 100%;
                    border-radius: 3px;
                    display: block;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ project_name }} - Progress Report</h1>
                <p>Date: {{ report_date }}</p>
                <p>Author: {{ author }}</p>
            </div>
            
            {% if show_summary and summary %}
            <div class="section">
                <h2>Summary</h2>
                <p>{{ summary }}</p>
            </div>
            {% endif %}
            
            {% if show_metrics and metrics %}
            <div class="section">
                <h2>Metrics</h2>
                <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                    {% for metric in metrics %}
                    <div class="metric-card" style="flex: 1; min-width: 200px;">
                        <div class="metric-name">{{ metric.name }}</div>
                        <div class="metric-value">
                            {{ metric.value }}{{ metric.unit }}
                            {% if metric.trend is not none %}
                                {% if metric.trend > 0 %}
                                <span class="trend-up">↑</span>
                                {% elif metric.trend < 0 %}
                                <span class="trend-down">↓</span>
                                {% else %}
                                <span class="trend-neutral">→</span>
                                {% endif %}
                            {% endif %}
                        </div>
                        {% if metric.target is not none %}
                        <div>Target: {{ metric.target }}{{ metric.unit }}</div>
                        {% endif %}
                        {% if detail_level >= 3 and metric.description %}
                        <div>{{ metric.description }}</div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if show_milestones and milestones %}
            <div class="section">
                <h2>Milestones</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Milestone</th>
                            <th>Due Date</th>
                            <th>Status</th>
                            <th>Completion</th>
                            {% if detail_level >= 3 %}
                            <th>Description</th>
                            {% endif %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for milestone in milestones %}
                        <tr>
                            <td>{{ milestone.title }}</td>
                            <td>{{ milestone.due_date.strftime('%Y-%m-%d') }}</td>
                            <td class="status-{{ milestone.status.lower().replace(' ', '-') }}">
                                {{ milestone.status }}
                            </td>
                            <td>
                                <div>{{ (milestone.completion_percentage * 100) | round(1) }}%</div>
                                <div class="progress-bar">
                                    <span class="progress-bar-fill" style="width: {{ (milestone.completion_percentage * 100) | round(1) }}%;"></span>
                                </div>
                            </td>
                            {% if detail_level >= 3 %}
                            <td>{{ milestone.description }}</td>
                            {% endif %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
            
            {% if show_issues and issues %}
            <div class="section">
                <h2>Issues</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Issue</th>
                            <th>Severity</th>
                            <th>Status</th>
                            {% if detail_level >= 2 %}
                            <th>Assigned To</th>
                            {% endif %}
                            {% if detail_level >= 3 %}
                            <th>Description</th>
                            {% endif %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for issue in issues %}
                        <tr>
                            <td>{{ issue.title }}</td>
                            <td class="severity-{{ issue.severity.lower() }}">{{ issue.severity }}</td>
                            <td>{{ issue.status }}</td>
                            {% if detail_level >= 2 %}
                            <td>{{ issue.assigned_to or 'Unassigned' }}</td>
                            {% endif %}
                            {% if detail_level >= 3 %}
                            <td>{{ issue.description }}</td>
                            {% endif %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
            
            {% if show_risks and risks %}
            <div class="section">
                <h2>Risks</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Risk</th>
                            <th>Score</th>
                            <th>Status</th>
                            {% if detail_level >= 2 %}
                            <th>Owner</th>
                            {% endif %}
                            {% if detail_level >= 3 %}
                            <th>Description</th>
                            <th>Mitigation</th>
                            {% endif %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for risk in risks %}
                        <tr>
                            <td>{{ risk.title }}</td>
                            <td>{{ (risk.risk_score * 10) | round(1) }}</td>
                            <td>{{ risk.status }}</td>
                            {% if detail_level >= 2 %}
                            <td>{{ risk.owner or 'Unassigned' }}</td>
                            {% endif %}
                            {% if detail_level >= 3 %}
                            <td>{{ risk.description }}</td>
                            <td>{{ risk.mitigation }}</td>
                            {% endif %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
            
            {% if show_recommendations and recommendations %}
            <div class="section">
                <h2>Recommendations</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Recommendation</th>
                            <th>Priority</th>
                            {% if detail_level >= 2 %}
                            <th>Effort</th>
                            {% endif %}
                            {% if detail_level >= 3 %}
                            <th>Description</th>
                            <th>Impact</th>
                            {% endif %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for recommendation in recommendations %}
                        <tr>
                            <td>{{ recommendation.title }}</td>
                            <td class="severity-{{ recommendation.priority.lower() }}">{{ recommendation.priority }}</td>
                            {% if detail_level >= 2 %}
                            <td>{{ recommendation.effort }}</td>
                            {% endif %}
                            {% if detail_level >= 3 %}
                            <td>{{ recommendation.description }}</td>
                            <td>{{ recommendation.impact }}</td>
                            {% endif %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
            
            {% if show_custom and custom_sections %}
            {% for title, content in custom_sections.items() %}
            <div class="section">
                <h2>{{ title }}</h2>
                <div>{{ content }}</div>
            </div>
            {% endfor %}
            {% endif %}
            
            <div class="footer">
                <p>End of Report - Generated on {{ report_date }}</p>
            </div>
        </body>
        </html>
        """
        
        # Prepare template data
        template_data = {
            "project_name": self.project_name,
            "report_date": self.report_date.strftime("%Y-%m-%d %H:%M"),
            "author": self.author,
            "summary": self.summary,
            "metrics": self.metrics,
            "milestones": self.milestones,
            "issues": self.issues,
            "risks": self.risks,
            "recommendations": self.recommendations,
            "custom_sections": self.custom_sections,
            "detail_level": self.detail_level,
            "show_summary": ReportSection.SUMMARY in self.sections,
            "show_metrics": ReportSection.METRICS in self.sections,
            "show_milestones": ReportSection.MILESTONES in self.sections,
            "show_issues": ReportSection.ISSUES in self.sections,
            "show_risks": ReportSection.RISKS in self.sections,
            "show_recommendations": ReportSection.RECOMMENDATIONS in self.sections,
            "show_custom": ReportSection.CUSTOM in self.sections
        }
        
        # Render template
        template = jinja2.Template(template_str)
        report_content = template.render(**template_data)
        
        if output_path:
            with open(output_path, "w") as f:
                f.write(report_content)
            return output_path
        
        return report_content
    
    def _generate_markdown_report(self, output_path: str = None) -> str:
        """Generate a Markdown report."""
        lines = []
        
        # Header
        lines.append(f"# {self.project_name} - Progress Report")
        lines.append(f"**Date:** {self.report_date.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Author:** {self.author}")
        lines.append("")
        
        # Summary
        if ReportSection.SUMMARY in self.sections and self.summary:
            lines.append("## Summary")
            lines.append(self.summary)
            lines.append("")
        
        # Metrics
        if ReportSection.METRICS in self.sections and self.metrics:
            lines.append("## Metrics")
            for metric in self.metrics:
                target_str = f" (Target: {metric.target}{metric.unit})" if metric.target is not None else ""
                trend_str = ""
                if metric.trend is not None:
                    trend_str = " :arrow_up:" if metric.trend > 0 else " :arrow_down:" if metric.trend < 0 else " :arrow_right:"
                
                lines.append(f"### {metric.name}: {metric.value}{metric.unit}{target_str}{trend_str}")
                if self.detail_level >= 3 and metric.description:
                    lines.append(metric.description)
                lines.append("")
        
        # Milestones
        if ReportSection.MILESTONES in self.sections and self.milestones:
            lines.append("## Milestones")
            lines.append("| Milestone | Due Date | Status | Completion |")
            lines.append("| --- | --- | --- | --- |")
            for milestone in self.milestones:
                lines.append(f"| {milestone.title} | {milestone.due_date.strftime('%Y-%m-%d')} | {milestone.status} | {milestone.completion_percentage * 100:.1f}% |")
            
            if self.detail_level >= 3:
                lines.append("")
                for milestone in self.milestones:
                    lines.append(f"### {milestone.title}")
                    lines.append(f"**Due Date:** {milestone.due_date.strftime('%Y-%m-%d')}")
                    lines.append(f"**Status:** {milestone.status}")
                    lines.append(f"**Completion:** {milestone.completion_percentage * 100:.1f}%")
                    lines.append(milestone.description)
                    lines.append("")
        
        # Issues
        if ReportSection.ISSUES in self.sections and self.issues:
            lines.append("## Issues")
            lines.append("| Issue | Severity | Status | Assigned To |")
            lines.append("| --- | --- | --- | --- |")
            for issue in self.issues:
                assigned = issue.assigned_to or "Unassigned"
                lines.append(f"| {issue.title} | {issue.severity} | {issue.status} | {assigned} |")
            
            if self.detail_level >= 3:
                lines.append("")
                for issue in self.issues:
                    lines.append(f"### {issue.title}")
                    lines.append(f"**Severity:** {issue.severity}")
                    lines.append(f"**Status:** {issue.status}")
                    lines.append(f"**Assigned To:** {issue.assigned_to or 'Unassigned'}")
                    lines.append(issue.description)
                    lines.append("")
        
        # Risks
        if ReportSection.RISKS in self.sections and self.risks:
            lines.append("## Risks")
            lines.append("| Risk | Score | Status | Owner |")
            lines.append("| --- | --- | --- | --- |")
            for risk in self.risks:
                owner = risk.owner or "Unassigned"
                lines.append(f"| {risk.title} | {risk.risk_score:.2f} | {risk.status} | {owner} |")
            
            if self.detail_level >= 3:
                lines.append("")
                for risk in self.risks:
                    lines.append(f"### {risk.title}")
                    lines.append(f"**Score:** {risk.risk_score:.2f}")
                    lines.append(f"**Status:** {risk.status}")
                    lines.append(f"**Owner:** {risk.owner or 'Unassigned'}")
                    lines.append(risk.description)
                    lines.append(f"**Mitigation:** {risk.mitigation}")
                    lines.append("")
        
        # Recommendations
        if ReportSection.RECOMMENDATIONS in self.sections and self.recommendations:
            lines.append("## Recommendations")
            lines.append("| Recommendation | Priority | Effort |")
            lines.append("| --- | --- | --- |")
            for recommendation in self.recommendations:
                lines.append(f"| {recommendation.title} | {recommendation.priority} | {recommendation.effort} |")
            
            if self.detail_level >= 3:
                lines.append("")
                for recommendation in self.recommendations:
                    lines.append(f"### {recommendation.title}")
                    lines.append(f"**Priority:** {recommendation.priority}")
                    lines.append(f"**Effort:** {recommendation.effort}")
                    lines.append(recommendation.description)
                    lines.append(f"**Impact:** {recommendation.impact}")
                    lines.append("")
        
        # Custom sections
        if ReportSection.CUSTOM in self.sections and self.custom_sections:
            for title, content in self.custom_sections.items():
                lines.append(f"## {title}")
                lines.append(content)
                lines.append("")
        
        # Footer
        lines.append("---")
        lines.append(f"*End of Report - Generated on {self.report_date.strftime('%Y-%m-%d %H:%M:%S')}*")
        
        report_content = "\n".join(lines)
        
        if output_path:
            with open(output_path, "w") as f:
                f.write(report_content)
            return output_path
        
        return report_content
    
    def _generate_json_report(self, output_path: str = None) -> str:
        """Generate a JSON report."""
        report_data = {
            "project_name": self.project_name,
            "report_date": self.report_date.isoformat(),
            "report_id": self.report_id,
            "author": self.author,
            "stakeholder_type": self.stakeholder_type.name,
            "detail_level": self.detail_level,
            "format": self.format.name,
            "sections": [section.name for section in self.sections],
            "content": {
                "summary": self.summary if ReportSection.SUMMARY in self.sections else "",
                "metrics": [metric.to_dict() for metric in self.metrics] if ReportSection.METRICS in self.sections else [],
                "milestones": [milestone.to_dict() for milestone in self.milestones] if ReportSection.MILESTONES in self.sections else [],
                "issues": [issue.to_dict() for issue in self.issues] if ReportSection.ISSUES in self.sections else [],
                "risks": [risk.to_dict() for risk in self.risks] if ReportSection.RISKS in self.sections else [],
                "recommendations": [recommendation.to_dict() for recommendation in self.recommendations] if ReportSection.RECOMMENDATIONS in self.sections else [],
                "custom_sections": self.custom_sections if ReportSection.CUSTOM in self.sections else {}
            }
        }
        
        report_content = json.dumps(report_data, indent=2)
        
        if output_path:
            with open(output_path, "w") as f:
                f.write(report_content)
            return output_path
        
        return report_content
    
    def _generate_pdf_report(self, output_path: str = None) -> str:
        """Generate a PDF report."""
        try:
            import weasyprint
        except ImportError:
            raise ImportError("WeasyPrint is required for PDF export. Install with 'pip install weasyprint'")
        
        # Generate HTML content first
        html_content = self._generate_html_report()
        
        if not output_path:
            output_path = f"{self.report_id}.pdf"
        
        # Convert HTML to PDF
        weasyprint.HTML(string=html_content).write_pdf(output_path)
        
        return output_path
    
    def _generate_dashboard_report(self, output_path: str = None) -> str:
        """Generate an interactive dashboard report."""
        try:
            import dash
            import dash_core_components as dcc
            import dash_html_components as html
            import plotly.express as px
            import plotly.graph_objects as go
        except ImportError:
            raise ImportError("Dash and Plotly are required for dashboard export. Install with 'pip install dash plotly'")
        
        # Generate a self-contained HTML file with the dashboard
        if not output_path:
            output_path = f"{self.report_id}_dashboard.html"
        
        # Create figures for metrics
        figures = []
        
        # Metrics visualization
        if ReportSection.METRICS in self.sections and self.metrics:
            # Create a gauge chart for each metric
            for metric in self.metrics:
                if metric.target is not None:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=metric.value,
                        title={"text": metric.name},
                        gauge={
                            "axis": {"range": [0, metric.target * 1.5]},
                            "bar": {"color": "#3498db"},
                            "steps": [
                                {"range": [0, metric.target * 0.6], "color": "#e74c3c"},
                                {"range": [metric.target * 0.6, metric.target * 0.8], "color": "#f39c12"},
                                {"range": [metric.target * 0.8, metric.target * 1.2], "color": "#27ae60"}
                            ],
                            "threshold": {
                                "line": {"color": "red", "width": 4},
                                "thickness": 0.75,
                                "value": metric.target
                            }
                        }
                    ))
                    figures.append((f"metric_{metric.name.lower().replace(' ', '_')}", fig))
        
        # Milestones visualization
        if ReportSection.MILESTONES in self.sections and self.milestones:
            # Create a timeline chart for milestones
            milestone_df = pd.DataFrame([
                {
                    "Milestone": m.title,
                    "Start": m.due_date - datetime.timedelta(days=30),  # Assuming 30 days before due date
                    "Finish": m.due_date,
                    "Completion": m.completion_percentage * 100,
                    "Status": m.status
                }
                for m in self.milestones
            ])
            
            fig = px.timeline(
                milestone_df, 
                x_start="Start", 
                x_end="Finish", 
                y="Milestone",
                color="Status",
                hover_data=["Completion"]
            )
            fig.update_layout(title="Project Milestones")
            figures.append(("milestones_timeline", fig))
            
            # Create a completion bar chart
            fig = px.bar(
                milestone_df,
                x="Milestone",
                y="Completion",
                color="Status",
                title="Milestone Completion"
            )
            figures.append(("milestones_completion", fig))
        
        # Issues visualization
        if ReportSection.ISSUES in self.sections and self.issues:
            # Create a pie chart for issues by severity
            severity_counts = {}
            for issue in self.issues:
                severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            
            fig = px.pie(
                values=list(severity_counts.values()),
                names=list(severity_counts.keys()),
                title="Issues by Severity"
            )
            figures.append(("issues_by_severity", fig))
            
            # Create a pie chart for issues by status
            status_counts = {}
            for issue in self.issues:
                status_counts[issue.status] = status_counts.get(issue.status, 0) + 1
            
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Issues by Status"
            )
            figures.append(("issues_by_status", fig))
        
        # Risks visualization
        if ReportSection.RISKS in self.sections and self.risks:
            # Create a scatter plot for risks (probability vs. impact)
            risk_df = pd.DataFrame([
                {
                    "Risk": r.title,
                    "Probability": r.probability,
                    "Impact": r.impact,
                    "Score": r.risk_score,
                    "Status": r.status
                }
                for r in self.risks
            ])
            
            fig = px.scatter(
                risk_df,
                x="Probability",
                y="Impact",
                size="Score",
                color="Status",
                hover_name="Risk",
                title="Risk Matrix"
            )
            fig.update_layout(
                xaxis={"title": "Probability", "range": [0, 1]},
                yaxis={"title": "Impact", "range": [0, 1]}
            )
            figures.append(("risk_matrix", fig))
        
        # Generate HTML with all figures
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{self.project_name} - Dashboard</title>",
            "<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }",
            ".header { margin-bottom: 20px; }",
            ".dashboard { display: flex; flex-wrap: wrap; gap: 20px; }",
            ".chart { flex: 1; min-width: 500px; height: 400px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 15px; border-radius: 5px; }",
            "</style>",
            "</head>",
            "<body>",
            "<div class='header'>",
            f"<h1>{self.project_name} - Progress Dashboard</h1>",
            f"<p>Date: {self.report_date.strftime('%Y-%m-%d %H:%M')}</p>",
            "</div>",
            "<div class='dashboard'>"
        ]
        
        # Add each figure
        for fig_id, fig in figures:
            html_parts.append(f"<div id='{fig_id}' class='chart'></div>")
        
        html_parts.append("</div>")  # Close dashboard div
        
        # Add scripts to render figures
        html_parts.append("<script>")
        for fig_id, fig in figures:
            fig_json = fig.to_json()
            html_parts.append(f"Plotly.newPlot('{fig_id}', {fig_json});")
        html_parts.append("</script>")
        
        html_parts.extend([
            "</body>",
            "</html>"
        ])
        
        html_content = "\n".join(html_parts)
        
        with open(output_path, "w") as f:
            f.write(html_content)
        
        return output_path
    
    def to_dict(self) -> Dict:
        """
        Convert report to dictionary for serialization.
        
        Returns:
            Dictionary representation of the report
        """
        return {
            "project_name": self.project_name,
            "report_date": self.report_date.isoformat(),
            "report_id": self.report_id,
            "author": self.author,
            "stakeholder_type": self.stakeholder_type.name,
            "detail_level": self.detail_level,
            "format": self.format.name,
            "sections": [section.name for section in self.sections],
            "summary": self.summary,
            "metrics": [metric.to_dict() for metric in self.metrics],
            "issues": [issue.to_dict() for issue in self.issues],
            "risks": [risk.to_dict() for risk in self.risks],
            "milestones": [milestone.to_dict() for milestone in self.milestones],
            "recommendations": [recommendation.to_dict() for recommendation in self.recommendations],
            "custom_sections": self.custom_sections
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProgressReport':
        """
        Create report from dictionary.
        
        Args:
            data: Dictionary representation of a report
            
        Returns:
            ProgressReport object
        """
        report = cls(
            project_name=data["project_name"],
            report_date=datetime.datetime.fromisoformat(data["report_date"])
        )
        
        report.report_id = data.get("report_id", report.report_id)
        report.author = data.get("author", report.author)
        report.stakeholder_type = StakeholderType[data["stakeholder_type"]]
        report.detail_level = data.get("detail_level", report.detail_level)
        report.format = ReportFormat[data["format"]]
        report.sections = [ReportSection[section] for section in data["sections"]]
        report.summary = data.get("summary", "")
        
        # Load metrics
        for metric_data in data.get("metrics", []):
            report.add_metric(ReportMetric.from_dict(metric_data))
        
        # Load issues
        for issue_data in data.get("issues", []):
            report.add_issue(ReportIssue.from_dict(issue_data))
        
        # Load risks
        for risk_data in data.get("risks", []):
            report.add_risk(ReportRisk.from_dict(risk_data))
        
        # Load milestones
        for milestone_data in data.get("milestones", []):
            report.add_milestone(ReportMilestone.from_dict(milestone_data))
        
        # Load recommendations
        for recommendation_data in data.get("recommendations", []):
            report.add_recommendation(ReportRecommendation.from_dict(recommendation_data))
        
        # Load custom sections
        report.custom_sections = data.get("custom_sections", {})
        
        return report


class ProgressReportGenerator:
    """
    Generates progress reports based on project data.
    """
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize a new progress report generator.
        
        Args:
            templates_dir: Directory containing report templates
        """
        self.templates_dir = templates_dir
        self.templates: Dict[str, ReportTemplate] = {}
        
        # Load default templates
        self._load_default_templates()
    
    def _load_default_templates(self) -> None:
        """Load default report templates."""
        # Executive template
        executive_template = ReportTemplate(
            name="Executive Summary",
            description="High-level overview for executives",
            stakeholder_type=StakeholderType.EXECUTIVE,
            format=ReportFormat.HTML,
            sections=[
                ReportSection.SUMMARY,
                ReportSection.METRICS,
                ReportSection.MILESTONES,
                ReportSection.RISKS
            ],
            detail_level=1
        )
        self.templates["executive"] = executive_template
        
        # Manager template
        manager_template = ReportTemplate(
            name="Manager Report",
            description="Detailed report for project managers",
            stakeholder_type=StakeholderType.MANAGER,
            format=ReportFormat.HTML,
            sections=[
                ReportSection.SUMMARY,
                ReportSection.METRICS,
                ReportSection.MILESTONES,
                ReportSection.ISSUES,
                ReportSection.RISKS,
                ReportSection.RECOMMENDATIONS
            ],
            detail_level=3
        )
        self.templates["manager"] = manager_template
        
        # Developer template
        developer_template = ReportTemplate(
            name="Developer Report",
            description="Technical report for developers",
            stakeholder_type=StakeholderType.DEVELOPER,
            format=ReportFormat.MARKDOWN,
            sections=[
                ReportSection.SUMMARY,
                ReportSection.TASKS,
                ReportSection.ISSUES,
                ReportSection.MILESTONES
            ],
            detail_level=5
        )
        self.templates["developer"] = developer_template
        
        # Client template
        client_template = ReportTemplate(
            name="Client Report",
            description="Progress report for clients",
            stakeholder_type=StakeholderType.CLIENT,
            format=ReportFormat.PDF,
            sections=[
                ReportSection.SUMMARY,
                ReportSection.MILESTONES,
                ReportSection.METRICS
            ],
            detail_level=2
        )
        self.templates["client"] = client_template
    
    def add_template(self, template_id: str, template: ReportTemplate) -> None:
        """
        Add a report template.
        
        Args:
            template_id: Unique template identifier
            template: Template to add
        """
        self.templates[template_id] = template
    
    def get_template(self, template_id: str) -> ReportTemplate:
        """
        Get a report template by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            ReportTemplate object
        """
        if template_id not in self.templates:
            raise ValueError(f"Template with ID {template_id} not found")
        
        return self.templates[template_id]
    
    def list_templates(self) -> List[Tuple[str, str, StakeholderType]]:
        """
        List all available report templates.
        
        Returns:
            List of (template_id, name, stakeholder_type) tuples
        """
        return [
            (template_id, template.name, template.stakeholder_type)
            for template_id, template in self.templates.items()
        ]
    
    def generate_from_template(self, project_name: str, template_id: str, 
                              data_sources: Dict[str, Any] = None) -> ProgressReport:
        """
        Generate a progress report using a template and data sources.
        
        Args:
            project_name: Name of the project
            template_id: Template identifier
            data_sources: Dictionary of data sources (optional)
            
        Returns:
            Generated ProgressReport object
        """
        if template_id not in self.templates:
            raise ValueError(f"Template with ID {template_id} not found")
        
        template = self.templates[template_id]
        
        # Create report with template settings
        report = ProgressReport(project_name)
        report.set_stakeholder_type(template.stakeholder_type)
        report.set_detail_level(template.detail_level)
        report.set_format(template.format)
        report.set_sections(template.sections)
        
        # If no data sources provided, return empty report with template settings
        if not data_sources:
            return report
        
        # Process data sources
        if "summary" in data_sources:
            report.set_summary(data_sources["summary"])
        
        if "metrics" in data_sources:
            for metric_data in data_sources["metrics"]:
                if isinstance(metric_data, ReportMetric):
                    report.add_metric(metric_data)
                elif isinstance(metric_data, dict):
                    report.add_metric(ReportMetric.from_dict(metric_data))
        
        if "issues" in data_sources:
            for issue_data in data_sources["issues"]:
                if isinstance(issue_data, ReportIssue):
                    report.add_issue(issue_data)
                elif isinstance(issue_data, dict):
                    report.add_issue(ReportIssue.from_dict(issue_data))
        
        if "risks" in data_sources:
            for risk_data in data_sources["risks"]:
                if isinstance(risk_data, ReportRisk):
                    report.add_risk(risk_data)
                elif isinstance(risk_data, dict):
                    report.add_risk(ReportRisk.from_dict(risk_data))
        
        if "milestones" in data_sources:
            for milestone_data in data_sources["milestones"]:
                if isinstance(milestone_data, ReportMilestone):
                    report.add_milestone(milestone_data)
                elif isinstance(milestone_data, dict):
                    report.add_milestone(ReportMilestone.from_dict(milestone_data))
        
        if "recommendations" in data_sources:
            for recommendation_data in data_sources["recommendations"]:
                if isinstance(recommendation_data, ReportRecommendation):
                    report.add_recommendation(recommendation_data)
                elif isinstance(recommendation_data, dict):
                    report.add_recommendation(ReportRecommendation.from_dict(recommendation_data))
        
        if "custom_sections" in data_sources:
            for title, content in data_sources["custom_sections"].items():
                report.add_custom_section(title, content)
        
        # Process Gantt chart data if available
        if MODULES_AVAILABLE and "gantt_chart" in data_sources:
            gantt_chart = data_sources["gantt_chart"]
            if isinstance(gantt_chart, GanttChart):
                self._process_gantt_chart(report, gantt_chart)
        
        # Process resource allocation data if available
        if MODULES_AVAILABLE and "resource_allocator" in data_sources:
            resource_allocator = data_sources["resource_allocator"]
            if isinstance(resource_allocator, ResourceAllocator):
                self._process_resource_allocator(report, resource_allocator)
        
        return report
    
    def _process_gantt_chart(self, report: ProgressReport, gantt_chart: 'GanttChart') -> None:
        """Process Gantt chart data for the report."""
        # Add project duration metric
        report.add_metric(ReportMetric(
            name="Project Duration",
            value=gantt_chart.get_project_duration(),
            unit=" days",
            description="Total duration of the project in days"
        ))
        
        # Add project progress metric
        report.add_metric(ReportMetric(
            name="Project Progress",
            value=round(gantt_chart.get_project_progress() * 100, 1),
            unit="%",
            target=100,
            description="Overall project completion percentage"
        ))
        
        # Add milestones
        for task in gantt_chart.get_all_tasks():
            if task.milestone:
                status = "Completed" if task.progress >= 1.0 else "In Progress" if task.progress > 0 else "Not Started"
                
                # Check if milestone is delayed
                if status != "Completed" and task.end_date < datetime.datetime.now():
                    status = "Delayed"
                
                report.add_milestone(ReportMilestone(
                    id=task.id,
                    title=task.name,
                    description=f"Milestone in the project timeline",
                    due_date=task.end_date,
                    status=status,
                    completion_percentage=task.progress
                ))
        
        # Add custom section with Gantt chart visualization if HTML format
        if report.format == ReportFormat.HTML:
            # Create a temporary file for the Gantt chart image
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            chart_path = os.path.join(temp_dir, f"gantt_{report.report_id}.png")
            
            # Export the Gantt chart as an image
            gantt_chart.export_image(os.path.splitext(chart_path)[0], dpi=100)
            
            # Add the image to the report as a custom section
            img_html = f'<img src="data:image/png;base64,{self._image_to_base64(chart_path)}" alt="Gantt Chart" style="max-width:100%;">'
            report.add_custom_section("Project Timeline", img_html)
    
    def _process_resource_allocator(self, report: ProgressReport, allocator: 'ResourceAllocator') -> None:
        """Process resource allocation data for the report."""
        # Calculate allocation metrics
        metrics = allocator.calculate_allocation_metrics()
        
        # Add resource utilization metrics
        report.add_metric(ReportMetric(
            name="Resource Utilization",
            value=round(sum(metrics["resource_utilization"].values()) / len(metrics["resource_utilization"]) if metrics["resource_utilization"] else 0, 1),
            unit="%",
            target=80,
            description="Average utilization of all resources"
        ))
        
        report.add_metric(ReportMetric(
            name="Task Allocation",
            value=round(metrics["allocation_percentage"], 1),
            unit="%",
            target=100,
            description="Percentage of estimated hours that have been allocated to resources"
        ))
        
        # Add resource allocation details as a custom section
        if report.format == ReportFormat.HTML:
            html_content = """
            <div>
                <h3>Resource Allocation Details</h3>
                <table style="width:100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Resource</th>
                            <th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Utilization</th>
                            <th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Allocated Hours</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for resource_id, resource in allocator.resources.items():
                utilization = metrics["resource_utilization"].get(resource_id, 0)
                allocated_hours = sum(resource.current_allocation.values())
                
                html_content += f"""
                <tr>
                    <td style="padding:8px; border-bottom:1px solid #ddd;">{resource.name}</td>
                    <td style="padding:8px; border-bottom:1px solid #ddd;">{utilization:.1f}%</td>
                    <td style="padding:8px; border-bottom:1px solid #ddd;">{allocated_hours:.1f}</td>
                </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
            </div>
            """
            
            report.add_custom_section("Resource Allocation", html_content)
    
    def _image_to_base64(self, image_path: str) -> str:
        """Convert an image file to base64 encoding."""
        import base64
        
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def save_template(self, template_id: str, filename: str) -> str:
        """
        Save a report template to a JSON file.
        
        Args:
            template_id: Template identifier
            filename: Output filename
            
        Returns:
            Path to the saved file
        """
        if template_id not in self.templates:
            raise ValueError(f"Template with ID {template_id} not found")
        
        template = self.templates[template_id]
        
        with open(filename, "w") as f:
            json.dump(template.to_dict(), f, indent=2)
        
        return filename
    
    def load_template(self, template_id: str, filename: str) -> ReportTemplate:
        """
        Load a report template from a JSON file.
        
        Args:
            template_id: Template identifier
            filename: Input filename
            
        Returns:
            Loaded ReportTemplate object
        """
        with open(filename, "r") as f:
            template_data = json.load(f)
        
        template = ReportTemplate.from_dict(template_data)
        self.templates[template_id] = template
        
        return template


class ProgressReportManager:
    """
    Manager for creating and maintaining multiple progress reports.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize a new progress report manager.
        
        Args:
            storage_dir: Directory for storing report data
        """
        self.storage_dir = storage_dir or os.path.join(os.getcwd(), "progress_reports")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.reports: Dict[str, ProgressReport] = {}
        self.generator = ProgressReportGenerator()
    
    def create_report(self, project_name: str, template_id: str = "manager",
                     data_sources: Dict[str, Any] = None) -> ProgressReport:
        """
        Create a new progress report.
        
        Args:
            project_name: Name of the project
            template_id: Template identifier (defaults to "manager")
            data_sources: Dictionary of data sources (optional)
            
        Returns:
            New ProgressReport object
        """
        report = self.generator.generate_from_template(project_name, template_id, data_sources)
        self.reports[report.report_id] = report
        
        return report
    
    def get_report(self, report_id: str) -> ProgressReport:
        """
        Get a progress report by ID.
        
        Args:
            report_id: Report identifier
            
        Returns:
            ProgressReport object
        """
        if report_id not in self.reports:
            raise ValueError(f"Report with ID {report_id} not found")
        
        return self.reports[report_id]
    
    def list_reports(self, project_name: str = None) -> List[Tuple[str, str, datetime.datetime]]:
        """
        List all available progress reports.
        
        Args:
            project_name: Filter by project name (optional)
            
        Returns:
            List of (report_id, project_name, report_date) tuples
        """
        if project_name:
            return [
                (report_id, report.project_name, report.report_date)
                for report_id, report in self.reports.items()
                if report.project_name == project_name
            ]
        else:
            return [
                (report_id, report.project_name, report.report_date)
                for report_id, report in self.reports.items()
            ]
    
    def save_report(self, report_id: str) -> str:
        """
        Save a progress report to disk.
        
        Args:
            report_id: Report identifier
            
        Returns:
            Path to the saved file
        """
        if report_id not in self.reports:
            raise ValueError(f"Report with ID {report_id} not found")
        
        report = self.reports[report_id]
        filename = os.path.join(self.storage_dir, f"{report_id}.json")
        
        with open(filename, "w") as f:
            json.dump(report.to_dict(), f, indent=2)
        
        return filename
    
    def load_report(self, filename: str) -> ProgressReport:
        """
        Load a progress report from disk.
        
        Args:
            filename: Input filename
            
        Returns:
            Loaded ProgressReport object
        """
        with open(filename, "r") as f:
            report_data = json.load(f)
        
        report = ProgressReport.from_dict(report_data)
        self.reports[report.report_id] = report
        
        return report
    
    def delete_report(self, report_id: str) -> None:
        """
        Delete a progress report.
        
        Args:
            report_id: Report identifier
        """
        if report_id not in self.reports:
            raise ValueError(f"Report with ID {report_id} not found")
        
        # Remove from memory
        del self.reports[report_id]
        
        # Remove from disk if exists
        filename = os.path.join(self.storage_dir, f"{report_id}.json")
        if os.path.exists(filename):
            os.remove(filename)
    
    def generate_report_file(self, report_id: str, output_dir: str = None) -> str:
        """
        Generate a report file in the specified format.
        
        Args:
            report_id: Report identifier
            output_dir: Output directory (defaults to storage_dir)
            
        Returns:
            Path to the generated file
        """
        if report_id not in self.reports:
            raise ValueError(f"Report with ID {report_id} not found")
        
        report = self.reports[report_id]
        output_dir = output_dir or self.storage_dir
        
        # Determine file extension based on format
        if report.format == ReportFormat.TEXT:
            ext = "txt"
        elif report.format == ReportFormat.HTML:
            ext = "html"
        elif report.format == ReportFormat.MARKDOWN:
            ext = "md"
        elif report.format == ReportFormat.JSON:
            ext = "json"
        elif report.format == ReportFormat.PDF:
            ext = "pdf"
        elif report.format == ReportFormat.DASHBOARD:
            ext = "html"
        else:
            ext = "txt"
        
        output_path = os.path.join(output_dir, f"{report_id}.{ext}")
        
        return report.generate_report(output_path)
    
    def save_all(self) -> List[str]:
        """
        Save all progress reports to disk.
        
        Returns:
            List of saved file paths
        """
        return [self.save_report(report_id) for report_id in self.reports]
    
    def load_all(self) -> List[str]:
        """
        Load all progress reports from disk.
        
        Returns:
            List of loaded report IDs
        """
        loaded = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                report = self.load_report(os.path.join(self.storage_dir, filename))
                loaded.append(report.report_id)
        
        return loaded
