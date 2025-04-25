"""
Test script for the Context Window Extension system.

This script tests the functionality of the Context Window Extension system,
which provides an almost limitless context window for the TORONTO AI TEAM AGENT.
"""

import os
import sys
import logging
import json
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import context extension components
from app.context_extension.vector_db_manager import VectorDatabaseManager
from app.context_extension.hierarchical_processor import HierarchicalProcessor
from app.context_extension.recursive_summarizer import RecursiveSummarizer
from app.context_extension.memory_manager import MemoryManager
from app.context_extension.multi_agent_context import MultiAgentContextDistributor
from app.context_extension.context_window_manager import ContextWindowManager

class MockAgent:
    """Mock agent for testing multi-agent context distribution."""
    
    def __init__(self, agent_id: str, specializations: List[str] = None):
        """
        Initialize the MockAgent.
        
        Args:
            agent_id: Unique identifier for the agent
            specializations: List of agent specializations
        """
        self.agent_id = agent_id
        self.specializations = specializations or []
        self.context = ""
        self.tasks = []
        self.results = {}
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task.
        
        Args:
            task: Task to process
        
        Returns:
            Task result
        """
        self.tasks.append(task)
        
        result = {
            "status": "completed",
            "result": f"Processed by agent {self.agent_id}",
            "task_id": task.get("id", "unknown")
        }
        
        self.results[task.get("id", "unknown")] = result
        return result
    
    def get_context_update(self) -> str:
        """
        Get context update from the agent.
        
        Returns:
            Context update
        """
        return f"Context update from agent {self.agent_id}: Processed {len(self.tasks)} tasks"


def test_vector_db_manager():
    """Test the Vector Database Manager."""
    logger.info("Testing Vector Database Manager...")
    
    # Initialize Vector Database Manager
    vector_db = VectorDatabaseManager(
        db_provider="chroma",
        embedding_model="sentence-transformers/all-mpnet-base-v2",
        collection_name="test_collection",
        persist_directory="/tmp/toronto_agent_vector_db_test"
    )
    
    # Test storing a document
    document = """
    # Test Document
    
    This is a test document for the Vector Database Manager.
    
    ## Section 1
    
    This is section 1 of the test document.
    
    ## Section 2
    
    This is section 2 of the test document.
    """
    
    metadata = {
        "document_type": "markdown",
        "author": "Test Author",
        "title": "Test Document"
    }
    
    chunk_ids = vector_db.store_document(document, metadata, "test_doc_1")
    logger.info(f"Stored document with {len(chunk_ids)} chunks")
    
    # Test retrieving context
    query = "section 1"
    results = vector_db.retrieve_relevant_context(query, 2)
    logger.info(f"Retrieved {len(results)} chunks for query: {query}")
    
    # Test sliding context window
    window = vector_db.get_sliding_context_window(query, 3)
    logger.info(f"Retrieved sliding context window of length: {len(window)}")
    
    # Test retrieving with metadata filter
    filter_metadata = {"document_type": "markdown"}
    filtered_results = vector_db.retrieve_relevant_context(query, 2, filter_metadata)
    logger.info(f"Retrieved {len(filtered_results)} chunks with metadata filter")
    
    logger.info("Vector Database Manager tests completed successfully")
    return True


def test_hierarchical_processor():
    """Test the Hierarchical Processor."""
    logger.info("Testing Hierarchical Processor...")
    
    # Initialize Hierarchical Processor
    processor = HierarchicalProcessor()
    
    # Test processing a document
    document = """
    # Test Document
    
    This is a test document for the Hierarchical Processor.
    
    ## Section 1
    
    This is section 1 of the test document.
    
    ### Subsection 1.1
    
    This is subsection 1.1 of the test document.
    
    ## Section 2
    
    This is section 2 of the test document.
    
    ### Subsection 2.1
    
    This is subsection 2.1 of the test document.
    
    ### Subsection 2.2
    
    This is subsection 2.2 of the test document.
    """
    
    result = processor.process_document(document, "markdown")
    logger.info(f"Processed document with {len(result['chunks'])} chunks and {len(result['hierarchy'])} hierarchy nodes")
    
    # Test navigating hierarchy
    query = "subsection 1.1"
    navigation_result = processor.navigate_hierarchy(result, query)
    logger.info(f"Navigation result for query '{query}': {len(navigation_result)} chunks")
    
    # Test extracting structure
    structure = processor.extract_document_structure(document, "markdown")
    logger.info(f"Extracted document structure with {len(structure)} sections")
    
    logger.info("Hierarchical Processor tests completed successfully")
    return True


def test_recursive_summarizer():
    """Test the Recursive Summarizer."""
    logger.info("Testing Recursive Summarizer...")
    
    # Initialize Recursive Summarizer
    summarizer = RecursiveSummarizer()
    
    # Test summarizing a document
    document = """
    # Test Document
    
    This is a test document for the Recursive Summarizer.
    
    ## Section 1
    
    This is section 1 of the test document. It contains important information about the test.
    The test is designed to verify the functionality of the Recursive Summarizer.
    
    ## Section 2
    
    This is section 2 of the test document. It contains additional information about the test.
    The Recursive Summarizer should be able to create a hierarchical summary of this document.
    
    ## Section 3
    
    This is section 3 of the test document. It contains the conclusion of the test.
    The test will be considered successful if the Recursive Summarizer can create a good summary.
    """
    
    summary_result = summarizer.summarize(document)
    logger.info(f"Generated summary with {summary_result['token_count']} tokens and compression ratio {summary_result['compression_ratio']}")
    
    # Test hierarchical summary
    hierarchical_summary = summarizer.get_hierarchical_summary(document)
    logger.info(f"Generated hierarchical summary with {len(hierarchical_summary.get('children', []))} children")
    
    # Test getting summary at level
    level_summary = summarizer.get_summary_at_level(hierarchical_summary, 0)
    logger.info(f"Generated level 0 summary of length: {len(level_summary)}")
    
    # Test drilling down
    drill_down_result = summarizer.drill_down(hierarchical_summary, "section 2")
    logger.info(f"Drill down result for query 'section 2': {drill_down_result.get('level', -1)} level")
    
    logger.info("Recursive Summarizer tests completed successfully")
    return True


def test_memory_manager():
    """Test the Memory Manager."""
    logger.info("Testing Memory Manager...")
    
    # Initialize Memory Manager
    memory_manager = MemoryManager(
        storage_dir="/tmp/toronto_agent_memory_test",
        short_term_capacity=5,
        working_memory_capacity=3,
        long_term_retention_days=30,
        enable_episodic_memory=True
    )
    
    # Test adding to short-term memory
    short_term_item = {
        "type": "message",
        "content": "This is a test message for short-term memory",
        "metadata": {"importance": "high"}
    }
    
    short_term_id = memory_manager.add_to_short_term_memory(short_term_item)
    logger.info(f"Added item to short-term memory with ID: {short_term_id}")
    
    # Test adding to working memory
    working_item = {
        "type": "task",
        "content": "This is a test task for working memory",
        "metadata": {"priority": "high"}
    }
    
    working_id = memory_manager.add_to_working_memory(working_item)
    logger.info(f"Added item to working memory with ID: {working_id}")
    
    # Test adding to long-term memory
    long_term_item = {
        "type": "document",
        "content": "This is a test document for long-term memory",
        "metadata": {"category": "test"}
    }
    
    long_term_id = memory_manager.add_to_long_term_memory(long_term_item)
    logger.info(f"Added item to long-term memory with ID: {long_term_id}")
    
    # Test adding to episodic memory
    episode = {
        "type": "episode",
        "content": "This is a test episode for episodic memory",
        "events": [
            {"type": "start", "timestamp": 1000},
            {"type": "action", "timestamp": 1100},
            {"type": "end", "timestamp": 1200}
        ]
    }
    
    episode_id = memory_manager.add_to_episodic_memory(episode)
    logger.info(f"Added episode to episodic memory with ID: {episode_id}")
    
    # Test retrieving from memory
    short_term_result = memory_manager.get_from_short_term_memory(short_term_id)
    logger.info(f"Retrieved item from short-term memory: {short_term_result.get('type')}")
    
    working_result = memory_manager.get_from_working_memory(working_id)
    logger.info(f"Retrieved item from working memory: {working_result.get('type')}")
    
    long_term_result = memory_manager.get_from_long_term_memory(long_term_id)
    logger.info(f"Retrieved item from long-term memory: {long_term_result.get('type')}")
    
    episodic_result = memory_manager.get_from_episodic_memory(episode_id)
    logger.info(f"Retrieved episode from episodic memory: {episodic_result.get('type')}")
    
    # Test searching memory
    search_results = memory_manager.search_memory("test document")
    logger.info(f"Search results for 'test document': {len(search_results)} items")
    
    # Test memory stats
    stats = memory_manager.get_memory_stats()
    logger.info(f"Memory stats: {stats}")
    
    logger.info("Memory Manager tests completed successfully")
    return True


def test_multi_agent_context_distributor():
    """Test the Multi-Agent Context Distributor."""
    logger.info("Testing Multi-Agent Context Distributor...")
    
    # Initialize Multi-Agent Context Distributor
    distributor = MultiAgentContextDistributor(
        max_agents=3,
        coordinator_role="coordinator",
        specialization_enabled=True
    )
    
    # Create mock agents
    agent1 = MockAgent("agent1", ["code", "python"])
    agent2 = MockAgent("agent2", ["document", "markdown"])
    agent3 = MockAgent("agent3", ["coordinator", "conversation"])
    
    # Register agents
    distributor.register_agent("agent1", agent1, ["code", "python"], 5000)
    distributor.register_agent("agent2", agent2, ["document", "markdown"], 5000)
    distributor.register_agent("agent3", agent3, ["coordinator", "conversation"], 10000)
    
    # Test distributing context
    context = """
    # Test Document
    
    This is a test document for the Multi-Agent Context Distributor.
    
    ## Python Code Section
    
    ```python
    def test_function():
        print("This is a test function")
        return True
    
    class TestClass:
        def __init__(self):
            self.value = "test"
        
        def test_method(self):
            return self.value
    ```
    
    ## Markdown Section
    
    This is a markdown section with some text.
    
    - Item 1
    - Item 2
    - Item 3
    
    ## Conversation Section
    
    User: Hello, this is a test conversation.
    Assistant: Hi there! I'm here to help with your test.
    User: Can you tell me about the Multi-Agent Context Distributor?
    Assistant: The Multi-Agent Context Distributor distributes context across specialized agents.
    """
    
    assignments = distributor.distribute_context(context, "mixed")
    logger.info(f"Distributed context across {len(assignments)} agents")
    
    # Test submitting tasks
    task1 = {
        "type": "code_analysis",
        "content": "Analyze the Python code in the document",
        "specialization": "python"
    }
    
    task2 = {
        "type": "document_analysis",
        "content": "Analyze the markdown section in the document",
        "specialization": "markdown"
    }
    
    task_id1 = distributor.submit_task(task1)
    task_id2 = distributor.submit_task(task2)
    
    logger.info(f"Submitted tasks with IDs: {task_id1}, {task_id2}")
    
    # Start processing
    distributor.start_processing()
    
    # Wait for processing to complete
    import time
    time.sleep(2)
    
    # Stop processing
    distributor.stop_processing()
    
    # Check system status
    status = distributor.get_system_status()
    logger.info(f"System status: {status}")
    
    logger.info("Multi-Agent Context Distributor tests completed successfully")
    return True


def test_context_window_manager():
    """Test the Context Window Manager."""
    logger.info("Testing Context Window Manager...")
    
    # Initialize Context Window Manager
    manager = ContextWindowManager(
        vector_db_config={
            "db_provider": "chroma",
            "embedding_model": "sentence-transformers/all-mpnet-base-v2",
            "collection_name": "test_collection",
            "persist_directory": "/tmp/toronto_agent_vector_db_test"
        },
        memory_manager_config={
            "storage_dir": "/tmp/toronto_agent_memory_test",
            "short_term_capacity": 5,
            "working_memory_capacity": 3
        }
    )
    
    # Test processing a document
    document = """
    # Test Document
    
    This is a test document for the Context Window Manager.
    
    ## Section 1
    
    This is section 1 of the test document. It contains important information about the test.
    The test is designed to verify the functionality of the Context Window Manager.
    
    ## Section 2
    
    This is section 2 of the test document. It contains additional information about the test.
    The Context Window Manager should be able to process this document and make it available for retrieval.
    
    ## Section 3
    
    This is section 3 of the test document. It contains the conclusion of the test.
    The test will be considered successful if the Context Window Manager can process and retrieve this document.
    """
    
    result = manager.process_document(document, "test_doc_2", "markdown")
    logger.info(f"Processed document with result: {result['status']}")
    
    # Test retrieving context
    query = "section 2"
    retrieval_result = manager.retrieve_context(query, "combined", 3)
    logger.info(f"Retrieved context for query '{query}': {len(retrieval_result['context'])} characters")
    
    # Test sliding context window
    window = manager.get_sliding_context_window(query, 3)
    logger.info(f"Retrieved sliding context window of length: {len(window)}")
    
    # Test drilling down
    drill_down_result = manager.drill_down_context(query, "test_doc_2")
    logger.info(f"Drill down result for query '{query}': {drill_down_result['status']}")
    
    # Test getting summary
    summary_result = manager.get_summary_at_level("test_doc_2", 0)
    logger.info(f"Summary at level 0: {len(summary_result['summary'])} characters")
    
    # Test registering an agent
    agent = MockAgent("test_agent", ["code", "python"])
    manager.register_agent("test_agent", agent, ["code", "python"], 5000)
    
    # Test system status
    status = manager.get_system_status()
    logger.info(f"System status: {status}")
    
    logger.info("Context Window Manager tests completed successfully")
    return True


def test_large_document_processing():
    """Test processing a large document."""
    logger.info("Testing large document processing...")
    
    # Initialize Context Window Manager
    manager = ContextWindowManager()
    
    # Generate a large document
    large_document = generate_large_document(50000)  # 50,000 words
    
    # Process the document
    result = manager.process_document(large_document, "large_doc", "text")
    logger.info(f"Processed large document with result: {result['status']}")
    
    # Test retrieving context
    query = "important information section 25"
    retrieval_result = manager.retrieve_context(query, "combined", 3)
    logger.info(f"Retrieved context for query '{query}': {len(retrieval_result['context'])} characters")
    
    logger.info("Large document processing tests completed successfully")
    return True


def test_code_repository_processing():
    """Test processing a code repository."""
    logger.info("Testing code repository processing...")
    
    # Initialize Context Window Manager
    manager = ContextWindowManager()
    
    # Generate a mock code repository
    code_repository = generate_mock_code_repository()
    
    # Process each file in the repository
    for filename, content in code_repository.items():
        result = manager.process_document(content, filename, "code")
        logger.info(f"Processed code file {filename} with result: {result['status']}")
    
    # Test retrieving context
    query = "process_data function"
    retrieval_result = manager.retrieve_context(query, "combined", 3)
    logger.info(f"Retrieved context for query '{query}': {len(retrieval_result['context'])} characters")
    
    logger.info("Code repository processing tests completed successfully")
    return True


def test_conversation_history_processing():
    """Test processing a conversation history."""
    logger.info("Testing conversation history processing...")
    
    # Initialize Context Window Manager
    manager = ContextWindowManager()
    
    # Generate a mock conversation history
    conversation_history = generate_mock_conversation(100)  # 100 turns
    
    # Process the conversation
    result = manager.process_document(conversation_history, "conversation", "conversation")
    logger.info(f"Processed conversation history with result: {result['status']}")
    
    # Test retrieving context
    query = "project requirements"
    retrieval_result = manager.retrieve_context(query, "combined", 3)
    logger.info(f"Retrieved context for query '{query}': {len(retrieval_result['context'])} characters")
    
    logger.info("Conversation history processing tests completed successfully")
    return True


def generate_large_document(word_count: int) -> str:
    """
    Generate a large document for testing.
    
    Args:
        word_count: Number of words in the document
    
    Returns:
        Generated document
    """
    import random
    
    # Define some sample words
    words = [
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "I",
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
        "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
        "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
        "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
        "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
        "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
        "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
        "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
        "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"
    ]
    
    # Generate document structure
    document = "# Large Test Document\n\n"
    document += "This is a large test document for testing the Context Window Extension system.\n\n"
    
    # Generate sections
    num_sections = word_count // 1000
    for i in range(num_sections):
        document += f"## Section {i+1}\n\n"
        document += f"This is section {i+1} of the large test document.\n\n"
        
        # Generate paragraphs
        num_paragraphs = random.randint(3, 7)
        for j in range(num_paragraphs):
            # Generate a paragraph
            paragraph_length = random.randint(50, 150)
            paragraph = []
            
            for _ in range(paragraph_length):
                paragraph.append(random.choice(words))
            
            # Add some important keywords
            if random.random() < 0.3:
                paragraph.insert(random.randint(0, len(paragraph)), "important")
                paragraph.insert(random.randint(0, len(paragraph)), "information")
                paragraph.insert(random.randint(0, len(paragraph)), f"section {i+1}")
            
            document += " ".join(paragraph) + "\n\n"
    
    return document


def generate_mock_code_repository() -> Dict[str, str]:
    """
    Generate a mock code repository for testing.
    
    Returns:
        Dictionary mapping filenames to file contents
    """
    repository = {}
    
    # main.py
    repository["main.py"] = """
    #!/usr/bin/env python3
    
    import os
    import sys
    import json
    import logging
    from typing import Dict, Any, List
    
    from data_processor import process_data
    from model import Model
    from utils import load_config, save_results
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    def main():
        # Load configuration
        config = load_config("config.json")
        logger.info("Loaded configuration")
        
        # Initialize model
        model = Model(config["model_params"])
        logger.info("Initialized model")
        
        # Process data
        data = process_data(config["data_path"])
        logger.info(f"Processed {len(data)} data points")
        
        # Train model
        model.train(data, config["training_params"])
        logger.info("Trained model")
        
        # Evaluate model
        results = model.evaluate(data)
        logger.info(f"Model evaluation results: {results}")
        
        # Save results
        save_results(results, config["output_path"])
        logger.info("Saved results")
    
    if __name__ == "__main__":
        main()
    """
    
    # data_processor.py
    repository["data_processor.py"] = """
    import os
    import json
    import pandas as pd
    from typing import List, Dict, Any
    
    def process_data(data_path: str) -> List[Dict[str, Any]]:
        '''
        Process data from the specified path.
        
        Args:
            data_path: Path to the data file
        
        Returns:
            Processed data
        '''
        # Load data
        if data_path.endswith(".csv"):
            df = pd.read_csv(data_path)
        elif data_path.endswith(".json"):
            with open(data_path, "r") as f:
                df = pd.DataFrame(json.load(f))
        else:
            raise ValueError(f"Unsupported file format: {data_path}")
        
        # Clean data
        df = clean_data(df)
        
        # Transform data
        df = transform_data(df)
        
        # Convert to list of dictionaries
        data = df.to_dict(orient="records")
        
        return data
    
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        '''
        Clean the data.
        
        Args:
            df: Input DataFrame
        
        Returns:
            Cleaned DataFrame
        '''
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Fill missing values
        df = df.fillna(0)
        
        # Remove outliers
        for col in df.select_dtypes(include=["float", "int"]).columns:
            mean = df[col].mean()
            std = df[col].std()
            df = df[(df[col] >= mean - 3 * std) & (df[col] <= mean + 3 * std)]
        
        return df
    
    def transform_data(df: pd.DataFrame) -> pd.DataFrame:
        '''
        Transform the data.
        
        Args:
            df: Input DataFrame
        
        Returns:
            Transformed DataFrame
        '''
        # Normalize numerical columns
        for col in df.select_dtypes(include=["float", "int"]).columns:
            df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
        
        # One-hot encode categorical columns
        for col in df.select_dtypes(include=["object"]).columns:
            dummies = pd.get_dummies(df[col], prefix=col)
            df = pd.concat([df, dummies], axis=1)
            df = df.drop(col, axis=1)
        
        return df
    """
    
    # model.py
    repository["model.py"] = """
    import numpy as np
    from typing import List, Dict, Any
    
    class Model:
        '''
        Model class for training and evaluation.
        '''
        
        def __init__(self, params: Dict[str, Any]):
            '''
            Initialize the model.
            
            Args:
                params: Model parameters
            '''
            self.params = params
            self.weights = None
        
        def train(self, data: List[Dict[str, Any]], training_params: Dict[str, Any]):
            '''
            Train the model.
            
            Args:
                data: Training data
                training_params: Training parameters
            '''
            # Extract features and labels
            X, y = self._extract_features_and_labels(data)
            
            # Initialize weights
            num_features = X.shape[1]
            self.weights = np.random.randn(num_features)
            
            # Train for specified number of epochs
            num_epochs = training_params.get("num_epochs", 100)
            learning_rate = training_params.get("learning_rate", 0.01)
            
            for epoch in range(num_epochs):
                # Make predictions
                y_pred = self._predict(X)
                
                # Compute gradients
                gradients = self._compute_gradients(X, y, y_pred)
                
                # Update weights
                self.weights -= learning_rate * gradients
                
                # Compute loss
                loss = self._compute_loss(y, y_pred)
                
                if epoch % 10 == 0:
                    print(f"Epoch {epoch}, Loss: {loss:.4f}")
        
        def evaluate(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
            '''
            Evaluate the model.
            
            Args:
                data: Evaluation data
            
            Returns:
                Evaluation results
            '''
            # Extract features and labels
            X, y = self._extract_features_and_labels(data)
            
            # Make predictions
            y_pred = self._predict(X)
            
            # Compute metrics
            mse = np.mean((y - y_pred) ** 2)
            mae = np.mean(np.abs(y - y_pred))
            r2 = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
            
            return {
                "mse": float(mse),
                "mae": float(mae),
                "r2": float(r2)
            }
        
        def _extract_features_and_labels(self, data: List[Dict[str, Any]]):
            '''
            Extract features and labels from data.
            
            Args:
                data: Input data
            
            Returns:
                Features and labels
            '''
            # Extract feature names
            feature_names = list(data[0].keys())
            feature_names.remove(self.params["target_column"])
            
            # Extract features and labels
            X = np.array([[item[feature] for feature in feature_names] for item in data])
            y = np.array([item[self.params["target_column"]] for item in data])
            
            return X, y
        
        def _predict(self, X):
            '''
            Make predictions.
            
            Args:
                X: Input features
            
            Returns:
                Predictions
            '''
            return X.dot(self.weights)
        
        def _compute_gradients(self, X, y, y_pred):
            '''
            Compute gradients.
            
            Args:
                X: Input features
                y: True labels
                y_pred: Predicted labels
            
            Returns:
                Gradients
            '''
            return X.T.dot(y_pred - y) / len(y)
        
        def _compute_loss(self, y, y_pred):
            '''
            Compute loss.
            
            Args:
                y: True labels
                y_pred: Predicted labels
            
            Returns:
                Loss value
            '''
            return np.mean((y - y_pred) ** 2)
    """
    
    # utils.py
    repository["utils.py"] = """
    import os
    import json
    from typing import Dict, Any
    
    def load_config(config_path: str) -> Dict[str, Any]:
        '''
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
        
        Returns:
            Configuration dictionary
        '''
        with open(config_path, "r") as f:
            config = json.load(f)
        
        return config
    
    def save_results(results: Dict[str, Any], output_path: str):
        '''
        Save results to a JSON file.
        
        Args:
            results: Results to save
            output_path: Path to save the results
        '''
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save results
        with open(output_path, "w") as f:
            json.dump(results, f, indent=4)
    """
    
    return repository


def generate_mock_conversation(num_turns: int) -> str:
    """
    Generate a mock conversation for testing.
    
    Args:
        num_turns: Number of conversation turns
    
    Returns:
        Generated conversation
    """
    import random
    
    # Define some sample messages
    user_messages = [
        "Hello, I need help with a project.",
        "Can you explain how the context window extension works?",
        "What are the main components of the system?",
        "How does the vector database integration work?",
        "Tell me about the hierarchical document processing.",
        "How does the recursive summarization pipeline work?",
        "What is the memory management system?",
        "How does the multi-agent context distribution work?",
        "Can you give me an example of how to use the system?",
        "What are the limitations of the system?",
        "How can I extend the system with new components?",
        "What are the project requirements?",
        "How can I test the system?",
        "Can you help me debug an issue?",
        "How can I optimize the performance?",
        "What are the best practices for using the system?",
        "Can you summarize the key features?",
        "How does the system handle large documents?",
        "What about code repositories?",
        "How does it process conversation histories?"
    ]
    
    assistant_messages = [
        "I'd be happy to help with your project.",
        "The context window extension system provides an almost limitless context window by combining multiple techniques.",
        "The main components are the Vector Database Integration, Hierarchical Document Processing, Recursive Summarization, Memory Management, and Multi-Agent Context Distribution.",
        "The vector database integration stores document chunks as vectors and enables semantic search and retrieval.",
        "The hierarchical document processing breaks down documents into a hierarchical structure for efficient navigation.",
        "The recursive summarization pipeline creates multi-level summaries to maintain high-level understanding while allowing access to details.",
        "The memory management system organizes information across different memory types, including short-term, working, long-term, and episodic memory.",
        "The multi-agent context distribution distributes context processing across specialized agents for efficient handling of large projects.",
        "You can use the ContextWindowManager class to process documents, retrieve context, and interact with the system.",
        "The system has some limitations in terms of processing speed and memory usage, but these can be mitigated with proper configuration.",
        "You can extend the system by implementing new components that adhere to the existing interfaces.",
        "The project requirements include handling extremely large projects, including code repositories, documents, and conversations.",
        "You can test the system using the provided test script, which tests all components individually and together.",
        "I can help you debug issues by examining the logs and error messages.",
        "To optimize performance, you can adjust the configuration parameters and use more efficient embedding models.",
        "Best practices include breaking down large documents into manageable chunks and using appropriate metadata.",
        "Key features include almost limitless context window, hierarchical navigation, recursive summarization, and multi-agent distribution.",
        "Large documents are processed by breaking them down into chunks and creating a hierarchical representation.",
        "Code repositories are processed file by file, with special handling for code structures like functions and classes.",
        "Conversation histories are processed by identifying message boundaries and creating a structured representation."
    ]
    
    # Generate conversation
    conversation = ""
    
    for i in range(num_turns):
        # Add user message
        user_message = random.choice(user_messages)
        conversation += f"User: {user_message}\n\n"
        
        # Add assistant message
        assistant_message = random.choice(assistant_messages)
        conversation += f"Assistant: {assistant_message}\n\n"
    
    return conversation


def run_all_tests():
    """Run all tests."""
    logger.info("Running all tests...")
    
    tests = [
        test_vector_db_manager,
        test_hierarchical_processor,
        test_recursive_summarizer,
        test_memory_manager,
        test_multi_agent_context_distributor,
        test_context_window_manager,
        test_large_document_processing,
        test_code_repository_processing,
        test_conversation_history_processing
    ]
    
    results = {}
    
    for test in tests:
        test_name = test.__name__
        logger.info(f"Running test: {test_name}")
        
        try:
            success = test()
            results[test_name] = "PASS" if success else "FAIL"
        except Exception as e:
            logger.error(f"Error in test {test_name}: {str(e)}")
            results[test_name] = "ERROR"
    
    # Print summary
    logger.info("Test results:")
    for test_name, result in results.items():
        logger.info(f"{test_name}: {result}")
    
    # Check if all tests passed
    all_passed = all(result == "PASS" for result in results.values())
    logger.info(f"All tests passed: {all_passed}")
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()
