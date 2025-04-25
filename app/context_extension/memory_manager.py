"""
Memory Manager for context extension.

This module provides the Memory Management System, which organizes information across
different memory types to ensure relevant context is always accessible.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Union, Tuple
import json
import os

# Set up logging
logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manager class for organizing information across different memory types.
    
    This class provides methods for storing and retrieving information from different
    memory types, including short-term, working, long-term, and episodic memory.
    """
    
    def __init__(
        self,
        storage_dir: str = "/tmp/toronto_agent_memory",
        short_term_capacity: int = 10,
        working_memory_capacity: int = 5,
        long_term_retention_days: int = 30,
        enable_episodic_memory: bool = True
    ):
        """
        Initialize the MemoryManager.
        
        Args:
            storage_dir: Directory for persistent storage
            short_term_capacity: Capacity of short-term memory
            working_memory_capacity: Capacity of working memory
            long_term_retention_days: Retention period for long-term memory
            enable_episodic_memory: Whether to enable episodic memory
        """
        self.storage_dir = storage_dir
        self.short_term_capacity = short_term_capacity
        self.working_memory_capacity = working_memory_capacity
        self.long_term_retention_days = long_term_retention_days
        self.enable_episodic_memory = enable_episodic_memory
        
        # Initialize memory stores
        self.short_term_memory = []
        self.working_memory = []
        self.episodic_memory = []
        
        # Ensure storage directory exists
        os.makedirs(storage_dir, exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "long_term"), exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "episodic"), exist_ok=True)
        
        logger.info(f"Initialized MemoryManager with storage_dir={storage_dir}")
    
    def add_to_short_term_memory(self, item: Dict[str, Any]) -> str:
        """
        Add an item to short-term memory.
        
        Args:
            item: Memory item to add
        
        Returns:
            ID of the added item
        """
        # Generate ID if not provided
        if "id" not in item:
            item["id"] = self._generate_id()
        
        # Add timestamp if not provided
        if "timestamp" not in item:
            item["timestamp"] = time.time()
        
        # Add to short-term memory
        self.short_term_memory.append(item)
        
        # Trim if over capacity
        if len(self.short_term_memory) > self.short_term_capacity:
            # Move oldest item to long-term memory
            oldest_item = self.short_term_memory.pop(0)
            self.add_to_long_term_memory(oldest_item)
        
        logger.debug(f"Added item {item['id']} to short-term memory")
        return item["id"]
    
    def add_to_working_memory(self, item: Dict[str, Any]) -> str:
        """
        Add an item to working memory.
        
        Args:
            item: Memory item to add
        
        Returns:
            ID of the added item
        """
        # Generate ID if not provided
        if "id" not in item:
            item["id"] = self._generate_id()
        
        # Add timestamp if not provided
        if "timestamp" not in item:
            item["timestamp"] = time.time()
        
        # Add to working memory
        self.working_memory.append(item)
        
        # Trim if over capacity
        if len(self.working_memory) > self.working_memory_capacity:
            # Remove oldest item
            self.working_memory.pop(0)
        
        logger.debug(f"Added item {item['id']} to working memory")
        return item["id"]
    
    def add_to_long_term_memory(self, item: Dict[str, Any]) -> str:
        """
        Add an item to long-term memory.
        
        Args:
            item: Memory item to add
        
        Returns:
            ID of the added item
        """
        # Generate ID if not provided
        if "id" not in item:
            item["id"] = self._generate_id()
        
        # Add timestamp if not provided
        if "timestamp" not in item:
            item["timestamp"] = time.time()
        
        # Save to disk
        file_path = os.path.join(self.storage_dir, "long_term", f"{item['id']}.json")
        with open(file_path, "w") as f:
            json.dump(item, f)
        
        logger.debug(f"Added item {item['id']} to long-term memory")
        return item["id"]
    
    def add_to_episodic_memory(self, episode: Dict[str, Any]) -> str:
        """
        Add an episode to episodic memory.
        
        Args:
            episode: Episode to add
        
        Returns:
            ID of the added episode
        """
        if not self.enable_episodic_memory:
            logger.warning("Episodic memory is disabled")
            return ""
        
        # Generate ID if not provided
        if "id" not in episode:
            episode["id"] = self._generate_id()
        
        # Add timestamp if not provided
        if "timestamp" not in episode:
            episode["timestamp"] = time.time()
        
        # Add to episodic memory
        self.episodic_memory.append(episode)
        
        # Save to disk
        file_path = os.path.join(self.storage_dir, "episodic", f"{episode['id']}.json")
        with open(file_path, "w") as f:
            json.dump(episode, f)
        
        logger.debug(f"Added episode {episode['id']} to episodic memory")
        return episode["id"]
    
    def get_from_short_term_memory(self, item_id: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get item(s) from short-term memory.
        
        Args:
            item_id: ID of the item to get, or None to get all items
        
        Returns:
            Memory item or list of items
        """
        if item_id is None:
            return self.short_term_memory
        
        for item in self.short_term_memory:
            if item["id"] == item_id:
                return item
        
        logger.warning(f"Item {item_id} not found in short-term memory")
        return {}
    
    def get_from_working_memory(self, item_id: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get item(s) from working memory.
        
        Args:
            item_id: ID of the item to get, or None to get all items
        
        Returns:
            Memory item or list of items
        """
        if item_id is None:
            return self.working_memory
        
        for item in self.working_memory:
            if item["id"] == item_id:
                return item
        
        logger.warning(f"Item {item_id} not found in working memory")
        return {}
    
    def get_from_long_term_memory(self, item_id: str) -> Dict[str, Any]:
        """
        Get an item from long-term memory.
        
        Args:
            item_id: ID of the item to get
        
        Returns:
            Memory item
        """
        file_path = os.path.join(self.storage_dir, "long_term", f"{item_id}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading item {item_id} from long-term memory: {str(e)}")
        
        logger.warning(f"Item {item_id} not found in long-term memory")
        return {}
    
    def get_from_episodic_memory(self, episode_id: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get episode(s) from episodic memory.
        
        Args:
            episode_id: ID of the episode to get, or None to get all episodes
        
        Returns:
            Episode or list of episodes
        """
        if not self.enable_episodic_memory:
            logger.warning("Episodic memory is disabled")
            return [] if episode_id is None else {}
        
        if episode_id is None:
            return self.episodic_memory
        
        # Check in-memory cache first
        for episode in self.episodic_memory:
            if episode["id"] == episode_id:
                return episode
        
        # Check disk
        file_path = os.path.join(self.storage_dir, "episodic", f"{episode_id}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading episode {episode_id} from episodic memory: {str(e)}")
        
        logger.warning(f"Episode {episode_id} not found in episodic memory")
        return {}
    
    def search_memory(
        self,
        query: str,
        memory_types: List[str] = ["short_term", "working", "long_term", "episodic"],
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search across memory types.
        
        Args:
            query: Search query
            memory_types: Types of memory to search
            max_results: Maximum number of results to return
        
        Returns:
            List of matching memory items
        """
        results = []
        
        # Search short-term memory
        if "short_term" in memory_types:
            for item in self.short_term_memory:
                if self._matches_query(item, query):
                    results.append({"item": item, "source": "short_term"})
        
        # Search working memory
        if "working" in memory_types:
            for item in self.working_memory:
                if self._matches_query(item, query):
                    results.append({"item": item, "source": "working"})
        
        # Search long-term memory
        if "long_term" in memory_types:
            long_term_items = self._list_long_term_memory()
            for item in long_term_items:
                if self._matches_query(item, query):
                    results.append({"item": item, "source": "long_term"})
        
        # Search episodic memory
        if "episodic" in memory_types and self.enable_episodic_memory:
            for episode in self.episodic_memory:
                if self._matches_query(episode, query):
                    results.append({"item": episode, "source": "episodic"})
            
            # Also search disk for older episodes
            episodic_items = self._list_episodic_memory()
            for item in episodic_items:
                if item not in self.episodic_memory and self._matches_query(item, query):
                    results.append({"item": item, "source": "episodic"})
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: self._relevance_score(x["item"], query), reverse=True)
        return results[:max_results]
    
    def _matches_query(self, item: Dict[str, Any], query: str) -> bool:
        """
        Check if an item matches a query.
        
        Args:
            item: Memory item to check
            query: Query to match against
        
        Returns:
            True if the item matches the query
        """
        query_lower = query.lower()
        
        # Check content field
        if "content" in item and isinstance(item["content"], str):
            if query_lower in item["content"].lower():
                return True
        
        # Check text field
        if "text" in item and isinstance(item["text"], str):
            if query_lower in item["text"].lower():
                return True
        
        # Check title field
        if "title" in item and isinstance(item["title"], str):
            if query_lower in item["title"].lower():
                return True
        
        # Check tags
        if "tags" in item and isinstance(item["tags"], list):
            for tag in item["tags"]:
                if isinstance(tag, str) and query_lower in tag.lower():
                    return True
        
        # Check metadata
        if "metadata" in item and isinstance(item["metadata"], dict):
            for key, value in item["metadata"].items():
                if isinstance(value, str) and query_lower in value.lower():
                    return True
        
        return False
    
    def _relevance_score(self, item: Dict[str, Any], query: str) -> float:
        """
        Calculate relevance score of an item for a query.
        
        Args:
            item: Memory item to score
            query: Query to score against
        
        Returns:
            Relevance score (higher is more relevant)
        """
        query_terms = query.lower().split()
        score = 0.0
        
        # Check content field
        if "content" in item and isinstance(item["content"], str):
            content_lower = item["content"].lower()
            for term in query_terms:
                score += content_lower.count(term) * 1.0
        
        # Check text field
        if "text" in item and isinstance(item["text"], str):
            text_lower = item["text"].lower()
            for term in query_terms:
                score += text_lower.count(term) * 1.0
        
        # Check title field (higher weight)
        if "title" in item and isinstance(item["title"], str):
            title_lower = item["title"].lower()
            for term in query_terms:
                score += title_lower.count(term) * 3.0
        
        # Check tags (higher weight)
        if "tags" in item and isinstance(item["tags"], list):
            for tag in item["tags"]:
                if isinstance(tag, str):
                    tag_lower = tag.lower()
                    for term in query_terms:
                        if term in tag_lower:
                            score += 2.0
        
        # Recency bonus
        if "timestamp" in item:
            time_diff = time.time() - item["timestamp"]
            recency_score = 1.0 / (1.0 + time_diff / (24 * 60 * 60))  # Decay over days
            score *= (1.0 + recency_score)
        
        return score
    
    def _list_long_term_memory(self) -> List[Dict[str, Any]]:
        """
        List all items in long-term memory.
        
        Returns:
            List of memory items
        """
        items = []
        
        try:
            for filename in os.listdir(os.path.join(self.storage_dir, "long_term")):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.storage_dir, "long_term", filename)
                    try:
                        with open(file_path, "r") as f:
                            item = json.load(f)
                            items.append(item)
                    except Exception as e:
                        logger.error(f"Error loading {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error listing long-term memory: {str(e)}")
        
        return items
    
    def _list_episodic_memory(self) -> List[Dict[str, Any]]:
        """
        List all episodes in episodic memory.
        
        Returns:
            List of episodes
        """
        if not self.enable_episodic_memory:
            return []
        
        episodes = []
        
        try:
            for filename in os.listdir(os.path.join(self.storage_dir, "episodic")):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.storage_dir, "episodic", filename)
                    try:
                        with open(file_path, "r") as f:
                            episode = json.load(f)
                            episodes.append(episode)
                    except Exception as e:
                        logger.error(f"Error loading {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error listing episodic memory: {str(e)}")
        
        return episodes
    
    def clean_up_memory(self) -> Tuple[int, int]:
        """
        Clean up old memory items.
        
        Returns:
            Tuple of (long_term_removed, episodic_removed)
        """
        long_term_removed = 0
        episodic_removed = 0
        
        # Clean up long-term memory
        try:
            for filename in os.listdir(os.path.join(self.storage_dir, "long_term")):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.storage_dir, "long_term", filename)
                    try:
                        with open(file_path, "r") as f:
                            item = json.load(f)
                            
                            # Check if item is too old
                            if "timestamp" in item:
                                age_days = (time.time() - item["timestamp"]) / (24 * 60 * 60)
                                if age_days > self.long_term_retention_days:
                                    os.remove(file_path)
                                    long_term_removed += 1
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error cleaning up long-term memory: {str(e)}")
        
        # Clean up episodic memory
        if self.enable_episodic_memory:
            try:
                for filename in os.listdir(os.path.join(self.storage_dir, "episodic")):
                    if filename.endswith(".json"):
                        file_path = os.path.join(self.storage_dir, "episodic", filename)
                        try:
                            with open(file_path, "r") as f:
                                episode = json.load(f)
                                
                                # Check if episode is too old
                                if "timestamp" in episode:
                                    age_days = (time.time() - episode["timestamp"]) / (24 * 60 * 60)
                                    if age_days > self.long_term_retention_days:
                                        os.remove(file_path)
                                        episodic_removed += 1
                        except Exception as e:
                            logger.error(f"Error processing {file_path}: {str(e)}")
            except Exception as e:
                logger.error(f"Error cleaning up episodic memory: {str(e)}")
        
        logger.info(f"Cleaned up memory: removed {long_term_removed} long-term items and {episodic_removed} episodes")
        return (long_term_removed, episodic_removed)
    
    def _generate_id(self) -> str:
        """
        Generate a unique ID.
        
        Returns:
            Unique ID
        """
        import uuid
        return str(uuid.uuid4())
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary of memory statistics
        """
        stats = {
            "short_term": {
                "count": len(self.short_term_memory),
                "capacity": self.short_term_capacity
            },
            "working": {
                "count": len(self.working_memory),
                "capacity": self.working_memory_capacity
            }
        }
        
        # Count long-term items
        long_term_count = 0
        try:
            for filename in os.listdir(os.path.join(self.storage_dir, "long_term")):
                if filename.endswith(".json"):
                    long_term_count += 1
        except Exception as e:
            logger.error(f"Error counting long-term memory: {str(e)}")
        
        stats["long_term"] = {
            "count": long_term_count,
            "retention_days": self.long_term_retention_days
        }
        
        # Count episodic items
        if self.enable_episodic_memory:
            episodic_count = len(self.episodic_memory)
            try:
                for filename in os.listdir(os.path.join(self.storage_dir, "episodic")):
                    if filename.endswith(".json"):
                        episodic_count += 1
            except Exception as e:
                logger.error(f"Error counting episodic memory: {str(e)}")
            
            stats["episodic"] = {
                "count": episodic_count,
                "enabled": True
            }
        else:
            stats["episodic"] = {
                "count": 0,
                "enabled": False
            }
        
        return stats
