# Exception Handling Reference

Common exception types by context for Python refactoring.

## File I/O Operations

```python
# Reading files
try:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
except FileNotFoundError:
    # File doesn't exist
    logger.error(f"File not found: {path}")
except PermissionError:
    # No read access
    logger.error(f"Permission denied: {path}")
except OSError as e:
    # Other OS-level errors (disk full, etc.)
    logger.error(f"OS error reading {path}: {e}")
```

```python
# Writing files
try:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
except PermissionError:
    # No write access
    logger.error(f"Cannot write {path}: permission denied")
except OSError as e:
    # Disk full, path too long, etc.
    logger.error(f"Cannot write {path}: {e}")
```

## JSON Operations

```python
import json

try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    logger.error(f"JSON file not found: {path}")
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in {path}: {e}")
except OSError as e:
    logger.error(f"Error reading {path}: {e}")
```

```python
# JSON encoding
try:
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
except (TypeError, ValueError) as e:
    # Data contains non-serializable objects
    logger.error(f"Cannot serialize to JSON: {e}")
```

## HTTP Requests

```python
import requests

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.Timeout:
    logger.error(f"Request timeout: {url}")
except requests.exceptions.ConnectionError:
    logger.error(f"Connection failed: {url}")
except requests.exceptions.HTTPError as e:
    logger.error(f"HTTP error {e.response.status_code}: {url}")
except requests.exceptions.RequestException as e:
    # Other request errors
    logger.error(f"Request failed: {e}")
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON response: {e}")
```

## Data Structure Operations

```python
# Dictionary access with validation
try:
    value = data["key"]["nested"]["field"]
except KeyError as e:
    logger.error(f"Missing key: {e}")
except TypeError as e:
    # data is None or not subscriptable
    logger.error(f"Invalid data structure: {e}")
```

```python
# Attribute access
try:
    result = obj.method().field
except AttributeError as e:
    logger.error(f"Attribute not found: {e}")
```

## Numeric/Math Operations

```python
# Color conversions, calculations
try:
    result = complex_math_operation(value)
except (ValueError, TypeError) as e:
    # Invalid input for operation
    logger.error(f"Cannot compute: {e}")
except ZeroDivisionError:
    logger.error("Division by zero")
```

## External Library Operations

```python
# colormath, PIL, etc.
try:
    color = convert_color(input_color, LabColor)
except (ValueError, AttributeError) as e:
    # Invalid color format or missing attributes
    logger.error(f"Color conversion failed: {e}")
```

## Database Operations

```python
# SQLite, PostgreSQL, etc.
try:
    cursor.execute(query, params)
    result = cursor.fetchall()
except sqlite3.DatabaseError as e:
    logger.error(f"Database error: {e}")
except sqlite3.IntegrityError:
    # Constraint violation
    logger.error(f"Integrity error: {query}")
```

## When to Use Broad Exceptions

**ACCEPTABLE** — At top-level request boundaries:
```python
def handle_request(request):
    try:
        result = process_request(request)
        return {"status": "success", "data": result}
    except Exception as e:
        # Last resort — log and return error response
        logger.exception(f"Unexpected error processing request")
        return {"status": "error", "message": str(e)}
```

**NOT ACCEPTABLE** — In library/internal functions:
```python
def parse_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:  # ❌ Too broad
        return {}
```

## Exception Hierarchy Best Practices

1. **Catch specific exceptions first**:
```python
try:
    operation()
except (ValueError, TypeError) as e:
    # Handle specific known errors
    handle_specific(e)
except Exception as e:
    # Handle unexpected errors
    handle_unexpected(e)
```

2. **Don't catch what you can't handle**:
```python
# Bad — silently swallowing errors
try:
    critical_operation()
except Exception:
    pass  # ❌ Error disappears, debugging impossible

# Good — either handle or re-raise
try:
    critical_operation()
except SpecificError as e:
    handle_it(e)
else:
    raise  # Re-raise if we can't handle it
```

3. **Use context managers for cleanup**:
```python
# No need for try-finally for file closing
with open(path) as f:  # Automatically closes
    data = f.read()
```
