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

"""Documentation Generation Service for technical capabilities module.

This module provides services for generating documentation based on code files."""

import os
import sys
import logging
import time
from typing import Dict, List, Any, Optional

from ..models.data_models import (
    DocumentationGenerationRequest,
    DocumentationGenerationResult
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentationGenerationService:
    """Service for generating documentation based on code files."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the documentation generation service.
        
        Args:
            config: Configuration settings"""
        self.config = config or {}
        self.templates_dir = self.config.get('templates_dir', 'templates')
        logger.info("Initialized documentation generation service")
    
    async def generate_documentation(self, request: DocumentationGenerationRequest) -> DocumentationGenerationResult:
        """
        Generate documentation based on code files.
        
        Args:
            request: Documentation generation request
            
        Returns:
            Documentation generation result
        """
        logger.info(f"Generating documentation for project: {request.project_id}")
        
        # Generate documentation files
        documentation_files = await self._generate_documentation_files(
            request.files, 
            request.documentation_format,
            request.documentation_level
        )
        
        # Create result
        result = DocumentationGenerationResult(
            project_id=request.project_id,
            documentation_files=documentation_files
        )
        
        logger.info(f"Generated documentation for project: {request.project_id}")
        return result
    
    async def _generate_documentation_files(
        self, 
        files: List[Dict[str, Any]], 
        documentation_format: str,
        documentation_level: str
    ) -> List[Dict[str, Any]]:
        """
        Generate documentation files based on code files.
        
        Args:
            files: List of code files
            documentation_format: Documentation format (e.g., 'markdown', 'html', 'jsdoc')
            documentation_level: Documentation level (e.g., 'basic', 'detailed', 'comprehensive')
            
        Returns:
            List of documentation files
        """
        # In a real implementation, this would generate actual documentation files
        # For now, return mock documentation files
        documentation_files = []
        
        # Generate project-level documentation
        project_doc = await self._generate_project_documentation(
            files, documentation_format, documentation_level
        )
        documentation_files.append(project_doc)
        
        # Generate file-level documentation
        for file in files:
            file_path = file.get('path', '')
            file_content = file.get('content', '')
            
            # Skip non-code files
            if not self._is_documentable_file(file_path):
                continue
            
            # Generate documentation file path
            doc_file_path = self._get_documentation_file_path(file_path, documentation_format)
            
            # Generate documentation file content
            doc_file_content = await self._generate_file_documentation(
                file_path, file_content, documentation_format, documentation_level
            )
            
            documentation_files.append({
                "path": doc_file_path,
                "content": doc_file_content,
                "description": f"Documentation for {file_path}"
            })
        
        return documentation_files
    
    def _is_documentable_file(self, file_path: str) -> bool:
        """Check if a file is documentable.
        
        Args:
            file_path: File path
            
        Returns:
            True if the file is documentable, False otherwise"""
        documentable_extensions = [
            '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cs', '.go', '.rb', '.php',
            '.html', '.css', '.scss', '.less', '.md', '.json', '.yaml', '.yml'
        ]
        return any(file_path.endswith(ext) for ext in documentable_extensions)
    
    def _get_documentation_file_path(self, file_path: str, documentation_format: str) -> str:
        """Get the documentation file path for a code file.
        
        Args:
            file_path: Code file path
            documentation_format: Documentation format
            
        Returns:
            Documentation file path"""
        # Extract file name and extension
        file_name = os.path.basename(file_path)
        file_name_without_ext, _ = os.path.splitext(file_name)
        
        # Get directory
        directory = os.path.dirname(file_path)
        
        # Generate documentation file path based on format
        if documentation_format.lower() == 'markdown':
            return os.path.join(directory, 'docs', f"{file_name_without_ext}.md")
        elif documentation_format.lower() == 'html':
            return os.path.join(directory, 'docs', f"{file_name_without_ext}.html")
        elif documentation_format.lower() == 'jsdoc':
            return os.path.join(directory, 'docs', 'jsdoc', f"{file_name_without_ext}.js")
        else:
            return os.path.join(directory, 'docs', f"{file_name_without_ext}.{documentation_format}")
    
    async def _generate_project_documentation(
        self, 
        files: List[Dict[str, Any]], 
        documentation_format: str,
        documentation_level: str
    ) -> Dict[str, Any]:
        """
        Generate project-level documentation.
        
        Args:
            files: List of code files
            documentation_format: Documentation format
            documentation_level: Documentation level
            
        Returns:
            Project documentation file
        """
        # In a real implementation, this would generate actual project documentation
        # For now, return mock project documentation
        
        # Determine file path based on format
        if documentation_format.lower() == 'markdown':
            file_path = 'docs/README.md'
        elif documentation_format.lower() == 'html':
            file_path = 'docs/index.html'
        else:
            file_path = f'docs/index.{documentation_format}'
        
        # Generate content based on format and level
        if documentation_format.lower() == 'markdown':
            content = self._generate_markdown_project_documentation(files, documentation_level)
        elif documentation_format.lower() == 'html':
            content = self._generate_html_project_documentation(files, documentation_level)
        else:
            content = f"Project Documentation\n\nGenerated with {documentation_format} format at {documentation_level} level."
        
        return {
            "path": file_path,
            "content": content,
            "description": "Project-level documentation"
        }
    
    def _generate_markdown_project_documentation(
        self, files: List[Dict[str, Any]], documentation_level: str
    ) -> str:
        """Generate Markdown project documentation.
        
        Args:
            files: List of code files
            documentation_level: Documentation level
            
        Returns:
            Markdown project documentation"""
        # Count files by type
        file_types = {}
        for file in files:
            file_path = file.get('path', '')
            _, ext = os.path.splitext(file_path)
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
        
        # Generate file type summary
        file_type_summary = "\n".join([f"- {ext}: {count} files" for ext, count in file_types.items()])
        
        # Generate documentation based on level
        if documentation_level.lower() == 'basic':
            return f"""# Project Documentation

## Overview
This project contains {len(files)} files.

## File Types
{file_type_summary}
"""
        elif documentation_level.lower() == 'detailed':
            # Generate file list
            file_list = "\n".join([f"- {file.get('path', '')}" for file in files])
            
            return f"""# Project Documentation

## Overview
This project contains {len(files)} files.

## File Types
{file_type_summary}

## File List
{file_list}
"""
        else:  # comprehensive
            # Generate file list with descriptions
            file_list_with_desc = "\n".join([
                f"- {file.get('path', '')}: {file.get('description', 'No description')}"
                for file in files
            ])
            
            return f"""# Project Documentation

## Overview
This project contains {len(files)} files.

## File Types
{file_type_summary}

## File List
{file_list_with_desc}

## Project Structure
The project is organized into the following directories:
- src/: Source code
- docs/: Documentation
- tests/: Test files

## Getting Started
To get started with this project, follow these steps:
1. Clone the repository
2. Install dependencies
3. Run the application

## Contributing
Contributions are welcome! Please follow the contribution guidelines.
"""
    
    def _generate_html_project_documentation(
        self, files: List[Dict[str, Any]], documentation_level: str
    ) -> str:
        """Generate HTML project documentation.
        
        Args:
            files: List of code files
            documentation_level: Documentation level
            
        Returns:
            HTML project documentation"""
        # Count files by type
        file_types = {}
        for file in files:
            file_path = file.get('path', '')
            _, ext = os.path.splitext(file_path)
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
        
        # Generate file type summary
        file_type_summary = "".join([f"<li>{ext}: {count} files</li>" for ext, count in file_types.items()])
        
        # Generate documentation based on level
        if documentation_level.lower() == 'basic':
            return f"""<!DOCTYPE html>
<html>
<head>
    <title>Project Documentation</title>
</head>
<body>
    <h1>Project Documentation</h1>
    
    <h2>Overview</h2>
    <p>This project contains {len(files)} files.</p>
    
    <h2>File Types</h2>
    <ul>
        {file_type_summary}
    </ul>
</body>
</html>
"""
        elif documentation_level.lower() == 'detailed':
            # Generate file list
            file_list = "".join([f"<li>{file.get('path', '')}</li>" for file in files])
            
            return f"""<!DOCTYPE html>
<html>
<head>
    <title>Project Documentation</title>
</head>
<body>
    <h1>Project Documentation</h1>
    
    <h2>Overview</h2>
    <p>This project contains {len(files)} files.</p>
    
    <h2>File Types</h2>
    <ul>
        {file_type_summary}
    </ul>
    
    <h2>File List</h2>
    <ul>
        {file_list}
    </ul>
</body>
</html>
"""
        else:  # comprehensive
            # Generate file list with descriptions
            file_list_with_desc = "".join([
                f"<li>{file.get('path', '')}: {file.get('description', 'No description')}</li>"
                for file in files
            ])
            
            return f"""<!DOCTYPE html>
<html>
<head>
    <title>Project Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; }}
        ul {{ margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>Project Documentation</h1>
    
    <h2>Overview</h2>
    <p>This project contains {len(files)} files.</p>
    
    <h2>File Types</h2>
    <ul>
        {file_type_summary}
    </ul>
    
    <h2>File List</h2>
    <ul>
        {file_list_with_desc}
    </ul>
    
    <h2>Project Structure</h2>
    <p>The project is organized into the following directories:</p>
    <ul>
        <li>src/: Source code</li>
        <li>docs/: Documentation</li>
        <li>tests/: Test files</li>
    </ul>
    
    <h2>Getting Started</h2>
    <p>To get started with this project, follow these steps:</p>
    <ol>
        <li>Clone the repository</li>
        <li>Install dependencies</li>
        <li>Run the application</li>
    </ol>
    
    <h2>Contributing</h2>
    <p>Contributions are welcome! Please follow the contribution guidelines.</p>
</body>
</html>
"""
    
    async def _generate_file_documentation(
        self, 
        file_path: str, 
        file_content: str, 
        documentation_format: str,
        documentation_level: str
    ) -> str:
        """
        Generate documentation for a specific file.
        
        Args:
            file_path: File path
            file_content: File content
            documentation_format: Documentation format
            documentation_level: Documentation level
            
        Returns:
            File documentation
        """
        # In a real implementation, this would generate actual file documentation
        # For now, return mock documentation based on format and level
        
        # Extract file name and extension
        file_name = os.path.basename(file_path)
        file_name_without_ext, file_ext = os.path.splitext(file_name)
        
        if documentation_format.lower() == 'markdown':
            return self._generate_markdown_file_documentation(
                file_path, file_content, documentation_level
            )
        elif documentation_format.lower() == 'html':
            return self._generate_html_file_documentation(
                file_path, file_content, documentation_level
            )
        elif documentation_format.lower() == 'jsdoc':
            return self._generate_jsdoc_file_documentation(
                file_path, file_content, documentation_level
            )
        else:
            return f"Documentation for {file_path}\nGenerated with {documentation_format} format at {documentation_level} level."
    
    def _generate_markdown_file_documentation(
        self, file_path: str, file_content: str, documentation_level: str
    ) -> str:
        """Generate Markdown file documentation.
        
        Args:
            file_path: File path
            file_content: File content
            documentation_level: Documentation level
            
        Returns:
            Markdown file documentation"""
        # Extract file name
        file_name = os.path.basename(file_path)
        
        # Count lines of code
        lines = file_content.split('\n')
        line_count = len(lines)
        
        # Generate documentation based on level
        if documentation_level.lower() == 'basic':
            return f"""# {file_name}

## Overview
This file contains {line_count} lines of code.
"""
        elif documentation_level.lower() == 'detailed':
            # Extract functions/classes (simplified)
            functions = []
            classes = []
            
            for line in lines:
                if 'function ' in line or 'def ' in line:
                    functions.append(line.strip())
                elif 'class ' in line:
                    classes.append(line.strip())
            
            # Generate function list
            function_list = "\n".join([f"- {func}" for func in functions])
            
            # Generate class list
            class_list = "\n".join([f"- {cls}" for cls in classes])
            
            return f"""# {file_name}

## Overview
This file contains {line_count} lines of code.

## Functions
{function_list if functions else "No functions found."}

## Classes
{class_list if classes else "No classes found."}
"""
        else:  # comprehensive
            # Extract functions/classes with more detail (simplified)
            functions = []
            classes = []
            imports = []
            
            for i, line in enumerate(lines):
                if 'import ' in line or 'from ' in line and 'import' in line:
                    imports.append(line.strip())
                elif 'function ' in line or 'def ' in line:
                    # Get function signature
                    func_signature = line.strip()
                    
                    # Get function description (simplified)
                    func_desc = "No description available."
                    if i > 0 and '/**' in lines[i-1] or '"""' in lines[i-1]:
                        for j in range(i-1, max(0, i-5), -1):
                            if '/**' in lines[j] or '"""' in lines[j]:
                                func_desc = lines[j+1].strip()
                                break
                    
                    functions.append((func_signature, func_desc))
                elif 'class ' in line:
                    # Get class signature
                    class_signature = line.strip()
                    
                    # Get class description (simplified)
                    class_desc = "No description available."
                    if i > 0 and '/**' in lines[i-1] or '"""' in lines[i-1]:
                        for j in range(i-1, max(0, i-5), -1):
                            if '/**' in lines[j] or '"""' in lines[j]:
                                class_desc = lines[j+1].strip()
                                break
                    
                    classes.append((class_signature, class_desc))
            
            # Generate import list
            import_list = "\n".join([f"- {imp}" for imp in imports])
            
            # Generate function list with descriptions
            function_list = "\n".join([
                f"### {func[0]}\n{func[1]}" for func in functions
            ])
            
            # Generate class list with descriptions
            class_list = "\n".join([
                f"### {cls[0]}\n{cls[1]}" for cls in classes
            ])
            
            return f"""# {file_name}

## Overview
This file contains {line_count} lines of code.

## Imports
{import_list if imports else "No imports found."}

## Functions
{function_list if functions else "No functions found."}

## Classes
{class_list if classes else "No classes found."}

## Usage Examples
```
// Example usage of this file
```

## Notes
- This documentation was automatically generated.
- Some details may be missing or incomplete.
"""
    
    def _generate_html_file_documentation(
        self, file_path: str, file_content: str, documentation_level: str
    ) -> str:
        """Generate HTML file documentation.
        
        Args:
            file_path: File path
            file_content: File content
            documentation_level: Documentation level
            
        Returns:
            HTML file documentation"""
        # Extract file name
        file_name = os.path.basename(file_path)
        
        # Count lines of code
        lines = file_content.split('\n')
        line_count = len(lines)
        
        # Generate documentation based on level
        if documentation_level.lower() == 'basic':
            return f"""<!DOCTYPE html>
<html>
<head>
    <title>{file_name} Documentation</title>
</head>
<body>
    <h1>{file_name}</h1>
    
    <h2>Overview</h2>
    <p>This file contains {line_count} lines of code.</p>
</body>
</html>
"""
        elif documentation_level.lower() == 'detailed':
            # Extract functions/classes (simplified)
            functions = []
            classes = []
            
            for line in lines:
                if 'function ' in line or 'def ' in line:
                    functions.append(line.strip())
                elif 'class ' in line:
                    classes.append(line.strip())
            
            # Generate function list
            function_list = "".join([f"<li>{func}</li>" for func in functions])
            
            # Generate class list
            class_list = "".join([f"<li>{cls}</li>" for cls in classes])
            
            return f"""<!DOCTYPE html>
<html>
<head>
    <title>{file_name} Documentation</title>
</head>
<body>
    <h1>{file_name}</h1>
    
    <h2>Overview</h2>
    <p>This file contains {line_count} lines of code.</p>
    
    <h2>Functions</h2>
    <ul>
        {function_list if functions else "<li>No functions found.</li>"}
    </ul>
    
    <h2>Classes</h2>
    <ul>
        {class_list if classes else "<li>No classes found.</li>"}
    </ul>
</body>
</html>
"""
        else:  # comprehensive
            # Extract functions/classes with more detail (simplified)
            functions = []
            classes = []
            imports = []
            
            for i, line in enumerate(lines):
                if 'import ' in line or 'from ' in line and 'import' in line:
                    imports.append(line.strip())
                elif 'function ' in line or 'def ' in line:
                    # Get function signature
                    func_signature = line.strip()
                    
                    # Get function description (simplified)
                    func_desc = "No description available."
                    if i > 0 and '/**' in lines[i-1] or '"""' in lines[i-1]:
                        for j in range(i-1, max(0, i-5), -1):
                            if '/**' in lines[j] or '"""' in lines[j]:
                                func_desc = lines[j+1].strip()
                                break
                    
                    functions.append((func_signature, func_desc))
                elif 'class ' in line:
                    # Get class signature
                    class_signature = line.strip()
                    
                    # Get class description (simplified)
                    class_desc = "No description available."
                    if i > 0 and '/**' in lines[i-1] or '"""' in lines[i-1]:
                        for j in range(i-1, max(0, i-5), -1):
                            if '/**' in lines[j] or '"""' in lines[j]:
                                class_desc = lines[j+1].strip()
                                break
                    
                    classes.append((class_signature, class_desc))
            
            # Generate import list
            import_list = "".join([f"<li>{imp}</li>" for imp in imports])
            
            # Generate function list with descriptions
            function_list = "".join([
                f"<h3>{func[0]}</h3><p>{func[1]}</p>" for func in functions
            ])
            
            # Generate class list with descriptions
            class_list = "".join([
                f"<h3>{cls[0]}</h3><p>{cls[1]}</p>" for cls in classes
            ])
            
            return f"""<!DOCTYPE html>
<html>
<head>
    <title>{file_name} Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; }}
        h3 {{ color: #999; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>{file_name}</h1>
    
    <h2>Overview</h2>
    <p>This file contains {line_count} lines of code.</p>
    
    <h2>Imports</h2>
    <ul>
        {import_list if imports else "<li>No imports found.</li>"}
    </ul>
    
    <h2>Functions</h2>
    {function_list if functions else "<p>No functions found.</p>"}
    
    <h2>Classes</h2>
    {class_list if classes else "<p>No classes found.</p>"}
    
    <h2>Usage Examples</h2>
    <pre>
// Example usage of this file
    </pre>
    
    <h2>Notes</h2>
    <ul>
        <li>This documentation was automatically generated.</li>
        <li>Some details may be missing or incomplete.</li>
    </ul>
</body>
</html>
"""
    
    def _generate_jsdoc_file_documentation(
        self, file_path: str, file_content: str, documentation_level: str
    ) -> str:
        """Generate JSDoc file documentation.
        
        Args:
            file_path: File path
            file_content: File content
            documentation_level: Documentation level
            
        Returns:
            JSDoc file documentation"""
        # Extract file name
        file_name = os.path.basename(file_path)
        
        # Generate documentation based on level
        if documentation_level.lower() == 'basic':
            return f"""/**
 * @file {file_name}
 * @description A file in the project.
 */
"""
        elif documentation_level.lower() == 'detailed':
            return f"""/**
 * @file {file_name}
 * @description A file in the project.
 * @module {os.path.dirname(file_path).replace('/', '.')}
 */
"""
        else:  # comprehensive
            return f"""/**
 * @file {file_name}
 * @description A file in the project.
 * @module {os.path.dirname(file_path).replace('/', '.')}
 * @requires module:some-dependency
 * @author TORONTO AI Team Agent
 * @copyright 2025 TORONTO AI
 */

/**
 * Example function documentation
 * @function exampleFunction
 * @param {{string}} param1 - The first parameter
 * @param {{number}} param2 - The second parameter
 * @returns {{boolean}} - The result
 * @throws {{Error}} - If something goes wrong
 * @example
 * // Example usage
 * const result = exampleFunction('test', 42);
 */
"""
