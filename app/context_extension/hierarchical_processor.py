"""
Hierarchical Processor for context extension.

This module provides the Hierarchical Document Processing System, which breaks down
large documents into manageable hierarchical structures, enabling efficient processing
of extremely large projects.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Union, Tuple

# Set up logging
logger = logging.getLogger(__name__)

class HierarchicalProcessor:
    """
    Processor class for hierarchical document processing.
    
    This class provides methods for breaking down large documents into hierarchical
    structures and navigating through these structures efficiently.
    """
    
    def __init__(
        self,
        max_chunk_size: int = 4000,
        overlap: int = 200,
        detect_structure: bool = True,
        preserve_hierarchy: bool = True
    ):
        """
        Initialize the HierarchicalProcessor.
        
        Args:
            max_chunk_size: Maximum size of each chunk in tokens
            overlap: Overlap between chunks to maintain context
            detect_structure: Whether to automatically detect document structure
            preserve_hierarchy: Whether to preserve the hierarchical structure in processing
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.detect_structure = detect_structure
        self.preserve_hierarchy = preserve_hierarchy
        
        logger.info(f"Initialized HierarchicalProcessor with max_chunk_size={max_chunk_size}")
    
    def process_document(self, document: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a document into a hierarchical structure.
        
        Args:
            document: Document to process
            document_type: Optional document type (code, text, markdown, etc.)
        
        Returns:
            Hierarchical representation of the document
        """
        # Detect document type if not provided
        if document_type is None:
            document_type = self._detect_document_type(document)
        
        # Analyze document structure
        structure = self._analyze_document_structure(document, document_type)
        
        # Create hierarchical representation
        hierarchical_chunks = self._create_hierarchical_representation(document, structure)
        
        return hierarchical_chunks
    
    def _detect_document_type(self, document: str) -> str:
        """
        Detect the type of document based on content.
        
        Args:
            document: Document to analyze
        
        Returns:
            Detected document type
        """
        # Check for code indicators
        code_patterns = [
            r'def\s+\w+\s*\(.*\)\s*:',  # Python function
            r'function\s+\w+\s*\(.*\)\s*{',  # JavaScript function
            r'class\s+\w+\s*[({]',  # Class definition
            r'import\s+[\w.]+',  # Import statement
            r'#include\s+[<"][\w.]+[>"]',  # C/C++ include
            r'public\s+static\s+void\s+main',  # Java main method
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, document):
                return "code"
        
        # Check for markdown indicators
        markdown_patterns = [
            r'^#\s+\w+',  # Heading
            r'^\*\s+\w+',  # Unordered list
            r'^\d+\.\s+\w+',  # Ordered list
            r'\[.*\]\(.*\)',  # Link
            r'```\w*\n',  # Code block
        ]
        
        markdown_count = 0
        for pattern in markdown_patterns:
            markdown_count += len(re.findall(pattern, document, re.MULTILINE))
        
        if markdown_count > 5:  # Arbitrary threshold
            return "markdown"
        
        # Default to text
        return "text"
    
    def _analyze_document_structure(self, document: str, document_type: str) -> Dict[str, Any]:
        """
        Analyze the structure of a document.
        
        Args:
            document: Document to analyze
            document_type: Type of document
        
        Returns:
            Document structure information
        """
        structure = {
            "type": document_type,
            "sections": [],
            "hierarchy_levels": []
        }
        
        if document_type == "code":
            structure = self._analyze_code_structure(document, structure)
        elif document_type == "markdown":
            structure = self._analyze_markdown_structure(document, structure)
        else:  # text
            structure = self._analyze_text_structure(document, structure)
        
        return structure
    
    def _analyze_code_structure(self, document: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the structure of code.
        
        Args:
            document: Code document to analyze
            structure: Initial structure dictionary
        
        Returns:
            Updated structure dictionary
        """
        # Detect language
        language = self._detect_code_language(document)
        structure["language"] = language
        
        # Find classes, functions, and methods
        if language in ["python", "unknown"]:
            # Python-like structure
            class_pattern = r'class\s+(\w+)\s*(?:\(.*\))?\s*:'
            function_pattern = r'def\s+(\w+)\s*\(.*\)\s*:'
            
            classes = re.finditer(class_pattern, document)
            functions = re.finditer(function_pattern, document)
            
            # Add classes to sections
            for match in classes:
                start = match.start()
                name = match.group(1)
                structure["sections"].append({
                    "type": "class",
                    "name": name,
                    "start": start,
                    "level": 1
                })
            
            # Add functions to sections
            for match in functions:
                start = match.start()
                name = match.group(1)
                # Check if this is a method within a class
                is_method = False
                indentation = len(document[:start]) - len(document[:start].rstrip())
                if indentation > 0:
                    is_method = True
                
                structure["sections"].append({
                    "type": "function" if not is_method else "method",
                    "name": name,
                    "start": start,
                    "level": 2 if is_method else 1
                })
        
        elif language in ["javascript", "typescript", "java", "c", "cpp", "csharp"]:
            # C-like structure with braces
            class_pattern = r'(?:class|interface|struct)\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w,\s]+)?\s*{'
            function_pattern = r'(?:function\s+(\w+)|(\w+)\s*:\s*function|\b(\w+)\s*\(.*\)\s*{)'
            
            classes = re.finditer(class_pattern, document)
            functions = re.finditer(function_pattern, document)
            
            # Add classes to sections
            for match in classes:
                start = match.start()
                name = match.group(1)
                structure["sections"].append({
                    "type": "class",
                    "name": name,
                    "start": start,
                    "level": 1
                })
            
            # Add functions to sections
            for match in functions:
                start = match.start()
                name = match.group(1) or match.group(2) or match.group(3)
                # Determine if this is a method by checking if it's inside a class
                is_method = False
                for section in structure["sections"]:
                    if section["type"] == "class" and section["start"] < start:
                        # Check if we're still in the class scope
                        class_end = document.find("}", start)
                        if class_end != -1 and document.count("{", section["start"], start) > document.count("}", section["start"], start):
                            is_method = True
                            break
                
                structure["sections"].append({
                    "type": "function" if not is_method else "method",
                    "name": name,
                    "start": start,
                    "level": 2 if is_method else 1
                })
        
        # Sort sections by start position
        structure["sections"].sort(key=lambda x: x["start"])
        
        # Determine hierarchy levels
        levels = set()
        for section in structure["sections"]:
            levels.add(section["level"])
        
        structure["hierarchy_levels"] = sorted(list(levels))
        
        return structure
    
    def _detect_code_language(self, code: str) -> str:
        """
        Detect the programming language of code.
        
        Args:
            code: Code to analyze
        
        Returns:
            Detected programming language
        """
        # Simple language detection based on patterns
        patterns = {
            "python": [r'def\s+\w+\s*\(.*\)\s*:', r'import\s+[\w.]+', r'from\s+[\w.]+\s+import'],
            "javascript": [r'function\s+\w+\s*\(.*\)\s*{', r'const\s+\w+\s*=', r'let\s+\w+\s*=', r'var\s+\w+\s*='],
            "typescript": [r'interface\s+\w+\s*{', r'type\s+\w+\s*=', r':\s*\w+\[\]'],
            "java": [r'public\s+class', r'private\s+\w+\s+\w+\s*\(', r'package\s+[\w.]+;'],
            "c": [r'#include\s+[<"][\w.]+[>"]', r'int\s+main\s*\(\s*(?:void|int\s+argc,\s*char\s*\*\s*argv\[\])\s*\)'],
            "cpp": [r'#include\s+[<"][\w.]+[>"]', r'std::', r'namespace\s+\w+'],
            "csharp": [r'namespace\s+[\w.]+', r'using\s+[\w.]+;', r'public\s+class']
        }
        
        scores = {lang: 0 for lang in patterns}
        
        for lang, patterns_list in patterns.items():
            for pattern in patterns_list:
                matches = re.findall(pattern, code)
                scores[lang] += len(matches)
        
        # Get the language with the highest score
        max_score = 0
        detected_language = "unknown"
        
        for lang, score in scores.items():
            if score > max_score:
                max_score = score
                detected_language = lang
        
        return detected_language
    
    def _analyze_markdown_structure(self, document: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the structure of markdown.
        
        Args:
            document: Markdown document to analyze
            structure: Initial structure dictionary
        
        Returns:
            Updated structure dictionary
        """
        # Find headings
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        
        for match in re.finditer(heading_pattern, document, re.MULTILINE):
            level = len(match.group(1))
            heading = match.group(2).strip()
            start = match.start()
            
            structure["sections"].append({
                "type": f"h{level}",
                "name": heading,
                "start": start,
                "level": level
            })
        
        # Find code blocks
        code_block_pattern = r'```(\w*)\n(.*?)```'
        
        for match in re.finditer(code_block_pattern, document, re.DOTALL):
            language = match.group(1) or "unknown"
            code = match.group(2)
            start = match.start()
            
            structure["sections"].append({
                "type": "code_block",
                "name": f"Code block ({language})",
                "start": start,
                "level": 0,  # Special level for code blocks
                "language": language
            })
        
        # Sort sections by start position
        structure["sections"].sort(key=lambda x: x["start"])
        
        # Determine hierarchy levels
        levels = set()
        for section in structure["sections"]:
            if section["type"].startswith("h"):
                levels.add(section["level"])
        
        structure["hierarchy_levels"] = sorted(list(levels))
        
        return structure
    
    def _analyze_text_structure(self, document: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the structure of plain text.
        
        Args:
            document: Text document to analyze
            structure: Initial structure dictionary
        
        Returns:
            Updated structure dictionary
        """
        # Split by paragraphs (double newlines)
        paragraphs = re.split(r'\n\s*\n', document)
        
        current_pos = 0
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                # Try to detect if this is a heading
                is_heading = False
                if len(paragraph.strip().split('\n')) == 1:  # Single line
                    if paragraph.strip().isupper():  # ALL CAPS
                        is_heading = True
                        level = 1
                    elif re.match(r'^\d+\.\s+\w+', paragraph.strip()):  # Numbered
                        is_heading = True
                        level = 2
                    elif len(paragraph.strip()) < 100 and paragraph.strip().endswith(':'):  # Short and ends with colon
                        is_heading = True
                        level = 3
                
                section_type = "heading" if is_heading else "paragraph"
                section_level = level if is_heading else 0
                
                structure["sections"].append({
                    "type": section_type,
                    "name": paragraph.strip()[:50] + ('...' if len(paragraph.strip()) > 50 else ''),
                    "start": current_pos,
                    "level": section_level
                })
            
            current_pos += len(paragraph) + 2  # +2 for the double newline
        
        # Determine hierarchy levels
        levels = set()
        for section in structure["sections"]:
            if section["type"] == "heading":
                levels.add(section["level"])
        
        structure["hierarchy_levels"] = sorted(list(levels))
        
        return structure
    
    def _create_hierarchical_representation(self, document: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a hierarchical representation of a document.
        
        Args:
            document: Document to process
            structure: Document structure information
        
        Returns:
            Hierarchical representation of the document
        """
        hierarchical_chunks = {
            "type": structure["type"],
            "chunks": [],
            "hierarchy": []
        }
        
        if "language" in structure:
            hierarchical_chunks["language"] = structure["language"]
        
        # Add document sections to hierarchy
        sections = structure["sections"]
        
        # If no sections were detected, create chunks based on size
        if not sections:
            chunks = self._chunk_by_size(document, self.max_chunk_size, self.overlap)
            for i, chunk in enumerate(chunks):
                hierarchical_chunks["chunks"].append({
                    "id": f"chunk_{i}",
                    "content": chunk,
                    "level": 0,
                    "type": "text"
                })
            
            # Create a flat hierarchy
            hierarchical_chunks["hierarchy"] = [{
                "id": "root",
                "name": "Document",
                "level": 0,
                "children": [f"chunk_{i}" for i in range(len(chunks))]
            }]
        
        else:
            # Process sections into chunks
            for i in range(len(sections)):
                section = sections[i]
                
                # Determine section end
                if i < len(sections) - 1:
                    end = sections[i + 1]["start"]
                else:
                    end = len(document)
                
                # Extract section content
                content = document[section["start"]:end]
                
                # Create chunks for this section
                if len(content) > self.max_chunk_size:
                    # Section is too large, chunk it
                    sub_chunks = self._chunk_by_size(content, self.max_chunk_size, self.overlap)
                    
                    section_chunks = []
                    for j, sub_chunk in enumerate(sub_chunks):
                        chunk_id = f"section_{i}_chunk_{j}"
                        hierarchical_chunks["chunks"].append({
                            "id": chunk_id,
                            "content": sub_chunk,
                            "level": section["level"],
                            "type": section["type"],
                            "parent_section": i
                        })
                        section_chunks.append(chunk_id)
                    
                    # Add section to hierarchy
                    hierarchical_chunks["hierarchy"].append({
                        "id": f"section_{i}",
                        "name": section.get("name", f"Section {i}"),
                        "level": section["level"],
                        "type": section["type"],
                        "children": section_chunks
                    })
                
                else:
                    # Section fits in a single chunk
                    chunk_id = f"section_{i}"
                    hierarchical_chunks["chunks"].append({
                        "id": chunk_id,
                        "content": content,
                        "level": section["level"],
                        "type": section["type"]
                    })
                    
                    # Add section to hierarchy
                    hierarchical_chunks["hierarchy"].append({
                        "id": chunk_id,
                        "name": section.get("name", f"Section {i}"),
                        "level": section["level"],
                        "type": section["type"],
                        "children": []
                    })
            
            # Build the hierarchy tree
            if self.preserve_hierarchy and structure["hierarchy_levels"]:
                hierarchical_chunks["hierarchy"] = self._build_hierarchy_tree(hierarchical_chunks["hierarchy"])
        
        return hierarchical_chunks
    
    def _chunk_by_size(self, text: str, max_size: int, overlap: int) -> List[str]:
        """
        Chunk text by size with overlap.
        
        Args:
            text: Text to chunk
            max_size: Maximum chunk size
            overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        # Simple chunking by characters with overlap
        chunks = []
        
        for i in range(0, len(text), max_size - overlap):
            chunk = text[i:i + max_size]
            chunks.append(chunk)
        
        return chunks
    
    def _build_hierarchy_tree(self, flat_hierarchy: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build a hierarchical tree from a flat list of sections.
        
        Args:
            flat_hierarchy: Flat list of hierarchy sections
        
        Returns:
            Hierarchical tree structure
        """
        # Sort by level and then by position in the document
        sorted_hierarchy = sorted(flat_hierarchy, key=lambda x: (x["level"], flat_hierarchy.index(x)))
        
        # Find root level (minimum level)
        min_level = min(section["level"] for section in sorted_hierarchy if "level" in section)
        
        # Create root nodes (sections at the minimum level)
        root_nodes = [section for section in sorted_hierarchy if section.get("level") == min_level]
        
        # Process each level
        for level in range(min_level + 1, max(section.get("level", min_level) for section in sorted_hierarchy) + 1):
            level_sections = [section for section in sorted_hierarchy if section.get("level") == level]
            
            for section in level_sections:
                # Find parent section (closest previous section with lower level)
                parent = None
                for potential_parent in reversed(sorted_hierarchy[:sorted_hierarchy.index(section)]):
                    if potential_parent.get("level", 0) < section["level"]:
                        parent = potential_parent
                        break
                
                if parent:
                    # Add this section as a child of the parent
                    if "children" not in parent:
                        parent["children"] = []
                    
                    # If this section has children, keep them
                    if "children" not in section:
                        section["children"] = []
                    
                    parent["children"].append(section)
                    
                    # Remove this section from the root level
                    if section in root_nodes:
                        root_nodes.remove(section)
        
        return root_nodes
    
    def navigate_hierarchy(self, hierarchical_chunks: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """
        Navigate the hierarchy to find relevant sections for a query.
        
        Args:
            hierarchical_chunks: Hierarchical representation of a document
            query: Query to search for
        
        Returns:
            List of relevant chunks with their context
        """
        # Identify relevant sections based on the query
        relevant_sections = self._identify_relevant_sections(hierarchical_chunks, query)
        
        # Retrieve chunks with context
        chunks_with_context = self._retrieve_with_context(hierarchical_chunks, relevant_sections)
        
        return chunks_with_context
    
    def _identify_relevant_sections(self, hierarchical_chunks: Dict[str, Any], query: str) -> List[str]:
        """
        Identify relevant sections based on a query.
        
        Args:
            hierarchical_chunks: Hierarchical representation of a document
            query: Query to search for
        
        Returns:
            List of relevant section IDs
        """
        # Simple keyword matching for now
        keywords = query.lower().split()
        relevant_section_ids = []
        
        # Check each chunk for relevance
        for chunk in hierarchical_chunks["chunks"]:
            content = chunk["content"].lower()
            
            # Count keyword matches
            match_count = sum(1 for keyword in keywords if keyword in content)
            
            if match_count > 0:
                relevant_section_ids.append(chunk["id"])
        
        return relevant_section_ids
    
    def _retrieve_with_context(self, hierarchical_chunks: Dict[str, Any], relevant_section_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve chunks with their context.
        
        Args:
            hierarchical_chunks: Hierarchical representation of a document
            relevant_section_ids: List of relevant section IDs
        
        Returns:
            List of chunks with context
        """
        chunks_with_context = []
        
        # Create a mapping from chunk ID to chunk
        chunk_map = {chunk["id"]: chunk for chunk in hierarchical_chunks["chunks"]}
        
        # Process each relevant section
        for section_id in relevant_section_ids:
            # Get the chunk
            if section_id in chunk_map:
                chunk = chunk_map[section_id]
                
                # Find parent sections for context
                parent_sections = self._find_parent_sections(hierarchical_chunks["hierarchy"], section_id)
                
                # Add chunk with context
                chunks_with_context.append({
                    "chunk": chunk,
                    "context": {
                        "parent_sections": parent_sections
                    }
                })
        
        return chunks_with_context
    
    def _find_parent_sections(self, hierarchy: List[Dict[str, Any]], section_id: str) -> List[Dict[str, Any]]:
        """
        Find parent sections for a given section ID.
        
        Args:
            hierarchy: Hierarchy structure
            section_id: Section ID to find parents for
        
        Returns:
            List of parent sections
        """
        parent_sections = []
        
        def search_hierarchy(nodes, current_path):
            for node in nodes:
                # Check if this node is the target
                if node["id"] == section_id:
                    return current_path + [node], True
                
                # Check children if any
                if "children" in node and node["children"]:
                    if isinstance(node["children"], list) and all(isinstance(child, str) for child in node["children"]):
                        # Children are IDs
                        if section_id in node["children"]:
                            return current_path + [node], True
                    else:
                        # Children are nodes
                        result, found = search_hierarchy(node["children"], current_path + [node])
                        if found:
                            return result, True
            
            return current_path, False
        
        path, found = search_hierarchy(hierarchy, [])
        
        if found:
            # Return all but the last node (which is the target)
            parent_sections = path[:-1]
        
        return parent_sections
