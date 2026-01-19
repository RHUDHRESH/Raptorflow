#!/usr/bin/env python3
"""
Quick script to fix error handling in base.py
"""

with open('base.py', 'r') as f:
    content = f.read()

# Replace the generic exception handling with specific error types
old_code = """        except Exception as e:
            logger.error(f"Tool execution failed for '{tool_name}': {e}")
            raise"""

new_code = """        except ValidationError as e:
            logger.error(f"Validation error for tool '{tool_name}': {e.message}")
            raise
        except DatabaseError as e:
            logger.error(f"Database error for tool '{tool_name}': {e.message}")
            raise
        except LLMError as e:
            logger.error(f"LLM error for tool '{tool_name}': {e.message}")
            raise
        except TimeoutError as e:
            logger.error(f"Timeout error for tool '{tool_name}': {e.message}")
            raise
        except RateLimitError as e:
            logger.error(f"Rate limit error for tool '{tool_name}': {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for tool '{tool_name}': {str(e)}")
            raise ToolError(f"Tool '{tool_name}' failed: {str(e)}")"""

content = content.replace(old_code, new_code)

with open('base.py', 'w') as f:
    f.write(content)

print("✅ Error handling updated in base.py")
