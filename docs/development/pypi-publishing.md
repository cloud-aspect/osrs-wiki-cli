# PyPI Publishing Setup

This document explains how to set up automated PyPI publishing for osrs-wiki-cli using **PyPI Trusted Publishers** (OIDC).

## Overview

osrs-wiki-cli uses **PyPI Trusted Publishers** with OpenID Connect (OIDC) for secure, token-free publishing. This is more secure than API tokens as it doesn't require storing secrets.

## Setup Requirements

### 1. PyPI Trusted Publisher Configuration

Configure trusted publishers on both PyPI platforms:

#### Production PyPI (pypi.org)
1. Go to [pypi.org](https://pypi.org/manage/account/publishing/)
2. Add a new **pending publisher**:
   ```
   Publisher Type: GitHub Actions
   Owner: cloud-aspect  
   Repository: osrs-wiki-cli
   Workflow: publish.yml
   Environment: (optional: pypi-production)
   ```

#### Test PyPI (test.pypi.org)  
1. Go to [test.pypi.org](https://test.pypi.org/manage/account/publishing/)
2. Add the same configuration as above

### 2. GitHub Repository Configuration

See the complete guide: [`github-oidc-setup.md`](github-oidc-setup.md)

**Key settings:**
- Workflow permissions: Read and write permissions
- No API token secrets needed (tokens are replaced by OIDC)
- Optional: Create environments for additional security

## Publishing Workflow

The automated workflow triggers on:

### Production Publishing
- **Push to main branch** - Creates development versions (1.0.0.dev123+abc1234)
- **Tagged releases** - Creates stable releases (v1.0.0, v1.1.0, etc.)

### Development Publishing  
- **Every push to main** - Publishes dev versions to Test PyPI for testing

## Release Process

### 1. Development Releases (Automatic)
```bash
# Every push to main automatically creates a development release
git push origin main
# Results in: osrs-wiki-cli==1.0.0.dev45+a1b2c3d on Test PyPI
```

### 2. Stable Releases (Tagged)
```bash
# Create and push a version tag for stable release
git tag v1.1.0
git push origin v1.1.0
# Results in: osrs-wiki-cli==1.1.0 on PyPI
```

### 3. Manual Version Updates
Edit version in both:
- `setup.py`: `version="1.1.0"`
- `pyproject.toml`: `version = "1.1.0"`

## Installation Testing

### From Test PyPI (Development)
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ osrs-wiki-cli
```

### From PyPI (Production)
```bash
pip install osrs-wiki-cli
```

## Quality Gates

Before publishing, the workflow:
1. ✅ Runs tests across Python 3.8-3.11
2. ✅ Tests CLI functionality with real wiki data
3. ✅ Builds and validates the package
4. ✅ Publishes to Test PyPI first
5. ✅ Tests installation from Test PyPI
6. ✅ Only then publishes to production PyPI

## Package Information

- **Name**: `osrs-wiki-cli`
- **Entry Point**: `osrs-wiki-cli` command
- **Dependencies**: `requests>=2.31.0`, `beautifulsoup4>=4.12.2`
- **Python Support**: 3.8+
- **License**: MIT

## Troubleshooting

### Common Issues

1. **"Package already exists"** - Normal for development versions, they're skipped
2. **"Invalid token"** - Check your API tokens are correctly set in GitHub Secrets  
3. **"Build failed"** - Check that `wiki_tool.py` has no syntax errors

### Manual Publishing (Emergency)

```bash
# Build package locally
python -m build

# Upload to PyPI manually  
twine upload dist/*
```

## Security Benefits

✅ **No API tokens stored** - Uses GitHub's OIDC identity instead of secrets  
✅ **Scoped permissions** - Publishing only works from the specified repository and workflow  
✅ **Audit trail** - All publishing actions are logged in GitHub Actions  
✅ **Revocable access** - Can be disabled instantly on PyPI without rotating tokens  
✅ **Time-limited tokens** - OIDC tokens are short-lived and automatically expire  
✅ **Git-based security** - Production releases require git tags for additional safety