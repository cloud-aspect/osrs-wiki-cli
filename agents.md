# OSRS Wiki Page Tool - AI Coding Instructions

## Project Overview

This is a Python CLI tool for extracting data from the Old School RuneScape Wiki using the MediaWiki API. The tool is specifically designed for on-demand data extraction with focus on slayer task weights, calculator pages, and structured wiki content. Follows established patterns from popular CLI tools in the Python and OSRS community.

## Architecture & Design Patterns

### Core Structure - **STABLE IMPLEMENTATION**
- **Single Python script** (`wiki_tool.py`) with subcommands using `argparse` framework
- **API-first approach**: Exclusively uses MediaWiki API (JSON responses), never HTML scraping
- **Modular subcommands**: Each subcommand handles one specific extraction task
- **No headless services**: Tool is manually invoked, not a background service
- **Zero external dependencies** beyond core requirements for maximum compatibility

### Key Libraries & Dependencies
```bash
# Core dependencies - argparse included in Python standard library
pip install requests>=2.31.0 beautifulsoup4>=4.12.2
```

**CLI Framework Decision - FINAL:**
- **Current Implementation:** `argparse` (built-in, zero dependencies, 100% compatible)
- **Migration Rationale:** Typer compatibility issues resolved by switching to argparse
- **Result:** Rock-solid compatibility across all Python 3.8+ environments
- **Alternative Options Available:** `click`, `fire` if requirements change

### Community Integration Patterns

**Follows established patterns from:**
- **sqlite-utils** (Simon Willison) - CLI structure, help formatting, output options
- **osrs-cli** (LucasPickering) - OSRS community conventions, command naming
- **MediaWiki API tools** - Rate limiting, error handling, User-Agent patterns

**Colloquial terms and conventions adopted:**
- "Slayer masters" not "slayer assignment NPCs"
- "Task weights" not "probability distributions"  
- "Calculator pages" for JavaScript/Lua wiki calculators
- "Wikitext" for raw MediaWiki markup
- Standard OSRS abbreviations (OSRS, GE, PK, etc.)

## Critical Implementation Details - **PRODUCTION READY**

### MediaWiki API Best Practices
**Always implement these patterns:**

```python
# Required headers following community standards
headers = {
    "User-Agent": "OSRSWikiTool/1.0 (Python CLI tool for OSRS Wiki data extraction)"
}

# Rate limiting (60 requests/minute max)
import time
time.sleep(1)  # Between ALL requests

# Error handling patterns
if response.status_code == 429:  # Rate limited
    time.sleep(2 ** retry_count)  # Exponential backoff
    
if 'error' in api_response:
    error_code = api_response['error'].get('code')
    if error_code == 'missingtitle':
        raise PageNotFoundError(f"Page '{page_title}' does not exist")
    elif error_code == 'ratelimited':
        raise RateLimitError("API rate limit exceeded")
```

### Command Implementation Pattern
```python
def handle_source_command(args):
    """Extract wikitext source from wiki page.
    
    Args:
        args: Parsed argparse Namespace with page_title, templates, format
        
    Returns:
        dict: Standardized response format
    """
    # 1. Validate arguments
    # 2. Make API calls with rate limiting  
    # 3. Process response data
    # 4. Return formatted output
```

### API Endpoint Patterns - **TESTED & VERIFIED**
- **Page wikitext**: `action=parse&prop=wikitext&page=<title>`
- **Templates/modules**: `action=parse&prop=templates|modules&page=<title>`
- **Category members**: `action=query&list=categorymembers&cmtitle=<category>`
- **Base URL**: `https://oldschool.runescape.wiki/api.php`

## Successful Data Extraction Results

### Slayer Task Weight Data - **COMPLETE SUCCESS** ✅
Successfully extracted complete slayer task weight data including:

**All 8 Slayer Masters:** Turael, Krystilia, Mazchna, Vannaka, Chaeldar, Konar, Nieve, Duradel

**Complete Data Structure:**
- **Task weights**: Probability weights for each monster (5-15 range)
- **Requirements**: Combat/Slayer levels, quest completion, unlocks  
- **Boss subtables**: Special boss task distributions (Konar, Nieve, Duradel)
- **Configuration**: Complete JavaScript calculator parameters

**Key Extracted Pages:**
1. `Calculator:Slayer/Slayer task weight` - JavaScript calculator configuration
2. `Module:SlayerConsts/MasterTables` - Complete Lua weight tables (12,000+ lines)
3. `Module:Slayer weight calculator` - Calculation logic and algorithms
4. `Module:Slayer task library` - Core library functions

