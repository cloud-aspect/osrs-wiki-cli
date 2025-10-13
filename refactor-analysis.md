# Refactor Analysis: OSRS Wiki CLI Tool

## Issues Identified in Test Loop

### 1. Typer Argument Handling Inconsistencies
- **Problem**: Mixed usage of `typer.Argument()`, `typer.Option()` with different syntaxes
- **Root Cause**: Typer 0.9.0 compatibility issues with argument definitions
- **Impact**: CLI fails to start, preventing any testing

### 2. Testing Approach Problems
- **Problem**: Testing complex commands before validating basic CLI structure
- **Better Approach**: Test help system first, then simple commands, then complex ones
- **Current Issue**: Jump straight to full API calls without validating CLI parsing

### 3. Error Handling Gaps
- **Problem**: Typer parsing errors aren't caught gracefully
- **Impact**: Cryptic stack traces instead of user-friendly messages
- **Solution**: Add top-level exception handling

## Recommended Refactor

### Phase 1: Simplify CLI Structure
```python
# Use the most basic Typer patterns that work across versions
@app.command()
def page(page_title: str):  # Simplest positional argument
    """Extract data from a wiki page"""
    # Implementation

@app.command("list")  # Explicit command name to avoid Python keyword issues
def list_category(category: str):  # Avoid 'list' name conflict
    """List pages in a category"""  
    # Implementation
```

### Phase 2: Add Options Incrementally
```python
# Add options one by one, testing each addition
@app.command()
def page(
    page_title: str,
    section: str = typer.Option(None, "--section"),
    format_output: str = typer.Option("json", "--format")
):
```

### Phase 3: Robust Error Handling
```python
def main():
    try:
        app()
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    main()
```

## Testing Strategy Improvements

### 1. Incremental Testing
1. Test basic CLI help: `python wiki_tool.py --help`
2. Test command help: `python wiki_tool.py page --help`
3. Test with dummy data before real API calls
4. Test real API calls only after CLI structure is solid

### 2. Validation Layers
- CLI argument parsing validation
- API client connection validation  
- Response data validation
- Output format validation

### 3. Fallback Patterns
- Graceful degradation when API fails
- Default values for all optional parameters
- Clear error messages for user guidance

## Implementation Priority
1. **High**: Fix basic CLI argument parsing
2. **High**: Add comprehensive error handling
3. **Medium**: Test with simplified commands first
4. **Medium**: Add back full feature set incrementally
5. **Low**: Optimize for different Typer versions