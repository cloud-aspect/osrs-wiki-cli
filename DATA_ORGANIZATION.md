# OSRS Wiki Data Organization System

A portable file writing and organization system for extracted OSRS Wiki data with structured storage and easy retrieval.

## Overview

The data organization system provides:
- **Structured file storage** with automatic categorization
- **Metadata preservation** for extraction tracking
- **Multiple format support** (JSON, text, Lua, wikitext)
- **Batch extraction capabilities** with organized output
- **Command-line management tools** for data exploration

## Quick Start

### 1. Basic Data Organization

```bash
# Run the data organizer (creates directory structure and organizes existing files)
python data_organizer.py

# Extract and save data with the enhanced wiki tool
python wiki_tool.py source "Module:SlayerConsts/MasterTables" --templates --save

# List organized data
python data_manager.py list
```

### 2. Batch Data Extraction

```bash
# Run the auto-generated batch extraction script
python batch_extract.py
```

### 3. Data Management

```bash
# List all organized files
python data_manager.py list

# Search for specific files
python data_manager.py extract "slayer"

# Export file content in different formats
python data_manager.py export "MasterTables" --format wikitext
```

## Directory Structure

The system automatically creates the following organized structure:

```
data/
├── raw/              # Raw extracted data (general)
├── processed/        # Cleaned and parsed data
├── slayer/           # Slayer-specific data (task weights, masters)
├── calculators/      # Calculator page data and JavaScript
├── modules/          # Lua module exports (.lua files)
├── templates/        # Template wikitext and data
└── metadata/         # Extraction logs and session info
```

## File Organization Rules

### Automatic Categorization

Files are automatically organized based on content:

- **Slayer data** → `data/slayer/`
  - Pages containing "slayer" in the title
  - Slayer master tables, task weights, requirements

- **Calculator data** → `data/calculators/`  
  - Pages starting with "Calculator:"
  - JavaScript calculator configurations

- **Lua modules** → `data/modules/`
  - Pages starting with "Module:"
  - Lua source code saved as `.lua` files

- **Templates** → `data/templates/`
  - Pages starting with "Template:"
  - Template wikitext and documentation

### File Naming

Page titles are sanitized for safe file storage:
- Special characters (`<>:"/\|?*`) replaced with underscores
- Spaces converted to underscores  
- Multiple underscores collapsed
- Examples:
  - `Module:SlayerConsts/MasterTables` → `Module_SlayerConsts_MasterTables.lua`
  - `Calculator:Slayer/Slayer task weight` → `Calculator_Slayer_Slayer_task_weight.json`

## Data Formats

### JSON Metadata Format

All extracted data includes comprehensive metadata:

```json
{
  "extraction_metadata": {
    "page_title": "Module:SlayerConsts/MasterTables",
    "data_type": "source", 
    "extraction_timestamp": "2025-10-13T06:33:59.773830",
    "tool_version": "1.0"
  },
  "data": {
    "page_title": "Module:SlayerConsts/MasterTables",
    "wikitext": "local SlayerConsts = require ('Module:SlayerConsts')...",
    "templates": ["Template:Documentation"],
    "modules": ["ext.pygments.view"]
  }
}
```

### Text Content Files

Source content saved in appropriate formats:
- **Wikitext**: `.wiki` files
- **Lua modules**: `.lua` files  
- **JavaScript**: `.js` files
- **General text**: `.txt` files

## Command-Line Tools

### wiki_tool.py --save

Enhanced extraction with automatic organization:

```bash
# Extract and save raw wikitext + metadata
python wiki_tool.py source "Page Title" --save

# Include templates and modules
python wiki_tool.py source "Module:SlayerConsts" --templates --save

# Save page content with tables and links
python wiki_tool.py page "Calculator:Combat level" --save

# Save category listings
python wiki_tool.py category "Slayer" --save --limit 50
```

### data_manager.py

Comprehensive data management:

```bash
# Organize existing JSON file
python data_manager.py organize calc_source.json --type calculator

# List all organized files
python data_manager.py list

# Filter by category
python data_manager.py list --category slayer

# Search for files by pattern
python data_manager.py extract "task_weight"

# Export content in different formats
python data_manager.py export "MasterTables" --format json
python data_manager.py export "MasterTables" --format wikitext  
python data_manager.py export "MasterTables" --format summary
```

### batch_extract.py

