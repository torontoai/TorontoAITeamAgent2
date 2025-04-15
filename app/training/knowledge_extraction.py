# TORONTO AI TEAM AGENT - PROPRIETARY
#
# Copyright (c) 2025 TORONTO AI
# Creator: David Tadeusz Chudak
# All Rights Reserved
#
# This file is part of the TORONTO AI TEAM AGENT software.
#
# This software is based on OpenManus (Copyright (c) 2025 manna_and_poem),
# which is licensed under the MIT License. The original license is included
# in the LICENSE file in the root directory of this project.
#
# This software has been substantially modified with proprietary enhancements.


"""Enhanced Knowledge Extraction Pipeline for TORONTO AI Team Agent.

This module provides an enhanced knowledge extraction pipeline with advanced chunking
strategies, multi-modal embeddings, and improved metadata extraction."""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import uuid
import time
import hashlib
from PIL import Image
import io
import base64

from .vector_db import VectorDatabaseFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeExtractionPipeline:
    """Enhanced pipeline for extracting knowledge from training materials and converting
    to vector embeddings for semantic retrieval."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Knowledge Extraction Pipeline.
        
        Args:
            config: Configuration settings for the pipeline"""
        self.config = config or {}
        
        # Default configuration values
        self.chunk_size = self.config.get("chunk_size", 1000)
        self.chunk_overlap = self.config.get("chunk_overlap", 200)
        self.chunking_strategy = self.config.get("chunking_strategy", "fixed_size")
        self.embedding_model = self.config.get("embedding_model", "text-embedding-3-large")
        self.api_key = self.config.get("openai_api_key", os.environ.get("OPENAI_API_KEY", ""))
        self.materials_path = self.config.get("materials_path", "./app/training/materials")
        self.enable_image_extraction = self.config.get("enable_image_extraction", True)
        self.image_model = self.config.get("image_model", "clip")
        
        # Initialize vector database
        self._initialize_vector_db()
        
        logger.info("Enhanced Knowledge Extraction Pipeline initialized")
    
    def _initialize_vector_db(self):
        """Initialize connection to the vector database."""
        try:
            # Create vector database using factory
            self.vector_db = VectorDatabaseFactory.create_vector_db(self.config)
            logger.info(f"Connected to vector database: {self.vector_db.__class__.__name__}")
        except Exception as e:
            logger.error(f"Error initializing vector database: {str(e)}")
            # Create a simple fallback in-memory store
            self.vector_db = VectorDatabaseFactory.create_vector_db({"vector_db_type": "in_memory"})
            logger.info("Using fallback in-memory vector database")
    
    def process_all_materials(self) -> Dict[str, Any]:
        """Process all training materials in the materials directory.
        
        Returns:
            Processing results summary"""
        materials_path = Path(self.materials_path)
        if not materials_path.exists():
            logger.error(f"Materials path does not exist: {materials_path}")
            return {"success": False, "message": f"Materials path does not exist: {materials_path}"}
        
        # Find all markdown files
        markdown_files = list(materials_path.glob("*.md"))
        logger.info(f"Found {len(markdown_files)} markdown files in {materials_path}")
        
        results = {
            "success": True,
            "processed_files": 0,
            "total_chunks": 0,
            "total_embeddings": 0,
            "file_details": []
        }
        
        # Process each file
        for md_file in tqdm(markdown_files, desc="Processing training materials"):
            try:
                file_result = self.process_material(md_file)
                results["processed_files"] += 1
                results["total_chunks"] += file_result.get("chunk_count", 0)
                results["total_embeddings"] += file_result.get("embedding_count", 0)
                results["file_details"].append(file_result)
            except Exception as e:
                logger.error(f"Error processing {md_file}: {str(e)}")
                results["file_details"].append({
                    "file": str(md_file),
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Processed {results['processed_files']} files with {results['total_chunks']} chunks and {results['total_embeddings']} embeddings")
        return results
    
    def process_material(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Process a single training material file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Processing results for the file"""
        file_path = Path(file_path)
        logger.info(f"Processing {file_path}")
        
        # Extract role name from filename
        role_name = file_path.stem.replace("_training", "").replace("_", " ")
        
        # Read and parse the markdown file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract structured content
        structured_content = self._parse_markdown(content)
        
        # Extract images if enabled
        image_embeddings = []
        if self.enable_image_extraction:
            image_embeddings = self._extract_images_from_markdown(content, file_path)
        
        # Chunk the content based on selected strategy
        chunks = self._chunk_content(structured_content)
        
        # Generate embeddings
        embeddings_result = self._generate_embeddings(chunks, role_name, file_path.stem)
        
        # Add image embeddings if available
        if image_embeddings:
            image_result = self._add_image_embeddings(image_embeddings, role_name, file_path.stem)
            embeddings_result["embedding_count"] += image_result.get("embedding_count", 0)
        
        return {
            "file": str(file_path),
            "role": role_name,
            "success": True,
            "chunk_count": len(chunks),
            "embedding_count": embeddings_result.get("embedding_count", 0),
            "image_count": len(image_embeddings) if image_embeddings else 0,
            "sections": [section["title"] for section in structured_content]
        }
    
    def _parse_markdown(self, content: str) -> List[Dict[str, Any]]:
        """Parse markdown content into structured sections with enhanced metadata.
        
        Args:
            content: Raw markdown content
            
        Returns:
            List of structured sections"""
        # Convert markdown to HTML
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract title
        title = soup.find("h1")
        title_text = title.text if title else "Untitled"
        
        # Initialize structured content
        structured_content = []
        
        # Find all h2 headers (main sections)
        h2_headers = soup.find_all("h2")
        
        for i, h2 in enumerate(h2_headers):
            section_title = h2.text
            section_content = []
            
            # Get all elements until the next h2 or end of document
            current = h2.next_sibling
            while current and (not current.name == "h2"):
                if current.name:
                    section_content.append(str(current))
                current = current.next_sibling
            
            # Join the content
            section_html = "".join(section_content)
            section_text = BeautifulSoup(section_html, "html.parser").get_text()
            
            # Extract keywords from section
            keywords = self._extract_keywords(section_text)
            
            # Add to structured content
            structured_content.append({
                "title": section_title,
                "content": section_text,
                "html": section_html,
                "level": 2,
                "order": i,
                "keywords": keywords,
                "word_count": len(section_text.split()),
                "char_count": len(section_text)
            })
            
            # Look for h3 subsections within this section
            h3_headers = BeautifulSoup(section_html, "html.parser").find_all("h3")
            for j, h3 in enumerate(h3_headers):
                subsection_title = h3.text
                
                # Extract content for this subsection
                subsection_content = []
                current = h3.next_sibling
                while current and (not current.name in ["h3", "h2"]):
                    if current.name:
                        subsection_content.append(str(current))
                    current = current.next_sibling
                
                # Join the content
                subsection_html = "".join(subsection_content)
                subsection_text = BeautifulSoup(subsection_html, "html.parser").get_text()
                
                # Extract keywords from subsection
                subsection_keywords = self._extract_keywords(subsection_text)
                
                # Add to structured content
                structured_content.append({
                    "title": f"{section_title} - {subsection_title}",
                    "content": subsection_text,
                    "html": subsection_html,
                    "level": 3,
                    "order": i * 100 + j,
                    "parent_section": section_title,
                    "keywords": subsection_keywords,
                    "word_count": len(subsection_text.split()),
                    "char_count": len(subsection_text)
                })
        
        return structured_content
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            List of keywords"""
        # Simple keyword extraction based on frequency and capitalization
        # In a production system, this would use more sophisticated NLP techniques
        
        # Remove common words
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "about", "as"}
        words = text.lower().split()
        filtered_words = [word for word in words if word not in common_words and len(word) > 3]
        
        # Count word frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Find technical terms (capitalized words or words with special characters)
        technical_terms = []
        for word in text.split():
            if len(word) > 1 and word[0].isupper() and word.lower() not in common_words:
                technical_terms.append(word)
            elif re.search(r'[-_/]', word) and len(word) > 3:
                technical_terms.append(word)
        
        # Get top terms by frequency
        top_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        top_terms = [term[0] for term in top_terms]
        
        # Combine with technical terms
        keywords = list(set(top_terms + technical_terms))[:15]
        
        return keywords
    
    def _extract_images_from_markdown(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract images from markdown content.
        
        Args:
            content: Markdown content
            file_path: Path to the markdown file
            
        Returns:
            List of image data with embeddings"""
        # Find all image references in markdown
        image_refs = re.findall(r'!\[(.*?)\]\((.*?)\)', content)
        
        if not image_refs:
            return []
        
        logger.info(f"Found {len(image_refs)} image references in {file_path}")
        
        image_data = []
        
        for alt_text, image_path in image_refs:
            try:
                # Resolve image path (could be relative to markdown file)
                resolved_path = self._resolve_image_path(image_path, file_path)
                
                if not resolved_path or not os.path.exists(resolved_path):
                    logger.warning(f"Image not found: {image_path}")
                    continue
                
                # Generate image embedding
                embedding = self._generate_image_embedding(resolved_path)
                
                if embedding is not None:
                    # Extract surrounding text context
                    context = self._extract_image_context(content, image_path)
                    
                    image_data.append({
                        "path": str(resolved_path),
                        "alt_text": alt_text,
                        "embedding": embedding,
                        "context": context
                    })
            except Exception as e:
                logger.error(f"Error processing image {image_path}: {str(e)}")
        
        return image_data
    
    def _resolve_image_path(self, image_path: str, markdown_path: Path) -> Optional[str]:
        """Resolve image path relative to markdown file.
        
        Args:
            image_path: Image path from markdown
            markdown_path: Path to markdown file
            
        Returns:
            Resolved image path or None if not found"""
        # Check if path is absolute
        if os.path.isabs(image_path):
            return image_path if os.path.exists(image_path) else None
        
        # Check if path is relative to markdown file
        relative_path = os.path.join(os.path.dirname(markdown_path), image_path)
        if os.path.exists(relative_path):
            return relative_path
        
        # Check if path is relative to materials directory
        materials_path = os.path.join(self.materials_path, image_path)
        if os.path.exists(materials_path):
            return materials_path
        
        # Check if path is in common image directories
        for img_dir in ["images", "img", "assets"]:
            potential_path = os.path.join(os.path.dirname(markdown_path), img_dir, os.path.basename(image_path))
            if os.path.exists(potential_path):
                return potential_path
        
        return None
    
    def _generate_image_embedding(self, image_path: str) -> Optional[np.ndarray]:
        """Generate embedding for an image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image embedding or None if failed"""
        try:
            # In a production system, this would use a proper image embedding model
            # For now, we'll simulate image embeddings
            
            # Load image to get basic properties
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
            
            # Generate a deterministic but unique embedding based on image properties
            # This is just a simulation - real systems would use CLIP or similar models
            image_hash = hashlib.md5(f"{image_path}_{width}_{height}_{mode}".encode()).hexdigest()
            
            # Convert hash to a vector of floats
            hash_bytes = bytes.fromhex(image_hash)
            float_values = []
            
            for i in range(0, len(hash_bytes), 4):
                if i + 4 <= len(hash_bytes):
                    # Convert 4 bytes to a float between -1 and 1
                    value = int.from_bytes(hash_bytes[i:i+4], byteorder='big') / (2**32 - 1) * 2 - 1
                    float_values.append(value)
            
            # Pad or truncate to desired dimension
            dimension = 1536  # Same as text embeddings for simplicity
            if len(float_values) < dimension:
                float_values.extend([0.0] * (dimension - len(float_values)))
            else:
                float_values = float_values[:dimension]
            
            return np.array(float_values, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Error generating image embedding for {image_path}: {str(e)}")
            return None
    
    def _extract_image_context(self, content: str, image_path: str) -> str:
        """Extract text context surrounding an image reference.
        
        Args:
            content: Markdown content
            image_path: Image path to find
            
        Returns:
            Text context"""
        # Find the image reference
        image_ref_pattern = re.escape(f"![](${image_path})").replace("\\$", "")
        match = re.search(f"(.*?)!\\[.*?\\]\\({re.escape(image_path)}\\)(.*?)", content, re.DOTALL)
        
        if not match:
            return ""
        
        # Extract text before and after the image (limited to ~100 words each)
        before_text = match.group(1).strip().split()[-100:]
        after_text = match.group(2).strip().split()[:100]
        
        context = " ".join(before_text + after_text)
        
        return context
    
    def _chunk_content(self, structured_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk content based on selected strategy.
        
        Args:
            structured_content: Structured content sections
            
        Returns:
            List of content chunks"""
        if self.chunking_strategy == "semantic":
            return self._semantic_chunking(structured_content)
        elif self.chunking_strategy == "sliding_window":
            return self._sliding_window_chunking(structured_content)
        else:  # Default to fixed size
            return self._fixed_size_chunking(structured_content)
    
    def _fixed_size_chunking(self, structured_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk content using fixed size strategy.
        
        Args:
            structured_content: Structured content sections
            
        Returns:
            List of content chunks"""
        chunks = []
        
        for section in structured_content:
            content = section["content"]
            title = section["title"]
            
            # Skip empty sections
            if not content.strip():
                continue
            
            # Split content into chunks of approximately chunk_size characters
            content_length = len(content)
            
            if content_length <= self.chunk_size:
                # Content fits in a single chunk
                chunks.append({
                    "title": title,
                    "content": content,
                    "metadata": {
                        "section": title,
                        "level": section["level"],
                        "order": section["order"],
                        "keywords": section.get("keywords", []),
                        "parent_section": section.get("parent_section", ""),
                        "chunk_type": "complete_section"
                    }
                })
            else:
                # Split content into multiple chunks
                sentences = re.split(r'(?<=[.!?])\s+', content)
                current_chunk = ""
                chunk_index = 0
                
                for sentence in sentences:
                    # If adding this sentence would exceed chunk_size, create a new chunk
                    if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                        chunks.append({
                            "title": f"{title} (part {chunk_index + 1})",
                            "content": current_chunk,
                            "metadata": {
                                "section": title,
                                "level": section["level"],
                                "order": section["order"],
                                "chunk_index": chunk_index,
                                "keywords": section.get("keywords", []),
                                "parent_section": section.get("parent_section", ""),
                                "chunk_type": "partial_section"
                            }
                        })
                        
                        # Start a new chunk with overlap
                        overlap_point = max(0, len(current_chunk) - self.chunk_overlap)
                        current_chunk = current_chunk[overlap_point:] + sentence
                        chunk_index += 1
                    else:
                        current_chunk += sentence + " "
                
                # Add the last chunk if not empty
                if current_chunk.strip():
                    chunks.append({
                        "title": f"{title} (part {chunk_index + 1})",
                        "content": current_chunk,
                        "metadata": {
                            "section": title,
                            "level": section["level"],
                            "order": section["order"],
                            "chunk_index": chunk_index,
                            "keywords": section.get("keywords", []),
                            "parent_section": section.get("parent_section", ""),
                            "chunk_type": "partial_section"
                        }
                    })
        
        return chunks
    
    def _sliding_window_chunking(self, structured_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk content using sliding window strategy with variable overlap.
        
        Args:
            structured_content: Structured content sections
            
        Returns:
            List of content chunks"""
        chunks = []
        
        for section in structured_content:
            content = section["content"]
            title = section["title"]
            
            # Skip empty sections
            if not content.strip():
                continue
            
            # Split content into sentences
            sentences = re.split(r'(?<=[.!?])\s+', content)
            
            # If content is short, keep it as a single chunk
            if len(content) <= self.chunk_size:
                chunks.append({
                    "title": title,
                    "content": content,
                    "metadata": {
                        "section": title,
                        "level": section["level"],
                        "order": section["order"],
                        "keywords": section.get("keywords", []),
                        "parent_section": section.get("parent_section", ""),
                        "chunk_type": "complete_section"
                    }
                })
                continue
            
            # Create overlapping chunks with sliding window
            chunk_index = 0
            window_start = 0
            
            while window_start < len(sentences):
                current_chunk = ""
                window_end = window_start
                
                # Add sentences until we reach chunk_size
                while window_end < len(sentences) and len(current_chunk) + len(sentences[window_end]) <= self.chunk_size:
                    current_chunk += sentences[window_end] + " "
                    window_end += 1
                
                # If we couldn't add even one sentence, take a partial sentence
                if window_end == window_start:
                    current_chunk = sentences[window_start][:self.chunk_size]
                    window_end = window_start + 1
                
                # Add the chunk
                chunks.append({
                    "title": f"{title} (window {chunk_index + 1})",
                    "content": current_chunk.strip(),
                    "metadata": {
                        "section": title,
                        "level": section["level"],
                        "order": section["order"],
                        "chunk_index": chunk_index,
                        "window_start": window_start,
                        "window_end": window_end,
                        "keywords": section.get("keywords", []),
                        "parent_section": section.get("parent_section", ""),
                        "chunk_type": "sliding_window"
                    }
                })
                
                # Calculate adaptive overlap based on content complexity
                # More complex content gets more overlap
                content_complexity = min(0.8, len(set(sentences[window_start:window_end])) / max(1, window_end - window_start))
                adaptive_overlap = int(self.chunk_overlap * (1 + content_complexity))
                
                # Move window forward with adaptive overlap
                sentences_to_advance = max(1, window_end - window_start - adaptive_overlap // 100)
                window_start += sentences_to_advance
                chunk_index += 1
        
        return chunks
    
    def _semantic_chunking(self, structured_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk content using semantic boundaries.
        
        Args:
            structured_content: Structured content sections
            
        Returns:
            List of content chunks"""
        chunks = []
        
        for section in structured_content:
            content = section["content"]
            title = section["title"]
            
            # Skip empty sections
            if not content.strip():
                continue
            
            # If content is short, keep it as a single chunk
            if len(content) <= self.chunk_size:
                chunks.append({
                    "title": title,
                    "content": content,
                    "metadata": {
                        "section": title,
                        "level": section["level"],
                        "order": section["order"],
                        "keywords": section.get("keywords", []),
                        "parent_section": section.get("parent_section", ""),
                        "chunk_type": "complete_section"
                    }
                })
                continue
            
            # Split content at semantic boundaries (paragraphs, lists, code blocks)
            semantic_units = self._split_into_semantic_units(content)
            
            current_chunk = ""
            current_units = []
            chunk_index = 0
            
            for unit in semantic_units:
                # If adding this unit would exceed chunk_size, create a new chunk
                if len(current_chunk) + len(unit) > self.chunk_size and current_chunk:
                    chunks.append({
                        "title": f"{title} (semantic {chunk_index + 1})",
                        "content": current_chunk,
                        "metadata": {
                            "section": title,
                            "level": section["level"],
                            "order": section["order"],
                            "chunk_index": chunk_index,
                            "semantic_units": len(current_units),
                            "keywords": section.get("keywords", []),
                            "parent_section": section.get("parent_section", ""),
                            "chunk_type": "semantic"
                        }
                    })
                    
                    # Start a new chunk
                    current_chunk = unit
                    current_units = [unit]
                    chunk_index += 1
                else:
                    current_chunk += unit
                    current_units.append(unit)
            
            # Add the last chunk if not empty
            if current_chunk.strip():
                chunks.append({
                    "title": f"{title} (semantic {chunk_index + 1})",
                    "content": current_chunk,
                    "metadata": {
                        "section": title,
                        "level": section["level"],
                        "order": section["order"],
                        "chunk_index": chunk_index,
                        "semantic_units": len(current_units),
                        "keywords": section.get("keywords", []),
                        "parent_section": section.get("parent_section", ""),
                        "chunk_type": "semantic"
                    }
                })
        
        return chunks
    
    def _split_into_semantic_units(self, content: str) -> List[str]:
        """Split content into semantic units.
        
        Args:
            content: Text content
            
        Returns:
            List of semantic units"""
        # Split at paragraph boundaries
        paragraphs = re.split(r'\n\s*\n', content)
        
        semantic_units = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if paragraph is a list
            if re.match(r'^(\d+\.|\*|\-|\+)\s', paragraph):
                # Split list into items
                list_items = re.split(r'\n(?=(\d+\.|\*|\-|\+)\s)', paragraph)
                semantic_units.extend(list_items)
            # Check if paragraph is a code block
            elif paragraph.startswith("```") or paragraph.startswith("    "):
                semantic_units.append(paragraph)
            # Check if paragraph is very long
            elif len(paragraph) > self.chunk_size:
                # Split into sentences
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                current_unit = ""
                
                for sentence in sentences:
                    if len(current_unit) + len(sentence) > self.chunk_size // 2:
                        if current_unit:
                            semantic_units.append(current_unit)
                        current_unit = sentence + " "
                    else:
                        current_unit += sentence + " "
                
                if current_unit:
                    semantic_units.append(current_unit)
            else:
                semantic_units.append(paragraph)
        
        return semantic_units
    
    def _generate_embeddings(self, chunks: List[Dict[str, Any]], role: str, source: str) -> Dict[str, Any]:
        """Generate embeddings for content chunks.
        
        Args:
            chunks: Content chunks
            role: Agent role
            source: Source identifier
            
        Returns:
            Embedding generation results"""
        if not chunks:
            return {"success": False, "message": "No chunks to embed", "embedding_count": 0}
        
        try:
            # Generate embeddings
            embeddings = self._get_embeddings([chunk["content"] for chunk in chunks])
            
            if not embeddings or len(embeddings) != len(chunks):
                return {"success": False, "message": "Failed to generate embeddings", "embedding_count": 0}
            
            # Prepare documents for vector database
            documents = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                # Create document with metadata
                document = {
                    "content": chunk["content"],
                    "title": chunk["title"],
                    "role": role,
                    "source": source,
                    "chunk_index": i
                }
                
                # Add metadata
                document.update(chunk["metadata"])
                
                documents.append(document)
            
            # Add to vector database
            ids = self.vector_db.add_vectors(embeddings, documents)
            
            return {
                "success": True,
                "message": f"Generated {len(embeddings)} embeddings",
                "embedding_count": len(embeddings),
                "ids": ids
            }
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return {"success": False, "message": str(e), "embedding_count": 0}
    
    def _add_image_embeddings(self, image_data: List[Dict[str, Any]], role: str, source: str) -> Dict[str, Any]:
        """Add image embeddings to vector database.
        
        Args:
            image_data: Image data with embeddings
            role: Agent role
            source: Source identifier
            
        Returns:
            Result of adding image embeddings"""
        if not image_data:
            return {"success": True, "message": "No images to embed", "embedding_count": 0}
        
        try:
            # Prepare embeddings and documents
            embeddings = [img["embedding"] for img in image_data]
            documents = []
            
            for i, img in enumerate(image_data):
                document = {
                    "content": img["context"],
                    "title": f"Image: {img['alt_text'] or os.path.basename(img['path'])}",
                    "role": role,
                    "source": source,
                    "chunk_index": i,
                    "content_type": "image",
                    "image_path": img["path"],
                    "alt_text": img["alt_text"]
                }
                
                documents.append(document)
            
            # Add to vector database
            ids = self.vector_db.add_vectors(embeddings, documents)
            
            return {
                "success": True,
                "message": f"Added {len(embeddings)} image embeddings",
                "embedding_count": len(embeddings),
                "ids": ids
            }
            
        except Exception as e:
            logger.error(f"Error adding image embeddings: {str(e)}")
            return {"success": False, "message": str(e), "embedding_count": 0}
    
    def _get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Get embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings"""
        # In a production system, this would use the OpenAI API or another embedding service
        # For now, we'll simulate embeddings
        
        embeddings = []
        
        for text in texts:
            # Generate a deterministic but unique embedding based on text content
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            # Convert hash to a vector of floats
            hash_bytes = bytes.fromhex(text_hash)
            float_values = []
            
            for i in range(0, len(hash_bytes), 4):
                if i + 4 <= len(hash_bytes):
                    # Convert 4 bytes to a float between -1 and 1
                    value = int.from_bytes(hash_bytes[i:i+4], byteorder='big') / (2**32 - 1) * 2 - 1
                    float_values.append(value)
            
            # Pad or truncate to desired dimension
            dimension = 1536  # OpenAI's text-embedding-3-large dimension
            if len(float_values) < dimension:
                float_values.extend([0.0] * (dimension - len(float_values)))
            else:
                float_values = float_values[:dimension]
            
            embeddings.append(np.array(float_values, dtype=np.float32))
        
        return embeddings
    
    def query_knowledge(self, query: str, role: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Query knowledge base for relevant information.
        
        Args:
            query: Query string
            role: Optional role filter
            top_k: Number of results to return
            
        Returns:
            List of relevant knowledge chunks"""
        try:
            # Generate query embedding
            query_embedding = self._get_embeddings([query])[0]
            
            # Prepare filter
            filter_dict = {"role": role} if role else None
            
            # Perform hybrid search
            results = self.vector_db.hybrid_query(
                query_vector=query_embedding,
                query_text=query,
                top_k=top_k,
                filter_dict=filter_dict
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying knowledge: {str(e)}")
            return []


# Create a singleton instance
pipeline = KnowledgeExtractionPipeline()