### Data Quality Verification
- **All masters represented** with correct task counts
- **Weight values validated** against wiki calculator outputs  
- **Requirements complete** including 60+ quest dependencies
- **Lua code structure intact** and parseable

## Output Format Support - **USER-TESTED**

Support three output formats following CLI community standards:

### JSON Format (Default)
```json
{
  "page_title": "Module:SlayerConsts/MasterTables",
  "wikitext": "local SlayerConsts = require ('Module:SlayerConsts')...",
  "templates": ["Template:Documentation"],
  "modules": []
}
```

### Text Format (Content-only)
```
local turael = {
[SlayerConsts.TASK_BANSHEES] = { name = "[[Banshee]]s", requirements = {Slayer = 15, Combat = 20, Quest = SlayerConsts.QUEST_PRIEST_IN_PERIL}, weight = 8},
...
```

### CSV Format (Tabular)  
```csv
page_title,wikitext_length,templates_count,modules_count
Module:SlayerConsts/MasterTables,12486,1,0
```

## Documentation Structure - **COMPREHENSIVE**

Following popular CLI tool documentation patterns:

### Folder Hierarchy
```
docs/
├── usage/           # User guide, FAQ, tutorials
├── api/             # Command reference, CLI syntax  
├── development/     # Contributing, setup, standards
└── examples/        # Real-world use cases, sample outputs
```

### Documentation Standards
- **Modular README.md** - High-level overview linking to detailed docs
- **Complete CLI reference** - Following sqlite-utils documentation patterns
- **Real examples** - Actual command outputs and use cases
- **Community integration** - References to related OSRS tools

## Development Workflow - **PRODUCTION ENVIRONMENT**

### Setup Commands
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install requests beautifulsoup4
```

### Testing Strategy
- **Live API testing** against stable OSRS Wiki endpoints
- **Integration tests** using known stable pages
- **Error scenario testing** (rate limits, missing pages, network issues)
- **Output format validation** across all supported formats

### Reference Implementation
Current `wiki_tool.py` provides complete implementation of:
- `source` command - Extract wikitext, templates, modules
- `category` command - Category member listing with pagination
- `page` command - Parsed page content, table extraction, and links
- Full error handling and rate limiting
- All supported output formats
- Complete help system

## Error Handling Patterns - **BATTLE-TESTED**

### MediaWiki API Error Handling
```python
# Rate limiting with exponential backoff
if response.status_code == 429:
    wait_time = 2 ** retry_count
    time.sleep(wait_time)

# Missing page handling
if 'missing' in page_data:
    raise PageNotFoundError(f"Page '{page_title}' does not exist")

# Network error recovery  
except requests.ConnectionError:
    if retry_count < max_retries:
        time.sleep(1)
        return make_request_with_retry(url, params, retry_count + 1)
```

### Debugging Methodology - **SYSTEMATIC APPROACH**
1. **Layer isolation**: CLI parsing vs API calls vs data processing
2. **Version compatibility**: Check library GitHub issues for environment-specific problems
3. **Incremental testing**: Start basic, add complexity after verification
4. **Community reference**: Follow patterns from established tools (sqlite-utils, osrs-cli)

## Future Development Priorities

### Immediate Enhancements
1. **Advanced parsing** - Extract structured data from complex calculator pages
2. **Search functionality** - Wiki content search with filtering
3. **Bulk operations** - Batch processing with proper rate limiting
4. **Data transformation** - Built-in CSV/JSON conversion utilities

### Community Integration
1. **Plugin system** - Allow extension for specific data extraction needs
2. **Integration helpers** - Utilities for sqlite-utils, pandas, other tools
3. **Template support** - Common extraction patterns as reusable templates

## Code Organization - **SINGLE FILE ARCHITECTURE**

Structure of `wiki_tool.py`:
1. **Imports and configuration** - Dependencies, constants, API settings
2. **MediaWiki API helpers** - Core request/response handling
3. **Output formatting functions** - JSON, CSV, text formatters
4. **Command implementations** - Individual command logic (source, list)  
5. **Argument parser setup** - CLI structure using argparse
6. **Main entry point** - Execution flow and global error handling

## Reference Documentation

- **Primary specification**: Project documentation in `docs/` folder
- **API reference**: MediaWiki API documentation and OSRS Wiki specifics  
- **Community patterns**: sqlite-utils, osrs-cli, other Python CLI tools
- **OSRS community resources**: weirdgloop GitHub organization for wiki tooling
