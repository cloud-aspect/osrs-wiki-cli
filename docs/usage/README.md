# User Guide

Complete instructions for using osrs-wiki-cli.

## Table of Contents

- [Getting Started](#getting-started)
- [Command Reference](#command-reference)
- [Common Use Cases](#common-use-cases)
- [Output Formats](#output-formats)
- [Tips & Best Practices](#tips--best-practices)

## Getting Started

osrs-wiki-cli is designed for extracting structured data from the Old School RuneScape Wiki. It uses the MediaWiki API to retrieve clean JSON data without HTML parsing.

### Basic Usage Pattern

All commands follow this pattern:
```bash
osrs-wiki-cli <command> [arguments] [options]
```

### Global Options

- `--format` - Output format: `json` (default), `csv`, or `text`
- `--help` - Show help for any command

## Command Reference

### `source` Command

Extract raw wikitext and template information from wiki pages.

```bash
python wiki_tool.py source <page_title> [options]
```

**Options:**
- `--templates` - Include list of templates used on the page
- `--format <format>` - Output format (json, csv, text)

**Examples:**
```bash
# Get Lua module source code
python wiki_tool.py source "Module:SlayerConsts/MasterTables" --format text

# Get calculator page with templates
python wiki_tool.py source "Calculator:Slayer/Slayer task weight" --templates --format json

# Get individual slayer master data
python wiki_tool.py source "Module:Slayer weight calculator" --format text
```

### `category` Command

List pages in a category with pagination support.

```bash
python wiki_tool.py category <category_name> [options]
```

**Options:**
- `--limit <number>` - Maximum pages to return (default: 50)
- `--format <format>` - Output format (json, csv, text)

**Examples:**
```bash
# List calculator pages
python wiki_tool.py category "Calculators" --format csv

# List all modules
python wiki_tool.py category "Modules" --limit 100 --format json
```

## Common Use Cases

### Slayer Task Weight Extraction

The primary use case for this tool is extracting slayer task weight data:

1. **Get the main calculator configuration:**
   ```bash
   python wiki_tool.py source "Calculator:Slayer/Slayer task weight" --templates --format text
   ```

2. **Extract the Lua weight tables:**
   ```bash
   python wiki_tool.py source "Module:SlayerConsts/MasterTables" --format text
   ```

3. **Get the calculation logic:**
   ```bash
   python wiki_tool.py source "Module:Slayer weight calculator" --format text
   ```

### Calculator Page Analysis

For other calculator pages:

1. **List all calculators:**
   ```bash
   python wiki_tool.py category "Calculators" --format csv
   ```

2. **Extract specific calculator:**
   ```bash
   python wiki_tool.py source "Calculator:Combat level" --templates --format json
   ```

### Template and Module Discovery

Find related templates and modules:

```bash
# List all Slayer-related modules
python wiki_tool.py category "Modules" --format json | grep -i slayer

# Get template source
python wiki_tool.py source "Template:Infobox Monster" --format text
```

## Output Formats

### JSON Format (Default)

Structured data with metadata:

```json
{
  "page_title": "Module:SlayerConsts/MasterTables",
  "wikitext": "local SlayerConsts = require ('Module:SlayerConsts')...",
  "templates": ["Template:Documentation"],
  "modules": ["Module:SlayerConsts"]
}
```

### Text Format

Clean wikitext content only:

```
local SlayerConsts = require ('Module:SlayerConsts')

local p = {}

local turael = {
[SlayerConsts.TASK_BANSHEES] = { name = "[[Banshee]]s", requirements = {Slayer = 15, Combat = 20, Quest = SlayerConsts.QUEST_PRIEST_IN_PERIL}, weight = 8},
...
```

### CSV Format

Tabular data (when applicable):

```csv
page_title,wikitext_length,templates_count,modules_count
Module:SlayerConsts/MasterTables,12486,1,1
```

## Tips & Best Practices

### Rate Limiting

- The tool automatically includes 1-second delays between requests
- Don't run multiple instances simultaneously
- Use specific page names rather than broad category searches when possible

### Page Title Format

- Use exact wiki page titles: `"Calculator:Slayer/Slayer task weight"`
- Include namespace prefixes: `"Module:"`, `"Template:"`, `"Category:"`
- Use underscores or spaces (both work): `"Desert_Treasure"` or `"Desert Treasure"`

### Working with Large Datasets

- Use `--limit` to control category list sizes
- Process data in chunks for large extractions
- Save intermediate results to files for complex workflows

### Error Handling

Common issues and solutions:

- **"Page not found"** - Check exact page title spelling and capitalization
- **"Rate limited"** - Wait a few minutes before retrying
- **"Empty response"** - Page may be empty or redirect; check on wiki

### MediaWiki API Best Practices

This tool follows MediaWiki API guidelines:

- Descriptive User-Agent header
- Sequential requests with rate limiting
- Proper error handling for API responses
- Respectful request patterns

---

**Next:** [API Reference](../api/README.md) | **Previous:** [Main README](../../README.md)