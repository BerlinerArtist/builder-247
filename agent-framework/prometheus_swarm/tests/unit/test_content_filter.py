"""
Unit tests for content filtering utility
"""

import pytest
from prometheus_swarm.utils.content_filter import filter_content, contains_sensitive_content


def test_basic_filter_content():
    # Test basic filtering
    content = "Hello, World!"
    assert filter_content(content) == "Hello, World!"


def test_max_length_filter():
    # Test maximum length constraint
    content = "This is a very long text that should be truncated"
    result = filter_content(content, max_length=20)
    assert len(result) <= 20
    assert result == "this is a very long te"


def test_regex_filter():
    # Test filtering using regex rules
    content = "Bad word: stupid, another bad: idiot"
    filtered_content = filter_content(
        content, 
        filter_rules=[r'\b(stupid|idiot)\b']
    )
    assert "stupid" not in filtered_content
    assert "idiot" not in filtered_content


def test_allowed_chars_filter():
    # Test filtering with allowed characters
    content = "Hello123 World!"
    filtered_content = filter_content(
        content, 
        allowed_chars='abcdefghijklmnopqrstuvwxyz '
    )
    assert filtered_content == "hello world"


def test_multiple_filters_combined():
    # Test multiple filters simultaneously
    content = "Bad word: stupid123, Very Long Text About Something"
    filtered_content = filter_content(
        content,
        filter_rules=[r'\b(stupid)\b'],
        max_length=20,
        allowed_chars='abcdefghijklmnopqrstuvwxyz '
    )
    assert len(filtered_content) <= 20
    assert "stupid" not in filtered_content.split()


def test_invalid_input_raises_error():
    # Test None input raises error
    with pytest.raises(ValueError, match="Content cannot be None"):
        filter_content(None)

    # Test non-string input raises error
    with pytest.raises(ValueError, match="Content must be a string"):
        filter_content(123)


def test_sensitive_content_detection():
    # Test detection of sensitive content
    assert contains_sensitive_content("My SSN is 123-45-6789") == True
    assert contains_sensitive_content("My credit card is 1234-5678-9012-3456") == True
    assert contains_sensitive_content("This is a safe message") == False


def test_custom_sensitive_patterns():
    # Test custom sensitive patterns
    custom_patterns = [r'\b(secret)\b']
    assert contains_sensitive_content(
        "This is a secret message", 
        sensitive_patterns=custom_patterns
    ) == True

    assert contains_sensitive_content(
        "This is a public message", 
        sensitive_patterns=custom_patterns
    ) == False