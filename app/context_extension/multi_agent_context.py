"""
Multi-Agent Context Distributor for context extension.

This module provides the Multi-Agent Context Distribution System, which distributes
context processing across specialized agents, enabling efficient handling of extremely
large projects.
"""

import logging
import threading
import queue
from typing import List, Dict, Any, Optional, Union, Tuple, Callable

# Set up logging
logger = logging.getLogger(__name__)

class MultiAgentContextDistributor:
    """
    Distributor class for multi-agent context distribution.
    
    This class provides methods for distributing context processing across specialized
    agents and coordinating their interactions.
    """
    
    def __init__(
        self,
        max_agents: int = 5,
        coordinator_role: str = "coordinator",
        specialization_enabled: bool = True,
        sync_interval: float = 1.0
    ):
        """
        Initialize the MultiAgentContextDistributor.
        
        Args:
            max_agents: Maximum number of agents to use
            coordinator_role: Role of the coordinator agent
            specialization_enabled: Whether to enable agent specialization
            sync_interval: Interval for context synchronization in seconds
        """
        self.max_agents = max_agents
        self.coordinator_role = coordinator_role
        self.specialization_enabled = specialization_enabled
        self.sync_interval = sync_interval
        
        # Initialize agent registry
        self.agents = {}
        self.agent_specializations = {}
        self.agent_contexts = {}
        
        # Initialize task queue
        self.task_queue = queue.Queue()
        self.results = {}
        
        # Initialize synchronization
        self.sync_event = threading.Event()
        self.sync_thread = None
        self.running = False
        
        logger.info(f"Initialized MultiAgentContextDistributor with max_agents={max_agents}")
    
    def register_agent(
        self,
        agent_id: str,
        agent_interface: Any,
        specializations: List[str] = None,
        context_capacity: int = 10000
    ) -> bool:
        """
        Register an agent with the distributor.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_interface: Interface for communicating with the agent
            specializations: List of agent specializations
            context_capacity: Maximum context capacity for the agent
        
        Returns:
            True if registration was successful
        """
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} is already registered")
            return False
        
        # Register agent
        self.agents[agent_id] = agent_interface
        
        # Register specializations
        if specializations:
            self.agent_specializations[agent_id] = specializations
        else:
            self.agent_specializations[agent_id] = []
        
        # Initialize context
        self.agent_contexts[agent_id] = {
            "capacity": context_capacity,
            "current_context": "",
            "context_size": 0,
            "assigned_tasks": []
        }
        
        logger.info(f"Registered agent {agent_id} with specializations: {specializations}")
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the distributor.
        
        Args:
            agent_id: Unique identifier for the agent
        
        Returns:
            True if unregistration was successful
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} is not registered")
            return False
        
        # Unregister agent
        del self.agents[agent_id]
        
        # Unregister specializations
        if agent_id in self.agent_specializations:
            del self.agent_specializations[agent_id]
        
        # Clear context
        if agent_id in self.agent_contexts:
            del self.agent_contexts[agent_id]
        
        logger.info(f"Unregistered agent {agent_id}")
        return True
    
    def assign_context(self, agent_id: str, context: str) -> bool:
        """
        Assign context to an agent.
        
        Args:
            agent_id: Unique identifier for the agent
            context: Context to assign
        
        Returns:
            True if assignment was successful
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} is not registered")
            return False
        
        # Check context size
        context_size = len(context.split())
        if context_size > self.agent_contexts[agent_id]["capacity"]:
            logger.warning(f"Context size {context_size} exceeds agent {agent_id}'s capacity {self.agent_contexts[agent_id]['capacity']}")
            return False
        
        # Assign context
        self.agent_contexts[agent_id]["current_context"] = context
        self.agent_contexts[agent_id]["context_size"] = context_size
        
        logger.info(f"Assigned context of size {context_size} to agent {agent_id}")
        return True
    
    def get_agent_context(self, agent_id: str) -> str:
        """
        Get the current context of an agent.
        
        Args:
            agent_id: Unique identifier for the agent
        
        Returns:
            Current context of the agent
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} is not registered")
            return ""
        
        return self.agent_contexts[agent_id]["current_context"]
    
    def distribute_context(self, context: str, context_type: str = "general") -> Dict[str, str]:
        """
        Distribute context across agents based on specialization.
        
        Args:
            context: Context to distribute
            context_type: Type of context (code, document, conversation, etc.)
        
        Returns:
            Dictionary mapping agent IDs to assigned context segments
        """
        if not self.agents:
            logger.warning("No agents registered")
            return {}
        
        # Identify coordinator agent
        coordinator_id = self._identify_coordinator()
        
        # Segment context
        context_segments = self._segment_context(context, context_type)
        
        # Assign segments to agents
        assignments = {}
        
        if self.specialization_enabled:
            # Distribute based on specialization
            for segment in context_segments:
                best_agent_id = self._find_best_agent_for_segment(segment, coordinator_id)
                
                if best_agent_id:
                    if best_agent_id not in assignments:
                        assignments[best_agent_id] = []
                    
                    assignments[best_agent_id].append(segment["content"])
        else:
            # Simple round-robin distribution
            agent_ids = list(self.agents.keys())
            for i, segment in enumerate(context_segments):
                agent_id = agent_ids[i % len(agent_ids)]
                
                if agent_id not in assignments:
                    assignments[agent_id] = []
                
                assignments[agent_id].append(segment["content"])
        
        # Combine segments for each agent
        final_assignments = {}
        for agent_id, segments in assignments.items():
            final_assignments[agent_id] = "\n\n".join(segments)
            
            # Assign to agent
            self.assign_context(agent_id, final_assignments[agent_id])
        
        # Ensure coordinator has overview
        if coordinator_id and coordinator_id not in final_assignments:
            # Create a summary for the coordinator
            coordinator_context = self._create_coordinator_context(context, final_assignments)
            final_assignments[coordinator_id] = coordinator_context
            self.assign_context(coordinator_id, coordinator_context)
        
        logger.info(f"Distributed context across {len(final_assignments)} agents")
        return final_assignments
    
    def _identify_coordinator(self) -> Optional[str]:
        """
        Identify the coordinator agent.
        
        Returns:
            ID of the coordinator agent, or None if not found
        """
        # Look for agent with coordinator role
        for agent_id, specializations in self.agent_specializations.items():
            if self.coordinator_role in specializations:
                return agent_id
        
        # If no dedicated coordinator, use the first agent
        if self.agents:
            return list(self.agents.keys())[0]
        
        return None
    
    def _segment_context(self, context: str, context_type: str) -> List[Dict[str, Any]]:
        """
        Segment context into manageable pieces.
        
        Args:
            context: Context to segment
            context_type: Type of context
        
        Returns:
            List of context segments with metadata
        """
        segments = []
        
        if context_type == "code":
            # Segment by functions, classes, etc.
            import re
            
            # Find potential code blocks
            patterns = [
                (r'class\s+(\w+)(?:\(.*\))?\s*:', "class"),  # Python class
                (r'def\s+(\w+)\s*\(.*\)\s*:', "function"),  # Python function
                (r'function\s+(\w+)\s*\(.*\)\s*{', "function"),  # JavaScript function
                (r'(?:public|private|protected)?\s*(?:static)?\s*(?:class|interface)\s+(\w+)(?:\s+extends|\s+implements|\s*{)', "class"),  # Java/C# class
                (r'(?:public|private|protected)?\s*(?:static)?\s*(?:void|int|String|boolean|float|double|\w+)\s+(\w+)\s*\(.*\)\s*{', "method")  # Java/C# method
            ]
            
            # Find all matches
            matches = []
            for pattern, segment_type in patterns:
                for match in re.finditer(pattern, context, re.MULTILINE):
                    name = match.group(1)
                    start = match.start()
                    matches.append((start, name, segment_type))
            
            # Sort by position
            matches.sort()
            
            # Create segments
            for i, (start, name, segment_type) in enumerate(matches):
                # Determine end position
                if i < len(matches) - 1:
                    end = matches[i + 1][0]
                else:
                    end = len(context)
                
                # Extract content
                content = context[start:end]
                
                segments.append({
                    "content": content,
                    "type": segment_type,
                    "name": name,
                    "specialization": segment_type
                })
            
            # If no segments were found, create a single segment
            if not segments:
                segments.append({
                    "content": context,
                    "type": "code",
                    "name": "code_block",
                    "specialization": "code"
                })
        
        elif context_type == "document":
            # Segment by sections, headings, etc.
            import re
            
            # Find headings
            heading_pattern = r'(?:^|\n)(#+)\s+(.+)(?:\n|$)'
            headings = [(len(m.group(1)), m.group(2), m.start()) for m in re.finditer(heading_pattern, context)]
            
            # Sort by position
            headings.sort(key=lambda x: x[2])
            
            # Create segments
            for i, (level, title, start) in enumerate(headings):
                # Determine end position
                if i < len(headings) - 1:
                    end = headings[i + 1][2]
                else:
                    end = len(context)
                
                # Extract content
                content = context[start:end]
                
                segments.append({
                    "content": content,
                    "type": "section",
                    "name": title,
                    "level": level,
                    "specialization": "document"
                })
            
            # If no segments were found, split by paragraphs
            if not segments:
                paragraphs = re.split(r'\n\s*\n', context)
                
                for i, paragraph in enumerate(paragraphs):
                    if paragraph.strip():
                        segments.append({
                            "content": paragraph,
                            "type": "paragraph",
                            "name": f"paragraph_{i}",
                            "specialization": "document"
                        })
        
        elif context_type == "conversation":
            # Segment by messages or turns
            import re
            
            # Try to identify message boundaries
            message_pattern = r'(?:^|\n)(?:[A-Za-z0-9_]+|User|Assistant|System):\s*(.+?)(?=(?:\n[A-Za-z0-9_]+|User|Assistant|System):|$)'
            messages = re.finditer(message_pattern, context, re.DOTALL)
            
            for i, match in enumerate(messages):
                content = match.group(0)
                
                segments.append({
                    "content": content,
                    "type": "message",
                    "name": f"message_{i}",
                    "specialization": "conversation"
                })
            
            # If no segments were found, split by lines
            if not segments:
                lines = context.split('\n')
                current_segment = []
                
                for line in lines:
                    current_segment.append(line)
                    
                    # Create a new segment every 10 lines
                    if len(current_segment) >= 10:
                        segments.append({
                            "content": '\n'.join(current_segment),
                            "type": "conversation_chunk",
                            "name": f"chunk_{len(segments)}",
                            "specialization": "conversation"
                        })
                        current_segment = []
                
                # Add the last segment if not empty
                if current_segment:
                    segments.append({
                        "content": '\n'.join(current_segment),
                        "type": "conversation_chunk",
                        "name": f"chunk_{len(segments)}",
                        "specialization": "conversation"
                    })
        
        else:
            # Generic segmentation by size
            import re
            
            # Try to split by paragraphs
            paragraphs = re.split(r'\n\s*\n', context)
            
            current_segment = []
            current_size = 0
            max_segment_size = 2000  # Approximate token count
            
            for paragraph in paragraphs:
                paragraph_size = len(paragraph.split())
                
                if current_size + paragraph_size <= max_segment_size:
                    current_segment.append(paragraph)
                    current_size += paragraph_size
                else:
                    # Current segment is full
                    if current_segment:
                        segments.append({
                            "content": '\n\n'.join(current_segment),
                            "type": "generic",
                            "name": f"segment_{len(segments)}",
                            "specialization": "general"
                        })
                    
                    # Start a new segment
                    current_segment = [paragraph]
                    current_size = paragraph_size
            
            # Add the last segment if not empty
            if current_segment:
                segments.append({
                    "content": '\n\n'.join(current_segment),
                    "type": "generic",
                    "name": f"segment_{len(segments)}",
                    "specialization": "general"
                })
        
        return segments
    
    def _find_best_agent_for_segment(self, segment: Dict[str, Any], coordinator_id: Optional[str]) -> Optional[str]:
        """
        Find the best agent for a context segment.
        
        Args:
            segment: Context segment
            coordinator_id: ID of the coordinator agent
        
        Returns:
            ID of the best agent, or None if no suitable agent found
        """
        best_agent_id = None
        best_score = -1
        
        for agent_id, specializations in self.agent_specializations.items():
            # Skip coordinator for specialized tasks
            if agent_id == coordinator_id and len(self.agents) > 1:
                continue
            
            # Calculate specialization score
            score = 0
            
            if "specialization" in segment:
                if segment["specialization"] in specializations:
                    score += 10
                
                if "type" in segment and segment["type"] in specializations:
                    score += 5
            
            # Consider current context size
            available_capacity = self.agent_contexts[agent_id]["capacity"] - self.agent_contexts[agent_id]["context_size"]
            segment_size = len(segment["content"].split())
            
            if segment_size <= available_capacity:
                score += 1
            else:
                # Segment won't fit
                continue
            
            # Update best agent if score is higher
            if score > best_score:
                best_score = score
                best_agent_id = agent_id
        
        # If no specialized agent found, use any agent with capacity
        if best_agent_id is None:
            for agent_id in self.agents:
                available_capacity = self.agent_contexts[agent_id]["capacity"] - self.agent_contexts[agent_id]["context_size"]
                segment_size = len(segment["content"].split())
                
                if segment_size <= available_capacity:
                    best_agent_id = agent_id
                    break
        
        return best_agent_id
    
    def _create_coordinator_context(self, original_context: str, assignments: Dict[str, str]) -> str:
        """
        Create a context overview for the coordinator agent.
        
        Args:
            original_context: Original full context
            assignments: Context assignments to other agents
        
        Returns:
            Context overview for the coordinator
        """
        # Create a summary of the original context
        summary = self._summarize_text(original_context, max_length=1000)
        
        # Create an overview of agent assignments
        assignment_overview = "Agent Assignments:\n"
        for agent_id, context in assignments.items():
            context_size = len(context.split())
            assignment_overview += f"- Agent {agent_id}: {context_size} tokens\n"
        
        # Combine summary and overview
        coordinator_context = f"Context Summary:\n{summary}\n\n{assignment_overview}"
        
        return coordinator_context
    
    def _summarize_text(self, text: str, max_length: int = 1000) -> str:
        """
        Summarize text to a maximum length.
        
        Args:
            text: Text to summarize
            max_length: Maximum length in tokens
        
        Returns:
            Summarized text
        """
        # Simple extractive summarization
        import re
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        if len(sentences) <= max_length / 20:  # Rough estimate of average sentence length
            return text
        
        # Score sentences
        scores = {}
        for i, sentence in enumerate(sentences):
            # Score based on position (first and last sentences are important)
            position_score = 1.0
            if i < len(sentences) * 0.1:
                position_score = 2.0
            elif i > len(sentences) * 0.9:
                position_score = 1.5
            
            # Score based on length (prefer medium-length sentences)
            length = len(sentence.split())
            length_score = 1.0
            if 5 <= length <= 25:
                length_score = 1.5
            
            # Score based on content (prefer sentences with important words)
            content_score = 1.0
            important_words = ["important", "significant", "key", "main", "critical", "essential", "crucial"]
            for word in important_words:
                if word in sentence.lower():
                    content_score = 2.0
                    break
            
            # Combine scores
            scores[i] = position_score * length_score * content_score
        
        # Select top sentences
        num_sentences = min(max_length // 20, len(sentences))
        top_indices = sorted(scores.keys(), key=lambda i: scores[i], reverse=True)[:num_sentences]
        top_indices.sort()  # Sort by position to maintain flow
        
        # Combine selected sentences
        summary = " ".join(sentences[i] for i in top_indices)
        
        return summary
    
    def submit_task(
        self,
        task: Dict[str, Any],
        agent_id: Optional[str] = None,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Submit a task for processing.
        
        Args:
            task: Task to process
            agent_id: Specific agent to assign the task to, or None for auto-assignment
            callback: Optional callback function to call when task is complete
        
        Returns:
            Task ID
        """
        # Generate task ID if not provided
        if "id" not in task:
            import uuid
            task["id"] = str(uuid.uuid4())
        
        # Add timestamp if not provided
        if "timestamp" not in task:
            import time
            task["timestamp"] = time.time()
        
        # Add callback if provided
        if callback:
            task["callback"] = callback
        
        # Assign to specific agent if requested
        if agent_id:
            if agent_id not in self.agents:
                logger.warning(f"Agent {agent_id} is not registered")
                return task["id"]
            
            task["assigned_agent"] = agent_id
            self.agent_contexts[agent_id]["assigned_tasks"].append(task["id"])
        
        # Add to task queue
        self.task_queue.put(task)
        
        logger.info(f"Submitted task {task['id']}")
        return task["id"]
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the result of a task.
        
        Args:
            task_id: ID of the task
        
        Returns:
            Task result, or None if not available
        """
        if task_id in self.results:
            return self.results[task_id]
        
        return None
    
    def start_processing(self) -> bool:
        """
        Start processing tasks and synchronizing context.
        
        Returns:
            True if started successfully
        """
        if self.running:
            logger.warning("Already running")
            return False
        
        self.running = True
        
        # Start synchronization thread
        self.sync_thread = threading.Thread(target=self._sync_loop)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        
        logger.info("Started processing")
        return True
    
    def stop_processing(self) -> bool:
        """
        Stop processing tasks and synchronizing context.
        
        Returns:
            True if stopped successfully
        """
        if not self.running:
            logger.warning("Not running")
            return False
        
        self.running = False
        self.sync_event.set()
        
        if self.sync_thread:
            self.sync_thread.join(timeout=5.0)
        
        logger.info("Stopped processing")
        return True
    
    def _sync_loop(self):
        """Synchronization loop for context sharing."""
        while self.running:
            # Process tasks
            self._process_tasks()
            
            # Synchronize context
            self._synchronize_context()
            
            # Wait for next sync interval or until explicitly triggered
            self.sync_event.wait(timeout=self.sync_interval)
            self.sync_event.clear()
    
    def _process_tasks(self):
        """Process tasks in the queue."""
        try:
            # Process up to 10 tasks per cycle
            for _ in range(10):
                if self.task_queue.empty():
                    break
                
                # Get task
                task = self.task_queue.get_nowait()
                
                # Determine agent to process task
                agent_id = task.get("assigned_agent")
                if not agent_id or agent_id not in self.agents:
                    # Auto-assign based on specialization
                    agent_id = self._assign_task_to_agent(task)
                
                if not agent_id:
                    logger.warning(f"No suitable agent found for task {task['id']}")
                    self.results[task["id"]] = {
                        "status": "failed",
                        "error": "No suitable agent found"
                    }
                    continue
                
                # Process task
                try:
                    agent = self.agents[agent_id]
                    
                    # Call agent's process_task method if available
                    if hasattr(agent, "process_task"):
                        result = agent.process_task(task)
                    else:
                        # Mock processing
                        result = {
                            "status": "completed",
                            "result": f"Processed by agent {agent_id}"
                        }
                    
                    # Store result
                    self.results[task["id"]] = result
                    
                    # Call callback if provided
                    if "callback" in task and callable(task["callback"]):
                        task["callback"](task["id"], result)
                    
                    logger.info(f"Processed task {task['id']} with agent {agent_id}")
                
                except Exception as e:
                    logger.error(f"Error processing task {task['id']} with agent {agent_id}: {str(e)}")
                    self.results[task["id"]] = {
                        "status": "failed",
                        "error": str(e)
                    }
                
                finally:
                    # Mark task as done
                    self.task_queue.task_done()
        
        except Exception as e:
            logger.error(f"Error in task processing loop: {str(e)}")
    
    def _assign_task_to_agent(self, task: Dict[str, Any]) -> Optional[str]:
        """
        Assign a task to an agent based on specialization and load.
        
        Args:
            task: Task to assign
        
        Returns:
            ID of the assigned agent, or None if no suitable agent found
        """
        best_agent_id = None
        best_score = -1
        
        for agent_id, specializations in self.agent_specializations.items():
            # Calculate specialization score
            score = 0
            
            if "specialization" in task:
                if task["specialization"] in specializations:
                    score += 10
            
            # Consider current load
            load = len(self.agent_contexts[agent_id]["assigned_tasks"])
            load_score = 1.0 / (1.0 + load)
            score *= load_score
            
            # Update best agent if score is higher
            if score > best_score:
                best_score = score
                best_agent_id = agent_id
        
        # If no specialized agent found, use the least loaded agent
        if best_agent_id is None:
            min_load = float('inf')
            for agent_id in self.agents:
                load = len(self.agent_contexts[agent_id]["assigned_tasks"])
                if load < min_load:
                    min_load = load
                    best_agent_id = agent_id
        
        return best_agent_id
    
    def _synchronize_context(self):
        """Synchronize context across agents."""
        if not self.agents:
            return
        
        # Identify coordinator agent
        coordinator_id = self._identify_coordinator()
        if not coordinator_id:
            return
        
        try:
            # Collect context updates from agents
            context_updates = {}
            
            for agent_id, agent in self.agents.items():
                if agent_id == coordinator_id:
                    continue
                
                # Get context update from agent if available
                if hasattr(agent, "get_context_update"):
                    update = agent.get_context_update()
                    if update:
                        context_updates[agent_id] = update
            
            # If no updates, nothing to synchronize
            if not context_updates:
                return
            
            # Update coordinator's context with agent updates
            coordinator_context = self.agent_contexts[coordinator_id]["current_context"]
            
            # Add agent updates
            update_summary = "\n\nAgent Context Updates:\n"
            for agent_id, update in context_updates.items():
                update_summary += f"\n--- Agent {agent_id} Update ---\n{update}\n"
            
            # Update coordinator context
            new_coordinator_context = coordinator_context + update_summary
            self.assign_context(coordinator_id, new_coordinator_context)
            
            logger.info(f"Synchronized context updates from {len(context_updates)} agents to coordinator")
        
        except Exception as e:
            logger.error(f"Error synchronizing context: {str(e)}")
    
    def trigger_sync(self):
        """Trigger immediate context synchronization."""
        self.sync_event.set()
        logger.info("Triggered immediate context synchronization")
    
    def get_agent_load(self, agent_id: str) -> int:
        """
        Get the current load of an agent.
        
        Args:
            agent_id: Unique identifier for the agent
        
        Returns:
            Number of assigned tasks
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} is not registered")
            return 0
        
        return len(self.agent_contexts[agent_id]["assigned_tasks"])
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current status of the system.
        
        Returns:
            Dictionary with system status information
        """
        status = {
            "agents": len(self.agents),
            "running": self.running,
            "pending_tasks": self.task_queue.qsize(),
            "completed_tasks": len(self.results),
            "agent_loads": {}
        }
        
        for agent_id in self.agents:
            status["agent_loads"][agent_id] = self.get_agent_load(agent_id)
        
        return status
