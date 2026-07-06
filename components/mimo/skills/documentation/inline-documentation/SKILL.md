---
name: inline-documentation
description: Add inline documentation explaining why not what, covering functions, complex logic, magic numbers, and TODOs
---

# Inline Documentation Prompt

Add clear, useful inline documentation to the following code:

## Code
```
[Paste code here]
```

## Documentation Goals
- Explain **why**, not **what**
- Document non-obvious logic
- Note assumptions and constraints
- Include examples for complex functions
- Document edge cases

## What to Document

### Functions/Methods
```python
def complex_function(data: list[dict], threshold: float) -> list[dict]:
    """
    Filter and transform data based on threshold.
    
    Args:
        data: List of records with 'value' field
        threshold: Minimum value to include (0.0-1.0)
    
    Returns:
        Filtered and sorted list of records
    
    Raises:
        ValueError: If threshold out of range
    
    Example:
        >>> complex_function([{'value': 0.5}], 0.3)
        [{'value': 0.5}]
    """
```

### Complex Logic
```python
# Binary search for optimal split point
# We use binary search instead of linear scan because
# the data is sorted and we need O(log n) performance
```

### Magic Numbers
```python
MAX_RETRIES = 3  # Based on exponential backoff analysis
TIMEOUT_MS = 5000  # 95th percentile response time + 2 sigma
```

### TODOs and FIXMEs
```python
# TODO: Optimize this query - currently does full table scan
# FIXME: Race condition when two threads update simultaneously
```

## Guidelines
- Keep comments concise
- Update comments when code changes
- Don't comment obvious code
- Use consistent style
