"""
Recursive Summarizer for context extension.

This module provides the Recursive Summarization Pipeline, which creates multi-level
summaries to maintain high-level understanding while allowing access to details.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import re

# Set up logging
logger = logging.getLogger(__name__)

class RecursiveSummarizer:
    """
    Summarizer class for recursive summarization.
    
    This class provides methods for creating multi-level summaries of large documents,
    enabling efficient processing of extremely large projects while maintaining context.
    """
    
    def __init__(
        self,
        model=None,
        tokenizer=None,
        target_size: int = 2000,
        min_size: int = 100,
        compression_ratio: float = 0.3,
        max_recursion_depth: int = 5,
        preserve_key_info: bool = True
    ):
        """
        Initialize the RecursiveSummarizer.
        
        Args:
            model: Language model for summarization (if None, will use a mock model)
            tokenizer: Tokenizer for the language model
            target_size: Target size for summaries in tokens
            min_size: Minimum size for summaries in tokens
            compression_ratio: Target compression ratio for summarization
            max_recursion_depth: Maximum recursion depth for summarization
            preserve_key_info: Whether to preserve key information in summaries
        """
        self.model = model
        self.tokenizer = tokenizer
        self.target_size = target_size
        self.min_size = min_size
        self.compression_ratio = compression_ratio
        self.max_recursion_depth = max_recursion_depth
        self.preserve_key_info = preserve_key_info
        
        # Initialize model and tokenizer if not provided
        if self.model is None or self.tokenizer is None:
            self._initialize_model_and_tokenizer()
        
        logger.info(f"Initialized RecursiveSummarizer with target_size={target_size}")
    
    def _initialize_model_and_tokenizer(self):
        """Initialize model and tokenizer if not provided."""
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            
            # Try to load a summarization model
            model_name = "facebook/bart-large-cnn"
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            logger.info(f"Loaded summarization model: {model_name}")
        
        except (ImportError, Exception) as e:
            logger.warning(f"Could not load summarization model: {str(e)}")
            logger.info("Using mock summarization model")
            
            # Use mock model and tokenizer
            self.model = MockSummarizationModel()
            self.tokenizer = MockTokenizer()
    
    def summarize(self, text: str, recursion_depth: int = 0) -> Dict[str, Any]:
        """
        Recursively summarize text.
        
        Args:
            text: Text to summarize
            recursion_depth: Current recursion depth
        
        Returns:
            Dictionary containing the summary and metadata
        """
        # Check if text is already small enough
        token_count = self._count_tokens(text)
        
        if token_count <= self.target_size or recursion_depth >= self.max_recursion_depth:
            # Text is small enough or we've reached max recursion depth
            return {
                "summary": text,
                "original_text": text,
                "token_count": token_count,
                "compression_ratio": 1.0,
                "recursion_depth": recursion_depth,
                "children": []
            }
        
        # Chunk the text
        chunks = self._chunk_text(text)
        
        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks:
            # Summarize the chunk
            summary = self._summarize_chunk(chunk)
            
            # Add to chunk summaries
            chunk_summaries.append({
                "summary": summary,
                "original_text": chunk,
                "token_count": self._count_tokens(summary),
                "original_token_count": self._count_tokens(chunk),
                "compression_ratio": self._count_tokens(summary) / max(1, self._count_tokens(chunk))
            })
        
        # Combine chunk summaries
        combined_summary = " ".join([cs["summary"] for cs in chunk_summaries])
        
        # If combined summary is still too large, recursively summarize
        if self._count_tokens(combined_summary) > self.target_size:
            result = self.summarize(combined_summary, recursion_depth + 1)
            
            # Add chunk summaries as children
            result["children"] = chunk_summaries
            
            return result
        
        # Combined summary is small enough
        return {
            "summary": combined_summary,
            "original_text": text,
            "token_count": self._count_tokens(combined_summary),
            "original_token_count": token_count,
            "compression_ratio": self._count_tokens(combined_summary) / token_count,
            "recursion_depth": recursion_depth + 1,
            "children": chunk_summaries
        }
    
    def _count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in text.
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Number of tokens
        """
        if hasattr(self.tokenizer, "encode"):
            return len(self.tokenizer.encode(text))
        else:
            # Fallback to simple word count
            return len(text.split())
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into manageable pieces.
        
        Args:
            text: Text to chunk
        
        Returns:
            List of text chunks
        """
        # Try to chunk by paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        
        # If we have very few paragraphs, split by sentences
        if len(paragraphs) < 3:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            return self._combine_chunks(sentences)
        
        # Combine paragraphs into chunks that fit the target size
        return self._combine_chunks(paragraphs)
    
    def _combine_chunks(self, elements: List[str]) -> List[str]:
        """
        Combine elements into chunks that fit the target size.
        
        Args:
            elements: List of text elements (paragraphs, sentences, etc.)
        
        Returns:
            List of combined chunks
        """
        chunks = []
        current_chunk = []
        current_size = 0
        
        for element in elements:
            element_size = self._count_tokens(element)
            
            if current_size + element_size <= self.target_size:
                # Add to current chunk
                current_chunk.append(element)
                current_size += element_size
            else:
                # Current chunk is full, start a new one
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                
                # Start new chunk with this element
                current_chunk = [element]
                current_size = element_size
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks
    
    def _summarize_chunk(self, chunk: str) -> str:
        """
        Summarize a single chunk of text.
        
        Args:
            chunk: Text chunk to summarize
        
        Returns:
            Summarized text
        """
        try:
            # Check if chunk is already small enough
            if self._count_tokens(chunk) <= self.target_size:
                return chunk
            
            # Determine target length
            target_length = max(self.min_size, int(self._count_tokens(chunk) * self.compression_ratio))
            
            # Extract key information if enabled
            key_info = self._extract_key_information(chunk) if self.preserve_key_info else ""
            
            # Generate summary
            if hasattr(self.model, "generate") and hasattr(self.tokenizer, "encode"):
                # Use transformer model
                inputs = self.tokenizer.encode(chunk, return_tensors="pt", max_length=1024, truncation=True)
                
                summary_ids = self.model.generate(
                    inputs,
                    max_length=target_length,
                    min_length=self.min_size,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True
                )
                
                summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            else:
                # Use mock model
                summary = self.model.generate_summary(chunk, target_length)
            
            # Combine key information with summary if needed
            if key_info and self.preserve_key_info:
                # Ensure we don't exceed target length
                combined_length = self._count_tokens(key_info) + self._count_tokens(summary)
                if combined_length > target_length:
                    # Reduce summary length to make room for key info
                    new_summary_target = target_length - self._count_tokens(key_info)
                    if new_summary_target > self.min_size:
                        # Regenerate shorter summary
                        if hasattr(self.model, "generate"):
                            summary_ids = self.model.generate(
                                inputs,
                                max_length=new_summary_target,
                                min_length=self.min_size,
                                length_penalty=2.0,
                                num_beams=4,
                                early_stopping=True
                            )
                            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                        else:
                            summary = self.model.generate_summary(chunk, new_summary_target)
                
                # Combine key info with summary
                summary = key_info + "\n\n" + summary
            
            return summary
        
        except Exception as e:
            logger.error(f"Error summarizing chunk: {str(e)}")
            # Return a truncated version of the chunk as fallback
            return chunk[:self.target_size * 4]  # Rough character estimate
    
    def _extract_key_information(self, text: str) -> str:
        """
        Extract key information from text.
        
        Args:
            text: Text to extract key information from
        
        Returns:
            Extracted key information
        """
        key_info = []
        
        # Extract names and entities
        names_and_entities = self._extract_names_and_entities(text)
        if names_and_entities:
            key_info.append("Key entities: " + ", ".join(names_and_entities))
        
        # Extract dates and numbers
        dates_and_numbers = self._extract_dates_and_numbers(text)
        if dates_and_numbers:
            key_info.append("Key dates and numbers: " + ", ".join(dates_and_numbers))
        
        # Extract code snippets
        code_snippets = self._extract_code_snippets(text)
        if code_snippets:
            key_info.append("Contains code snippets: " + str(len(code_snippets)))
        
        # Join key info
        return "\n".join(key_info)
    
    def _extract_names_and_entities(self, text: str) -> List[str]:
        """
        Extract names and entities from text.
        
        Args:
            text: Text to extract from
        
        Returns:
            List of extracted names and entities
        """
        # Simple regex-based extraction
        # Look for capitalized words that aren't at the start of sentences
        entities = re.findall(r'(?<![\.\?\!]\s)(?<!^)([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)', text)
        
        # Deduplicate and limit
        unique_entities = list(set(entities))
        return unique_entities[:10]  # Limit to 10 entities
    
    def _extract_dates_and_numbers(self, text: str) -> List[str]:
        """
        Extract dates and important numbers from text.
        
        Args:
            text: Text to extract from
        
        Returns:
            List of extracted dates and numbers
        """
        # Extract dates (simple patterns)
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'  # Month DD, YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))
        
        # Extract numbers with context
        # Look for numbers with units or percentages
        number_patterns = [
            r'\$\d+(?:,\d+)*(?:\.\d+)?',  # Money
            r'\d+(?:,\d+)*(?:\.\d+)?\s*%',  # Percentages
            r'\d+(?:,\d+)*(?:\.\d+)?\s*(?:kg|mg|g|km|m|cm|mm|GB|MB|KB|TB|Hz|MHz|GHz)'  # Measurements
        ]
        
        numbers = []
        for pattern in number_patterns:
            numbers.extend(re.findall(pattern, text))
        
        # Combine and limit
        combined = dates + numbers
        return combined[:15]  # Limit to 15 items
    
    def _extract_code_snippets(self, text: str) -> List[str]:
        """
        Extract code snippets from text.
        
        Args:
            text: Text to extract from
        
        Returns:
            List of extracted code snippets
        """
        # Look for code blocks in markdown
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', text, re.DOTALL)
        
        # Look for indented code
        indented_code = re.findall(r'(?:^|\n)(?:\s{4}|\t)(.+)(?:\n|$)', text)
        
        return code_blocks + indented_code
    
    def get_hierarchical_summary(self, text: str) -> Dict[str, Any]:
        """
        Generate a hierarchical summary of text.
        
        Args:
            text: Text to summarize
        
        Returns:
            Hierarchical summary structure
        """
        # Generate the recursive summary
        summary_result = self.summarize(text)
        
        # Format as hierarchical structure
        hierarchical_summary = self._format_hierarchical_summary(summary_result)
        
        return hierarchical_summary
    
    def _format_hierarchical_summary(self, summary_result: Dict[str, Any], level: int = 0) -> Dict[str, Any]:
        """
        Format summary result as a hierarchical structure.
        
        Args:
            summary_result: Summary result from summarize()
            level: Current hierarchy level
        
        Returns:
            Formatted hierarchical summary
        """
        formatted = {
            "level": level,
            "summary": summary_result["summary"],
            "token_count": summary_result["token_count"],
            "compression_ratio": summary_result.get("compression_ratio", 1.0),
            "children": []
        }
        
        # Add original text for leaf nodes
        if not summary_result.get("children"):
            formatted["original_text"] = summary_result["original_text"]
        
        # Process children recursively
        for child in summary_result.get("children", []):
            if isinstance(child, dict) and "summary" in child:
                # This is a summary result
                child_formatted = self._format_hierarchical_summary(child, level + 1)
                formatted["children"].append(child_formatted)
        
        return formatted
    
    def get_summary_at_level(self, hierarchical_summary: Dict[str, Any], target_level: int) -> str:
        """
        Get summary at a specific level of detail.
        
        Args:
            hierarchical_summary: Hierarchical summary structure
            target_level: Target level of detail (0 = most summarized)
        
        Returns:
            Summary at the specified level
        """
        if hierarchical_summary["level"] == target_level:
            return hierarchical_summary["summary"]
        
        if hierarchical_summary["level"] > target_level:
            # We're already past the target level
            return hierarchical_summary["summary"]
        
        # Combine children summaries
        if hierarchical_summary["children"]:
            child_summaries = []
            for child in hierarchical_summary["children"]:
                child_summary = self.get_summary_at_level(child, target_level)
                child_summaries.append(child_summary)
            
            return "\n\n".join(child_summaries)
        
        # No children, return current summary
        return hierarchical_summary["summary"]
    
    def drill_down(self, hierarchical_summary: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Drill down into a hierarchical summary based on a query.
        
        Args:
            hierarchical_summary: Hierarchical summary structure
            query: Query to search for
        
        Returns:
            Most relevant section of the hierarchical summary
        """
        # Score the current node
        current_score = self._relevance_score(hierarchical_summary["summary"], query)
        
        # Score children
        child_scores = []
        for i, child in enumerate(hierarchical_summary.get("children", [])):
            score = self._relevance_score(child["summary"], query)
            child_scores.append((i, score))
        
        # Sort children by score
        child_scores.sort(key=lambda x: x[1], reverse=True)
        
        # If we have children and the best child is more relevant than current node
        if child_scores and child_scores[0][1] > current_score:
            best_child_index = child_scores[0][0]
            best_child = hierarchical_summary["children"][best_child_index]
            
            # Recursively drill down into the best child
            return self.drill_down(best_child, query)
        
        # Current node is most relevant
        return hierarchical_summary
    
    def _relevance_score(self, text: str, query: str) -> float:
        """
        Calculate relevance score of text for a query.
        
        Args:
            text: Text to score
            query: Query to score against
        
        Returns:
            Relevance score (higher is more relevant)
        """
        # Simple keyword matching
        query_terms = query.lower().split()
        text_lower = text.lower()
        
        # Count term occurrences
        term_counts = {}
        for term in query_terms:
            term_counts[term] = text_lower.count(term)
        
        # Calculate score based on term frequency
        score = sum(term_counts.values()) / max(1, len(text.split()))
        
        # Boost score if all terms are present
        if all(count > 0 for count in term_counts.values()):
            score *= 2
        
        return score


