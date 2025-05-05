"""
Content Filtering Utility

This module provides functions for filtering and sanitizing content based on
predefined rules and customizable filters.
"""

import re
from typing import List, Union


def filter_content(
    content: str,
    filter_rules: List[str] = None,
    max_length: int = None,
    allowed_chars: str = None,
) -> str:
    """
    Filter and sanitize input content based on specified rules.

    Args:
        content (str): The input content to be filtered
        filter_rules (List[str], optional): List of regex patterns to filter out
        max_length (int, optional): Maximum allowed length of content
        allowed_chars (str, optional): String of allowed characters

    Returns:
        str: Filtered and sanitized content

    Raises:
        ValueError: If content is None or not a string
    """
    # Validate input
    if content is None:
        raise ValueError("Content cannot be None")
    
    if not isinstance(content, str):
        raise ValueError("Content must be a string")

    # Apply filtering with regex rules first
    if filter_rules:
        for rule in filter_rules:
            content = re.sub(rule, '', content, flags=re.IGNORECASE)
    
    # Filter allowed characters if specified
    if allowed_chars is not None:
        content = ''.join(char.lower() for char in content if char.lower() in allowed_chars)

    # Remove extra whitespace
    content = re.sub(r'\s+', ' ', content).strip()

    # Apply maximum length filtering last
    if max_length is not None:
        content = content[:max_length]

    return content


def contains_sensitive_content(
    content: str,
    sensitive_patterns: List[str] = None
) -> bool:
    """
    Check if content contains any sensitive patterns.

    Args:
        content (str): Input content to check
        sensitive_patterns (List[str], optional): List of regex patterns 
                                                 indicating sensitive content

    Returns:
        bool: True if sensitive content is found, False otherwise
    """
    # Default sensitive patterns if none provided
    default_sensitive_patterns = [
        r'\b(password|credit card|ssn|social security)\b',
        r'\b([0-9]{3}-[0-9]{2}-[0-9]{4})\b',  # SSN pattern
        r'\b([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4})\b'  # Credit card pattern
    ]

    patterns_to_check = sensitive_patterns or default_sensitive_patterns

    for pattern in patterns_to_check:
        if re.search(pattern, content, re.IGNORECASE):
            return True

    return False