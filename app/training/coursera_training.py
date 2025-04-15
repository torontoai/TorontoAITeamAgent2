"""TORONTO AI TEAM AGENT - Integration with Training System

This module integrates the Coursera API with the existing training system
to enhance agent knowledge and capabilities.

Copyright (c) 2025 TORONTO AI
Created by David Tadeusz Chudak
All rights reserved."""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime

from .coursera_integration import (
    CourseraConfig,
    CourseraAPIClient,
    CourseraContentExtractor,
    CourseraKnowledgePipeline,
    create_role_specific_queries,
    initialize_coursera_integration
)
from .knowledge_extraction import KnowledgeExtractor
from .knowledge_integration import KnowledgeIntegrator
from .vector_db import VectorDBManager
from .config import TrainingConfig

logger = logging.getLogger(__name__)


class CourseraTrainingIntegration:
    """Integrates Coursera content with the existing training system."""
    
    def __init__(
        self,
        training_config: TrainingConfig,
        vector_db_manager: VectorDBManager,
        knowledge_integrator: KnowledgeIntegrator,
        coursera_api_key: str,
        coursera_api_secret: str,
        coursera_business_id: Optional[str] = None
    ):
        """Initialize the Coursera training integration.
        
        Args:
            training_config: Training system configuration
            vector_db_manager: Vector database manager
            knowledge_integrator: Knowledge integrator
            coursera_api_key: Coursera API key
            coursera_api_secret: Coursera API secret
            coursera_business_id: Coursera Business ID (optional)"""
        self.training_config = training_config
        self.vector_db_manager = vector_db_manager
        self.knowledge_integrator = knowledge_integrator
        
        # Initialize Coursera integration
        token_cache_path = os.path.join(training_config.cache_dir, "coursera_token.json")
        self.knowledge_pipeline = initialize_coursera_integration(
            api_key=coursera_api_key,
            api_secret=coursera_api_secret,
            business_id=coursera_business_id,
            token_cache_path=token_cache_path
        )
        
        # Create knowledge extractor
        self.knowledge_extractor = KnowledgeExtractor(
            chunk_size=training_config.chunk_size,
            chunk_overlap=training_config.chunk_overlap,
            embedding_model=training_config.embedding_model
        )
        
        # Create role-specific queries
        self.role_queries = create_role_specific_queries()
    
    def train_agent_role(
        self,
        role: str,
        custom_queries: Optional[List[str]] = None,
        limit_per_query: int = 3,
        collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Train an agent for a specific role using Coursera content.
        
        Args:
            role: The agent role
            custom_queries: Custom search queries (optional)
            limit_per_query: Maximum number of courses to process per query
            collection_name: Vector database collection name (optional)
            
        Returns:
            Training summary"""
        # Determine queries to use
        queries = custom_queries or self.role_queries.get(role, [])
        if not queries:
            logger.warning(f"No queries defined for role: {role}")
            queries = [role]  # Use the role name as a fallback query
        
        # Determine collection name
        if not collection_name:
            collection_name = f"coursera_{role}_{datetime.now().strftime('%Y%m%d')}"
        
        # Create output directory for course content
        output_dir = os.path.join(self.training_config.data_dir, "coursera", role)
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate knowledge base
        logger.info(f"Generating knowledge base for role: {role}")
        knowledge_base = self.knowledge_pipeline.generate_knowledge_base_for_role(
            role=role,
            queries=queries,
            output_dir=output_dir,
            limit_per_query=limit_per_query
        )
        
        # Process and integrate knowledge
        logger.info(f"Processing and integrating knowledge for role: {role}")
        processed_files = []
        for course in knowledge_base["courses"]:
            filepath = course["filepath"]
            processed_files.append(filepath)
        
        # Extract knowledge from processed files
        knowledge_chunks = []
        for filepath in processed_files:
            try:
                with open(filepath, 'r') as f:
                    content = json.load(f)
                
                # Extract text from course content
                course_text = self._extract_text_from_course(content)
                
                # Chunk the text
                chunks = self.knowledge_extractor.extract_chunks(course_text)
                
                # Add metadata
                for chunk in chunks:
                    chunk.metadata.update({
                        "source": "coursera",
                        "course_id": content.get("course_id", ""),
                        "course_title": content.get("title", ""),
                        "role": role
                    })
                
                knowledge_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Failed to process file {filepath}: {str(e)}")
        
        # Store in vector database
        logger.info(f"Storing {len(knowledge_chunks)} chunks in vector database")
        self.vector_db_manager.create_collection(collection_name)
        self.vector_db_manager.add_documents(collection_name, knowledge_chunks)
        
        # Integrate with existing knowledge
        logger.info("Integrating with existing knowledge")
        self.knowledge_integrator.integrate_knowledge(
            collection_name=collection_name,
            role=role,
            source="coursera"
        )
        
        # Create training summary
        training_summary = {
            "role": role,
            "queries": queries,
            "courses_processed": len(processed_files),
            "knowledge_chunks": len(knowledge_chunks),
            "collection_name": collection_name,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save training summary
        summary_filepath = os.path.join(output_dir, f"{role}_training_summary.json")
        with open(summary_filepath, 'w') as f:
            json.dump(training_summary, f, indent=2)
        
        logger.info(f"Training completed for role: {role}")
        return training_summary
    
    def _extract_text_from_course(self, course_content: Dict[str, Any]) -> str:
        """Extract text from course content.
        
        Args:
            course_content: Course content
            
        Returns:
            Extracted text"""
        text_parts = []
        
        # Add course title and description
        text_parts.append(f"# {course_content.get('title', '')}")
        text_parts.append(course_content.get('description', ''))
        
        # Add skills
        skills = course_content.get('skills', [])
        if skills:
            text_parts.append("## Skills")
            text_parts.append(", ".join(skills))
        
        # Process modules
        for module in course_content.get('modules', []):
            module_title = module.get('title', '')
            text_parts.append(f"## {module_title}")
            
            # Process lectures
            for lecture in module.get('lectures', []):
                lecture_title = lecture.get('title', '')
                lecture_content = lecture.get('content', '')
                text_parts.append(f"### {lecture_title}")
                text_parts.append(lecture_content)
            
            # Process readings
            for reading in module.get('readings', []):
                reading_title = reading.get('title', '')
                reading_content = reading.get('content', '')
                text_parts.append(f"### {reading_title}")
                text_parts.append(reading_content)
            
            # Process quizzes
            for quiz in module.get('quizzes', []):
                quiz_title = quiz.get('title', '')
                text_parts.append(f"### {quiz_title}")
                
                # Process questions
                for question in quiz.get('questions', []):
                    question_text = question.get('text', '')
                    text_parts.append(question_text)
                    
                    # Process options
                    for option in question.get('options', []):
                        option_text = option.get('text', '')
                        text_parts.append(f"- {option_text}")
        
        return "\n\n".join(text_parts)
    
    def train_all_agent_roles(
        self,
        roles: Optional[List[str]] = None,
        limit_per_query: int = 3
    ) -> Dict[str, Any]:
        """Train multiple agent roles using Coursera content.
        
        Args:
            roles: List of roles to train (optional, defaults to all roles with queries)
            limit_per_query: Maximum number of courses to process per query
            
        Returns:
            Training summary for all roles"""
        # Determine roles to train
        if not roles:
            roles = list(self.role_queries.keys())
        
        # Train each role
        training_summaries = {}
        for role in roles:
            try:
                summary = self.train_agent_role(
                    role=role,
                    limit_per_query=limit_per_query
                )
                training_summaries[role] = summary
            except Exception as e:
                logger.error(f"Failed to train role {role}: {str(e)}")
                training_summaries[role] = {"error": str(e)}
        
        # Create overall summary
        overall_summary = {
            "roles_trained": len(training_summaries),
            "successful_roles": sum(1 for r in training_summaries.values() if "error" not in r),
            "failed_roles": sum(1 for r in training_summaries.values() if "error" in r),
            "role_summaries": training_summaries,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save overall summary
        summary_dir = os.path.join(self.training_config.data_dir, "coursera")
        os.makedirs(summary_dir, exist_ok=True)
        summary_filepath = os.path.join(
            summary_dir, 
            f"training_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(summary_filepath, 'w') as f:
            json.dump(overall_summary, f, indent=2)
        
        logger.info(f"Training completed for {overall_summary['successful_roles']} roles")
        return overall_summary
