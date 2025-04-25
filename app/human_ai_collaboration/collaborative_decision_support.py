"""
Collaborative Decision Support Module

This module implements structured frameworks for human-AI joint decision-making.
It provides tools for collaborative decision processes, consensus building, and transparent reasoning.
"""

import json
import os
import datetime
import uuid
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
import numpy as np
from collections import defaultdict

class DecisionStatus(Enum):
    """Status of a collaborative decision."""
    INITIATED = "initiated"
    GATHERING_INPUT = "gathering_input"
    ANALYZING = "analyzing"
    PROPOSING = "proposing"
    DELIBERATING = "deliberating"
    FINALIZED = "finalized"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"


class DecisionFramework(Enum):
    """Types of decision frameworks supported."""
    PROS_CONS = "pros_cons"
    WEIGHTED_CRITERIA = "weighted_criteria"
    DECISION_MATRIX = "decision_matrix"
    SCENARIO_ANALYSIS = "scenario_analysis"
    DELPHI_METHOD = "delphi_method"
    SWOT_ANALYSIS = "swot_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    MULTI_VOTING = "multi_voting"


class DecisionParticipantRole(Enum):
    """Roles that participants can have in a decision."""
    DECISION_MAKER = "decision_maker"  # Has final authority
    ADVISOR = "advisor"  # Provides input but doesn't make final decision
    STAKEHOLDER = "stakeholder"  # Affected by decision but may not have direct input
    EXPERT = "expert"  # Provides specialized knowledge
    FACILITATOR = "facilitator"  # Manages the decision process
    OBSERVER = "observer"  # Observes but doesn't participate


