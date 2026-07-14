---
name: project-cleanup
summary: Update documentation, CI workflows, and validation procedures for osrs-wiki-cli
---

# project-cleanup

## Purpose
Create a reusable workflow skill for updating project documentation, deployment settings, and validation procedures in the `osrs-wiki-cli` repository. This skill captures the exact commands and error recovery steps used during the recent workspace update.

## When to Use
- After changing CLI behavior or documentation
- When repository CI/workflow files need validation
- When adding dependency or deployment automation support
- When ensuring `uv` is the preferred runtime for local validation

## Procedure

### 1. Audit current files and CLI behavior
1. Confirm the CLI implementation in `wiki_tool.py`.
2. Locate documentation and workflow files:
   - `README.md`
   - `docs/usage/README.md`
   - `docs/api/README.md`
   - `docs/development/README.md`
   - `docs/development/contributing.md`
   - `docs/usage/faq.md`
   - `.github/workflows/test.yml`
   - `.github/workflows/publish.yml`
   - `.github/dependabot.yml`
3. Inspect `pyproject.toml`, `setup.py`, and any dependency files.

### 2. Standardize docs for current CLI and `uv`
- Replace direct `python wiki_tool.py` examples with `uv run python .\wiki_tool.py`.
- Ensure `source`, `category`, and `page` are described accurately.
- Confirm `--tables`, `--save`, and `--data-dir` flags match `wiki_tool.py`.
- For batch or helper scripts, prefer `uv run python .\batch_extract.py` and `uv run python .\data_manager.py`.

### 3. Fix deployment and validation dependencies
- Add `requirements.txt` when workflows reference it.
- Use pinned minimal runtime dependencies:
  - `requests>=2.31.0`
  - `beautifulsoup4>=4.12.2`
- Ensure workflows install dependencies from `requirements.txt`:
  ```yaml
  - name: Install dependencies
    run: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt
  ```
- Add Dependabot config in `.github/dependabot.yml`:
  ```yaml
  version: 2
  updates:
    - package-ecosystem: "github-actions"
      directory: "/"
      schedule:
        interval: "weekly"
    - package-ecosystem: "pip"
      directory: "/"
      schedule:
        interval: "weekly"
      open-pull-requests-limit: 5
      allow:
        - dependency-type: "direct"
  ```

### 4. Validate workflow and config files with `uv`
1. Confirm `uv` is installed:
   ```powershell
   uv --version
   ```
2. Use `uv` to run Python validation commands:
   ```powershell
   uv run python -m ensurepip --upgrade
   uv run python -m pip install --upgrade pip
   uv run python -m pip install pyyaml
   ```
3. Validate YAML files:
   ```powershell
   uv run python -c "import yaml, pathlib, sys; paths=['.github/workflows/test.yml','.github/workflows/publish.yml','.github/dependabot.yml'];
   for p in paths:
       path=pathlib.Path(p)
       yaml.safe_load(path.read_text(encoding='utf-8'))
       print(f'VALID {p}')"
   ```

### 5. Verify CLI help and examples
- Run core CLI help and commands with `uv`:
  ```powershell
  uv run python .\wiki_tool.py --help
  uv run python .\wiki_tool.py source --help
  uv run python .\wiki_tool.py category --help
  uv run python .\wiki_tool.py page --help
  ```
- Test extraction examples:
  ```powershell
  uv run python .\wiki_tool.py source "Module:SlayerConsts/MasterTables" --format json
  uv run python .\wiki_tool.py source "Calculator:Combat level" --format json
  uv run python .\wiki_tool.py category "Calculators" --limit 5 --format json
  uv run python .\batch_extract.py
  ```

## Error Resolution

### Missing `requirements.txt`
- Create it with the project runtime dependencies.
- Update workflows to use `pip install -r requirements.txt`.

### `uv run` environment missing pip
- Bootstrap pip with:
  ```powershell
  uv run python -m ensurepip --upgrade
  ```
- Then install packages with `uv run python -m pip install ...`.

### YAML validation failure
- Use `uv run python -m pip install pyyaml`.
- Load the file with `yaml.safe_load()` and inspect the reported line number.

### Stale CLI examples or commands
- Confirm actual commands in `wiki_tool.py`.
- Replace dead command references in docs with the current CLI names.
- Prefer `uv run python .\wiki_tool.py` for local usage.

## Output
- A documented procedure for updating docs, deployment, and validation.
- Specific commands for `uv`, dependency management, and YAML validation.
- Error handling sections for the most common failure modes.
- A reusable skill saved at `.agents/skills/SKILL.md`.

## Suggested prompts
- "Update project documentation and validation procedure for osrs-wiki-cli"
- "Validate GitHub Actions workflows and Dependabot configuration using uv"
- "Fix docs and CI to use the current wiki_tool.py CLI commands"
