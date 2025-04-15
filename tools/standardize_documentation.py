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

"""
Documentation Standardization Script

This script standardizes documentation across the codebase by updating docstrings
to follow the project's documentation style guide. It processes Python files
in the specified directory and its subdirectories, updating docstrings to match
the standardized format.

Example:
    $ python standardize_documentation.py --dir /path/to/codebase

Note:
    This script is non-destructive and creates backup files before making changes.
"""

import os
import re
import argparse
import ast
import astor
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocstringStandardizer:
    """
    Standardizes docstrings in Python files to follow the project's documentation style guide.
    
    This class parses Python files, identifies docstrings, and updates them to follow
    the standardized format defined in the documentation style guide.
    
    Attributes:
        style_guide (dict): Configuration for docstring style
        processed_files (int): Number of files processed
        updated_files (int): Number of files updated
        skipped_files (int): Number of files skipped
    
    Example:
        >>> standardizer = DocstringStandardizer()
        >>> standardizer.process_directory("/path/to/codebase")
        >>> print(f"Processed {standardizer.processed_files} files")
        >>> print(f"Updated {standardizer.updated_files} files")
    """
    
    def __init__(self):
        """
        Initialize the DocstringStandardizer with default style guide settings.
        """
        self.style_guide = {
            'module': {
                'required_sections': ['Description'],
                'optional_sections': ['Important', 'Example', 'Dependencies']
            },
            'class': {
                'required_sections': ['Description'],
                'optional_sections': ['Attributes', 'Example', 'Note']
            },
            'function': {
                'required_sections': ['Description', 'Args', 'Returns'],
                'optional_sections': ['Raises', 'Example', 'Note']
            }
        }
        self.processed_files = 0
        self.updated_files = 0
        self.skipped_files = 0
    
    def process_directory(self, directory: str) -> None:
        """
        Process all Python files in the specified directory and its subdirectories.
        
        Args:
            directory (str): Path to the directory to process
        
        Raises:
            FileNotFoundError: If the directory does not exist
            PermissionError: If the directory cannot be accessed
        """
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        logger.info(f"Processing directory: {directory}")
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        self.process_file(file_path)
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {str(e)}")
                        self.skipped_files += 1
        
        logger.info(f"Processed {self.processed_files} files")
        logger.info(f"Updated {self.updated_files} files")
        logger.info(f"Skipped {self.skipped_files} files")
    
    def process_file(self, file_path: str) -> None:
        """
        Process a single Python file to standardize its docstrings.
        
        Args:
            file_path (str): Path to the Python file to process
        
        Raises:
            FileNotFoundError: If the file does not exist
            SyntaxError: If the file contains invalid Python syntax
        """
        logger.info(f"Processing file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {str(e)}")
            self.skipped_files += 1
            return
        
        # Create a visitor to find and update docstrings
        visitor = DocstringVisitor(content, self.style_guide)
        visitor.visit(tree)
        
        self.processed_files += 1
        
        # If docstrings were updated, write the changes
        if visitor.updated:
            # Create backup
            backup_path = f"{file_path}.bak"
            shutil.copy2(file_path, backup_path)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(visitor.updated_content)
            
            self.updated_files += 1
            logger.info(f"Updated docstrings in {file_path}")
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the standardization process.
        
        Returns:
            Dict[str, int]: Dictionary containing statistics:
                - processed_files: Number of files processed
                - updated_files: Number of files updated
                - skipped_files: Number of files skipped
        """
        return {
            'processed_files': self.processed_files,
            'updated_files': self.updated_files,
            'skipped_files': self.skipped_files
        }

class DocstringVisitor(ast.NodeVisitor):
    """
    AST visitor that finds and updates docstrings in Python files.
    
    This visitor traverses the AST of a Python file, identifies docstrings,
    and updates them to follow the standardized format.
    
    Attributes:
        content (str): Original content of the file
        style_guide (dict): Configuration for docstring style
        updated (bool): Whether any docstrings were updated
        updated_content (str): Updated content of the file
    """
    
    def __init__(self, content: str, style_guide: Dict[str, Any]):
        """
        Initialize the DocstringVisitor.
        
        Args:
            content (str): Original content of the file
            style_guide (dict): Configuration for docstring style
        """
        self.content = content
        self.style_guide = style_guide
        self.updated = False
        self.updated_content = content
        self.replacements = []
    
    def visit_Module(self, node: ast.Module) -> None:
        """
        Visit a module node to process its docstring.
        
        Args:
            node (ast.Module): The module node to visit
        """
        # Check for module docstring
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            docstring = node.body[0].value.s
            standardized = self.standardize_docstring(docstring, 'module')
            
            if standardized != docstring:
                self.replacements.append((
                    self._get_docstring_start_end(node.body[0]),
                    standardized
                ))
        
        # Continue visiting other nodes
        self.generic_visit(node)
        
        # Apply all replacements at once
        if self.replacements:
            self.updated = True
            self.updated_content = self._apply_replacements()
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Visit a class definition node to process its docstring.
        
        Args:
            node (ast.ClassDef): The class definition node to visit
        """
        # Check for class docstring
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            docstring = node.body[0].value.s
            standardized = self.standardize_docstring(docstring, 'class')
            
            if standardized != docstring:
                self.replacements.append((
                    self._get_docstring_start_end(node.body[0]),
                    standardized
                ))
        
        # Continue visiting other nodes
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Visit a function definition node to process its docstring.
        
        Args:
            node (ast.FunctionDef): The function definition node to visit
        """
        # Check for function docstring
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            docstring = node.body[0].value.s
            standardized = self.standardize_docstring(docstring, 'function')
            
            if standardized != docstring:
                self.replacements.append((
                    self._get_docstring_start_end(node.body[0]),
                    standardized
                ))
        
        # Continue visiting other nodes
        self.generic_visit(node)
    
    def _get_docstring_start_end(self, node: ast.Expr) -> Tuple[int, int]:
        """
        Get the start and end positions of a docstring in the source code.
        
        Args:
            node (ast.Expr): The expression node containing the docstring
        
        Returns:
            Tuple[int, int]: Start and end positions of the docstring
        """
        start_lineno = node.lineno
        end_lineno = node.end_lineno if hasattr(node, 'end_lineno') else start_lineno
        
        # Find the actual start and end in the source code
        lines = self.content.split('\n')
        
        # Find the start of the docstring (including quotes)
        start_line = lines[start_lineno - 1]
        start_col = node.col_offset
        start_pos = sum(len(line) + 1 for line in lines[:start_lineno - 1]) + start_col
        
        # Find the end of the docstring (including quotes)
        end_line = lines[end_lineno - 1]
        end_col = getattr(node, 'end_col_offset', len(end_line))
        end_pos = sum(len(line) + 1 for line in lines[:end_lineno - 1]) + end_col
        
        return (start_pos, end_pos)
    
    def _apply_replacements(self) -> str:
        """
        Apply all docstring replacements to the content.
        
        Returns:
            str: Updated content with standardized docstrings
        """
        # Sort replacements in reverse order to avoid position shifts
        self.replacements.sort(key=lambda x: x[0][0], reverse=True)
        
        content = self.content
        for (start, end), replacement in self.replacements:
            # Format the replacement with proper quotes
            if '"""' in replacement:
                formatted = f"'''{replacement}'''"
            else:
                formatted = f'"""{replacement}"""'
            
            content = content[:start] + formatted + content[end:]
        
        return content
    
    def standardize_docstring(self, docstring: str, node_type: str) -> str:
        """
        Standardize a docstring according to the style guide.
        
        Args:
            docstring (str): The original docstring
            node_type (str): Type of node ('module', 'class', or 'function')
        
        Returns:
            str: Standardized docstring
        """
        # Remove quotes
        docstring = docstring.strip('\'\"')
        
        # Parse the docstring into sections
        sections = self._parse_docstring_sections(docstring)
        
        # Ensure required sections exist
        for section in self.style_guide[node_type]['required_sections']:
            if section not in sections:
                sections[section] = ""
        
        # Format the docstring
        result = []
        
        # Add description (always first)
        if 'Description' in sections:
            result.append(sections['Description'].strip())
        
        # Add other sections
        for section, content in sections.items():
            if section != 'Description' and content:
                # Use string concatenation instead of f-strings with backslashes
                section_text = "\n" + section + ":\n    "
                content_text = content.strip().replace("\n", "\n    ")
                result.append(section_text + content_text)
        
        return "\n".join(result)
    
    def _parse_docstring_sections(self, docstring: str) -> Dict[str, str]:
        """
        Parse a docstring into sections.
        
        Args:
            docstring (str): The docstring to parse
        
        Returns:
            Dict[str, str]: Dictionary mapping section names to content
        """
        lines = docstring.strip().split('\n')
        
        # Initialize with description
        sections = {'Description': lines[0] if lines else ""}
        current_section = 'Description'
        
        # Process remaining lines
        for i, line in enumerate(lines[1:], 1):
            # Check if this line starts a new section
            match = re.match(r'^(\w+):\s*$', line)
            if match:
                current_section = match.group(1)
                sections[current_section] = ""
            else:
                # Add to current section
                if current_section in sections:
                    if sections[current_section]:
                        sections[current_section] += '\n'
                    sections[current_section] += line
                else:
                    # If no section is identified, add to description
                    if sections['Description']:
                        sections['Description'] += '\n'
                    sections['Description'] += line
        
        return sections

def main():
    """
    Main entry point for the script.
    
    Parses command-line arguments and runs the docstring standardization process.
    """
    parser = argparse.ArgumentParser(description='Standardize docstrings in Python files')
    parser.add_argument('--dir', type=str, required=True, help='Directory to process')
    args = parser.parse_args()
    
    standardizer = DocstringStandardizer()
    try:
        standardizer.process_directory(args.dir)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
    
    stats = standardizer.get_statistics()
    logger.info(f"Summary: Processed {stats['processed_files']} files, "
                f"Updated {stats['updated_files']} files, "
                f"Skipped {stats['skipped_files']} files")
    
    return 0

if __name__ == "__main__":
    exit(main())
