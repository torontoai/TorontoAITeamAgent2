"""
Grok 3 MaAS integration module.

This module provides integration between Grok 3 and the Multi-agent Architecture Search (MaAS) framework.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple

from app.models.adapters.model_adapter import Grok3Adapter
from app.models.adapters.reasoning_adapters import ReasoningGrok3Adapter
from app.code_execution.code_execution import CodeExecutionGrok3Adapter

# Set up logging
logger = logging.getLogger(__name__)

class Grok3MaaSIntegration:
    """
    Integration class for Grok 3 and the Multi-agent Architecture Search (MaAS) framework.
    
    This class provides methods for creating and optimizing agent architectures using Grok 3's
    advanced reasoning capabilities.
    """
    
    def __init__(
        self,
        grok3_adapter: Optional[Grok3Adapter] = None,
        reasoning_adapter: Optional[ReasoningGrok3Adapter] = None,
        code_execution_adapter: Optional[CodeExecutionGrok3Adapter] = None,
        supernet = None,
        evaluator = None,
        search_algorithm = None
    ):
        """
        Initialize the Grok3MaaSIntegration.
        
        Args:
            grok3_adapter: Optional Grok3Adapter instance.
            reasoning_adapter: Optional ReasoningGrok3Adapter instance.
            code_execution_adapter: Optional CodeExecutionGrok3Adapter instance.
            supernet: Optional AgenticSupernet instance.
            evaluator: Optional ArchitectureEvaluator instance.
            search_algorithm: Optional SearchAlgorithm instance.
        """
        self.grok3_adapter = grok3_adapter or Grok3Adapter()
        self.reasoning_adapter = reasoning_adapter or ReasoningGrok3Adapter(self.grok3_adapter)
        self.code_execution_adapter = code_execution_adapter or CodeExecutionGrok3Adapter(self.grok3_adapter, self.reasoning_adapter)
        
        # Store MaAS components
        self.supernet = supernet
        self.evaluator = evaluator
        self.search_algorithm = search_algorithm
        
        logger.info("Initialized Grok3MaaSIntegration")
    
    def create_grok3_architecture_template(
        self,
        template_name: str,
        num_agents: int = 3,
        use_reasoning: bool = True,
        use_code_execution: bool = True,
        architecture_type: str = "hierarchical"
    ) -> Dict[str, Any]:
        """
        Create a Grok 3-powered architecture template.
        
        Args:
            template_name: Name of the template.
            num_agents: Number of agents in the architecture.
            use_reasoning: Whether to enable advanced reasoning capabilities.
            use_code_execution: Whether to enable code execution capabilities.
            architecture_type: Type of architecture (hierarchical, mesh, star, pipeline, hybrid).
        
        Returns:
            Architecture template as a dictionary.
        """
        if not self.supernet:
            logger.warning("AgenticSupernet not provided, creating basic template")
            return self._create_basic_template(
                template_name=template_name,
                num_agents=num_agents,
                use_reasoning=use_reasoning,
                use_code_execution=use_code_execution,
                architecture_type=architecture_type
            )
        
        # Use the supernet to create a template
        template_config = {
            "name": template_name,
            "num_agents": num_agents,
            "capabilities": {
                "reasoning": use_reasoning,
                "code_execution": use_code_execution
            },
            "architecture_type": architecture_type,
            "model": "grok-3"
        }
        
        return self.supernet.create_architecture_template(template_config)
    
    def optimize_architecture_for_task(
        self,
        task_description: str,
        initial_template: Optional[Dict[str, Any]] = None,
        optimization_steps: int = 3
    ) -> Dict[str, Any]:
        """
        Optimize an architecture for a specific task using Grok 3's reasoning capabilities.
        
        Args:
            task_description: Description of the task.
            initial_template: Optional initial architecture template.
            optimization_steps: Number of optimization steps to perform.
        
        Returns:
            Optimized architecture as a dictionary.
        """
        if not all([self.supernet, self.evaluator, self.search_algorithm]):
            logger.warning("MaAS components not provided, using reasoning to create architecture")
            return self._create_architecture_with_reasoning(
                task_description=task_description,
                initial_template=initial_template
            )
        
        # Use MaAS components to optimize the architecture
        if initial_template is None:
            initial_template = self.create_grok3_architecture_template(
                template_name="task_optimized",
                num_agents=3,
                use_reasoning=True,
                use_code_execution=True
            )
        
        # Analyze the task to determine required capabilities
        task_analysis = self._analyze_task(task_description)
        
        # Configure the search algorithm
        search_config = {
            "task_description": task_description,
            "task_analysis": task_analysis,
            "initial_template": initial_template,
            "optimization_steps": optimization_steps,
            "model": "grok-3"
        }
        
        # Run the search algorithm
        optimized_architecture = self.search_algorithm.search(search_config)
        
        # Evaluate the architecture
        evaluation = self.evaluator.evaluate_architecture(
            architecture=optimized_architecture,
            task_description=task_description
        )
        
        # Return the optimized architecture with evaluation
        return {
            "architecture": optimized_architecture,
            "evaluation": evaluation
        }
    
    def _create_basic_template(
        self,
        template_name: str,
        num_agents: int,
        use_reasoning: bool,
        use_code_execution: bool,
        architecture_type: str
    ) -> Dict[str, Any]:
        """
        Create a basic architecture template without using the supernet.
        
        Args:
            template_name: Name of the template.
            num_agents: Number of agents in the architecture.
            use_reasoning: Whether to enable advanced reasoning capabilities.
            use_code_execution: Whether to enable code execution capabilities.
            architecture_type: Type of architecture (hierarchical, mesh, star, pipeline, hybrid).
        
        Returns:
            Architecture template as a dictionary.
        """
        # Define agent roles based on architecture type and number of agents
        agent_roles = []
        
        if architecture_type == "hierarchical":
            # Hierarchical architecture with a coordinator and specialized agents
            agent_roles.append({
                "id": "coordinator",
                "name": "Coordinator",
                "role": "coordinator",
                "capabilities": ["planning", "coordination"]
            })
            
            for i in range(1, num_agents):
                if i == 1:
                    role = "researcher"
                    capabilities = ["research", "analysis"]
                elif i == 2:
                    role = "developer"
                    capabilities = ["coding", "testing"]
                else:
                    role = f"specialist_{i}"
                    capabilities = ["specialized_task"]
                
                agent_roles.append({
                    "id": f"agent_{i}",
                    "name": f"Agent {i}",
                    "role": role,
                    "capabilities": capabilities
                })
        
        elif architecture_type == "mesh":
            # Mesh architecture with equal agents
            for i in range(num_agents):
                agent_roles.append({
                    "id": f"agent_{i}",
                    "name": f"Agent {i}",
                    "role": "peer",
                    "capabilities": ["general_task"]
                })
        
        elif architecture_type == "star":
            # Star architecture with a central hub and peripheral agents
            agent_roles.append({
                "id": "hub",
                "name": "Hub",
                "role": "hub",
                "capabilities": ["coordination", "integration"]
            })
            
            for i in range(1, num_agents):
                agent_roles.append({
                    "id": f"spoke_{i}",
                    "name": f"Spoke {i}",
                    "role": "spoke",
                    "capabilities": ["specialized_task"]
                })
        
        elif architecture_type == "pipeline":
            # Pipeline architecture with sequential processing
            for i in range(num_agents):
                agent_roles.append({
                    "id": f"stage_{i}",
                    "name": f"Stage {i}",
                    "role": f"stage_{i}",
                    "capabilities": [f"stage_{i}_processing"]
                })
        
        else:  # hybrid or unknown
            # Hybrid architecture with mixed roles
            agent_roles.append({
                "id": "coordinator",
                "name": "Coordinator",
                "role": "coordinator",
                "capabilities": ["planning", "coordination"]
            })
            
            agent_roles.append({
                "id": "researcher",
                "name": "Researcher",
                "role": "researcher",
                "capabilities": ["research", "analysis"]
            })
            
            agent_roles.append({
                "id": "developer",
                "name": "Developer",
                "role": "developer",
                "capabilities": ["coding", "testing"]
            })
            
            for i in range(3, num_agents):
                agent_roles.append({
                    "id": f"agent_{i}",
                    "name": f"Agent {i}",
                    "role": "general",
                    "capabilities": ["general_task"]
                })
        
        # Define connections based on architecture type
        connections = []
        
        if architecture_type == "hierarchical":
            # Hierarchical connections from coordinator to all other agents
            for i in range(1, num_agents):
                connections.append({
                    "from": "coordinator",
                    "to": f"agent_{i}",
                    "type": "directive"
                })
                connections.append({
                    "from": f"agent_{i}",
                    "to": "coordinator",
                    "type": "report"
                })
        
        elif architecture_type == "mesh":
            # Mesh connections between all agents
            for i in range(num_agents):
                for j in range(num_agents):
                    if i != j:
                        connections.append({
                            "from": f"agent_{i}",
                            "to": f"agent_{j}",
                            "type": "peer"
                        })
        
        elif architecture_type == "star":
            # Star connections from hub to all spokes
            for i in range(1, num_agents):
                connections.append({
                    "from": "hub",
                    "to": f"spoke_{i}",
                    "type": "directive"
                })
                connections.append({
                    "from": f"spoke_{i}",
                    "to": "hub",
                    "type": "report"
                })
        
        elif architecture_type == "pipeline":
            # Pipeline connections between sequential stages
            for i in range(num_agents - 1):
                connections.append({
                    "from": f"stage_{i}",
                    "to": f"stage_{i+1}",
                    "type": "flow"
                })
        
        else:  # hybrid or unknown
            # Hybrid connections
            # Coordinator to all
            for role in ["researcher", "developer"]:
                connections.append({
                    "from": "coordinator",
                    "to": role,
                    "type": "directive"
                })
                connections.append({
                    "from": role,
                    "to": "coordinator",
                    "type": "report"
                })
            
            # Additional connections for other agents
            for i in range(3, num_agents):
                connections.append({
                    "from": "coordinator",
                    "to": f"agent_{i}",
                    "type": "directive"
                })
                connections.append({
                    "from": f"agent_{i}",
                    "to": "coordinator",
                    "type": "report"
                })
        
        # Create the template
        template = {
            "name": template_name,
            "type": architecture_type,
            "agents": agent_roles,
            "connections": connections,
            "capabilities": {
                "reasoning": use_reasoning,
                "code_execution": use_code_execution
            },
            "model": "grok-3"
        }
        
        return template
    
    def _create_architecture_with_reasoning(
        self,
        task_description: str,
        initial_template: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an architecture for a task using Grok 3's reasoning capabilities.
        
        Args:
            task_description: Description of the task.
            initial_template: Optional initial architecture template.
        
        Returns:
            Architecture as a dictionary.
        """
        # Analyze the task
        task_analysis = self._analyze_task(task_description)
        
        # Determine the best architecture type
        architecture_type = self._determine_architecture_type(task_analysis)
        
        # Determine the number of agents
        num_agents = self._determine_num_agents(task_analysis)
        
        # Create a template
        if initial_template:
            template = initial_template
        else:
            template = self._create_basic_template(
                template_name="task_optimized",
                num_agents=num_agents,
                use_reasoning=True,
                use_code_execution=True,
                architecture_type=architecture_type
            )
        
        # Customize the template for the task
        customized_template = self._customize_template_for_task(
            template=template,
            task_description=task_description,
            task_analysis=task_analysis
        )
        
        return customized_template
    
    def _analyze_task(self, task_description: str) -> Dict[str, Any]:
        """
        Analyze a task using Grok 3's reasoning capabilities.
        
        Args:
            task_description: Description of the task.
        
        Returns:
            Task analysis as a dictionary.
        """
        # Use the reasoning adapter to analyze the task
        prompt = f"""
        Analyze the following task and provide a structured analysis:
        
        Task: {task_description}
        
        Please provide:
        1. Task complexity (low, medium, high)
        2. Required capabilities (list)
        3. Recommended number of agents (1-5)
        4. Recommended architecture type (hierarchical, mesh, star, pipeline, hybrid)
        5. Key subtasks (list)
        
        Format your response as a JSON object.
        """
        
        analysis_text = self.reasoning_adapter.generate_text(
            prompt=prompt,
            reasoning_mode="think"
        )
        
        # Extract JSON from the response
        import json
        import re
        
        # Look for JSON in the response
        json_pattern = r'\{[\s\S]*\}'
        json_match = re.search(json_pattern, analysis_text)
        
        if json_match:
            try:
                analysis = json.loads(json_match.group(0))
                return analysis
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from analysis response")
        
        # If JSON parsing fails, create a basic analysis
        return {
            "complexity": "medium",
            "required_capabilities": ["planning", "research", "coding"],
            "recommended_num_agents": 3,
            "recommended_architecture_type": "hierarchical",
            "key_subtasks": ["planning", "research", "implementation"]
        }
    
    def _determine_architecture_type(self, task_analysis: Dict[str, Any]) -> str:
        """
        Determine the best architecture type based on task analysis.
        
        Args:
            task_analysis: Task analysis dictionary.
        
        Returns:
            Architecture type as a string.
        """
        # Extract the recommended architecture type from the analysis
        architecture_type = task_analysis.get("recommended_architecture_type", "hierarchical")
        
        # Validate the architecture type
        valid_types = ["hierarchical", "mesh", "star", "pipeline", "hybrid"]
        if architecture_type not in valid_types:
            logger.warning(f"Invalid architecture type: {architecture_type}. Using hierarchical.")
            architecture_type = "hierarchical"
        
        return architecture_type
    
    def _determine_num_agents(self, task_analysis: Dict[str, Any]) -> int:
        """
        Determine the number of agents based on task analysis.
        
        Args:
            task_analysis: Task analysis dictionary.
        
        Returns:
            Number of agents as an integer.
        """
        # Extract the recommended number of agents from the analysis
        num_agents = task_analysis.get("recommended_num_agents", 3)
        
        # Validate the number of agents
        if not isinstance(num_agents, int) or num_agents < 1:
            logger.warning(f"Invalid number of agents: {num_agents}. Using 3.")
            num_agents = 3
        
        # Cap the number of agents at 5
        if num_agents > 5:
            logger.warning(f"Number of agents ({num_agents}) exceeds maximum (5). Using 5.")
            num_agents = 5
        
        return num_agents
    
    def _customize_template_for_task(
        self,
        template: Dict[str, Any],
        task_description: str,
        task_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Customize a template for a specific task.
        
        Args:
            template: Architecture template.
            task_description: Description of the task.
            task_analysis: Task analysis dictionary.
        
        Returns:
            Customized template as a dictionary.
        """
        # Create a copy of the template
        customized = template.copy()
        
        # Update the name
        customized["name"] = f"Task-Optimized-{customized.get('name', 'Architecture')}"
        
        # Add task information
        customized["task"] = {
            "description": task_description,
            "analysis": task_analysis
        }
        
        # Customize agent capabilities based on task analysis
        required_capabilities = task_analysis.get("required_capabilities", [])
        key_subtasks = task_analysis.get("key_subtasks", [])
        
        # Update agent capabilities
        for agent in customized.get("agents", []):
            role = agent.get("role", "")
            
            if role == "coordinator":
                agent["capabilities"] = ["planning", "coordination"] + [cap for cap in required_capabilities if cap in ["planning", "oversight", "evaluation"]]
            elif role == "researcher":
                agent["capabilities"] = ["research", "analysis"] + [cap for cap in required_capabilities if cap in ["research", "data_analysis", "information_gathering"]]
            elif role == "developer":
                agent["capabilities"] = ["coding", "testing"] + [cap for cap in required_capabilities if cap in ["coding", "testing", "debugging", "implementation"]]
            else:
                # Assign remaining capabilities to other agents
                remaining_caps = [cap for cap in required_capabilities if cap not in agent.get("capabilities", [])]
                if remaining_caps:
                    agent["capabilities"] = agent.get("capabilities", []) + remaining_caps[:2]  # Add up to 2 more capabilities
        
        return customized
