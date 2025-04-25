"""
Personalized Agent Adaptation Module

This module enables agents to learn from individual human team members' preferences and working styles.
It tracks user interactions, builds preference profiles, and adapts agent behavior accordingly.
"""

import json
import os
import datetime
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from collections import defaultdict

class UserPreferenceProfile:
    """Represents a user's preferences and working style profile."""
    
    def __init__(self, user_id: str, name: Optional[str] = None):
        """
        Initialize a new user preference profile.
        
        Args:
            user_id: Unique identifier for the user
            name: Optional user name
        """
        self.user_id = user_id
        self.name = name or user_id
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        
        # Communication preferences
        self.communication_style = {
            "verbosity": 0.5,  # 0.0 = concise, 1.0 = detailed
            "formality": 0.5,  # 0.0 = casual, 1.0 = formal
            "technical_level": 0.5,  # 0.0 = non-technical, 1.0 = highly technical
            "preferred_update_frequency": "daily",  # daily, hourly, weekly, etc.
            "preferred_communication_channels": ["chat"],  # chat, email, voice, etc.
        }
        
        # Work style preferences
        self.work_style = {
            "autonomy_level": 0.5,  # 0.0 = high guidance, 1.0 = high autonomy
            "risk_tolerance": 0.5,  # 0.0 = risk-averse, 1.0 = risk-tolerant
            "preferred_working_hours": {
                "start": "09:00",
                "end": "17:00",
                "timezone": "UTC",
            },
            "preferred_task_size": "medium",  # small, medium, large
            "preferred_deadline_buffer": 0.2,  # percentage of time to add as buffer
        }
        
        # Decision-making preferences
        self.decision_making = {
            "data_vs_intuition": 0.5,  # 0.0 = data-driven, 1.0 = intuition-driven
            "speed_vs_accuracy": 0.5,  # 0.0 = speed-focused, 1.0 = accuracy-focused
            "exploration_vs_exploitation": 0.5,  # 0.0 = exploit known, 1.0 = explore new
            "preferred_decision_frameworks": ["pros_cons"],  # pros_cons, weighted_criteria, etc.
        }
        
        # Feedback preferences
        self.feedback_preferences = {
            "feedback_frequency": "task_completion",  # continuous, task_completion, milestone, etc.
            "criticism_style": "constructive",  # direct, constructive, sandwich, etc.
            "preferred_feedback_detail": 0.5,  # 0.0 = high-level, 1.0 = detailed
        }
        
        # Interaction history
        self.interaction_history = []
        
        # Learned preferences (derived from interactions)
        self.learned_preferences = {}
        
        # Adaptation metrics
        self.adaptation_metrics = {
            "satisfaction_scores": [],
            "adaptation_success_rate": 1.0,
            "preference_confidence": {},
        }
    
    def update_preference(self, category: str, preference: str, value: Any) -> None:
        """
        Update a specific preference value.
        
        Args:
            category: The preference category (communication_style, work_style, etc.)
            preference: The specific preference to update
            value: The new preference value
        """
        if hasattr(self, category) and isinstance(getattr(self, category), dict):
            category_dict = getattr(self, category)
            if preference in category_dict:
                category_dict[preference] = value
                self.updated_at = datetime.datetime.now()
                
                # Update confidence in this preference
                if preference not in self.adaptation_metrics["preference_confidence"]:
                    self.adaptation_metrics["preference_confidence"][preference] = 0.3  # Initial confidence
                else:
                    # Increase confidence with each explicit update
                    current = self.adaptation_metrics["preference_confidence"][preference]
                    self.adaptation_metrics["preference_confidence"][preference] = min(1.0, current + 0.1)
    
    def record_interaction(self, interaction_type: str, content: Dict[str, Any], 
                          outcome: Optional[str] = None, satisfaction: Optional[float] = None) -> None:
        """
        Record an interaction with the user.
        
        Args:
            interaction_type: Type of interaction (message, task, decision, etc.)
            content: Details of the interaction
            outcome: Optional outcome of the interaction
            satisfaction: Optional satisfaction score (0.0 to 1.0)
        """
        interaction = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": interaction_type,
            "content": content,
            "outcome": outcome,
            "satisfaction": satisfaction
        }
        
        self.interaction_history.append(interaction)
        self.updated_at = datetime.datetime.now()
        
        # Update satisfaction metrics if provided
        if satisfaction is not None:
            self.adaptation_metrics["satisfaction_scores"].append(satisfaction)
    
    def infer_preferences_from_interactions(self) -> Dict[str, Any]:
        """
        Analyze interaction history to infer user preferences.
        
        Returns:
            Dictionary of inferred preferences
        """
        if not self.interaction_history:
            return {}
        
        inferred = {}
        
        # Analyze message interactions for communication style
        messages = [i for i in self.interaction_history if i["type"] == "message"]
        if messages:
            # Infer verbosity preference from message lengths
            user_messages = [m for m in messages if m["content"].get("sender") == "user"]
            if user_messages:
                avg_length = sum(len(m["content"].get("text", "")) for m in user_messages) / len(user_messages)
                # Normalize to 0-1 scale (assuming 500 chars is verbose)
                verbosity = min(1.0, avg_length / 500)
                inferred["verbosity"] = verbosity
        
        # Analyze task interactions for work style
        tasks = [i for i in self.interaction_history if i["type"] == "task"]
        if tasks:
            # Infer autonomy level from task instructions detail
            avg_instruction_detail = sum(len(t["content"].get("instructions", "")) for t in tasks) / len(tasks)
            # More detailed instructions suggest preference for less autonomy
            autonomy = 1.0 - min(1.0, avg_instruction_detail / 1000)
            inferred["autonomy_level"] = autonomy
        
        # Analyze feedback interactions
        feedback = [i for i in self.interaction_history if i["type"] == "feedback"]
        if feedback:
            # Analyze feedback timing patterns
            feedback_times = [datetime.datetime.fromisoformat(f["timestamp"]) for f in feedback]
            if len(feedback_times) > 1:
                # Calculate average time between feedback instances
                time_diffs = [(feedback_times[i+1] - feedback_times[i]).total_seconds() / 3600 
                             for i in range(len(feedback_times)-1)]
                avg_hours_between_feedback = sum(time_diffs) / len(time_diffs)
                
                if avg_hours_between_feedback < 2:
                    inferred["feedback_frequency"] = "continuous"
                elif avg_hours_between_feedback < 12:
                    inferred["feedback_frequency"] = "multiple_daily"
                elif avg_hours_between_feedback < 36:
                    inferred["feedback_frequency"] = "daily"
                else:
                    inferred["feedback_frequency"] = "periodic"
        
        # Update learned preferences
        for key, value in inferred.items():
            self.learned_preferences[key] = value
            
            # Update confidence in learned preferences
            if key not in self.adaptation_metrics["preference_confidence"]:
                self.adaptation_metrics["preference_confidence"][key] = 0.1  # Initial confidence is low
            else:
                # Gradually increase confidence with more data
                current = self.adaptation_metrics["preference_confidence"][key]
                self.adaptation_metrics["preference_confidence"][key] = min(0.8, current + 0.05)
        
        return inferred
    
    def get_effective_preferences(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the effective preferences, combining explicit and learned preferences.
        
        Returns:
            Dictionary of effective preferences
        """
        effective = {
            "communication_style": dict(self.communication_style),
            "work_style": dict(self.work_style),
            "decision_making": dict(self.decision_making),
            "feedback_preferences": dict(self.feedback_preferences)
        }
        
        # Override with learned preferences where confidence is sufficient
        for key, value in self.learned_preferences.items():
            confidence = self.adaptation_metrics["preference_confidence"].get(key, 0)
            
            # Only apply learned preferences with sufficient confidence
            if confidence >= 0.3:
                # Determine which category this preference belongs to
                for category in effective:
                    if key in effective[category]:
                        effective[category][key] = value
                        break
        
        return effective
    
    def calculate_adaptation_success_rate(self) -> float:
        """
        Calculate the success rate of adaptations based on satisfaction scores.
        
        Returns:
            Adaptation success rate (0.0 to 1.0)
        """
        scores = self.adaptation_metrics["satisfaction_scores"]
        if not scores:
            return 1.0  # Default to perfect if no data
            
        # Consider scores above 0.7 as successful adaptations
        success_count = sum(1 for score in scores if score >= 0.7)
        success_rate = success_count / len(scores)
        
        # Update the stored metric
        self.adaptation_metrics["adaptation_success_rate"] = success_rate
        
        return success_rate
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the profile to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the profile
        """
        return {
            "user_id": self.user_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "communication_style": self.communication_style,
            "work_style": self.work_style,
            "decision_making": self.decision_making,
            "feedback_preferences": self.feedback_preferences,
            "learned_preferences": self.learned_preferences,
            "adaptation_metrics": self.adaptation_metrics,
            # Exclude interaction history as it can be large
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferenceProfile':
        """
        Create a profile from a dictionary.
        
        Args:
            data: Dictionary representation of a profile
            
        Returns:
            UserPreferenceProfile instance
        """
        profile = cls(data["user_id"], data.get("name"))
        
        profile.created_at = datetime.datetime.fromisoformat(data["created_at"])
        profile.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
        
        profile.communication_style = data.get("communication_style", profile.communication_style)
        profile.work_style = data.get("work_style", profile.work_style)
        profile.decision_making = data.get("decision_making", profile.decision_making)
        profile.feedback_preferences = data.get("feedback_preferences", profile.feedback_preferences)
        
        profile.learned_preferences = data.get("learned_preferences", {})
        profile.adaptation_metrics = data.get("adaptation_metrics", profile.adaptation_metrics)
        
        return profile


class PersonalizedAgentAdapter:
    """
    Adapter that modifies agent behavior based on user preferences.
    """
    
    def __init__(self, base_agent: Any, user_profile: UserPreferenceProfile):
        """
        Initialize the personalized agent adapter.
        
        Args:
            base_agent: The base agent to adapt
            user_profile: The user preference profile to adapt to
        """
        self.base_agent = base_agent
        self.user_profile = user_profile
        self.adaptation_history = []
    
    def adapt_communication(self, message: str) -> str:
        """
        Adapt communication based on user preferences.
        
        Args:
            message: Original message
            
        Returns:
            Adapted message
        """
        prefs = self.user_profile.get_effective_preferences()["communication_style"]
        
        # Adapt verbosity
        verbosity = prefs.get("verbosity", 0.5)
        if verbosity < 0.3:
            # Make more concise
            message = self._make_concise(message)
        elif verbosity > 0.7:
            # Make more detailed
            message = self._add_detail(message)
        
        # Adapt formality
        formality = prefs.get("formality", 0.5)
        if formality < 0.3:
            # Make more casual
            message = self._make_casual(message)
        elif formality > 0.7:
            # Make more formal
            message = self._make_formal(message)
        
        # Adapt technical level
        tech_level = prefs.get("technical_level", 0.5)
        if tech_level < 0.3:
            # Make less technical
            message = self._simplify_technical(message)
        elif tech_level > 0.7:
            # Make more technical
            message = self._enhance_technical(message)
        
        # Record adaptation
        self._record_adaptation("communication", {
            "original": message,
            "adapted": message,
            "preferences_applied": {
                "verbosity": verbosity,
                "formality": formality,
                "technical_level": tech_level
            }
        })
        
        return message
    
    def adapt_task_assignment(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt task assignment based on user preferences.
        
        Args:
            task: Original task
            
        Returns:
            Adapted task
        """
        prefs = self.user_profile.get_effective_preferences()["work_style"]
        adapted_task = dict(task)
        
        # Adapt autonomy level
        autonomy = prefs.get("autonomy_level", 0.5)
        if autonomy < 0.3:
            # Add more guidance
            if "instructions" in adapted_task:
                adapted_task["instructions"] = self._add_guidance(adapted_task["instructions"])
            if "checkpoints" not in adapted_task:
                adapted_task["checkpoints"] = self._create_checkpoints(adapted_task)
        elif autonomy > 0.7:
            # Reduce guidance, focus on outcomes
            if "instructions" in adapted_task:
                adapted_task["instructions"] = self._focus_on_outcomes(adapted_task["instructions"])
        
        # Adapt deadline based on buffer preference
        if "deadline" in adapted_task:
            buffer = prefs.get("preferred_deadline_buffer", 0.2)
            original_deadline = datetime.datetime.fromisoformat(adapted_task["deadline"])
            
            # Calculate task duration and add buffer
            if "created_at" in adapted_task:
                created_at = datetime.datetime.fromisoformat(adapted_task["created_at"])
                duration = (original_deadline - created_at).total_seconds()
                buffer_seconds = duration * buffer
                
                # Apply buffer to create internal deadline
                internal_deadline = original_deadline - datetime.timedelta(seconds=buffer_seconds)
                adapted_task["internal_deadline"] = internal_deadline.isoformat()
        
        # Record adaptation
        self._record_adaptation("task_assignment", {
            "original": task,
            "adapted": adapted_task,
            "preferences_applied": {
                "autonomy_level": autonomy,
                "preferred_deadline_buffer": prefs.get("preferred_deadline_buffer", 0.2)
            }
        })
        
        return adapted_task
    
    def adapt_decision_process(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt decision-making process based on user preferences.
        
        Args:
            decision_context: Context for the decision
            
        Returns:
            Adapted decision context with recommended approach
        """
        prefs = self.user_profile.get_effective_preferences()["decision_making"]
        adapted_context = dict(decision_context)
        
        # Select appropriate decision framework
        preferred_frameworks = prefs.get("preferred_decision_frameworks", ["pros_cons"])
        data_vs_intuition = prefs.get("data_vs_intuition", 0.5)
        speed_vs_accuracy = prefs.get("speed_vs_accuracy", 0.5)
        
        # Determine the best framework based on preferences and context
        if "urgency" in decision_context and decision_context["urgency"] == "high":
            # For urgent decisions, bias toward speed
            if "pros_cons" in preferred_frameworks:
                framework = "pros_cons"
            else:
                framework = preferred_frameworks[0]
        elif data_vs_intuition < 0.3:
            # Data-driven approach
            if "weighted_criteria" in preferred_frameworks:
                framework = "weighted_criteria"
            elif "decision_matrix" in preferred_frameworks:
                framework = "decision_matrix"
            else:
                framework = preferred_frameworks[0]
        elif data_vs_intuition > 0.7:
            # Intuition-driven approach
            if "scenario_analysis" in preferred_frameworks:
                framework = "scenario_analysis"
            else:
                framework = preferred_frameworks[0]
        else:
            # Use the first preferred framework as default
            framework = preferred_frameworks[0]
        
        adapted_context["recommended_framework"] = framework
        
        # Adjust analysis depth based on speed vs accuracy preference
        if speed_vs_accuracy < 0.3:
            # Speed-focused
            adapted_context["recommended_analysis_depth"] = "quick"
        elif speed_vs_accuracy > 0.7:
            # Accuracy-focused
            adapted_context["recommended_analysis_depth"] = "thorough"
        else:
            # Balanced
            adapted_context["recommended_analysis_depth"] = "balanced"
        
        # Record adaptation
        self._record_adaptation("decision_process", {
            "original": decision_context,
            "adapted": adapted_context,
            "preferences_applied": {
                "preferred_decision_frameworks": preferred_frameworks,
                "data_vs_intuition": data_vs_intuition,
                "speed_vs_accuracy": speed_vs_accuracy
            }
        })
        
        return adapted_context
    
    def adapt_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt feedback based on user preferences.
        
        Args:
            feedback: Original feedback
            
        Returns:
            Adapted feedback
        """
        prefs = self.user_profile.get_effective_preferences()["feedback_preferences"]
        adapted_feedback = dict(feedback)
        
        # Adapt criticism style
        criticism_style = prefs.get("criticism_style", "constructive")
        if "criticism" in feedback:
            if criticism_style == "direct":
                adapted_feedback["criticism"] = self._make_direct(feedback["criticism"])
            elif criticism_style == "constructive":
                adapted_feedback["criticism"] = self._make_constructive(feedback["criticism"])
            elif criticism_style == "sandwich":
                adapted_feedback["criticism"] = self._apply_sandwich_method(feedback["criticism"], feedback.get("positive", ""))
        
        # Adapt detail level
        detail_level = prefs.get("preferred_feedback_detail", 0.5)
        if detail_level < 0.3:
            # Make more high-level
            if "details" in adapted_feedback:
                adapted_feedback["details"] = self._make_high_level(adapted_feedback["details"])
        elif detail_level > 0.7:
            # Make more detailed
            if "details" in adapted_feedback:
                adapted_feedback["details"] = self._add_detail(adapted_feedback["details"])
        
        # Record adaptation
        self._record_adaptation("feedback", {
            "original": feedback,
            "adapted": adapted_feedback,
            "preferences_applied": {
                "criticism_style": criticism_style,
                "preferred_feedback_detail": detail_level
            }
        })
        
        return adapted_feedback
    
    def _record_adaptation(self, adaptation_type: str, details: Dict[str, Any]) -> None:
        """
        Record an adaptation for analysis.
        
        Args:
            adaptation_type: Type of adaptation
            details: Details of the adaptation
        """
        adaptation = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": adaptation_type,
            "details": details
        }
        
        self.adaptation_history.append(adaptation)
    
    def get_adaptation_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about adaptations performed.
        
        Returns:
            Dictionary of adaptation metrics
        """
        if not self.adaptation_history:
            return {"count": 0}
        
        metrics = {
            "count": len(self.adaptation_history),
            "types": {}
        }
        
        # Count adaptations by type
        for adaptation in self.adaptation_history:
            adaptation_type = adaptation["type"]
            if adaptation_type not in metrics["types"]:
                metrics["types"][adaptation_type] = 0
            metrics["types"][adaptation_type] += 1
        
        return metrics
    
    # Helper methods for adaptations
    
    def _make_concise(self, text: str) -> str:
        """Make text more concise."""
        # This would use NLP techniques to summarize
        # Simplified implementation for demonstration
        sentences = text.split('. ')
        if len(sentences) <= 2:
            return text
        
        # Keep first and last sentence, and about half of the middle ones
        middle_sentences = sentences[1:-1]
        selected_middle = middle_sentences[:max(1, len(middle_sentences)//2)]
        
        return '. '.join([sentences[0]] + selected_middle + [sentences[-1]])
    
    def _add_detail(self, text: str) -> str:
        """Add more detail to text."""
        # In a real implementation, this would use an LLM to expand the text
        # Simplified implementation for demonstration
        return text + "\n\nAdditional context: This approach takes into account the latest best practices and is designed to be scalable for future requirements."
    
    def _make_casual(self, text: str) -> str:
        """Make text more casual."""
        # Simplified implementation
        casual_replacements = {
            "utilize": "use",
            "implement": "set up",
            "facilitate": "help",
            "regarding": "about",
            "commence": "start",
            "additional": "more",
            "sufficient": "enough"
        }
        
        for formal, casual in casual_replacements.items():
            text = text.replace(formal, casual)
        
        return text
    
    def _make_formal(self, text: str) -> str:
        """Make text more formal."""
        # Simplified implementation
        formal_replacements = {
            "use": "utilize",
            "set up": "implement",
            "help": "facilitate",
            "about": "regarding",
            "start": "commence",
            "more": "additional",
            "enough": "sufficient"
        }
        
        for casual, formal in formal_replacements.items():
            text = text.replace(casual, formal)
        
        return text
    
    def _simplify_technical(self, text: str) -> str:
        """Simplify technical language."""
        # Simplified implementation
        technical_replacements = {
            "API": "connection",
            "database schema": "data structure",
            "authentication": "login system",
            "deployment": "installation",
            "algorithm": "process",
            "asynchronous": "background",
            "latency": "delay"
        }
        
        for technical, simple in technical_replacements.items():
            text = text.replace(technical, simple)
        
        return text
    
    def _enhance_technical(self, text: str) -> str:
        """Enhance technical language."""
        # Simplified implementation
        technical_replacements = {
            "connection": "API",
            "data structure": "database schema",
            "login system": "authentication",
            "installation": "deployment",
            "process": "algorithm",
            "background": "asynchronous",
            "delay": "latency"
        }
        
        for simple, technical in technical_replacements.items():
            text = text.replace(simple, technical)
        
        return text
    
    def _add_guidance(self, instructions: str) -> str:
        """Add more guidance to instructions."""
        # Simplified implementation
        return instructions + "\n\nStep-by-step approach:\n1. Begin by analyzing the requirements\n2. Create a plan before implementation\n3. Implement in small, testable increments\n4. Test each component thoroughly\n5. Document your approach and decisions"
    
    def _create_checkpoints(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create checkpoints for a task."""
        # Simplified implementation
        if "deadline" not in task:
            return []
            
        deadline = datetime.datetime.fromisoformat(task["deadline"])
        now = datetime.datetime.now()
        
        total_duration = (deadline - now).total_seconds()
        
        # Create 3 checkpoints
        checkpoints = []
        for i in range(1, 4):
            checkpoint_time = now + datetime.timedelta(seconds=total_duration * i / 4)
            checkpoints.append({
                "id": f"checkpoint_{i}",
                "name": f"Checkpoint {i}",
                "deadline": checkpoint_time.isoformat(),
                "expected_progress": i * 25  # percentage
            })
            
        return checkpoints
    
    def _focus_on_outcomes(self, instructions: str) -> str:
        """Focus instructions on outcomes rather than process."""
        # Simplified implementation
        # Remove step-by-step guidance if present
        lines = instructions.split('\n')
        filtered_lines = [line for line in lines if not line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.'))]
        
        outcome_focused = '\n'.join(filtered_lines)
        outcome_focused += "\n\nKey outcomes expected:\n- High-quality solution that meets all requirements\n- Well-documented approach\n- Maintainable and extensible implementation"
        
        return outcome_focused
    
    def _make_direct(self, criticism: str) -> str:
        """Make criticism more direct."""
        # Simplified implementation
        # Remove softening language
        softeners = ["perhaps", "maybe", "might want to consider", "could potentially", "slightly", "somewhat"]
        result = criticism
        for softener in softeners:
            result = result.replace(softener, "")
        
        return result.strip()
    
    def _make_constructive(self, criticism: str) -> str:
        """Make criticism more constructive."""
        # Simplified implementation
        if not criticism.endswith('.'):
            criticism += '.'
            
        return criticism + " Here's how this could be improved: consider focusing on the core requirements first, then adding additional features as time permits. This approach would ensure the essential functionality is solid before expanding scope."
    
    def _apply_sandwich_method(self, criticism: str, positive: str) -> str:
        """Apply the feedback sandwich method (positive-criticism-positive)."""
        # Simplified implementation
        if not positive:
            positive = "The work shows good effort and attention to detail."
            
        return f"{positive} {criticism} Overall, this is progressing well and with these adjustments will be excellent."
    
    def _make_high_level(self, details: str) -> str:
        """Make detailed feedback more high-level."""
        # Simplified implementation
        # Extract first sentence from each paragraph
        paragraphs = details.split('\n\n')
        high_level = []
        
        for paragraph in paragraphs:
            sentences = paragraph.split('. ')
            if sentences:
                high_level.append(sentences[0])
        
        return '. '.join(high_level) + '.'


class PersonalizedAgentManager:
    """
    Manages personalized agent adaptations across multiple users.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the personalized agent manager.
        
        Args:
            storage_dir: Directory to store user profiles
        """
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "user_profiles")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.profiles = {}  # user_id -> UserPreferenceProfile
        self.adapters = {}  # user_id -> PersonalizedAgentAdapter
        
        # Load existing profiles
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load all user profiles from storage."""
        if not os.path.exists(self.storage_dir):
            return
            
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                user_id = filename[:-5]  # Remove .json extension
                profile_path = os.path.join(self.storage_dir, filename)
                
                try:
                    with open(profile_path, 'r') as f:
                        profile_data = json.load(f)
                        profile = UserPreferenceProfile.from_dict(profile_data)
                        self.profiles[user_id] = profile
                except Exception as e:
                    print(f"Error loading profile for {user_id}: {e}")
    
    def _save_profile(self, profile: UserPreferenceProfile) -> None:
        """
        Save a user profile to storage.
        
        Args:
            profile: The profile to save
        """
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)
            
        profile_path = os.path.join(self.storage_dir, f"{profile.user_id}.json")
        
        try:
            with open(profile_path, 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving profile for {profile.user_id}: {e}")
    
    def get_user_profile(self, user_id: str, create_if_missing: bool = True) -> Optional[UserPreferenceProfile]:
        """
        Get a user's preference profile.
        
        Args:
            user_id: The user ID
            create_if_missing: Whether to create a new profile if none exists
            
        Returns:
            The user's preference profile, or None if not found and create_if_missing is False
        """
        if user_id in self.profiles:
            return self.profiles[user_id]
            
        if create_if_missing:
            profile = UserPreferenceProfile(user_id)
            self.profiles[user_id] = profile
            self._save_profile(profile)
            return profile
            
        return None
    
    def get_personalized_agent(self, base_agent: Any, user_id: str) -> PersonalizedAgentAdapter:
        """
        Get a personalized agent adapter for a user.
        
        Args:
            base_agent: The base agent to adapt
            user_id: The user ID
            
        Returns:
            A personalized agent adapter
        """
        # Get or create user profile
        profile = self.get_user_profile(user_id)
        
        # Create adapter if it doesn't exist
        if user_id not in self.adapters:
            self.adapters[user_id] = PersonalizedAgentAdapter(base_agent, profile)
        else:
            # Update the adapter with the latest profile and agent
            self.adapters[user_id].user_profile = profile
            self.adapters[user_id].base_agent = base_agent
            
        return self.adapters[user_id]
    
    def update_user_preference(self, user_id: str, category: str, preference: str, value: Any) -> None:
        """
        Update a specific user preference.
        
        Args:
            user_id: The user ID
            category: The preference category
            preference: The specific preference
            value: The new value
        """
        profile = self.get_user_profile(user_id)
        profile.update_preference(category, preference, value)
        self._save_profile(profile)
    
    def record_user_interaction(self, user_id: str, interaction_type: str, 
                               content: Dict[str, Any], outcome: Optional[str] = None, 
                               satisfaction: Optional[float] = None) -> None:
        """
        Record a user interaction.
        
        Args:
            user_id: The user ID
            interaction_type: Type of interaction
            content: Details of the interaction
            outcome: Optional outcome
            satisfaction: Optional satisfaction score
        """
        profile = self.get_user_profile(user_id)
        profile.record_interaction(interaction_type, content, outcome, satisfaction)
        
        # Infer preferences from interactions
        profile.infer_preferences_from_interactions()
        
        self._save_profile(profile)
    
    def get_adaptation_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Get adaptation metrics for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Dictionary of adaptation metrics
        """
        if user_id not in self.profiles:
            return {}
            
        profile = self.profiles[user_id]
        
        metrics = {
            "profile_age_days": (datetime.datetime.now() - profile.created_at).days,
            "last_updated": profile.updated_at.isoformat(),
            "interaction_count": len(profile.interaction_history),
            "preference_confidence": profile.adaptation_metrics["preference_confidence"],
            "satisfaction_trend": self._calculate_satisfaction_trend(profile),
            "adaptation_success_rate": profile.calculate_adaptation_success_rate()
        }
        
        # Add adapter metrics if available
        if user_id in self.adapters:
            adapter_metrics = self.adapters[user_id].get_adaptation_metrics()
            metrics["adaptations"] = adapter_metrics
        
        return metrics
    
    def _calculate_satisfaction_trend(self, profile: UserPreferenceProfile) -> Dict[str, Any]:
        """
        Calculate the trend in user satisfaction scores.
        
        Args:
            profile: The user profile
            
        Returns:
            Dictionary with satisfaction trend metrics
        """
        scores = profile.adaptation_metrics["satisfaction_scores"]
        if len(scores) < 2:
            return {"trend": "insufficient_data"}
            
        # Calculate moving average
        window_size = min(5, len(scores))
        recent_avg = sum(scores[-window_size:]) / window_size
        
        if len(scores) < window_size * 2:
            return {"trend": "insufficient_data", "recent_average": recent_avg}
            
        previous_avg = sum(scores[-window_size*2:-window_size]) / window_size
        
        trend_value = recent_avg - previous_avg
        
        if trend_value > 0.1:
            trend = "improving"
        elif trend_value < -0.1:
            trend = "declining"
        else:
            trend = "stable"
            
        return {
            "trend": trend,
            "recent_average": recent_avg,
            "previous_average": previous_avg,
            "change": trend_value
        }
    
    def get_all_user_ids(self) -> List[str]:
        """
        Get all user IDs with profiles.
        
        Returns:
            List of user IDs
        """
        return list(self.profiles.keys())
    
    def delete_user_profile(self, user_id: str) -> bool:
        """
        Delete a user profile.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if successful, False otherwise
        """
        if user_id not in self.profiles:
            return False
            
        # Remove from memory
        del self.profiles[user_id]
        if user_id in self.adapters:
            del self.adapters[user_id]
            
        # Remove from storage
        profile_path = os.path.join(self.storage_dir, f"{user_id}.json")
        if os.path.exists(profile_path):
            try:
                os.remove(profile_path)
                return True
            except Exception as e:
                print(f"Error deleting profile for {user_id}: {e}")
                return False
        
        return True
