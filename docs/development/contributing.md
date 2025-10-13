# Contributing to OSRS Wiki Page Tool

Thank you for your interest in contributing! This document provides comprehensive guidelines for contributors.

## Table of Contents

- [Quick Start](#quick-start)
- [Ways to Contribute](#ways-to-contribute)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community Guidelines](#community-guidelines)

## Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/osrs-wiki-page-tool.git
   cd osrs-wiki-page-tool
   ```
3. **Set up development environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/macOS
   pip install requests beautifulsoup4
   ```
4. **Test the installation:**
   ```bash
   python wiki_tool.py --help
   python wiki_tool.py source "Template:Documentation" --format json
   ```

## Ways to Contribute

### 🐛 Bug Reports

Help us improve by reporting issues:

**Before submitting:**
- Check existing issues to avoid duplicates
- Test with the latest version
- Try to reproduce the issue consistently

**When submitting, include:**
- **Command that failed:** `python wiki_tool.py source "Page Name" --options`
- **Full error message and traceback**
- **System information:**
  - Python version: `python --version`
  - Operating system
  - Dependencies: `pip list | grep -E "(requests|beautifulsoup4)"`
- **Expected vs actual behavior**
- **Steps to reproduce**

### 💡 Feature Requests

Suggest new functionality:

- Describe the use case and motivation
- Provide examples of how it would be used
- Consider MediaWiki API limitations
- Think about how it fits with existing commands

### 🔧 Code Contributions

#### Good First Issues

Look for issues tagged with `good-first-issue`:
- Documentation improvements
- Error message enhancements
- Simple command additions
- Test coverage improvements

#### Feature Development

For larger features:
1. **Discuss first** - Open an issue to discuss the approach
2. **Start small** - Break large features into smaller PRs
3. **Follow patterns** - Use existing command structure as a template

## Development Workflow

### Setting Up Your Branch

```bash
# Create feature branch from main
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### Making Changes

1. **Focus on one thing** - Keep PRs focused on a single feature or fix
2. **Test thoroughly** - Test your changes with various inputs
3. **Update documentation** - Update relevant docs in the `docs/` folder
4. **Follow code standards** - See [Code Standards](#code-standards) below

### Commit Guidelines

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "feat(list): add --limit option for category listings"
git commit -m "fix(source): handle Unicode page titles correctly"
git commit -m "docs(api): update source command examples"

# Less good
git commit -m "fix stuff"
git commit -m "update"
```

**Commit message format:**
```
type(scope): brief description

Detailed explanation if needed.

- Additional context or reasoning
- Reference issues: Fixes #123, Relates to #456
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix  
- `docs` - Documentation changes
- `refactor` - Code refactoring without behavior change
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

### Submitting Pull Requests

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create pull request** on GitHub with:
   - Clear title and description
   - Link to related issues
   - Screenshots for UI changes (if applicable)
   - Test instructions for reviewers

3. **Respond to feedback** promptly and professionally

## Code Standards

### Python Style Guidelines

- **Formatter:** Black (88 character line length)
- **Linter:** Flake8 with Black compatibility
- **Type hints:** Encouraged for new code
- **Docstrings:** Google style for functions and classes

**Before submitting:**
```bash
# Format code
black wiki_tool.py

# Check linting
flake8 wiki_tool.py --max-line-length 88 --extend-ignore E203,W503
```

### MediaWiki API Best Practices

Always follow these patterns when adding API functionality:

```python
# 1. Include proper headers
headers = {
    "User-Agent": "OSRSWikiTool/1.0 (Python CLI tool for OSRS Wiki data extraction)"
}

# 2. Implement rate limiting
import time
time.sleep(1)  # Between requests

# 3. Handle errors gracefully
if response.status_code == 429:  # Rate limited
    # Implement exponential backoff
    time.sleep(2 ** retry_count)
    
if 'error' in data:
    # Handle API errors with helpful messages
    error_code = data['error'].get('code', 'unknown')
    error_info = data['error'].get('info', 'Unknown error')
    raise RuntimeError(f"MediaWiki API error ({error_code}): {error_info}")
```

### Command Implementation Pattern

Use this pattern for new commands:

```python
def handle_new_command(args):
    """Brief command description.
    
    Args:
        args: Parsed command arguments from argparse
        
    Returns:
        dict: Standardized response format
        
    Raises:
        RuntimeError: For API errors or invalid responses
    """
    # 1. Validate arguments
    if not args.required_param:
        raise ValueError("Required parameter missing")
    
    # 2. Make API calls with proper error handling
    try:
        response = make_api_request(params)
        data = validate_response(response)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch data: {e}")
    
    # 3. Process and return standardized format
    return {
        "status": "success",
        "data": processed_data,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "source": "mediawiki-api"
        }
    }
```

### Output Format Standards

All commands must support these output formats:

```python
def format_output(data, format_type):
    """Format command output according to specified type."""
    if format_type == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif format_type == "csv":
        # Implement CSV formatting appropriate for the data
        return format_as_csv(data)
    elif format_type == "text":
        # Return primary content only
        return extract_primary_content(data)
    else:
        raise ValueError(f"Unsupported format: {format_type}")
```

## Testing Guidelines

### Manual Testing

Test all changes with real API calls:

```bash
# Test successful cases
python wiki_tool.py source "Template:Documentation" --format json
python wiki_tool.py list "Category:Calculators" --limit 5

# Test error cases
python wiki_tool.py source "Nonexistent Page Name"
python wiki_tool.py list "Nonexistent Category"

# Test edge cases
python wiki_tool.py source "Page:With/Special/Characters"
python wiki_tool.py list "Category:Empty" --limit 1
```

### Integration Testing

For new commands, test against these stable pages:

- `Template:Documentation` - Basic template
- `Module:Coins` - Simple Lua module  
- `Calculator:Combat level` - JavaScript calculator
- `Category:Calculators` - Well-populated category
- `Category:Modules` - Module category

### Error Scenario Testing

Test error handling:

1. **Network issues:**
   ```bash
   # Temporarily disable network and test
   python wiki_tool.py source "Any Page"
   ```

2. **Invalid inputs:**
   ```bash
   python wiki_tool.py source ""
   python wiki_tool.py list "Not A Category"
   ```

3. **Rate limiting:**
   ```bash
   # Make rapid requests (carefully!)
   for i in {1..5}; do python wiki_tool.py source "Template:Documentation"; done
   ```

### Regression Testing

Before submitting, verify core functionality works:

```bash
# Slayer data extraction (primary use case)
python wiki_tool.py source "Module:SlayerConsts/MasterTables" --format text
python wiki_tool.py source "Calculator:Slayer/Slayer task weight" --templates

# All output formats
python wiki_tool.py list "Category:Modules" --limit 5 --format json
python wiki_tool.py list "Category:Modules" --limit 5 --format csv  
python wiki_tool.py list "Category:Modules" --limit 5 --format text
```

## Documentation

### Documentation Requirements

When adding features, update:

1. **API Reference** (`docs/api/README.md`) - Add command syntax and options
2. **User Guide** (`docs/usage/README.md`) - Add usage examples
3. **Examples** (`docs/examples/README.md`) - Add real-world examples
4. **README.md** - Update feature list if significant

### Documentation Style

- Use clear, concise language
- Include practical examples
- Show both command and expected output
- Explain the "why" not just the "how"
- Use consistent formatting and structure

### Example Documentation Format

```markdown
### `new-command` Command

Extract specific data type from wiki pages.

**Usage:**
```bash
python wiki_tool.py new-command <argument> [options]
```

**Arguments:**
- `argument` - Description of what this argument does

**Options:**
- `--option` - Description of this option

**Examples:**
```bash
# Basic usage
python wiki_tool.py new-command "Example Page"

# With options
python wiki_tool.py new-command "Example Page" --option value --format json
```

**Output:**
```json
{
  "example": "Expected output structure"
}
```
```

## Community Guidelines

### Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Help others learn and improve
- Respect different perspectives and experience levels

### Communication

- **Issues:** For bug reports and feature requests
- **Pull Requests:** For code discussions and reviews  
- **Discussions:** For general questions and ideas

### Review Process

**As a contributor:**
- Be patient with feedback and review cycles
- Address feedback promptly and professionally
- Ask questions if feedback is unclear
- Update documentation along with code changes

**As a reviewer:**
- Provide constructive, specific feedback
- Test the changes when possible
- Focus on code quality, maintainability, and user experience
- Acknowledge good work and improvements

### Getting Help

If you need help:

1. **Check existing documentation** in the `docs/` folder
2. **Search existing issues** for similar problems
3. **Ask in discussions** for general questions
4. **Open an issue** for specific bugs or feature requests

---

## Recognition

Contributors will be acknowledged in:
- Repository contributors list
- Release notes for significant contributions
- Documentation credits

Thank you for contributing to the OSRS Wiki Page Tool! 🎉