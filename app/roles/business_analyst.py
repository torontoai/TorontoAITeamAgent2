"""TORONTO AI TEAM AGENT - Business Analyst Role Implementation

This module implements the Business Analyst role for the TORONTO AI TEAM AGENT system,
providing specialized knowledge, skills, and capabilities for business analysis tasks.

Copyright (c) 2025 TORONTO AI
Created by David Tadeusz Chudak
All rights reserved."""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..training.knowledge_extraction import KnowledgeExtractor
from ..training.knowledge_integration import KnowledgeIntegrator
from ..training.vector_db import VectorDBManager
from ..training.config import TrainingConfig
from ..collaboration.hierarchy.role_manager import Role

logger = logging.getLogger(__name__)

class BusinessAnalystRole:
    """Implementation of the Business Analyst role for the TORONTO AI TEAM AGENT system.
    
    The Business Analyst role bridges the gap between technical teams and non-technical
    stakeholders, ensuring requirements are well-understood and communicated."""
    
    def __init__(
        self,
        training_config: TrainingConfig,
        vector_db_manager: VectorDBManager,
        knowledge_integrator: KnowledgeIntegrator
    ):
        """Initialize the Business Analyst role.
        
        Args:
            training_config: Training system configuration
            vector_db_manager: Vector database manager
            knowledge_integrator: Knowledge integrator"""
        self.training_config = training_config
        self.vector_db_manager = vector_db_manager
        self.knowledge_integrator = knowledge_integrator
        self.role_id = "business_analyst"
        self.collection_name = f"{self.role_id}_knowledge"
        
        # Create knowledge extractor
        self.knowledge_extractor = KnowledgeExtractor(
            chunk_size=training_config.chunk_size,
            chunk_overlap=training_config.chunk_overlap,
            embedding_model=training_config.embedding_model
        )
    
    def get_role_definition(self) -> Role:
        """Get the role definition for the Business Analyst.
        
        Returns:
            Role definition"""
        return Role(
            role_id=self.role_id,
            role_name="Business Analyst",
            role_description="Bridges the gap between technical teams and non-technical stakeholders, ensuring requirements are well-understood and communicated.",
            tier="core",
            responsibilities=[
                "Requirements gathering and analysis",
                "Business process modeling",
                "Stakeholder analysis and communication",
                "Data analysis for business insights",
                "Documentation of business requirements",
                "Gap analysis between current and future states",
                "Facilitation of workshops and meetings",
                "Creation of business cases"
            ],
            authority_level="medium",
            required_skills=[
                "Business analysis",
                "Requirements engineering",
                "Process modeling",
                "Data analysis",
                "Stakeholder management",
                "Communication",
                "Documentation",
                "Problem solving"
            ],
            reports_to="project_manager",
            direct_reports=[],
            communication_channels=["email", "chat", "meetings", "documentation"],
            performance_metrics=[
                "Requirements quality",
                "Stakeholder satisfaction",
                "Documentation completeness",
                "Issue resolution time"
            ],
            suitable_for="both"  # Can be assigned to human or AI
        )
    
    def initialize_knowledge_base(self) -> Dict[str, Any]:
        """Initialize the knowledge base for the Business Analyst role with basic knowledge.
        
        Returns:
            Summary of the initialization"""
        # Create output directory
        output_dir = os.path.join(self.training_config.data_dir, "roles", self.role_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create basic knowledge
        knowledge_chunks = self._create_basic_knowledge()
        
        # Store in vector database
        logger.info(f"Storing {len(knowledge_chunks)} chunks in vector database")
        self.vector_db_manager.create_collection(self.collection_name)
        self.vector_db_manager.add_documents(self.collection_name, knowledge_chunks)
        
        # Integrate with existing knowledge
        logger.info("Integrating with existing knowledge")
        self.knowledge_integrator.integrate_knowledge(
            collection_name=self.collection_name,
            role=self.role_id,
            source="base_knowledge"
        )
        
        # Create initialization summary
        initialization_summary = {
            "role": self.role_id,
            "knowledge_chunks": len(knowledge_chunks),
            "collection_name": self.collection_name,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save initialization summary
        summary_filepath = os.path.join(output_dir, f"{self.role_id}_initialization_summary.json")
        with open(summary_filepath, 'w') as f:
            json.dump(initialization_summary, f, indent=2)
        
        logger.info(f"Knowledge base initialization completed for role: {self.role_id}")
        return initialization_summary
    
    def _create_basic_knowledge(self) -> List[Any]:
        """Create basic knowledge for the Business Analyst role.
        
        Returns:
            List of knowledge chunks"""
        # Basic knowledge text
        basic_knowledge = """
# Business Analysis Fundamentals

Business analysis is the practice of enabling change in an organizational context by defining needs and recommending solutions that deliver value to stakeholders. The business analyst is responsible for identifying and articulating the needs of the business and its stakeholders, and helping to determine solutions to business problems.

## Core Concepts

### Requirements Engineering

Requirements engineering is the process of defining, documenting, and maintaining requirements in the engineering design process. It involves:

1. **Elicitation**: Gathering requirements from stakeholders through interviews, workshops, surveys, and observation.
2. **Analysis**: Examining, refining, and organizing requirements to ensure they are clear, complete, consistent, and testable.
3. **Specification**: Documenting requirements in a structured format that can be understood by all stakeholders.
4. **Validation**: Confirming that requirements accurately represent stakeholder needs.
5. **Management**: Tracking and controlling changes to requirements throughout the project lifecycle.

### Business Process Modeling

Business process modeling is the activity of representing processes of an enterprise, so that the current process may be analyzed, improved, and automated. Common notation systems include:

1. **BPMN (Business Process Model and Notation)**: A graphical representation for specifying business processes in a workflow.
2. **UML Activity Diagrams**: Visual representations of workflows of stepwise activities and actions.
3. **Flowcharts**: Simple diagrams that map out a process, helping to understand it better.
4. **Value Stream Mapping**: A lean-management method for analyzing the current state and designing a future state for the series of events that take a product or service from its beginning through to the customer.

### Stakeholder Analysis

Stakeholder analysis is the process of identifying and analyzing stakeholders, and systematically gathering and analyzing qualitative information to determine whose interests should be taken into account throughout the project. It involves:

1. **Identification**: Determining who the stakeholders are.
2. **Analysis**: Assessing their interests, influence, and impact on the project.
3. **Prioritization**: Ranking stakeholders based on their importance to the project.
4. **Engagement**: Developing strategies for effectively communicating and working with stakeholders.

### Data Analysis for Business

Data analysis in business involves examining data sets to draw conclusions about the information they contain. It includes:

1. **Descriptive Analysis**: Understanding what happened in the past.
2. **Diagnostic Analysis**: Understanding why something happened.
3. **Predictive Analysis**: Forecasting what might happen in the future.
4. **Prescriptive Analysis**: Determining what should be done to achieve a desired outcome.

## Key Techniques

### SWOT Analysis

SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis is a framework used to evaluate a company's competitive position and to develop strategic planning. It involves identifying:

1. **Strengths**: Internal factors that give an advantage over others.
2. **Weaknesses**: Internal factors that place the business at a disadvantage.
3. **Opportunities**: External factors that could be exploited to the advantage.
4. **Threats**: External factors that could cause trouble for the business.

### PESTLE Analysis

PESTLE analysis is a framework used to analyze the external factors that might impact an organization. It examines:

1. **Political**: Government policies, political stability, trade regulations.
2. **Economic**: Economic growth, interest rates, inflation, unemployment.
3. **Social**: Cultural aspects, health consciousness, population growth rate.
4. **Technological**: Technological advancements, R&D activity, automation.
5. **Legal**: Discrimination laws, consumer laws, employment laws.
6. **Environmental**: Environmental regulations, climate change, sustainability.

### MoSCoW Prioritization

MoSCoW is a prioritization technique used in business analysis to reach a common understanding with stakeholders on the importance they place on the delivery of each requirement. It stands for:

1. **Must Have**: Requirements that are critical to the current delivery.
2. **Should Have**: Important but not vital requirements.
3. **Could Have**: Desirable but not necessary requirements.
4. **Won't Have**: Requirements that are not a priority for the current delivery.

### Use Case Modeling

Use case modeling is a technique used to identify, clarify, and organize system requirements. It involves:

1. **Actors**: Users or systems that interact with the system being modeled.
2. **Use Cases**: Specific actions that actors can perform with the system.
3. **Relationships**: Connections between actors and use cases, or between different use cases.

## Tools and Methodologies

### Requirements Management Tools

1. **JIRA**: Issue and project tracking software.
2. **Confluence**: Collaboration and documentation platform.
3. **ReqView**: Requirements management tool.
4. **Modern Requirements**: Requirements management suite integrated with Microsoft Office.

### Business Intelligence Tools

1. **Tableau**: Data visualization and business intelligence tool.
2. **Power BI**: Business analytics service by Microsoft.
3. **QlikView**: Business discovery platform.
4. **Looker**: Business intelligence software and big data analytics platform.

### Agile Methodologies

1. **Scrum**: Framework for developing, delivering, and sustaining complex products.
2. **Kanban**: Method for managing knowledge work with an emphasis on just-in-time delivery.
3. **Lean**: Methodology focused on eliminating waste and maximizing value.
4. **SAFe (Scaled Agile Framework)**: Framework for implementing agile practices at enterprise scale.

## Best Practices

### Effective Communication

1. **Active Listening**: Fully concentrating on what is being said rather than just passively hearing.
2. **Clear and Concise Writing**: Communicating information in a way that is easy to understand.
3. **Visual Communication**: Using diagrams, charts, and other visual aids to convey complex information.
4. **Tailored Communication**: Adapting communication style and content based on the audience.

### Documentation Standards

1. **Consistency**: Using consistent terminology, formatting, and structure.
2. **Traceability**: Ensuring requirements can be traced back to business objectives and forward to design elements.
3. **Version Control**: Maintaining a history of changes to requirements and other documents.
4. **Accessibility**: Making documentation available and understandable to all stakeholders.

### Continuous Learning

1. **Professional Development**: Pursuing certifications and training to enhance skills.
2. **Industry Knowledge**: Staying informed about trends and developments in the industry.
3. **Feedback Loop**: Seeking and incorporating feedback to improve performance.
4. **Knowledge Sharing**: Contributing to the organization's knowledge base and mentoring others.

## Certifications

1. **IIBA CBAP (Certified Business Analysis Professional)**: Certification for experienced business analysts.
2. **IIBA CCBA (Certification of Capability in Business Analysis)**: Certification for business analysts with 2-3 years of experience.
3. **PMI-PBA (Professional in Business Analysis)**: Certification for business analysts working in project environments.
4. **BCS Business Analysis Certification**: Series of certifications offered by the British Computer Society.

# Business Analysis in Practice

## Requirements Gathering Techniques

### Interviews

Interviews are one-on-one or small group discussions with stakeholders to gather information about their needs, expectations, and constraints. Effective interviewing involves:

1. **Preparation**: Researching the interviewee and preparing questions in advance.
2. **Structure**: Following a logical flow from general to specific questions.
3. **Open-ended Questions**: Asking questions that encourage detailed responses.
4. **Active Listening**: Paying attention to verbal and non-verbal cues.
5. **Follow-up**: Clarifying and expanding on responses to gain deeper insights.

### Workshops

Workshops are facilitated sessions where stakeholders collaborate to define requirements, solve problems, or make decisions. Successful workshops require:

1. **Clear Objectives**: Defining what the workshop aims to achieve.
2. **Appropriate Participants**: Involving the right stakeholders with the necessary knowledge and authority.
3. **Structured Agenda**: Planning activities and timeframes to keep the workshop focused.
4. **Facilitation Techniques**: Using methods like brainstorming, affinity diagrams, and prioritization exercises.
5. **Documentation**: Recording decisions, actions, and outcomes.

### Surveys and Questionnaires

Surveys and questionnaires are tools for collecting information from a large number of stakeholders. They are useful for:

1. **Quantitative Data**: Gathering numerical data that can be analyzed statistically.
2. **Qualitative Insights**: Collecting opinions, preferences, and suggestions.
3. **Benchmarking**: Comparing results across different groups or over time.
4. **Validation**: Confirming findings from other requirements gathering techniques.

### Observation

Observation involves watching users perform their tasks to understand their workflows, challenges, and needs. It includes:

1. **Shadowing**: Following users as they perform their daily activities.
2. **Contextual Inquiry**: Combining observation with questions about what users are doing and why.
3. **Process Mapping**: Documenting the steps, decisions, and handoffs in a process.
4. **Pain Point Identification**: Noting inefficiencies, workarounds, and frustrations.

## Business Process Improvement

### As-Is Process Analysis

As-Is process analysis involves documenting and analyzing current business processes to understand how they work and identify areas for improvement. It includes:

1. **Process Documentation**: Creating detailed descriptions of existing processes.
2. **Process Mapping**: Visualizing workflows using diagrams and flowcharts.
3. **Metrics Collection**: Gathering data on process performance, such as cycle time, error rates, and resource utilization.
4. **Root Cause Analysis**: Identifying the underlying causes of process issues.

### To-Be Process Design

To-Be process design involves creating new or improved business processes that address the issues identified in the As-Is analysis. It includes:

1. **Process Redesign**: Developing new workflows that eliminate inefficiencies and add value.
2. **Automation Opportunities**: Identifying tasks that can be automated to improve efficiency.
3. **Role Definition**: Clarifying responsibilities and handoffs between process participants.
4. **Performance Targets**: Setting goals for the improved process, such as reduced cycle time or increased quality.

### Gap Analysis

Gap analysis is the comparison of actual performance with potential or desired performance. It helps identify:

1. **Performance Gaps**: Differences between current and desired process performance.
2. **Capability Gaps**: Skills, knowledge, or resources needed to implement the improved process.
3. **Technology Gaps**: Systems or tools required to support the new process.
4. **Implementation Strategies**: Approaches for closing the identified gaps.

## Business Case Development

### Problem Statement

A problem statement clearly articulates the business problem that needs to be solved. It should:

1. **Be Specific**: Clearly define the problem and its impact.
2. **Be Measurable**: Include quantifiable aspects of the problem.
3. **Be Relevant**: Connect to business objectives and stakeholder needs.
4. **Avoid Solutions**: Focus on the problem, not potential solutions.

### Solution Options

Solution options present alternative approaches to addressing the business problem. Each option should include:

1. **Description**: Clear explanation of what the solution entails.
2. **Benefits**: Expected positive outcomes and how they address the problem.
3. **Costs**: Financial and non-financial resources required.
4. **Risks**: Potential negative consequences and mitigation strategies.
5. **Feasibility**: Assessment of technical, operational, and organizational viability.

### Cost-Benefit Analysis

Cost-benefit analysis evaluates the financial and non-financial impacts of each solution option. It involves:

1. **Cost Estimation**: Calculating initial and ongoing costs.
2. **Benefit Quantification**: Assigning monetary values to expected benefits where possible.
3. **ROI Calculation**: Determining return on investment over time.
4. **Intangible Factors**: Considering benefits and costs that cannot be easily quantified.

### Recommendation

The recommendation presents the preferred solution option and justifies why it should be pursued. It should:

1. **Be Clear**: Explicitly state the recommended course of action.
2. **Be Justified**: Explain why this option is superior to alternatives.
3. **Address Risks**: Acknowledge potential issues and how they will be managed.
4. **Include Implementation Considerations**: Outline key steps and resources needed.

## Stakeholder Management

### Stakeholder Identification

Stakeholder identification involves determining who will be affected by or can influence the project. Methods include:

1. **Brainstorming**: Generating a list of potential stakeholders with the project team.
2. **Organizational Charts**: Reviewing formal structures to identify relevant roles and departments.
3. **RACI Matrix**: Defining who is Responsible, Accountable, Consulted, and Informed.
4. **Previous Project Review**: Examining stakeholder lists from similar past projects.

### Stakeholder Analysis

Stakeholder analysis assesses each stakeholder's interest, influence, and attitude toward the project. Tools include:

1. **Power/Interest Grid**: Mapping stakeholders based on their power to influence the project and their interest in it.
2. **Influence/Impact Matrix**: Categorizing stakeholders based on their influence over and impact from the project.
3. **Salience Model**: Evaluating stakeholders based on power, legitimacy, and urgency.
4. **Stakeholder Engagement Assessment Matrix**: Analyzing current and desired engagement levels.

### Stakeholder Engagement

Stakeholder engagement involves developing and implementing strategies to effectively involve stakeholders in the project. It includes:

1. **Communication Planning**: Determining what information to share with each stakeholder, when, and how.
2. **Relationship Building**: Establishing trust and rapport with key stakeholders.
3. **Expectation Management**: Ensuring stakeholders have realistic expectations about the project.
4. **Conflict Resolution**: Addressing disagreements and competing interests constructively.

## Data Analysis Techniques

### Descriptive Statistics

Descriptive statistics summarize and describe the main features of a dataset. Common measures include:

1. **Central Tendency**: Mean, median, and mode.
2. **Dispersion**: Range, variance, and standard deviation.
3. **Distribution**: Frequency distributions and percentiles.
4. **Correlation**: Relationships between variables.

### Data Visualization

Data visualization presents data in graphical or pictorial format to facilitate understanding and analysis. Common types include:

1. **Bar Charts**: Comparing values across categories.
2. **Line Charts**: Showing trends over time.
3. **Pie Charts**: Displaying proportions of a whole.
4. **Scatter Plots**: Revealing relationships between two variables.
5. **Heat Maps**: Showing patterns in complex datasets.

### Trend Analysis

Trend analysis identifies patterns and changes in data over time. Techniques include:

1. **Time Series Analysis**: Examining data points collected at regular intervals.
2. **Moving Averages**: Smoothing data to highlight long-term trends.
3. **Regression Analysis**: Modeling relationships between variables to predict future values.
4. **Seasonality Analysis**: Identifying recurring patterns within time periods.

### Root Cause Analysis

Root cause analysis is a problem-solving method used to identify the underlying causes of issues. Approaches include:

1. **5 Whys**: Repeatedly asking why to drill down to the root cause.
2. **Fishbone Diagram (Ishikawa)**: Categorizing potential causes of a problem.
3. **Pareto Analysis**: Identifying the 20% of causes that create 80% of problems.
4. **Fault Tree Analysis**: Breaking down a problem into its contributing factors.
"""
        
        # Chunk the text
        chunks = self.knowledge_extractor.extract_chunks(basic_knowledge)
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata.update({
                "source": "base_knowledge",
                "role": self.role_id,
                "category": "fundamentals"
            })
        
        return chunks