class MockSummarizationModel:
    """Mock summarization model for development and testing."""
    
    def generate_summary(self, text: str, target_length: int) -> str:
        """
        Generate a summary of the text.
        
        Args:
            text: Text to summarize
            target_length: Target length in tokens
        
        Returns:
            Summarized text
        """
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Calculate target number of sentences
        target_sentences = max(1, int(len(sentences) * 0.3))
        
        # Take first sentence and some distributed sentences
        summary_sentences = [sentences[0]]
        
        if len(sentences) > 1:
            # Add distributed sentences
            step = max(1, len(sentences) // target_sentences)
            for i in range(step, len(sentences), step):
                summary_sentences.append(sentences[i])
        
        # Join sentences
        summary = " ".join(summary_sentences)
        
        # Truncate if still too long (rough approximation)
        words = summary.split()
        if len(words) > target_length:
            summary = " ".join(words[:target_length])
        
        return summary


class MockTokenizer:
    """Mock tokenizer for development and testing."""
    
    def encode(self, text: str, **kwargs) -> List[int]:
        """
        Encode text to token IDs.
        
        Args:
            text: Text to encode
            **kwargs: Additional arguments
        
        Returns:
            List of token IDs
        """
        # Simple word-based tokenization
        return [1] * len(text.split())
    
    def decode(self, token_ids: List[int], **kwargs) -> str:
        """
        Decode token IDs to text.
        
        Args:
            token_ids: Token IDs to decode
            **kwargs: Additional arguments
        
        Returns:
            Decoded text
        """
        # Return placeholder text
        return "Decoded text of length " + str(len(token_ids))
