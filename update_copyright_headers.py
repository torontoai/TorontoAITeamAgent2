#!/usr/bin/env python3
"""
Copyright Header Update Script for TORONTO AI TEAM AGENT.

This script adds the proprietary copyright header to source files.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('copyright_update.log')
    ]
)
logger = logging.getLogger(__name__)

# Copyright header template
COPYRIGHT_HEADER = """/**
 * TORONTO AI TEAM AGENT - PROPRIETARY
 * 
 * Copyright (c) 2025 TORONTO AI
 * Creator: David Tadeusz Chudak
 * All Rights Reserved
 * 
 * This file is part of the TORONTO AI TEAM AGENT software.
 * 
 * This software is based on OpenManus (Copyright (c) 2025 manna_and_poem),
 * which is licensed under the MIT License. The original license is included
 * in the LICENSE file in the root directory of this project.
 * 
 * This software has been substantially modified with proprietary enhancements.
 */
"""

# Python comment version
PYTHON_COPYRIGHT_HEADER = """# TORONTO AI TEAM AGENT - PROPRIETARY
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

# JavaScript/JSX comment version
JS_COPYRIGHT_HEADER = """/**
 * TORONTO AI TEAM AGENT - PROPRIETARY
 * 
 * Copyright (c) 2025 TORONTO AI
 * Creator: David Tadeusz Chudak
 * All Rights Reserved
 * 
 * This file is part of the TORONTO AI TEAM AGENT software.
 * 
 * This software is based on OpenManus (Copyright (c) 2025 manna_and_poem),
 * which is licensed under the MIT License. The original license is included
 * in the LICENSE file in the root directory of this project.
 * 
 * This software has been substantially modified with proprietary enhancements.
 */
"""

def add_copyright_header(file_path, dry_run=False):
    """
    Add copyright header to a file if it doesn't already have one.
    
    Args:
        file_path: Path to the file
        dry_run: If True, don't actually modify files
        
    Returns:
        True if file was modified, False otherwise
    """
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file already has copyright header
        if "TORONTO AI TEAM AGENT - PROPRIETARY" in content:
            # Check if it has the old header without creator info
            if "Creator: David Tadeusz Chudak" not in content:
                # Replace old header with new one
                if content.startswith("# TORONTO AI TEAM AGENT - PROPRIETARY"):
                    # Python style header
                    end_header_idx = content.find("\n\n", content.find("# TORONTO AI TEAM AGENT - PROPRIETARY"))
                    if end_header_idx == -1:
                        end_header_idx = content.find("\nimport", content.find("# TORONTO AI TEAM AGENT - PROPRIETARY"))
                    if end_header_idx == -1:
                        end_header_idx = content.find("\nfrom", content.find("# TORONTO AI TEAM AGENT - PROPRIETARY"))
                    if end_header_idx == -1:
                        end_header_idx = content.find("\ndef", content.find("# TORONTO AI TEAM AGENT - PROPRIETARY"))
                    if end_header_idx == -1:
                        end_header_idx = content.find("\nclass", content.find("# TORONTO AI TEAM AGENT - PROPRIETARY"))
                    
                    if end_header_idx != -1:
                        new_content = PYTHON_COPYRIGHT_HEADER + content[end_header_idx:]
                        
                        if dry_run:
                            logger.info(f"Would update copyright header in: {file_path}")
                            return True
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        logger.info(f"Updated copyright header in: {file_path}")
                        return True
                
                elif content.startswith("/**\n * TORONTO AI TEAM AGENT - PROPRIETARY"):
                    # JS/C style header
                    end_header_idx = content.find("*/\n", content.find("/**\n * TORONTO AI TEAM AGENT - PROPRIETARY"))
                    
                    if end_header_idx != -1:
                        new_content = JS_COPYRIGHT_HEADER + content[end_header_idx + 3:]
                        
                        if dry_run:
                            logger.info(f"Would update copyright header in: {file_path}")
                            return True
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        logger.info(f"Updated copyright header in: {file_path}")
                        return True
            
            logger.info(f"File already has up-to-date copyright header: {file_path}")
            return False
        
        # Determine appropriate header based on file extension
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.py']:
            header = PYTHON_COPYRIGHT_HEADER
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            header = JS_COPYRIGHT_HEADER
        else:
            # Default to standard header
            header = COPYRIGHT_HEADER
        
        # Add header to file
        new_content = header + "\n" + content
        
        if dry_run:
            logger.info(f"Would add copyright header to: {file_path}")
            return True
        
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Added copyright header to: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding copyright header to {file_path}: {str(e)}")
        return False

def process_directory(directory, extensions, exclude_dirs=None, dry_run=False):
    """
    Process all files in a directory and its subdirectories.
    
    Args:
        directory: Directory to process
        extensions: List of file extensions to process
        exclude_dirs: List of directories to exclude
        dry_run: If True, don't actually modify files
        
    Returns:
        Tuple of (processed_count, modified_count)
    """
    if exclude_dirs is None:
        exclude_dirs = []
    
    processed_count = 0
    modified_count = 0
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for file in files:
            # Check if file has one of the specified extensions
            if not any(file.endswith(ext) for ext in extensions):
                continue
            
            file_path = os.path.join(root, file)
            processed_count += 1
            
            if add_copyright_header(file_path, dry_run):
                modified_count += 1
    
    return processed_count, modified_count

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Add copyright headers to source files")
    parser.add_argument("--directory", type=str, default="/home/ubuntu/openmanus-team-ai", help="Directory to process")
    parser.add_argument("--extensions", type=str, default=".py,.js,.jsx,.ts,.tsx,.java,.c,.cpp,.h,.hpp", help="Comma-separated list of file extensions to process")
    parser.add_argument("--exclude", type=str, default="node_modules,venv,__pycache__,dist,build", help="Comma-separated list of directories to exclude")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually modify files")
    
    args = parser.parse_args()
    
    # Parse arguments
    directory = os.path.abspath(args.directory)
    extensions = args.extensions.split(',')
    exclude_dirs = args.exclude.split(',')
    
    if not os.path.exists(directory):
        logger.error(f"Directory does not exist: {directory}")
        return 1
    
    logger.info(f"Processing directory: {directory}")
    logger.info(f"File extensions: {', '.join(extensions)}")
    logger.info(f"Excluded directories: {', '.join(exclude_dirs)}")
    logger.info(f"Dry run: {args.dry_run}")
    
    # Process directory
    processed_count, modified_count = process_directory(
        directory=directory,
        extensions=extensions,
        exclude_dirs=exclude_dirs,
        dry_run=args.dry_run
    )
    
    logger.info(f"Processed {processed_count} files")
    logger.info(f"Modified {modified_count} files")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
