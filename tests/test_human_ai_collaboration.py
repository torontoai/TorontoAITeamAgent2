"""
Test script for the Human-AI Collaboration features.

This script tests the functionality of the Personalized Agent Adaptation and
Collaborative Decision Support features.
"""

import os
import sys
import logging
import json
import datetime
import unittest
from typing import Dict, Any, List
from unittest.mock import MagicMock, patch

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import human-ai collaboration components
from app.human_ai_collaboration.personalized_agent_adaptation import (
    UserPreferenceProfile, PersonalizedAgentAdapter
)
from app.human_ai_collaboration.collaborative_decision_support import (
    DecisionStatus, DecisionFramework, DecisionParticipantRole,
    DecisionParticipant, DecisionOption, EvaluationCriterion,
    CollaborativeDecision, CollaborativeDecisionSupport
)


class TestPersonalizedAgentAdaptation(unittest.TestCase):
    """Test cases for Personalized Agent Adaptation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_profile = UserPreferenceProfile(
            user_id="test_user_1",
            name="Test User"
        )
        
        # Mock base agent
        self.base_agent = MagicMock()
        self.base_agent.generate_response.return_value = "This is a test response."
        
        self.adapter = PersonalizedAgentAdapter(
            base_agent=self.base_agent,
            user_profile=self.user_profile
        )
    
    def test_user_preference_profile_creation(self):
        """Test creating a user preference profile."""
        profile = UserPreferenceProfile(
            user_id="test_user_2",
            name="Another Test User"
        )
        
        self.assertEqual(profile.user_id, "test_user_2")
        self.assertEqual(profile.name, "Another Test User")
        self.assertIsInstance(profile.created_at, datetime.datetime)
        self.assertIsInstance(profile.updated_at, datetime.datetime)
        
        # Check default preferences
        self.assertIn("verbosity", profile.communication_style)
        self.assertIn("autonomy_level", profile.work_style)
        self.assertIn("data_vs_intuition", profile.decision_making)
        self.assertIn("feedback_frequency", profile.feedback_preferences)
    
    def test_update_preference(self):
        """Test updating a user preference."""
        self.user_profile.update_preference(
            category="communication_style",
            preference="verbosity",
            value=0.8
        )
        
        self.assertEqual(self.user_profile.communication_style["verbosity"], 0.8)
        
        # Check that confidence was updated
        self.assertIn("verbosity", self.user_profile.adaptation_metrics["preference_confidence"])
        self.assertGreater(self.user_profile.adaptation_metrics["preference_confidence"]["verbosity"], 0)
    
    def test_record_interaction(self):
        """Test recording a user interaction."""
        self.user_profile.record_interaction(
            interaction_type="message",
            content={"sender": "user", "text": "This is a test message."},
            outcome="response_generated",
            satisfaction=0.9
        )
        
        self.assertEqual(len(self.user_profile.interaction_history), 1)
        self.assertEqual(self.user_profile.interaction_history[0]["type"], "message")
        self.assertEqual(self.user_profile.interaction_history[0]["satisfaction"], 0.9)
        
        # Check that satisfaction metrics were updated
        self.assertEqual(len(self.user_profile.adaptation_metrics["satisfaction_scores"]), 1)
        self.assertEqual(self.user_profile.adaptation_metrics["satisfaction_scores"][0], 0.9)
    
    def test_infer_preferences_from_interactions(self):
        """Test inferring preferences from interactions."""
        # Add multiple interactions
        self.user_profile.record_interaction(
            interaction_type="message",
            content={"sender": "user", "text": "This is a short message."},
            satisfaction=0.7
        )
        
        self.user_profile.record_interaction(
            interaction_type="message",
            content={"sender": "user", "text": "This is another short message."},
            satisfaction=0.8
        )
        
        self.user_profile.record_interaction(
            interaction_type="task",
            content={"instructions": "Please complete this task with minimal guidance."},
            satisfaction=0.9
        )
        
        # Infer preferences
        inferred = self.user_profile.infer_preferences_from_interactions()
        
        self.assertIsInstance(inferred, dict)
        self.assertGreater(len(inferred), 0)
        
        # Check that learned preferences were updated
        self.assertGreater(len(self.user_profile.learned_preferences), 0)
    
    def test_get_effective_preferences(self):
        """Test getting effective preferences."""
        # Set explicit preferences
        self.user_profile.update_preference(
            category="communication_style",
            preference="verbosity",
            value=0.8
        )
        
        # Add learned preference with high confidence
        self.user_profile.learned_preferences["autonomy_level"] = 0.7
        self.user_profile.adaptation_metrics["preference_confidence"]["autonomy_level"] = 0.5
        
        # Get effective preferences
        effective = self.user_profile.get_effective_preferences()
        
        self.assertEqual(effective["communication_style"]["verbosity"], 0.8)
        self.assertEqual(effective["work_style"]["autonomy_level"], 0.7)
    
    def test_calculate_adaptation_success_rate(self):
        """Test calculating adaptation success rate."""
        # Add satisfaction scores
        self.user_profile.adaptation_metrics["satisfaction_scores"] = [0.6, 0.7, 0.8, 0.9]
        
        # Calculate success rate
        success_rate = self.user_profile.calculate_adaptation_success_rate()
        
        self.assertEqual(success_rate, 0.75)  # 3 out of 4 scores are >= 0.7
    
    def test_adapt_communication(self):
        """Test adapting communication based on user preferences."""
        # Set preferences
        self.user_profile.update_preference(
            category="communication_style",
            preference="verbosity",
            value=0.8
        )
        
        self.user_profile.update_preference(
            category="communication_style",
            preference="formality",
            value=0.3
        )
        
        # Adapt communication
        message = "This is a test message."
        adapted_message = self.adapter.adapt_communication(message)
        
        self.assertIsInstance(adapted_message, str)
    
    def test_adapt_task_assignment(self):
        """Test adapting task assignment based on user preferences."""
        # Set preferences
        self.user_profile.update_preference(
            category="work_style",
            preference="autonomy_level",
            value=0.2
        )
        
        # Create task
        task = {
            "title": "Test Task",
            "instructions": "Complete this test task.",
            "deadline": datetime.datetime.now().isoformat()
        }
        
        # Adapt task
        adapted_task = self.adapter.adapt_task_assignment(task)
        
        self.assertIsInstance(adapted_task, dict)
        self.assertIn("instructions", adapted_task)
        
        # Low autonomy should result in more guidance
        self.assertGreater(len(adapted_task["instructions"]), len(task["instructions"]))
    
    def test_serialization(self):
        """Test serialization and deserialization of user profile."""
        # Add some data to the profile
        self.user_profile.update_preference(
            category="communication_style",
            preference="verbosity",
            value=0.8
        )
        
        self.user_profile.record_interaction(
            interaction_type="message",
            content={"sender": "user", "text": "This is a test message."},
            satisfaction=0.9
        )
        
        # Convert to dictionary
        profile_dict = self.user_profile.to_dict()
        
        # Create new profile from dictionary
        new_profile = UserPreferenceProfile.from_dict(profile_dict)
        
        self.assertEqual(new_profile.user_id, self.user_profile.user_id)
        self.assertEqual(new_profile.name, self.user_profile.name)
        self.assertEqual(new_profile.communication_style["verbosity"], 0.8)


class TestCollaborativeDecisionSupport(unittest.TestCase):
    """Test cases for Collaborative Decision Support."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create decision support system
        self.decision_support = CollaborativeDecisionSupport()
        
        # Create a decision
        self.decision = self.decision_support.create_decision(
            title="Test Decision",
            description="This is a test decision.",
            framework=DecisionFramework.PROS_CONS,
            created_by="user_1"
        )
        
        # Add participants
        self.human_participant = self.decision_support.add_participant(
            decision_id=self.decision.decision_id,
            name="Test User",
            role=DecisionParticipantRole.DECISION_MAKER,
            is_ai=False
        )
        
        self.ai_participant = self.decision_support.add_participant(
            decision_id=self.decision.decision_id,
            name="AI Assistant",
            role=DecisionParticipantRole.ADVISOR,
            is_ai=True,
            expertise=["data_analysis", "technology"]
        )
        
        # Add options
        self.option_a = self.decision_support.add_option(
            decision_id=self.decision.decision_id,
            name="Option A",
            description="This is option A.",
            proposed_by=self.human_participant.participant_id
        )
        
        self.option_b = self.decision_support.add_option(
            decision_id=self.decision.decision_id,
            name="Option B",
            description="This is option B.",
            proposed_by=self.ai_participant.participant_id
        )
    
    def test_decision_creation(self):
        """Test creating a collaborative decision."""
        decision = self.decision_support.create_decision(
            title="Another Test Decision",
            description="This is another test decision.",
            framework=DecisionFramework.WEIGHTED_CRITERIA,
            created_by="user_2"
        )
        
        self.assertIsInstance(decision, CollaborativeDecision)
        self.assertEqual(decision.title, "Another Test Decision")
        self.assertEqual(decision.framework, DecisionFramework.WEIGHTED_CRITERIA)
        self.assertEqual(decision.status, DecisionStatus.INITIATED)
    
    def test_participant_management(self):
        """Test participant management."""
        # Add another participant
        observer = self.decision_support.add_participant(
            decision_id=self.decision.decision_id,
            name="Observer",
            role=DecisionParticipantRole.OBSERVER,
            is_ai=False
        )
        
        self.assertIsInstance(observer, DecisionParticipant)
        self.assertEqual(observer.name, "Observer")
        self.assertEqual(observer.role, DecisionParticipantRole.OBSERVER)
        
        # Get participants
        participants = self.decision_support.get_participants(self.decision.decision_id)
        
        self.assertEqual(len(participants), 3)
        self.assertIn(self.human_participant.participant_id, [p.participant_id for p in participants])
        self.assertIn(self.ai_participant.participant_id, [p.participant_id for p in participants])
        self.assertIn(observer.participant_id, [p.participant_id for p in participants])
    
    def test_option_management(self):
        """Test option management."""
        # Add pros and cons to options
        self.decision_support.add_pro(
            decision_id=self.decision.decision_id,
            option_id=self.option_a.option_id,
            description="This is a pro for option A.",
            added_by=self.human_participant.participant_id,
            weight=0.8
        )
        
        self.decision_support.add_con(
            decision_id=self.decision.decision_id,
            option_id=self.option_a.option_id,
            description="This is a con for option A.",
            added_by=self.ai_participant.participant_id,
            weight=0.5
        )
        
        self.decision_support.add_pro(
            decision_id=self.decision.decision_id,
            option_id=self.option_b.option_id,
            description="This is a pro for option B.",
            added_by=self.ai_participant.participant_id,
            weight=0.7
        )
        
        # Get options
        options = self.decision_support.get_options(self.decision.decision_id)
        
        self.assertEqual(len(options), 2)
        
        # Check pros and cons
        option_a = next(o for o in options if o.option_id == self.option_a.option_id)
        option_b = next(o for o in options if o.option_id == self.option_b.option_id)
        
        self.assertEqual(len(option_a.pros), 1)
        self.assertEqual(len(option_a.cons), 1)
        self.assertEqual(len(option_b.pros), 1)
        self.assertEqual(len(option_b.cons), 0)
    
    def test_criteria_management(self):
        """Test criteria management."""
        # Add criteria
        criterion_1 = self.decision_support.add_criterion(
            decision_id=self.decision.decision_id,
            name="Cost",
            description="Financial cost of the option.",
            weight=0.7,
            created_by=self.human_participant.participant_id
        )
        
        criterion_2 = self.decision_support.add_criterion(
            decision_id=self.decision.decision_id,
            name="Time",
            description="Time required to implement the option.",
            weight=0.5,
            created_by=self.ai_participant.participant_id
        )
        
        self.assertIsInstance(criterion_1, EvaluationCriterion)
        self.assertEqual(criterion_1.name, "Cost")
        self.assertEqual(criterion_1.weight, 0.7)
        
        # Get criteria
        criteria = self.decision_support.get_criteria(self.decision.decision_id)
        
        self.assertEqual(len(criteria), 2)
        self.assertIn(criterion_1.criterion_id, [c.criterion_id for c in criteria])
        self.assertIn(criterion_2.criterion_id, [c.criterion_id for c in criteria])
    
    def test_evaluation_management(self):
        """Test evaluation management."""
        # Add criteria
        criterion_1 = self.decision_support.add_criterion(
            decision_id=self.decision.decision_id,
            name="Cost",
            description="Financial cost of the option.",
            weight=0.7,
            created_by=self.human_participant.participant_id
        )
        
        criterion_2 = self.decision_support.add_criterion(
            decision_id=self.decision.decision_id,
            name="Time",
            description="Time required to implement the option.",
            weight=0.5,
            created_by=self.ai_participant.participant_id
        )
        
        # Record evaluations
        self.decision_support.record_evaluation(
            decision_id=self.decision.decision_id,
            participant_id=self.human_participant.participant_id,
            option_id=self.option_a.option_id,
            criterion_id=criterion_1.criterion_id,
            score=0.8,
            comment="Option A has a reasonable cost."
        )
        
        self.decision_support.record_evaluation(
            decision_id=self.decision.decision_id,
            participant_id=self.human_participant.participant_id,
            option_id=self.option_a.option_id,
            criterion_id=criterion_2.criterion_id,
            score=0.6,
            comment="Option A takes a moderate amount of time."
        )
        
        self.decision_support.record_evaluation(
            decision_id=self.decision.decision_id,
            participant_id=self.ai_participant.participant_id,
            option_id=self.option_b.option_id,
            criterion_id=criterion_1.criterion_id,
            score=0.9,
            comment="Option B is very cost-effective."
        )
        
        self.decision_support.record_evaluation(
            decision_id=self.decision.decision_id,
            participant_id=self.ai_participant.participant_id,
            option_id=self.option_b.option_id,
            criterion_id=criterion_2.criterion_id,
            score=0.4,
            comment="Option B takes longer to implement."
        )
        
        # Get evaluations
        evaluations = self.decision_support.get_evaluations(self.decision.decision_id)
        
        self.assertEqual(len(evaluations), 4)
    
    def test_decision_workflow(self):
        """Test decision workflow."""
        # Update decision status
        self.decision_support.update_decision_status(
            decision_id=self.decision.decision_id,
            status=DecisionStatus.GATHERING_INPUT
        )
        
        self.assertEqual(self.decision.status, DecisionStatus.GATHERING_INPUT)
        
        # Add contributions
        self.decision_support.add_contribution(
            decision_id=self.decision.decision_id,
            participant_id=self.human_participant.participant_id,
            contribution_type="comment",
            content="I think we should consider the long-term implications."
        )
        
        self.decision_support.add_contribution(
            decision_id=self.decision.decision_id,
            participant_id=self.ai_participant.participant_id,
            contribution_type="analysis",
            content="Based on the data, Option B appears to be more sustainable."
        )
        
        # Get timeline
        timeline = self.decision_support.get_timeline(self.decision.decision_id)
        
        self.assertGreater(len(timeline), 0)
        
        # Finalize decision
        self.decision_support.finalize_decision(
            decision_id=self.decision.decision_id,
            selected_option_id=self.option_b.option_id,
            rationale="Option B is more cost-effective and sustainable in the long run."
        )
        
        self.assertEqual(self.decision.status, DecisionStatus.FINALIZED)
        self.assertEqual(self.decision.final_decision, self.option_b.option_id)
        self.assertEqual(self.decision.decision_rationale, "Option B is more cost-effective and sustainable in the long run.")
    
    def test_decision_analysis(self):
        """Test decision analysis."""
        # Add criteria
        criterion_1 = self.decision_support.add_criterion(
            decision_id=self.decision.decision_id,
            name="Cost",
            description="Financial cost of the option.",
            weight=0.7,
            created_by=self.human_participant.participant_id
        )
        
        criterion_2 = self.decision_support.add_criterion(
            decision_id=self.decision.decision_id,
            name="Time",
            description="Time required to implement the option.",
            weight=0.5,
            created_by=self.ai_participant.participant_id
        )
        
        # Record evaluations
        self.decision_support.record_evaluation(
            decision_id=self.decision.decision_id,
            participant_id=self.human_participant.participant_id,
            option_id=self.option_a.option_id,
            criterion_id=criterion_1.criterion_id,
            score=0.8
        )
        
        self.decision_support.record_evaluation(
            decision_id=self.decision.decision_id,
            participant_id=self.human_participant.participant_id,
            option_id=self.option_a.option_id,
            criterion_id=criterion_2.criterion_id,
            score=0.6
        )
        
        self.decision_support.record_evaluation(
            decision_id=self.decision.decision_id,
            participant_id=self.ai_participant.participant_id,
            option_id=self.option_b.option_id,
            criterion_id=criterion_1.criterion_id,
            score=0.9
        )
        
        self.decision_support.record_evaluation(
            decision_id=self.decision.decision_id,
            participant_id=self.ai_participant.participant_id,
            option_id=self.option_b.option_id,
            criterion_id=criterion_2.criterion_id,
            score=0.4
        )
        
        # Generate analysis
        analysis = self.decision_support.analyze_decision(self.decision.decision_id)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn("options", analysis)
        self.assertIn("criteria", analysis)
        self.assertIn("scores", analysis)
        self.assertIn("recommendation", analysis)
    
    def test_serialization(self):
        """Test serialization and deserialization of decision."""
        # Convert to dictionary
        decision_dict = self.decision.to_dict()
        
        # Create new decision from dictionary
        new_decision = CollaborativeDecision.from_dict(decision_dict)
        
        self.assertEqual(new_decision.decision_id, self.decision.decision_id)
        self.assertEqual(new_decision.title, self.decision.title)
        self.assertEqual(new_decision.framework, self.decision.framework)


if __name__ == "__main__":
    unittest.main()
