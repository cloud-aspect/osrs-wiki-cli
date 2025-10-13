# GitHub Repository Setup for PyPI Trusted Publishers (OIDC)

This guide shows how to configure your GitHub repository to work with PyPI Trusted Publishers using OpenID Connect (OIDC). This is more secure than API tokens as it doesn't require storing secrets.

## Prerequisites

✅ You mentioned you already set up the **Pending Publisher OIDC setting on PyPI** - great!

## GitHub Repository Configuration

### 1. Repository Settings → Actions → General

Navigate to: **Settings** → **Actions** → **General**

#### Workflow Permissions
Configure these settings:

```
Workflow permissions: ✅ Read and write permissions
                     ✅ Allow GitHub Actions to create and approve pull requests
```

**Why**: This allows the workflow to read repository contents and write releases.

#### Fork Pull Request Workflows  
```
Fork pull request workflows from outside collaborators:
✅ Require approval for first-time contributors who are new to GitHub

Fork pull request workflows in private repositories: 
✅ Require approval for all outside collaborators
```

### 2. Repository Settings → Environments (Optional but Recommended)

Create environments for additional security:

1. **Settings** → **Environments** → **New environment**

2. **Create two environments:**
   - Name: `pypi-production`
   - Name: `test-pypi`

3. **For each environment**, configure:
   ```
   Environment protection rules:
   ✅ Required reviewers (add yourself)
   ✅ Wait timer: 0 minutes (or longer for production)
   
   Deployment branches:
   ✅ Selected branches: main, tags matching v*
   ```

### 3. Repository Settings → Secrets and Variables → Actions

Since you're using Trusted Publishers, you **DON'T need to add API token secrets**. However, you should verify these are **NOT** set:

```
❌ PYPI_API_TOKEN (remove if exists)
❌ TEST_PYPI_API_TOKEN (remove if exists)
```

**The Trusted Publisher configuration replaces these tokens entirely.**

## PyPI Trusted Publisher Configuration Verification

Since you set this up already, verify your configuration matches:

### Production PyPI (pypi.org)
```
Publisher Type: GitHub Actions
Repository: cloud-aspect/osrs-wiki-cli
Workflow: publish.yml
Environment: (leave blank or use "pypi-production")
```

### Test PyPI (test.pypi.org)
```
Publisher Type: GitHub Actions  
Repository: cloud-aspect/osrs-wiki-cli
Workflow: publish.yml
Environment: (leave blank or use "test-pypi")
```

## Workflow Configuration Details

The updated workflow (`.github/workflows/publish.yml`) now includes:

### Required OIDC Permissions
```yaml
permissions:
  id-token: write  # REQUIRED for PyPI trusted publishing
  contents: read   # REQUIRED for repository access
```

### Trusted Publishing Actions
```yaml
- name: Publish to PyPI using Trusted Publishing
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    skip-existing: true
```

## Testing the Setup

### 1. Test Development Publishing
```bash
# Push to main branch (triggers dev version to Test PyPI)
git push origin main
```

**Expected result**: Creates version like `1.0.0.dev123+abc1234` on Test PyPI

### 2. Test Production Publishing  
```bash
# Create and push a release tag
git tag v1.0.0
git push origin v1.0.0
```

**Expected result**: Creates version `1.0.0` on production PyPI

## Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Verify the PyPI Trusted Publisher configuration matches exactly
   - Check that `permissions: id-token: write` is set in workflow
   - Ensure repository name matches exactly: `cloud-aspect/osrs-wiki-cli`

2. **"Workflow not found"**  
   - Verify workflow file is named exactly `publish.yml`
   - Check that the workflow is on the `main` branch

3. **"Environment required"**
   - If you set up environments in PyPI config, create matching GitHub environments
   - Or remove environment from PyPI configuration

### Verification Steps

1. **Check workflow runs**: Actions tab → Recent workflow runs
2. **Verify PyPI uploads**: Check [pypi.org/project/osrs-wiki-cli](https://pypi.org/project/osrs-wiki-cli) and [test.pypi.org/project/osrs-wiki-cli](https://test.pypi.org/project/osrs-wiki-cli)
3. **Test installation**: `pip install osrs-wiki-cli`

## Security Benefits

✅ **No API tokens stored** - Uses GitHub's OIDC identity  
✅ **Scoped permissions** - Only works from specified repo/workflow  
✅ **Audit trail** - All publishes logged in GitHub Actions  
✅ **Revocable** - Can be disabled instantly on PyPI  
✅ **Time-limited** - Tokens are short-lived and auto-expire  

## Next Steps

After configuring these settings:

1. **Commit the updated workflow**:
   ```bash
   git add .github/workflows/publish.yml
   git commit -m "Update to PyPI Trusted Publishers (OIDC)"
   git push origin main
   ```

2. **Monitor the first run** in the Actions tab

3. **Verify successful publishing** to Test PyPI

4. **Create your first release tag** when ready for production:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

The setup is complete! Your repository will now automatically publish to PyPI securely without storing any API tokens.