class DecisionParticipant:
    """Represents a participant in a collaborative decision."""
    
    def __init__(self, participant_id: str, name: str, role: DecisionParticipantRole, 
                is_ai: bool = False, expertise: Optional[List[str]] = None):
        """
        Initialize a decision participant.
        
        Args:
            participant_id: Unique identifier for the participant
            name: Name of the participant
            role: Role of the participant in the decision
            is_ai: Whether the participant is an AI
            expertise: Areas of expertise for the participant
        """
        self.participant_id = participant_id
        self.name = name
        self.role = role
        self.is_ai = is_ai
        self.expertise = expertise or []
        self.contributions = []
        self.votes = {}
        
    def add_contribution(self, contribution_type: str, content: Any, 
                        timestamp: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        """
        Add a contribution from this participant.
        
        Args:
            contribution_type: Type of contribution (e.g., "comment", "proposal", "vote")
            content: Content of the contribution
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            The contribution record
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()
            
        contribution = {
            "id": str(uuid.uuid4()),
            "participant_id": self.participant_id,
            "type": contribution_type,
            "content": content,
            "timestamp": timestamp.isoformat()
        }
        
        self.contributions.append(contribution)
        return contribution
        
    def record_vote(self, option_id: str, value: Union[bool, float, str], 
                   rationale: Optional[str] = None) -> None:
        """
        Record a vote from this participant.
        
        Args:
            option_id: ID of the option being voted on
            value: Vote value (boolean, numeric rating, or string)
            rationale: Optional explanation for the vote
        """
        self.votes[option_id] = {
            "value": value,
            "timestamp": datetime.datetime.now().isoformat(),
            "rationale": rationale
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the participant
        """
        return {
            "participant_id": self.participant_id,
            "name": self.name,
            "role": self.role.value,
            "is_ai": self.is_ai,
            "expertise": self.expertise,
            # Exclude contributions and votes as they're stored with the decision
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionParticipant':
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation
            
        Returns:
            DecisionParticipant instance
        """
        return cls(
            participant_id=data["participant_id"],
            name=data["name"],
            role=DecisionParticipantRole(data["role"]),
            is_ai=data.get("is_ai", False),
            expertise=data.get("expertise", [])
        )


class DecisionOption:
    """Represents an option in a decision."""
    
    def __init__(self, option_id: str, name: str, description: str, 
                proposed_by: str, created_at: Optional[datetime.datetime] = None):
        """
        Initialize a decision option.
        
        Args:
            option_id: Unique identifier for the option
            name: Short name of the option
            description: Detailed description of the option
            proposed_by: ID of the participant who proposed this option
            created_at: Creation timestamp (defaults to now)
        """
        self.option_id = option_id
        self.name = name
        self.description = description
        self.proposed_by = proposed_by
        self.created_at = created_at or datetime.datetime.now()
        self.attributes = {}  # Additional attributes for evaluation
        self.pros = []  # List of pros
        self.cons = []  # List of cons
        self.comments = []  # Comments about this option
        
    def add_attribute(self, name: str, value: Any) -> None:
        """
        Add an attribute to this option.
        
        Args:
            name: Attribute name
            value: Attribute value
        """
        self.attributes[name] = value
        
    def add_pro(self, description: str, added_by: str, weight: float = 1.0) -> None:
        """
        Add a pro (advantage) to this option.
        
        Args:
            description: Description of the advantage
            added_by: ID of the participant who added this
            weight: Relative importance (0.0 to 1.0)
        """
        self.pros.append({
            "id": str(uuid.uuid4()),
            "description": description,
            "added_by": added_by,
            "weight": weight,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    def add_con(self, description: str, added_by: str, weight: float = 1.0) -> None:
        """
        Add a con (disadvantage) to this option.
        
        Args:
            description: Description of the disadvantage
            added_by: ID of the participant who added this
            weight: Relative importance (0.0 to 1.0)
        """
        self.cons.append({
            "id": str(uuid.uuid4()),
            "description": description,
            "added_by": added_by,
            "weight": weight,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    def add_comment(self, content: str, added_by: str) -> None:
        """
        Add a comment about this option.
        
        Args:
            content: Comment content
            added_by: ID of the participant who added this
        """
        self.comments.append({
            "id": str(uuid.uuid4()),
            "content": content,
            "added_by": added_by,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    def calculate_score(self) -> Dict[str, Any]:
        """
        Calculate a score for this option based on pros and cons.
        
        Returns:
            Dictionary with score details
        """
        pro_score = sum(pro["weight"] for pro in self.pros)
        con_score = sum(con["weight"] for con in self.cons)
        
        net_score = pro_score - con_score
        
        return {
            "pro_score": pro_score,
            "con_score": con_score,
            "net_score": net_score,
            "pro_count": len(self.pros),
            "con_count": len(self.cons)
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the option
        """
        return {
            "option_id": self.option_id,
            "name": self.name,
            "description": self.description,
            "proposed_by": self.proposed_by,
            "created_at": self.created_at.isoformat(),
            "attributes": self.attributes,
            "pros": self.pros,
            "cons": self.cons,
            "comments": self.comments
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionOption':
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation
            
        Returns:
            DecisionOption instance
        """
        option = cls(
            option_id=data["option_id"],
            name=data["name"],
            description=data["description"],
            proposed_by=data["proposed_by"],
            created_at=datetime.datetime.fromisoformat(data["created_at"])
        )
        
        option.attributes = data.get("attributes", {})
        option.pros = data.get("pros", [])
        option.cons = data.get("cons", [])
        option.comments = data.get("comments", [])
        
        return option


class EvaluationCriterion:
    """Represents a criterion for evaluating decision options."""
    
    def __init__(self, criterion_id: str, name: str, description: str, 
                weight: float = 1.0, created_by: Optional[str] = None):
        """
        Initialize an evaluation criterion.
        
        Args:
            criterion_id: Unique identifier for the criterion
            name: Name of the criterion
            description: Description of the criterion
            weight: Relative importance (0.0 to 1.0)
            created_by: ID of the participant who created this
        """
        self.criterion_id = criterion_id
        self.name = name
        self.description = description
        self.weight = weight
        self.created_by = created_by
        self.created_at = datetime.datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the criterion
        """
        return {
            "criterion_id": self.criterion_id,
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationCriterion':
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation
            
        Returns:
            EvaluationCriterion instance
        """
        criterion = cls(
            criterion_id=data["criterion_id"],
            name=data["name"],
            description=data["description"],
            weight=data.get("weight", 1.0),
            created_by=data.get("created_by")
        )
        
        if "created_at" in data:
            criterion.created_at = datetime.datetime.fromisoformat(data["created_at"])
            
        return criterion


class CollaborativeDecision:
    """Represents a collaborative decision process."""
    
    def __init__(self, decision_id: str, title: str, description: str, 
                framework: DecisionFramework, created_by: str):
        """
        Initialize a collaborative decision.
        
        Args:
            decision_id: Unique identifier for the decision
            title: Title of the decision
            description: Description of the decision context
            framework: Decision framework to use
            created_by: ID of the participant who created this
        """
        self.decision_id = decision_id
        self.title = title
        self.description = description
        self.framework = framework
        self.created_by = created_by
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.status = DecisionStatus.INITIATED
        
        self.participants = {}  # participant_id -> DecisionParticipant
        self.options = {}  # option_id -> DecisionOption
        self.criteria = {}  # criterion_id -> EvaluationCriterion
        
        self.timeline = []  # List of events in the decision process
        self.evaluations = {}  # participant_id -> {option_id -> {criterion_id -> score}}
        self.final_decision = None  # ID of the selected option
        self.decision_rationale = None  # Explanation for the final decision
        
        # Record creation event
        self._add_timeline_event("decision_created", {
            "created_by": created_by
        })
        
    def add_participant(self, participant: DecisionParticipant) -> None:
        """
        Add a participant to the decision.
        
        Args:
            participant: The participant to add
        """
        self.participants[participant.participant_id] = participant
        
        # Record event
        self._add_timeline_event("participant_added", {
            "participant_id": participant.participant_id,
            "name": participant.name,
            "role": participant.role.value
        })
        
    def add_option(self, option: DecisionOption) -> None:
        """
        Add an option to the decision.
        
        Args:
            option: The option to add
        """
        self.options[option.option_id] = option
        
        # Record event
        self._add_timeline_event("option_added", {
            "option_id": option.option_id,
            "name": option.name,
            "proposed_by": option.proposed_by
        })
        
    def add_criterion(self, criterion: EvaluationCriterion) -> None:
        """
        Add an evaluation criterion to the decision.
        
        Args:
            criterion: The criterion to add
        """
        self.criteria[criterion.criterion_id] = criterion
        
        # Record event
        self._add_timeline_event("criterion_added", {
            "criterion_id": criterion.criterion_id,
            "name": criterion.name,
            "weight": criterion.weight,
            "created_by": criterion.created_by
        })
        
    def record_evaluation(self, participant_id: str, option_id: str, 
                         criterion_id: str, score: float, 
                         comment: Optional[str] = None) -> None:
        """
        Record an evaluation of an option against a criterion.
        
        Args:
            participant_id: ID of the evaluating participant
            option_id: ID of the option being evaluated
            criterion_id: ID of the criterion being used
            score: Evaluation score (typically 0.0 to 1.0)
            comment: Optional comment explaining the evaluation
        """
        # Ensure participant, option, and criterion exist
        if participant_id not in self.participants:
            raise ValueError(f"Participant {participant_id} not found")
        if option_id not in self.options:
            raise ValueError(f"Option {option_id} not found")
        if criterion_id not in self.criteria:
            raise ValueError(f"Criterion {criterion_id} not found")
            
        # Initialize nested dictionaries if needed
        if participant_id not in self.evaluations:
            self.evaluations[participant_id] = {}
        if option_id not in self.evaluations[participant_id]:
            self.evaluations[participant_id][option_id] = {}
            
        # Record the evaluation
        self.evaluations[participant_id][option_id][criterion_id] = {
            "score": score,
            "comment": comment,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Record event
        self._add_timeline_event("evaluation_recorded", {
            "participant_id": participant_id,
            "option_id": option_id,
            "criterion_id": criterion_id,
            "score": score
        })
        
        self.updated_at = datetime.datetime.now()
        
    def add_contribution(self, participant_id: str, contribution_type: str, 
                        content: Any) -> Dict[str, Any]:
        """
        Add a contribution from a participant.
        
        Args:
            participant_id: ID of the contributing participant
            contribution_type: Type of contribution
            content: Content of the contribution
            
        Returns:
            The contribution record
        """
        if participant_id not in self.participants:
            raise ValueError(f"Participant {participant_id} not found")
            
        contribution = self.participants[participant_id].add_contribution(
            contribution_type, content)
            
        # Record event
        self._add_timeline_event("contribution_added", {
            "participant_id": participant_id,
            "contribution_id": contribution["id"],
            "type": contribution_type
        })
        
        self.updated_at = datetime.datetime.now()
        return contribution
        
    def record_vote(self, participant_id: str, option_id: str, 
                   value: Union[bool, float, str], 
                   rationale: Optional[str] = None) -> None:
        """
        Record a vote from a participant.
        
        Args:
            participant_id: ID of the voting participant
            option_id: ID of the option being voted on
            value: Vote value
            rationale: Optional explanation for the vote
        """
        if participant_id not in self.participants:
            raise ValueError(f"Participant {participant_id} not found")
        if option_id not in self.options:
            raise ValueError(f"Option {option_id} not found")
            
        self.participants[participant_id].record_vote(option_id, value, rationale)
        
        # Record event
        self._add_timeline_event("vote_recorded", {
            "participant_id": participant_id,
            "option_id": option_id,
            "value": value
        })
        
        self.updated_at = datetime.datetime.now()
        
    def update_status(self, new_status: DecisionStatus, 
                     comment: Optional[str] = None) -> None:
        """
        Update the status of the decision.
        
        Args:
            new_status: New status
            comment: Optional comment explaining the status change
        """
        old_status = self.status
        self.status = new_status
        
        # Record event
        self._add_timeline_event("status_changed", {
            "old_status": old_status.value,
            "new_status": new_status.value,
            "comment": comment
        })
        
        self.updated_at = datetime.datetime.now()
        
    def finalize_decision(self, selected_option_id: str, 
                         rationale: str, decided_by: str) -> None:
        """
        Finalize the decision by selecting an option.
        
        Args:
            selected_option_id: ID of the selected option
            rationale: Explanation for the selection
            decided_by: ID of the participant who made the final decision
        """
        if selected_option_id not in self.options:
            raise ValueError(f"Option {selected_option_id} not found")
        if decided_by not in self.participants:
            raise ValueError(f"Participant {decided_by} not found")
            
        self.final_decision = selected_option_id
        self.decision_rationale = rationale
        
        # Update status
        self.update_status(DecisionStatus.FINALIZED, 
                          f"Decision finalized by {self.participants[decided_by].name}")
        
        # Record event
        self._add_timeline_event("decision_finalized", {
            "selected_option_id": selected_option_id,
            "rationale": rationale,
            "decided_by": decided_by
        })
        
    def _add_timeline_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Add an event to the decision timeline.
        
        Args:
            event_type: Type of event
            details: Event details
        """
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "type": event_type,
            "details": details
        }
        
        self.timeline.append(event)
        
    def calculate_option_scores(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculate scores for all options based on evaluations.
        
        Returns:
            Dictionary mapping option IDs to score details
        """
        results = {}
        
        for option_id, option in self.options.items():
            # Get base scores from pros/cons
            base_scores = option.calculate_score()
            
            # Calculate weighted scores from criteria evaluations
            criteria_scores = {}
            weighted_sum = 0
            total_weight = 0
            
            # For each criterion
            for criterion_id, criterion in self.criteria.items():
                criterion_scores = []
                
                # Collect scores from all participants for this option and criterion
                for participant_id, participant_evals in self.evaluations.items():
                    if option_id in participant_evals and criterion_id in participant_evals[option_id]:
                        criterion_scores.append(participant_evals[option_id][criterion_id]["score"])
                
                # Calculate average score for this criterion if there are any evaluations
                if criterion_scores:
                    avg_score = sum(criterion_scores) / len(criterion_scores)
                    weighted_score = avg_score * criterion.weight
                    
                    criteria_scores[criterion_id] = {
                        "average_score": avg_score,
                        "weighted_score": weighted_score,
                        "criterion_weight": criterion.weight,
                        "evaluation_count": len(criterion_scores)
                    }
                    
                    weighted_sum += weighted_score
                    total_weight += criterion.weight
            
            # Calculate overall weighted average if there are any criteria with weights
            overall_score = weighted_sum / total_weight if total_weight > 0 else None
            
            # Combine results
            results[option_id] = {
                **base_scores,
                "criteria_scores": criteria_scores,
                "overall_score": overall_score,
                "vote_count": sum(1 for p in self.participants.values() if option_id in p.votes),
                "positive_votes": sum(1 for p in self.participants.values() 
                                    if option_id in p.votes and p.votes[option_id]["value"] is True)
            }
            
        return results
        
    def get_decision_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the decision process.
        
        Returns:
            Dictionary with decision summary
        """
        # Calculate current scores
        option_scores = self.calculate_option_scores()
        
        # Count participants by role
        role_counts = defaultdict(int)
        for participant in self.participants.values():
            role_counts[participant.role.value] += 1
            
        # Get final decision details if available
        final_decision_details = None
        if self.final_decision:
            selected_option = self.options.get(self.final_decision)
            if selected_option:
                final_decision_details = {
                    "option_id": self.final_decision,
                    "name": selected_option.name,
                    "rationale": self.decision_rationale,
                    "scores": option_scores.get(self.final_decision)
                }
        
        return {
            "decision_id": self.decision_id,
            "title": self.title,
            "status": self.status.value,
            "framework": self.framework.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "participant_count": len(self.participants),
            "participant_roles": dict(role_counts),
            "option_count": len(self.options),
            "criteria_count": len(self.criteria),
            "evaluation_count": sum(len(p_evals) for p_evals in self.evaluations.values()),
            "timeline_event_count": len(self.timeline),
            "option_scores": option_scores,
            "final_decision": final_decision_details,
            "duration": (self.updated_at - self.created_at).total_seconds()
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the decision
        """
        return {
            "decision_id": self.decision_id,
            "title": self.title,
            "description": self.description,
            "framework": self.framework.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value,
            "participants": {p_id: p.to_dict() for p_id, p in self.participants.items()},
            "options": {o_id: o.to_dict() for o_id, o in self.options.items()},
            "criteria": {c_id: c.to_dict() for c_id, c in self.criteria.items()},
            "timeline": self.timeline,
            "evaluations": self.evaluations,
            "final_decision": self.final_decision,
            "decision_rationale": self.decision_rationale
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollaborativeDecision':
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation
            
        Returns:
            CollaborativeDecision instance
        """
        decision = cls(
            decision_id=data["decision_id"],
            title=data["title"],
            description=data["description"],
            framework=DecisionFramework(data["framework"]),
            created_by=data["created_by"]
        )
        
        # Restore timestamps
        decision.created_at = datetime.datetime.fromisoformat(data["created_at"])
        decision.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
        
        # Restore status
        decision.status = DecisionStatus(data["status"])
        
        # Restore participants
        for p_id, p_data in data.get("participants", {}).items():
            decision.participants[p_id] = DecisionParticipant.from_dict(p_data)
            
        # Restore options
        for o_id, o_data in data.get("options", {}).items():
            decision.options[o_id] = DecisionOption.from_dict(o_data)
            
        # Restore criteria
        for c_id, c_data in data.get("criteria", {}).items():
            decision.criteria[c_id] = EvaluationCriterion.from_dict(c_data)
            
        # Restore other fields
        decision.timeline = data.get("timeline", [])
        decision.evaluations = data.get("evaluations", {})
        decision.final_decision = data.get("final_decision")
        decision.decision_rationale = data.get("decision_rationale")
        
        return decision


class CollaborativeDecisionManager:
    """Manages collaborative decisions."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the collaborative decision manager.
        
        Args:
            storage_dir: Directory to store decisions
        """
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "decisions")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.decisions = {}  # decision_id -> CollaborativeDecision
        
        # Load existing decisions
        self._load_decisions()
        
    def _load_decisions(self) -> None:
        """Load all decisions from storage."""
        if not os.path.exists(self.storage_dir):
            return
            
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                decision_id = filename[:-5]  # Remove .json extension
                decision_path = os.path.join(self.storage_dir, filename)
                
                try:
                    with open(decision_path, 'r') as f:
                        decision_data = json.load(f)
                        decision = CollaborativeDecision.from_dict(decision_data)
                        self.decisions[decision_id] = decision
                except Exception as e:
                    print(f"Error loading decision {decision_id}: {e}")
                    
    def _save_decision(self, decision: CollaborativeDecision) -> None:
        """
        Save a decision to storage.
        
        Args:
            decision: The decision to save
        """
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)
            
        decision_path = os.path.join(self.storage_dir, f"{decision.decision_id}.json")
        
        try:
            with open(decision_path, 'w') as f:
                json.dump(decision.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving decision {decision.decision_id}: {e}")
            
    def create_decision(self, title: str, description: str, 
                       framework: DecisionFramework, created_by: str) -> CollaborativeDecision:
        """
        Create a new collaborative decision.
        
        Args:
            title: Title of the decision
            description: Description of the decision context
            framework: Decision framework to use
            created_by: ID of the participant who created this
            
        Returns:
            The created decision
        """
        decision_id = str(uuid.uuid4())
        decision = CollaborativeDecision(
            decision_id=decision_id,
            title=title,
            description=description,
            framework=framework,
            created_by=created_by
        )
        
        self.decisions[decision_id] = decision
        self._save_decision(decision)
        
        return decision
        
    def get_decision(self, decision_id: str) -> Optional[CollaborativeDecision]:
        """
        Get a decision by ID.
        
        Args:
            decision_id: ID of the decision
            
        Returns:
            The decision, or None if not found
        """
        return self.decisions.get(decision_id)
        
    def update_decision(self, decision: CollaborativeDecision) -> None:
        """
        Update a decision in storage.
        
        Args:
            decision: The decision to update
        """
        self.decisions[decision.decision_id] = decision
        self._save_decision(decision)
        
    def delete_decision(self, decision_id: str) -> bool:
        """
        Delete a decision.
        
        Args:
            decision_id: ID of the decision to delete
            
        Returns:
            True if successful, False otherwise
        """
        if decision_id not in self.decisions:
            return False
            
        # Remove from memory
        del self.decisions[decision_id]
        
        # Remove from storage
        decision_path = os.path.join(self.storage_dir, f"{decision_id}.json")
        if os.path.exists(decision_path):
            try:
                os.remove(decision_path)
                return True
            except Exception as e:
                print(f"Error deleting decision {decision_id}: {e}")
                return False
        
        return True
        
    def get_all_decisions(self) -> List[CollaborativeDecision]:
        """
        Get all decisions.
        
        Returns:
            List of all decisions
        """
        return list(self.decisions.values())
        
    def get_decisions_by_participant(self, participant_id: str) -> List[CollaborativeDecision]:
        """
        Get all decisions involving a participant.
        
        Args:
            participant_id: ID of the participant
            
        Returns:
            List of decisions involving the participant
        """
        return [d for d in self.decisions.values() 
               if participant_id in d.participants]
               
    def get_decisions_by_status(self, status: DecisionStatus) -> List[CollaborativeDecision]:
        """
        Get all decisions with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of decisions with the specified status
        """
        return [d for d in self.decisions.values() 
               if d.status == status]
               
    def get_decision_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all decisions.
        
        Returns:
            Dictionary with decision statistics
        """
        if not self.decisions:
            return {"count": 0}
            
        # Count decisions by status
        status_counts = defaultdict(int)
        for decision in self.decisions.values():
            status_counts[decision.status.value] += 1
            
        # Count decisions by framework
        framework_counts = defaultdict(int)
        for decision in self.decisions.values():
            framework_counts[decision.framework.value] += 1
            
        # Calculate average participants per decision
        avg_participants = sum(len(d.participants) for d in self.decisions.values()) / len(self.decisions)
        
        # Calculate average options per decision
        avg_options = sum(len(d.options) for d in self.decisions.values()) / len(self.decisions)
        
        # Calculate average decision duration (for finalized decisions)
        finalized_decisions = [d for d in self.decisions.values() 
                              if d.status in (DecisionStatus.FINALIZED, DecisionStatus.IMPLEMENTED)]
        avg_duration = None
        if finalized_decisions:
            durations = [(d.updated_at - d.created_at).total_seconds() for d in finalized_decisions]
            avg_duration = sum(durations) / len(durations)
            
        return {
            "count": len(self.decisions),
            "status_counts": dict(status_counts),
            "framework_counts": dict(framework_counts),
            "avg_participants": avg_participants,
            "avg_options": avg_options,
            "avg_duration_seconds": avg_duration,
            "finalized_count": len(finalized_decisions)
        }


class DecisionSupportAgent:
    """Agent that provides decision support in collaborative decisions."""
    
    def __init__(self, agent_id: str, name: str):
        """
        Initialize a decision support agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Name of the agent
        """
        self.agent_id = agent_id
        self.name = name
        
    def create_participant(self, role: DecisionParticipantRole, 
                          expertise: Optional[List[str]] = None) -> DecisionParticipant:
        """
        Create a participant representation of this agent.
        
        Args:
            role: Role for the agent in the decision
            expertise: Areas of expertise
            
        Returns:
            DecisionParticipant instance
        """
        return DecisionParticipant(
            participant_id=self.agent_id,
            name=self.name,
            role=role,
            is_ai=True,
            expertise=expertise
        )
        
    def analyze_decision(self, decision: CollaborativeDecision) -> Dict[str, Any]:
        """
        Analyze a decision and provide insights.
        
        Args:
            decision: The decision to analyze
            
        Returns:
            Dictionary with analysis results
        """
        # Get current scores
        option_scores = decision.calculate_option_scores()
        
        # Rank options by overall score
        ranked_options = sorted(
            [(option_id, scores.get("overall_score", 0)) 
             for option_id, scores in option_scores.items() if scores.get("overall_score") is not None],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Identify consensus and disagreement
        consensus_level = self._calculate_consensus_level(decision)
        
        # Identify missing information
        missing_info = self._identify_missing_information(decision)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(decision, option_scores, consensus_level, missing_info)
        
        return {
            "ranked_options": ranked_options,
            "consensus_level": consensus_level,
            "missing_information": missing_info,
            "recommendations": recommendations
        }
        
    def _calculate_consensus_level(self, decision: CollaborativeDecision) -> Dict[str, Any]:
        """
        Calculate the level of consensus among participants.
        
        Args:
            decision: The decision to analyze
            
        Returns:
            Dictionary with consensus metrics
        """
        # If no evaluations or votes, return low consensus
        if not decision.evaluations and not any(p.votes for p in decision.participants.values()):
            return {
                "level": "unknown",
                "score": 0.0,
                "description": "Insufficient data to determine consensus"
            }
            
        # Calculate consensus based on evaluations
        evaluation_consensus = None
        if decision.evaluations:
            # Calculate variance in scores for each option and criterion
            variances = []
            
            for option_id in decision.options:
                for criterion_id in decision.criteria:
                    scores = []
                    
                    for participant_evals in decision.evaluations.values():
                        if (option_id in participant_evals and 
                            criterion_id in participant_evals[option_id]):
                            scores.append(participant_evals[option_id][criterion_id]["score"])
                    
                    if len(scores) >= 2:  # Need at least 2 scores to calculate variance
                        variances.append(np.var(scores))
            
            if variances:
                # Lower variance means higher consensus
                avg_variance = sum(variances) / len(variances)
                # Convert to a 0-1 scale where 1 is perfect consensus
                evaluation_consensus = max(0, 1 - min(1, avg_variance * 4))
        
        # Calculate consensus based on votes
        vote_consensus = None
        vote_counts = defaultdict(int)
        total_votes = 0
        
        for participant in decision.participants.values():
            for option_id, vote in participant.votes.items():
                vote_value = vote["value"]
                if isinstance(vote_value, bool) and vote_value is True:
                    vote_counts[option_id] += 1
                    total_votes += 1
        
        if total_votes > 0:
            # Calculate entropy of vote distribution
            vote_probs = [count / total_votes for count in vote_counts.values()]
            entropy = -sum(p * np.log2(p) for p in vote_probs)
            max_entropy = np.log2(len(vote_counts)) if len(vote_counts) > 0 else 0
            
            # Normalize to 0-1 scale where 1 is perfect consensus
            if max_entropy > 0:
                vote_consensus = 1 - (entropy / max_entropy)
            else:
                vote_consensus = 1.0
        
        # Combine consensus measures
        if evaluation_consensus is not None and vote_consensus is not None:
            consensus_score = (evaluation_consensus + vote_consensus) / 2
        elif evaluation_consensus is not None:
            consensus_score = evaluation_consensus
        elif vote_consensus is not None:
            consensus_score = vote_consensus
        else:
            consensus_score = 0.0
        
        # Determine consensus level
        if consensus_score >= 0.8:
            level = "high"
            description = "Strong consensus among participants"
        elif consensus_score >= 0.5:
            level = "moderate"
            description = "Some consensus with areas of disagreement"
        else:
            level = "low"
            description = "Significant disagreement among participants"
            
        return {
            "level": level,
            "score": consensus_score,
            "description": description,
            "evaluation_consensus": evaluation_consensus,
            "vote_consensus": vote_consensus
        }
        
    def _identify_missing_information(self, decision: CollaborativeDecision) -> List[Dict[str, Any]]:
        """
        Identify missing information in the decision.
        
        Args:
            decision: The decision to analyze
            
        Returns:
            List of missing information items
        """
        missing_info = []
        
        # Check for options without evaluations
        for option_id, option in decision.options.items():
            has_evaluations = False
            
            for participant_evals in decision.evaluations.values():
                if option_id in participant_evals:
                    has_evaluations = True
                    break
                    
            if not has_evaluations:
                missing_info.append({
                    "type": "missing_evaluations",
                    "item_id": option_id,
                    "name": option.name,
                    "description": f"Option '{option.name}' has not been evaluated"
                })
                
        # Check for criteria without weights
        for criterion_id, criterion in decision.criteria.items():
            if criterion.weight is None or criterion.weight == 0:
                missing_info.append({
                    "type": "missing_criterion_weight",
                    "item_id": criterion_id,
                    "name": criterion.name,
                    "description": f"Criterion '{criterion.name}' has no weight assigned"
                })
                
        # Check for decision makers without votes
        decision_makers = [p for p in decision.participants.values() 
                          if p.role == DecisionParticipantRole.DECISION_MAKER]
        
        for participant in decision_makers:
            if not participant.votes:
                missing_info.append({
                    "type": "missing_decision_maker_vote",
                    "item_id": participant.participant_id,
                    "name": participant.name,
                    "description": f"Decision maker '{participant.name}' has not voted"
                })
                
        return missing_info
        
    def _generate_recommendations(self, decision: CollaborativeDecision, 
                                option_scores: Dict[str, Dict[str, Any]],
                                consensus_level: Dict[str, Any],
                                missing_info: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate recommendations for the decision.
        
        Args:
            decision: The decision to analyze
            option_scores: Scores for each option
            consensus_level: Consensus analysis results
            missing_info: Missing information analysis
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Recommend next steps based on status
        if decision.status == DecisionStatus.INITIATED:
            recommendations.append({
                "type": "next_step",
                "recommendation": "Define evaluation criteria to structure the decision process"
            })
            
        elif decision.status == DecisionStatus.GATHERING_INPUT:
            if not decision.options:
                recommendations.append({
                    "type": "next_step",
                    "recommendation": "Add options to consider in the decision"
                })
            elif not decision.criteria:
                recommendations.append({
                    "type": "next_step",
                    "recommendation": "Define evaluation criteria to assess the options"
                })
            else:
                recommendations.append({
                    "type": "next_step",
                    "recommendation": "Begin evaluating options against criteria"
                })
                
        elif decision.status == DecisionStatus.ANALYZING:
            if missing_info:
                recommendations.append({
                    "type": "next_step",
                    "recommendation": "Address missing information before proceeding"
                })
            else:
                recommendations.append({
                    "type": "next_step",
                    "recommendation": "Review analysis and prepare to propose a decision"
                })
                
        elif decision.status == DecisionStatus.PROPOSING:
            if consensus_level["level"] == "low":
                recommendations.append({
                    "type": "next_step",
                    "recommendation": "Facilitate discussion to address areas of disagreement"
                })
            else:
                recommendations.append({
                    "type": "next_step",
                    "recommendation": "Proceed to deliberation and final decision"
                })
                
        # Recommend addressing missing information
        for item in missing_info:
            recommendations.append({
                "type": "missing_information",
                "recommendation": item["description"]
            })
            
        # Recommend based on consensus level
        if consensus_level["level"] == "low":
            recommendations.append({
                "type": "consensus",
                "recommendation": "Consider additional discussion to build consensus before finalizing"
            })
            
        # Recommend top option if clear leader exists
        ranked_options = sorted(
            [(option_id, scores.get("overall_score", 0)) 
             for option_id, scores in option_scores.items() if scores.get("overall_score") is not None],
            key=lambda x: x[1],
            reverse=True
        )
        
        if ranked_options and len(ranked_options) >= 2:
            top_option_id, top_score = ranked_options[0]
            second_option_id, second_score = ranked_options[1]
            
            if top_score > second_score * 1.2:  # Clear leader (20% better than second)
                top_option = decision.options[top_option_id]
                recommendations.append({
                    "type": "leading_option",
                    "recommendation": f"'{top_option.name}' is the clear leading option based on evaluations"
                })
                
        return recommendations
        
    def generate_decision_summary(self, decision: CollaborativeDecision) -> str:
        """
        Generate a human-readable summary of the decision.
        
        Args:
            decision: The decision to summarize
            
        Returns:
            Summary text
        """
        # Get decision details
        summary = decision.get_decision_summary()
        
        # Format as text
        text = f"# Decision Summary: {decision.title}\n\n"
        text += f"**Status:** {decision.status.value}\n"
        text += f"**Framework:** {decision.framework.value}\n"
        text += f"**Created:** {decision.created_at.strftime('%Y-%m-%d')}\n\n"
        
        text += f"## Participants ({len(decision.participants)})\n"
        role_counts = defaultdict(int)
        for p in decision.participants.values():
            role_counts[p.role.value] += 1
        for role, count in role_counts.items():
            text += f"- {role}: {count}\n"
        text += "\n"
        
        text += f"## Options ({len(decision.options)})\n"
        
        # Sort options by score if available
        option_items = list(decision.options.items())
        option_scores = summary.get("option_scores", {})
        if option_scores:
            option_items.sort(
                key=lambda x: option_scores.get(x[0], {}).get("overall_score", 0),
                reverse=True
            )
            
        for option_id, option in option_items:
            text += f"### {option.name}\n"
            text += f"{option.description}\n\n"
            
            if option_id in option_scores:
                scores = option_scores[option_id]
                if scores.get("overall_score") is not None:
                    text += f"**Overall Score:** {scores['overall_score']:.2f}\n"
                text += f"**Pros:** {scores['pro_count']}, **Cons:** {scores['con_count']}\n"
                text += f"**Votes:** {scores['vote_count']}, **Positive Votes:** {scores['positive_votes']}\n\n"
                
        if decision.final_decision:
            text += "## Final Decision\n"
            selected_option = decision.options.get(decision.final_decision)
            if selected_option:
                text += f"**Selected Option:** {selected_option.name}\n\n"
                text += f"**Rationale:** {decision.decision_rationale}\n\n"
                
        # Add analysis
        analysis = self.analyze_decision(decision)
        
        text += "## Analysis\n"
        text += f"**Consensus Level:** {analysis['consensus_level']['level']} "
        text += f"({analysis['consensus_level']['score']:.2f})\n"
        text += f"**Description:** {analysis['consensus_level']['description']}\n\n"
        
        if analysis['missing_information']:
            text += "### Missing Information\n"
            for item in analysis['missing_information']:
                text += f"- {item['description']}\n"
            text += "\n"
            
        if analysis['recommendations']:
            text += "### Recommendations\n"
            for item in analysis['recommendations']:
                text += f"- {item['recommendation']}\n"
                
        return text
        
    def facilitate_decision(self, decision: CollaborativeDecision) -> Dict[str, Any]:
        """
        Provide facilitation for a decision in progress.
        
        Args:
            decision: The decision to facilitate
            
        Returns:
            Dictionary with facilitation actions
        """
        # Analyze current state
        analysis = self.analyze_decision(decision)
        
        # Determine appropriate facilitation actions
        actions = []
        
        # Add missing participants if needed
        if len(decision.participants) < 3:
            actions.append({
                "type": "suggestion",
                "action": "add_participants",
                "description": "Consider adding more participants for diverse perspectives"
            })
            
        # Suggest adding options if few exist
        if len(decision.options) < 2:
            actions.append({
                "type": "suggestion",
                "action": "add_options",
                "description": "Add more options to consider for a thorough decision process"
            })
            
        # Suggest adding criteria if few exist
        if len(decision.criteria) < 2:
            actions.append({
                "type": "suggestion",
                "action": "add_criteria",
                "description": "Define evaluation criteria to structure the assessment"
            })
            
        # Suggest status updates
        if decision.status == DecisionStatus.INITIATED and decision.options and decision.criteria:
            actions.append({
                "type": "suggestion",
                "action": "update_status",
                "target_status": DecisionStatus.GATHERING_INPUT.value,
                "description": "Move to gathering input phase to begin evaluations"
            })
            
        elif (decision.status == DecisionStatus.GATHERING_INPUT and 
              decision.evaluations and not analysis['missing_information']):
            actions.append({
                "type": "suggestion",
                "action": "update_status",
                "target_status": DecisionStatus.ANALYZING.value,
                "description": "Move to analyzing phase to review evaluations"
            })
            
        elif (decision.status == DecisionStatus.ANALYZING and 
              analysis['consensus_level']['level'] in ('moderate', 'high')):
            actions.append({
                "type": "suggestion",
                "action": "update_status",
                "target_status": DecisionStatus.PROPOSING.value,
                "description": "Move to proposing phase to consider final decision"
            })
            
        # Add contribution if agent is a participant
        if self.agent_id in decision.participants:
            participant = decision.participants[self.agent_id]
            
            # Add evaluations if missing
            missing_evals = []
            for option_id in decision.options:
                for criterion_id in decision.criteria:
                    if (self.agent_id not in decision.evaluations or
                        option_id not in decision.evaluations.get(self.agent_id, {}) or
                        criterion_id not in decision.evaluations.get(self.agent_id, {}).get(option_id, {})):
                        missing_evals.append((option_id, criterion_id))
                        
            if missing_evals:
                option_id, criterion_id = missing_evals[0]
                actions.append({
                    "type": "contribution",
                    "action": "add_evaluation",
                    "option_id": option_id,
                    "criterion_id": criterion_id,
                    "description": f"Evaluate option '{decision.options[option_id].name}' against criterion '{decision.criteria[criterion_id].name}'"
                })
                
            # Add vote if missing and decision maker
            if (participant.role == DecisionParticipantRole.DECISION_MAKER and
                not participant.votes and decision.options):
                
                # Find best option based on evaluations
                option_scores = decision.calculate_option_scores()
                best_option_id = None
                best_score = -1
                
                for option_id, scores in option_scores.items():
                    if scores.get("overall_score", 0) > best_score:
                        best_score = scores.get("overall_score", 0)
                        best_option_id = option_id
                        
                if best_option_id:
                    actions.append({
                        "type": "contribution",
                        "action": "add_vote",
                        "option_id": best_option_id,
                        "value": True,
                        "description": f"Vote for option '{decision.options[best_option_id].name}' based on evaluation scores"
                    })
                    
        return {
            "analysis": analysis,
            "actions": actions
        }
