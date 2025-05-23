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


"""Knowledge Integration Layer for processing certification content.

This module provides functionality for processing and integrating certification
content into the knowledge base for agent training."""

from typing import Dict, Any, List, Optional
import logging
import os
import json
import uuid
import re
import shutil
import datetime
import hashlib

logger = logging.getLogger(__name__)

class KnowledgeIntegrationLayer:
    """Knowledge Integration Layer for processing certification content.
    
    This class provides functionality for processing various types of certification
    content (PDF, Markdown, JSON, etc.) and integrating it into a structured
    knowledge base for agent training."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Knowledge Integration Layer.
        
        Args:
            config: Configuration settings"""
        self.config = config or {}
        
        # Set knowledge base path
        self.knowledge_base_path = self.config.get("knowledge_base_path", "data/knowledge_base")
        
        # Ensure knowledge base directory exists
        os.makedirs(self.knowledge_base_path, exist_ok=True)
        
        logger.info(f"Knowledge Integration Layer initialized with knowledge base at {self.knowledge_base_path}")
    
    def process_certification_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process certification content and integrate it into the knowledge base.
        
        Args:
            params: Processing parameters including content_path, certification_name, and role
            
        Returns:
            Processing result"""
        content_path = params.get("content_path")
        certification_name = params.get("certification_name")
        role = params.get("role")
        
        if not content_path:
            return {
                "success": False,
                "message": "Content path is required"
            }
        
        if not certification_name:
            return {
                "success": False,
                "message": "Certification name is required"
            }
        
        if not role:
            return {
                "success": False,
                "message": "Role is required"
            }
        
        # Determine content type and process accordingly
        content_type = self._determine_content_type(content_path)
        
        if content_type == "directory":
            result = self._process_directory(content_path, certification_name, role)
        elif content_type == "pdf":
            result = self._process_pdf(content_path, certification_name, role)
        elif content_type == "markdown":
            result = self._process_markdown(content_path, certification_name, role)
        elif content_type == "json":
            result = self._process_json(content_path, certification_name, role)
        elif content_type == "csv":
            result = self._process_csv(content_path, certification_name, role)
        else:
            return {
                "success": False,
                "message": f"Unsupported content type: {content_type}"
            }
        
        if result["success"]:
            # Generate content ID
            content_id = self._generate_content_id(certification_name, role)
            
            # Update content registry
            self._save_content_registry(content_id, {
                "certification_name": certification_name,
                "role": role,
                "content_path": content_path,
                "processed_at": datetime.datetime.now().isoformat(),
                "content_type": content_type,
                "chunks": result.get("chunks", [])
            })
            
            logger.info(f"Processed {content_type} content for {certification_name} ({role})")
            
            return {
                "success": True,
                "message": f"Successfully processed {content_type} content",
                "content_id": content_id,
                "content_type": content_type,
                "chunks": len(result.get("chunks", []))
            }
        else:
            return result
    
    def _determine_content_type(self, content_path: str) -> str:
        """Determine the type of content based on the path.
        
        Args:
            content_path: Path to the content
            
        Returns:
            Content type"""
        if os.path.isdir(content_path):
            return "directory"
        
        _, ext = os.path.splitext(content_path)
        ext = ext.lower()
        
        if ext == ".pdf":
            return "pdf"
        elif ext in [".md", ".markdown"]:
            return "markdown"
        elif ext == ".json":
            return "json"
        elif ext in [".csv", ".tsv"]:
            return "csv"
        else:
            return "unknown"
    
    def _process_directory(self, directory_path: str, certification_name: str, role: str) -> Dict[str, Any]:
        """Process a directory of certification content.
        
        Args:
            directory_path: Path to the directory
            certification_name: Name of the certification
            role: Agent role
            
        Returns:
            Processing result"""
        if not os.path.isdir(directory_path):
            return {
                "success": False,
                "message": f"Directory not found: {directory_path}"
            }
        
        # Create role and certification directories in knowledge base
        role_dir = os.path.join(self.knowledge_base_path, role)
        cert_dir = os.path.join(role_dir, self._sanitize_filename(certification_name))
        
        os.makedirs(role_dir, exist_ok=True)
        os.makedirs(cert_dir, exist_ok=True)
        
        # Process all files in the directory
        all_chunks = []
        processed_files = 0
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                content_type = self._determine_content_type(file_path)
                
                if content_type in ["pdf", "markdown", "json", "csv"]:
                    # Process the file
                    if content_type == "pdf":
                        result = self._process_pdf(file_path, certification_name, role)
                    elif content_type == "markdown":
                        result = self._process_markdown(file_path, certification_name, role)
                    elif content_type == "json":
                        result = self._process_json(file_path, certification_name, role)
                    elif content_type == "csv":
                        result = self._process_csv(file_path, certification_name, role)
                    
                    if result["success"]:
                        all_chunks.extend(result.get("chunks", []))
                        processed_files += 1
        
        if processed_files == 0:
            return {
                "success": False,
                "message": f"No supported files found in directory: {directory_path}"
            }
        
        return {
            "success": True,
            "message": f"Processed {processed_files} files from directory",
            "chunks": all_chunks
        }
    
    def _process_pdf(self, pdf_path: str, certification_name: str, role: str) -> Dict[str, Any]:
        """Process a PDF certification content.
        
        Args:
            pdf_path: Path to the PDF file
            certification_name: Name of the certification
            role: Agent role
            
        Returns:
            Processing result"""
        try:
            # In a real implementation, this would use a PDF processing library
            # For now, return a simulated result
            
            # Create role and certification directories in knowledge base
            role_dir = os.path.join(self.knowledge_base_path, role)
            cert_dir = os.path.join(role_dir, self._sanitize_filename(certification_name))
            
            os.makedirs(role_dir, exist_ok=True)
            os.makedirs(cert_dir, exist_ok=True)
            
            # Generate chunks (simulated)
            chunks = []
            
            for i in range(10):
                chunk_id = f"pdf_chunk_{i}_{uuid.uuid4().hex[:8]}"
                chunk_path = os.path.join(cert_dir, f"{chunk_id}.json")
                
                # Create simulated chunk content
                chunk_content = {
                    "chunk_id": chunk_id,
                    "source": os.path.basename(pdf_path),
                    "page": i + 1,
                    "content": f"Simulated content from PDF page {i + 1}",
                    "metadata": {
                        "certification": certification_name,
                        "role": role,
                        "content_type": "pdf"
                    }
                }
                
                # Save chunk
                with open(chunk_path, "w") as f:
                    json.dump(chunk_content, f, indent=2)
                
                chunks.append(chunk_id)
            
            return {
                "success": True,
                "message": f"Processed PDF: {pdf_path}",
                "chunks": chunks
            }
        
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing PDF: {str(e)}"
            }
    
    def _process_markdown(self, markdown_path: str, certification_name: str, role: str) -> Dict[str, Any]:
        """Process a Markdown certification content.
        
        Args:
            markdown_path: Path to the Markdown file
            certification_name: Name of the certification
            role: Agent role
            
        Returns:
            Processing result"""
        try:
            # Create role and certification directories in knowledge base
            role_dir = os.path.join(self.knowledge_base_path, role)
            cert_dir = os.path.join(role_dir, self._sanitize_filename(certification_name))
            
            os.makedirs(role_dir, exist_ok=True)
            os.makedirs(cert_dir, exist_ok=True)
            
            # Read markdown content
            with open(markdown_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Split content into chunks
            chunks = self._split_markdown_into_chunks(content)
            chunk_ids = []
            
            # Save chunks
            for i, chunk in enumerate(chunks):
                chunk_id = f"md_chunk_{i}_{uuid.uuid4().hex[:8]}"
                chunk_path = os.path.join(cert_dir, f"{chunk_id}.json")
                
                # Create chunk content
                chunk_content = {
                    "chunk_id": chunk_id,
                    "source": os.path.basename(markdown_path),
                    "index": i,
                    "content": chunk,
                    "metadata": {
                        "certification": certification_name,
                        "role": role,
                        "content_type": "markdown"
                    }
                }
                
                # Save chunk
                with open(chunk_path, "w") as f:
                    json.dump(chunk_content, f, indent=2)
                
                chunk_ids.append(chunk_id)
            
            return {
                "success": True,
                "message": f"Processed Markdown: {markdown_path}",
                "chunks": chunk_ids
            }
        
        except Exception as e:
            logger.error(f"Error processing Markdown: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing Markdown: {str(e)}"
            }
    
    def _process_json(self, json_path: str, certification_name: str, role: str) -> Dict[str, Any]:
        """Process a JSON certification content.
        
        Args:
            json_path: Path to the JSON file
            certification_name: Name of the certification
            role: Agent role
            
        Returns:
            Processing result"""
        try:
            # Create role and certification directories in knowledge base
            role_dir = os.path.join(self.knowledge_base_path, role)
            cert_dir = os.path.join(role_dir, self._sanitize_filename(certification_name))
            
            os.makedirs(role_dir, exist_ok=True)
            os.makedirs(cert_dir, exist_ok=True)
            
            # Read JSON content
            with open(json_path, "r", encoding="utf-8") as f:
                content = json.load(f)
            
            # Process JSON content based on structure
            return self._process_module_json(content, json_path, certification_name, role, cert_dir)
        
        except Exception as e:
            logger.error(f"Error processing JSON: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing JSON: {str(e)}"
            }
    
    def _process_csv(self, csv_path: str, certification_name: str, role: str) -> Dict[str, Any]:
        """Process a CSV certification content.
        
        Args:
            csv_path: Path to the CSV file
            certification_name: Name of the certification
            role: Agent role
            
        Returns:
            Processing result"""
        try:
            # In a real implementation, this would use a CSV processing library
            # For now, return a simulated result
            
            # Create role and certification directories in knowledge base
            role_dir = os.path.join(self.knowledge_base_path, role)
            cert_dir = os.path.join(role_dir, self._sanitize_filename(certification_name))
            
            os.makedirs(role_dir, exist_ok=True)
            os.makedirs(cert_dir, exist_ok=True)
            
            # Generate chunks (simulated)
            chunks = []
            
            for i in range(5):
                chunk_id = f"csv_chunk_{i}_{uuid.uuid4().hex[:8]}"
                chunk_path = os.path.join(cert_dir, f"{chunk_id}.json")
                
                # Create simulated chunk content
                chunk_content = {
                    "chunk_id": chunk_id,
                    "source": os.path.basename(csv_path),
                    "row_range": f"{i*10+1}-{(i+1)*10}",
                    "content": f"Simulated content from CSV rows {i*10+1}-{(i+1)*10}",
                    "metadata": {
                        "certification": certification_name,
                        "role": role,
                        "content_type": "csv"
                    }
                }
                
                # Save chunk
                with open(chunk_path, "w") as f:
                    json.dump(chunk_content, f, indent=2)
                
                chunks.append(chunk_id)
            
            return {
                "success": True,
                "message": f"Processed CSV: {csv_path}",
                "chunks": chunks
            }
        
        except Exception as e:
            logger.error(f"Error processing CSV: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing CSV: {str(e)}"
            }
    
    def _split_markdown_into_chunks(self, content: str) -> List[str]:
        """Split markdown content into chunks.
        
        Args:
            content: Markdown content
            
        Returns:
            List of content chunks"""
        # Split by headers
        header_pattern = r'^#{1,3}\s+.+$'
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        
        for line in lines:
            if re.match(header_pattern, line) and current_chunk:
                # New header, save current chunk and start a new one
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
            else:
                current_chunk.append(line)
        
        # Add the last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        # If no headers were found, split by paragraphs
        if len(chunks) <= 1:
            chunks = re.split(r'\n\s*\n', content)
        
        # Ensure chunks aren't too large
        max_chunk_size = 1000  # characters
        result_chunks = []
        
        for chunk in chunks:
            if len(chunk) <= max_chunk_size:
                result_chunks.append(chunk)
            else:
                # Split large chunks by paragraphs
                paragraphs = re.split(r'\n\s*\n', chunk)
                current_chunk = []
                current_size = 0
                
                for para in paragraphs:
                    if current_size + len(para) <= max_chunk_size:
                        current_chunk.append(para)
                        current_size += len(para)
                    else:
                        if current_chunk:
                            result_chunks.append('\n\n'.join(current_chunk))
                        current_chunk = [para]
                        current_size = len(para)
                
                if current_chunk:
                    result_chunks.append('\n\n'.join(current_chunk))
        
        return result_chunks
    
    def _process_module_json(
        self, content: Dict[str, Any], json_path: str, certification_name: str, role: str, cert_dir: str
    ) -> Dict[str, Any]:
        """Process a module JSON content.
        
        Args:
            content: JSON content
            json_path: Path to the JSON file
            certification_name: Name of the certification
            role: Agent role
            cert_dir: Certification directory
            
        Returns:
            Processing result"""
        chunk_ids = []
        
        # Check if content has a standard structure
        if "name" in content and "sections" in content:
            # Process as a module with sections
            module_name = content["name"]
            sections = content["sections"]
            
            for i, section in enumerate(sections):
                section_name = section.get("name", f"Section {i+1}")
                section_content = section.get("content", "")
                
                chunk_id = f"json_section_{i}_{uuid.uuid4().hex[:8]}"
                chunk_path = os.path.join(cert_dir, f"{chunk_id}.json")
                
                # Create chunk content
                chunk_content = {
                    "chunk_id": chunk_id,
                    "source": os.path.basename(json_path),
                    "module": module_name,
                    "section": section_name,
                    "content": section_content,
                    "metadata": {
                        "certification": certification_name,
                        "role": role,
                        "content_type": "json",
                        "module_index": i
                    }
                }
                
                # Add additional metadata if available
                for key, value in section.items():
                    if key not in ["name", "content"]:
                        chunk_content["metadata"][key] = value
                
                # Save chunk
                with open(chunk_path, "w") as f:
                    json.dump(chunk_content, f, indent=2)
                
                chunk_ids.append(chunk_id)
        
        else:
            # Process as a generic JSON
            chunk_id = f"json_generic_{uuid.uuid4().hex[:8]}"
            chunk_path = os.path.join(cert_dir, f"{chunk_id}.json")
            
            # Create chunk content
            chunk_content = {
                "chunk_id": chunk_id,
                "source": os.path.basename(json_path),
                "content": json.dumps(content),
                "metadata": {
                    "certification": certification_name,
                    "role": role,
                    "content_type": "json"
                }
            }
            
            # Save chunk
            with open(chunk_path, "w") as f:
                json.dump(chunk_content, f, indent=2)
            
            chunk_ids.append(chunk_id)
        
        return {
            "success": True,
            "message": f"Processed JSON: {json_path}",
            "chunks": chunk_ids
        }
    
    def _generate_content_id(self, certification_name: str, role: str) -> str:
        """Generate a unique content ID.
        
        Args:
            certification_name: Name of the certification
            role: Agent role
            
        Returns:
            Content ID"""
        timestamp = datetime.datetime.now().isoformat()
        unique_string = f"{certification_name}_{role}_{timestamp}_{uuid.uuid4().hex}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _save_content_registry(self, content_id: str, metadata: Dict[str, Any]) -> None:
        """Save content metadata to the registry.
        
        Args:
            content_id: Content ID
            metadata: Content metadata"""
        registry_path = os.path.join(self.knowledge_base_path, "content_registry.json")
        
        # Load existing registry
        registry = self._load_content_registry()
        
        # Add new content
        registry[content_id] = metadata
        
        # Save registry
        with open(registry_path, "w") as f:
            json.dump(registry, f, indent=2)
    
    def _load_content_registry(self) -> Dict[str, Any]:
        """Load the content registry.
        
        Returns:
            Content registry"""
        registry_path = os.path.join(self.knowledge_base_path, "content_registry.json")
        
        if os.path.exists(registry_path):
            try:
                with open(registry_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading content registry: {str(e)}")
                return {}
        else:
            return {}
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a name for use as a filename.
        
        Args:
            name: Name to sanitize
            
        Returns:
            Sanitized name"""
        # Replace spaces with underscores
        name = name.replace(" ", "_")
        
        # Remove special characters
        name = re.sub(r"[^\w\-]", "", name)
        
        # Ensure name is not too long
        if len(name) > 64:
            name = name[:64]
        
        return name