Automated batch processing:

```bash
# Run pre-configured extraction of slayer and calculator data
python batch_extract.py

# Automatically extracts:
# - All slayer master tables and calculation modules
# - Popular calculator pages
# - Creates extraction log with session info
```

## Integration Examples

### Use with Data Analysis

```python
import json
from pathlib import Path

# Load organized slayer data
with open('data/slayer/Module_SlayerConsts_MasterTables.json', 'r') as f:
    slayer_data = json.load(f)

# Extract the Lua source code
lua_source = slayer_data['data']['wikitext']

# Or read the Lua file directly
with open('data/modules/Module_SlayerConsts_MasterTables.lua', 'r') as f:
    lua_code = f.read()
```

### Use with sqlite-utils

```bash
# Convert JSON data to SQLite database
sqlite-utils insert slayer.db extractions data/slayer/*.json

# Query the database
sqlite-utils query slayer.db "SELECT page_title, extraction_timestamp FROM extractions"
```

### Use with Pandas

```python
import pandas as pd
import json
from pathlib import Path

# Load all slayer data into DataFrame
slayer_files = Path('data/slayer').glob('*.json')
data = []

for file in slayer_files:
    with open(file, 'r') as f:
        content = json.load(f)
        data.append({
            'page': content['extraction_metadata']['page_title'],
            'timestamp': content['extraction_metadata']['extraction_timestamp'],
            'wikitext_size': len(content['data'].get('wikitext', '')),
            'templates': len(content['data'].get('templates', []))
        })

df = pd.DataFrame(data)
print(df)
```

## Real-World Use Cases

### Slayer Task Analysis

1. **Extract master tables**:
   ```bash
   python wiki_tool.py source "Module:SlayerConsts/MasterTables" --templates --save
   ```

2. **Access organized data**:
   - Raw JSON: `data/slayer/Module_SlayerConsts_MasterTables.json`
   - Lua source: `data/modules/Module_SlayerConsts_MasterTables.lua`

3. **Parse task weights** from Lua tables for statistical analysis

### Calculator Data Extraction

1. **Extract calculator configs**:
   ```bash
   python wiki_tool.py source "Calculator:Combat level" --save
   python wiki_tool.py source "Calculator:Skill calculators/Hitpoints" --save
   ```

2. **Access organized data**:
   - All calculator data in: `data/calculators/`
   - JavaScript configurations preserved with metadata

### Bulk Wiki Analysis

1. **Run batch extraction**:
   ```bash
   python batch_extract.py
   ```

2. **Analyze extraction logs**:
   ```bash
   python data_manager.py list --category metadata
   ```

3. **Export summaries**:
   ```bash
   python data_manager.py extract "*" > extraction_summary.txt
   ```

## Advanced Features

### Extraction Logging

Every batch extraction creates detailed logs:

```json
{
  "extraction_session": {
    "timestamp": "2025-10-13T06:33:59.773830",
    "pages_extracted": [
      "Module:SlayerConsts/MasterTables",
      "Calculator:Slayer/Slayer task weight"
    ],
    "total_pages": 2,
    "notes": "Batch extraction of slayer and calculator data"
  }
}
```

### Custom Data Processing

Extend the system with custom processors:

```python
from data_organizer import DataOrganizer

organizer = DataOrganizer("my_data")

# Save processed analysis results
analysis_results = {"task_probabilities": {...}}
organizer.save_processed_data("slayer_analysis", analysis_results, "slayer")

# Create custom extraction log
organizer.create_extraction_log(
    ["Page1", "Page2"], 
    "Custom analysis extraction"
)
```

## Best Practices

1. **Always use --save** when extracting data you want to keep
2. **Run batch_extract.py** for comprehensive data collection
3. **Check data_manager.py list** to see what you have
4. **Use extraction logs** to track your data collection sessions
5. **Organize existing files** with `data_manager.py organize`

## Troubleshooting

### Common Issues

**Permission errors**: Ensure write access to the data directory
**Missing files**: Run `python data_organizer.py` to create directory structure
**Import errors**: Ensure `data_organizer.py` is in the same directory as `wiki_tool.py`

### Getting Help

```bash
# Show tool help
python wiki_tool.py --help
python data_manager.py --help

# List available commands
python data_manager.py --help
```

This portable system makes OSRS Wiki data extraction organized, trackable, and ready for analysis or integration with other tools.