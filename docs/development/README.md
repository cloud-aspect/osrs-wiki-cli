# Development Guide

Guide for contributing to and developing the OSRS Wiki Page Tool.

## Table of Contents

- [Project Architecture](#project-architecture)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Contributing](#contributing)
- [Release Process](#release-process)

## Project Architecture

### Design Principles

The tool follows these core design principles established during development:

1. **MediaWiki API First** - Uses only JSON API responses, never HTML scraping
2. **Rate Limiting Respect** - Built-in 1-second delays and exponential backoff
3. **Modular Commands** - Each command handles one specific extraction task
4. **No Background Services** - Manual invocation only, no headless services
5. **Single File Architecture** - Everything in `wiki_tool.py` for simplicity

### Framework Decision

**Current Implementation:** `argparse` (built-in, zero dependencies)

**Rationale:** After testing with Typer and encountering compatibility issues, the project migrated to argparse for:
- 100% Python compatibility across environments
- Zero external dependencies beyond requests and BeautifulSoup4
- Rock-solid reliability and extensive documentation
- Full featured CLI with help system and validation

**Alternative Frameworks Available:**
- `click` - Feature-rich but adds dependency
- `fire` - Automatic CLI generation but less control
- `typer` - Modern but had compatibility issues in testing environment

### Dependencies

**Core Requirements:**
```bash
requests>=2.31.0      # HTTP client for MediaWiki API
beautifulsoup4>=4.12.2  # HTML parsing for complex responses
```

**Development Tools:**
```bash
pytest>=7.0.0         # Testing framework
black>=23.0.0          # Code formatting
flake8>=5.0.0         # Linting
mypy>=1.0.0           # Type checking
```

### Code Organization

The `wiki_tool.py` file is organized as:

1. **Imports and Configuration** - All dependencies and constants
2. **MediaWiki API Helpers** - Core API interaction functions
3. **Output Formatting Functions** - JSON, CSV, text formatters  
4. **Command Implementations** - Individual command logic
5. **Argument Parser Setup** - CLI structure and validation
6. **Main Entry Point** - Execution and error handling

## Development Setup

### Environment Setup

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd osrs-wiki-page-tool
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/macOS
   ```

2. **Install dependencies:**
   ```bash
   pip install requests beautifulsoup4
   pip install pytest black flake8 mypy  # dev tools
   ```

3. **Verify installation:**
   ```bash
   python wiki_tool.py --help
   python wiki_tool.py source "Template:Documentation" --format json
   ```

### Testing Strategy

**Live API Testing:**
- Test against real OSRS Wiki endpoints
- Use known stable pages for integration tests
- Validate against MediaWiki API sandbox for query development

**Test Pages for Development:**
```bash
# Stable test targets
python wiki_tool.py source "Template:Documentation"
python wiki_tool.py source "Module:Coins"
python wiki_tool.py list "Category:Skill calculators" --limit 5
```

**MediaWiki API Sandbox:**
Use https://www.mediawiki.org/wiki/Special:ApiSandbox for developing new queries.

### Local Development Workflow

1. **Make changes** to `wiki_tool.py`
2. **Test locally:**
   ```bash
   python wiki_tool.py source "Test Page" --format json
   ```
3. **Run linting:**
   ```bash
   black wiki_tool.py
   flake8 wiki_tool.py --max-line-length 88
   ```
4. **Test edge cases** (missing pages, network errors, etc.)

## Code Standards

### Python Style

- **Formatter:** Black (88 character line length)
- **Linter:** Flake8 with Black compatibility
- **Type Hints:** Encouraged but not required
- **Docstrings:** Google style for functions and classes

### API Interaction Patterns

**Always implement these MediaWiki API best practices:**

```python
# User-Agent header
headers = {
    "User-Agent": "OSRSWikiTool/1.0 (Python CLI tool for OSRS Wiki data extraction)"
}

# Rate limiting
time.sleep(1)  # Between requests

# Error handling  
if response.status_code == 429:  # Rate limited
    # Implement exponential backoff
    pass

# Response validation
if 'error' in data:
    # Handle API errors appropriately
    pass
```

### Command Implementation Pattern

```python
def command_name(args):
    """Command description.
    
    Args:
        args: Parsed command arguments
        
    Returns:
        dict: Command results in standard format
    """
    # 1. Validate arguments
    # 2. Make API calls with rate limiting
    # 3. Process response data
    # 4. Return standardized format
```

### Output Format Standards

All commands should support consistent output formats:

```python
def format_output(data, format_type):
    """Format output according to specified type."""
    if format_type == "json":
        return json.dumps(data, indent=2)
    elif format_type == "csv":
        return format_as_csv(data)
    elif format_type == "text":
        return extract_primary_content(data)
```

## Testing

### Integration Tests

Test against live MediaWiki API:

```bash
# Test successful cases
python wiki_tool.py source "Template:Documentation" --format json
python wiki_tool.py list "Category:Calculators" --limit 5

# Test error cases  
python wiki_tool.py source "Nonexistent Page Name"
python wiki_tool.py list "Nonexistent Category"
```

### Error Scenario Testing

Test common failure modes:

1. **Network Issues:**
   - Disconnect network and test error handling
   - Test timeout scenarios

2. **API Errors:**
   - Test with invalid page names
   - Test with malformed requests

3. **Rate Limiting:**
   - Test rapid successive requests
   - Verify backoff behavior

### Regression Testing

Before releases, test core functionality:

```bash
# Slayer data extraction (primary use case)
python wiki_tool.py source "Module:SlayerConsts/MasterTables" --format text
python wiki_tool.py source "Calculator:Slayer/Slayer task weight" --templates

# Category listing
python wiki_tool.py list "Category:Modules" --limit 10 --format csv

# Error handling
python wiki_tool.py source "Does Not Exist"
```

## Contributing

### Issue Reporting

When reporting issues, include:

1. **Command that failed:**
   ```bash
   python wiki_tool.py source "Page Name" --options
   ```

2. **Full error message and traceback**

3. **System information:**
   - Python version: `python --version`
   - Operating system
   - Dependencies: `pip list`

4. **Expected vs actual behavior**

### Pull Request Process

1. **Fork and branch:**
   ```bash
   git checkout -b feature/new-command
   ```

2. **Make focused changes:**
   - Single feature or bug fix per PR
   - Update documentation if needed
   - Add tests for new functionality

3. **Test thoroughly:**
   ```bash
   python wiki_tool.py --help  # Verify CLI works
   # Test your specific changes
   # Test error cases
   ```

4. **Code quality:**
   ```bash
   black wiki_tool.py
   flake8 wiki_tool.py --max-line-length 88
   ```

5. **Documentation updates:**
   - Update relevant docs in `docs/` folder
   - Update README.md if needed
   - Include examples of new functionality

### Commit Message Format

```
type(scope): brief description

Detailed explanation if needed.

- Bullet points for multiple changes
- Reference issues: Fixes #123
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Release Process

### Version Management

- Use semantic versioning: `MAJOR.MINOR.PATCH`
- Update version in code comments and documentation
- Tag releases in git: `v1.2.3`

### Pre-Release Checklist

1. **Test core functionality:**
   ```bash
   python wiki_tool.py source "Module:SlayerConsts/MasterTables" --format json
   python wiki_tool.py list "Category:Calculators" --limit 5
   ```

2. **Update documentation:**
   - README.md feature list
   - API reference for new commands
   - Usage examples

3. **Code quality:**
   ```bash
   black wiki_tool.py
   flake8 wiki_tool.py
   ```

4. **Test in clean environment:**
   ```bash
   python -m venv test_env
   test_env\Scripts\activate
   pip install requests beautifulsoup4
   python wiki_tool.py --help
   ```

### Release Notes Template

```markdown
## v1.2.3 - 2025-01-15

### Added
- New `search` command for wiki content search
- CSV output format for list command

### Fixed  
- Improved error handling for network timeouts
- Fixed Unicode handling in page titles

### Changed
- Updated rate limiting to be more conservative
- Improved help text clarity

### Developer Notes
- Migrated from Typer to argparse for compatibility
- Added integration tests for error scenarios
```

---

**Next:** [Examples](../examples/README.md) | **Previous:** [API Reference](../api/README.md)