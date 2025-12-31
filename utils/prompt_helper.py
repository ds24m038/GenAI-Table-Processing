"""
Prompt helper utilities for placeholder replacement.
"""
import re
from typing import Any, Dict


def replace_placeholders(prompt: str, row_data: Dict[str, Any]) -> str:
    """
    Replace {@ColumnName} placeholders in prompt with actual row values.
    
    Args:
        prompt: Template string with {@ColumnName} placeholders
        row_data: Dictionary of column name -> value
        
    Returns:
        Prompt with placeholders replaced by actual values
    """
    result = prompt
    
    # Find all {@...} patterns
    pattern = r'\{@(\w+)\}'
    matches = re.findall(pattern, prompt)
    
    for column_name in matches:
        placeholder = f'{{@{column_name}}}'
        value = row_data.get(column_name, '')
        result = result.replace(placeholder, str(value))
    
    return result


def extract_placeholders(prompt: str) -> list[str]:
    """
    Extract all column names used as placeholders in a prompt.
    
    Args:
        prompt: Template string with {@ColumnName} placeholders
        
    Returns:
        List of column names referenced in the prompt
    """
    pattern = r'\{@(\w+)\}'
    return re.findall(pattern, prompt)
