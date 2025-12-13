#!/usr/bin/env python3
"""
Python File Consolidation Script
Consolidates all Python files in the workspace into a single file.
"""

import os
import glob
from pathlib import Path

def collect_python_files():
    """Collect all Python files from the workspace."""
    python_files = []
    
    # Collect from root directory
    for file in glob.glob("*.py"):
        python_files.append(file)
    
    # Collect from subdirectories
    for root, dirs, files in os.walk("."):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__', 'node_modules', 'droxai-env']]
        
        for file in files:
            if file.endswith('.py') and file != 'consolidate_python_files.py':
                rel_path = os.path.relpath(os.path.join(root, file))
                python_files.append(rel_path)
    
    return sorted(set(python_files))

def read_file_safely(file_path):
    """Read file content safely with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def consolidate_python_files():
    """Main consolidation function."""
    python_files = collect_python_files()
    
    print(f"Found {len(python_files)} Python files to consolidate:")
    for file in python_files:
        print(f"  - {file}")
    
    # Create consolidated file
    consolidated_content = []
    consolidated_content.append('#!/usr/bin/env python3')
    consolidated_content.append('"""')
    consolidated_content.append('CONSOLIDATED DROX_AI PYTHON FILES')
    consolidated_content.append('======================================')
    consolidated_content.append('')
    consolidated_content.append('This file contains all Python code from the Drox_AI workspace.')
    consolidated_content.append('Original file structure has been preserved with clear section headers.')
    consolidated_content.append('')
    consolidated_content.append('Generated on: 2025-11-29 10:26:58')
    consolidated_content.append('Total files consolidated: {}'.format(len(python_files)))
    consolidated_content.append('"""')
    consolidated_content.append('')
    
    # Process each file
    for i, file_path in enumerate(python_files, 1):
        print(f"Processing file {i}/{len(python_files)}: {file_path}")
        
        content = read_file_safely(file_path)
        
        # Add section header
        consolidated_content.append('=' * 80)
        consolidated_content.append(f'# FILE: {file_path}')
        consolidated_content.append('=' * 80)
        consolidated_content.append('')
        
        # Add file content
        if content:
            consolidated_content.append(content)
        else:
            consolidated_content.append('# Error reading file content')
        
        consolidated_content.append('')
        consolidated_content.append('')
    
    # Write consolidated file
    output_file = 'DROX_AI_CONSOLIDATED.py'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(consolidated_content))
    
    print(f"\nConsolidation complete!")
    print(f"Output file: {output_file}")
    print(f"Total lines: {sum(len(content.splitlines()) for content in consolidated_content)}")
    
    return output_file

if __name__ == "__main__":
    consolidate_python_files()
