# PyPI Publishing Setup

This document explains how to set up automated PyPI publishing for osrs-wiki-cli.

## GitHub Secrets Configuration

To enable automated publishing, you need to configure these secrets in your GitHub repository:

### Required Secrets

1. **`PYPI_API_TOKEN`** - Your PyPI API token for production releases
2. **`TEST_PYPI_API_TOKEN`** - Your Test PyPI API token for testing

### Setting Up API Tokens

#### 1. PyPI Production Token

1. Go to [pypi.org](https://pypi.org/manage/account/token/)
2. Create a new API token with scope "Entire account" or specific to your project
3. Copy the token (starts with `pypi-`)
4. In GitHub: Settings → Secrets and variables → Actions → New repository secret
5. Name: `PYPI_API_TOKEN`, Value: your token

#### 2. Test PyPI Token  

1. Go to [test.pypi.org](https://test.pypi.org/manage/account/token/)
2. Create a new API token with scope "Entire account" or specific to your project
3. Copy the token (starts with `pypi-`)
4. In GitHub: Settings → Secrets and variables → Actions → New repository secret
5. Name: `TEST_PYPI_API_TOKEN`, Value: your token

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

## Security Notes

- API tokens are stored as GitHub Secrets (encrypted)
- Development versions are published to Test PyPI first
- Production releases require git tags for extra safety
- All uploads use `--skip-existing` to prevent overwrites