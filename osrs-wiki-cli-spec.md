````markdown
# osrs-wiki-cli: Project Definition

This document outlines the project specifications for osrs-wiki-cli, a modern command-line utility designed for on-demand data extraction from the Old School RuneScape Wiki. The tool reliably extracts structured data in formats optimized for RuneLite plugins, web applications, and data analysis workflows using the MediaWiki API.

## 1. Core Objectives

The primary goal is to create a data extraction pipeline that enables developers and tool creators to access wiki content in structured, programmable formats. Users can extract data for their own plugin development, spreadsheet analysis, database integration, or custom tool creation.

### Key Requirements:
- **Structured Data Output**: JSON, CSV, and raw text formats optimized for programmatic consumption
- **Plugin-Ready Formats**: Data structures suitable for RuneLite plugins, calculators, and third-party tools  
- **Modular Extraction**: One command extracts one specific data type with consistent output structure
- **Developer Integration**: Clean API responses enabling seamless integration into existing workflows
- **Batch Processing**: Support for extracting multiple related pages for comprehensive data sets
- **Template Access**: Direct access to underlying templates, modules, and Lua scripts for custom parsing
- **Category Enumeration**: Complete lists for building indexes and data catalogs
- **Command-Line Interface**: Manual invocation for development workflows and automation scripts

## 2. Tool Stack & Architecture

- **Language**: Python (3.8+ for maximum compatibility)
- **CLI Framework**: argparse (built-in, zero external dependencies for maximum portability)
- **API Interaction**: `requests` library for MediaWiki API communication
- **Text Processing**: Beautiful Soup for parsing structured content when needed
- **Output Formats**: Native JSON and CSV libraries for structured data output
- **Data Organization**: Automatic categorization and file management for batch operations

The architecture follows a single-script design pattern with modular subcommands, each producing consistent output formats that can be directly consumed by external tools, plugins, and data processing pipelines.

## 3. Data Extraction Method

The tool exclusively uses the **MediaWiki API** to retrieve clean, structured data without HTML parsing dependencies. All responses are processed as JSON, ensuring consistent data formats suitable for:

- **Plugin Development**: Direct integration into RuneLite plugins and other game clients
- **Database Population**: Clean data structures for SQLite, PostgreSQL, or other databases  
- **Spreadsheet Analysis**: CSV outputs optimized for Excel, Google Sheets, and data analysis
- **Custom Tools**: JSON formats suitable for web applications, mobile apps, and desktop tools
- **Data Processing**: Structured formats compatible with pandas, numpy, and other data libraries

## 4. Command Structure

The tool follows a consistent pattern designed for integration into development workflows:

```
python wiki_tool.py COMMAND PAGE_TITLE [OPTIONS]
```

### Output Format Standards:
- **JSON**: Structured data with consistent field names and nesting for programmatic access
- **CSV**: Tabular data optimized for spreadsheet import and database loading
- **Text**: Raw content (wikitext, Lua code, template source) for custom parsing

### Integration-Focused Options:
- `--format`: Choose output format based on intended use case
- `--save`: Organize extracted data into categorized file structures  
- `--data-dir`: Specify output directory for batch processing workflows

## 5. Subcommands

### `source` Command - Raw Data Extraction

- **Purpose**: Extract underlying source code and structure for custom parsing and plugin development
- **Use Cases**: 
  - Lua modules for game logic integration
  - Template structures for custom parsers  
  - JavaScript calculator configurations
  - Wikitext for content analysis
- **Output**: Raw source code, template dependencies, module references in structured format

### `category` Command - Content Discovery  

- **Purpose**: Generate comprehensive lists for building data catalogs and indexes
- **Use Cases**:
  - Item databases for trading applications
  - Monster lists for combat calculators  
  - Complete category enumeration for data mining
  - Page discovery for batch processing workflows
- **Output**: Paginated lists with metadata suitable for database loading

### `page` Command - Structured Content (Planned)

- **Purpose**: Extract parsed content in formats optimized for direct integration
- **Use Cases**:
  - Infobox data for item databases
  - Table extraction for statistical analysis
  - Cross-reference data for relationship mapping
- **Output**: Structured JSON with consistent field naming and type handling

## 6. API Integration & Data Standards

### Developer-Friendly Practices:
- **User-Agent**: Descriptive headers for API monitoring and debugging
- **Rate Limiting**: Built-in 1-second delays between requests for sustainable batch processing
- **Error Handling**: Clear error messages with retry logic for production workflows
- **Response Validation**: Automatic verification of data completeness and format consistency

### Output Format Specifications:

#### JSON Output Structure:
```json
{
  "page_title": "Module:SlayerConsts/MasterTables", 
  "extraction_date": "2024-01-15T10:30:00Z",
  "data_type": "lua_module",
  "wikitext": "local SlayerConsts = require ('Module:SlayerConsts')...",
  "dependencies": {
    "templates": ["Template:Documentation"],
    "modules": ["Module:SlayerConsts"]
  },
  "metadata": {
    "size_bytes": 12486,
    "last_modified": "2023-12-10T15:22:00Z"
  }
}
```

#### CSV Output Standards:
- Consistent column naming for database import
- Proper escaping for complex text content  
- Metadata columns for data lineage tracking
- UTF-8 encoding for international character support

### API Endpoint Mapping:
- **Raw Content**: `action=parse&prop=wikitext` for template and module source
- **Dependencies**: `action=parse&prop=templates|modules` for dependency mapping  
- **Category Lists**: `action=query&list=categorymembers` with pagination support
- **Page Metadata**: Combined queries for comprehensive data extraction

## 7. Implementation Architecture

### Development Environment Setup:
```bash
# Minimal dependency setup for maximum compatibility
python -m venv venv
venv\Scripts\activate  # Windows
pip install requests beautifulsoup4

# Zero-dependency CLI framework using built-in argparse
python wiki_tool.py --help
```

### Core Implementation Pattern:

#### Data Extraction Pipeline:
1. **Input Validation**: Page existence verification and parameter validation
2. **API Communication**: MediaWiki API calls with proper rate limiting and error handling  
3. **Format Processing**: Convert raw API responses to structured output formats
4. **Output Generation**: JSON, CSV, or text output optimized for target use case

#### Plugin Integration Support:
```python
# Example: Extract Lua module for RuneLite plugin
def extract_for_plugin_development(page_title):
    """Extract structured data suitable for game client integration"""
    response = get_wikitext_source(page_title)
    return {
        'source_code': response['wikitext'],
        'dependencies': response['modules'],  
        'last_updated': response['timestamp'],
        'integration_ready': True
    }
```

#### Batch Processing Architecture:
- **Data Organization**: Automatic categorization by content type (modules, calculators, templates)
- **Dependency Tracking**: Map template and module relationships for complete data sets
- **Incremental Updates**: Track modification timestamps for efficient re-processing
- **Output Management**: Organized file structures for large-scale data extraction

### Plugin Development Integration Points:

#### RuneLite Plugin Data Format:
```java
// Generated from: python wiki_tool.py source "Module:SlayerConsts/MasterTables" 
public class SlayerTaskWeights {
    private static final Map<String, Integer> DURADEL_WEIGHTS = Map.of(
        "Abyssal demons", 12,
        "Black dragons", 9,
        // ... extracted from Lua module
    );
}
```

#### Database Integration Format:
```sql
-- Generated from: python wiki_tool.py category "Items" --format csv
CREATE TABLE osrs_items (
    item_name VARCHAR(255),
    category VARCHAR(100), 
    extraction_date TIMESTAMP,
    wiki_page_url VARCHAR(500)
);
```

## 8. API Reference Documentation

The following URLs provide authoritative documentation for the APIs and libraries used in this project:

### MediaWiki & OSRS Wiki API Documentation:
- MediaWiki Action API: `https://www.mediawiki.org/wiki/API:Main_page`
- MediaWiki API Query Module: `https://www.mediawiki.org/wiki/API:Query`
- MediaWiki API Parsing Module: `https://www.mediawiki.org/wiki/API:Parsing`
- OSRS Wiki API Endpoint: `https://oldschool.runescape.wiki/api.php`
- MediaWiki API Sandbox (for testing): `https://www.mediawiki.org/wiki/Special:ApiSandbox`

### Python Library Documentation:
- Typer: `https://typer.tiangolo.com/`
- Requests: `https://requests.readthedocs.io/en/latest/`
- Beautiful Soup 4: `https://www.crummy.com/software/BeautifulSoup/bs4/doc/`
- Python `json` module: `https://docs.python.org/3/library/json.html`
- Python `csv` module: `https://docs.python.org/3/library/csv.html`

## 9. Real-World Integration Examples

### Plugin Development Workflow:
```bash
# Extract complete monster data for combat plugin
python wiki_tool.py category "Monsters" --format json --save

# Get calculator configurations for DPS analysis
python wiki_tool.py source "Calculator:Combat level" --format text

# Extract item data for trade tracking plugin  
python wiki_tool.py category "Items" --format csv --limit 1000
```

### Data Analysis Pipeline:
```python
# Integration with pandas for statistical analysis
import json, pandas as pd

# Load extracted wiki data
with open('data/modules/Module_SlayerConsts_MasterTables.json') as f:
    slayer_data = json.load(f)

# Convert to DataFrame for analysis
df = pd.DataFrame(slayer_data['parsed_tables'])
print(df.groupby('slayer_master')['task_weight'].sum())
```

### Database Integration Example:
```bash
# Extract all calculator pages for comprehensive dataset
python wiki_tool.py category "Calculators" --format csv --save

# Import CSV data into SQLite database
sqlite3 osrs_data.db ".import data/calculators.csv calculators"
sqlite3 osrs_data.db "SELECT * FROM calculators WHERE page_title LIKE '%Combat%'"
```

### Custom Tool Development:
The structured output formats enable developers to build:
- **Trading Applications**: Using item category data and price calculators  
- **Combat Analyzers**: Using monster stats and combat calculators
- **Quest Guides**: Using quest requirement templates and walkthroughs
- **Skill Calculators**: Using experience tables and training method data
- **Game Databases**: Using comprehensive category extractions for complete datasets

## 10. Success Criteria & Integration Goals

### Primary Success Metrics:
- **Developer Adoption**: Clean output formats that integrate seamlessly into existing development workflows
- **Data Completeness**: Extract all available structured data without requiring manual post-processing  
- **Format Consistency**: Standardized JSON/CSV schemas suitable for database loading and API consumption
- **Batch Reliability**: Handle large-scale extractions (1000+ pages) with proper error recovery
- **Plugin-Ready Output**: Data formats that can be directly consumed by RuneLite, web applications, and mobile apps

### Integration Success Examples:

#### RuneLite Plugin Integration:
```java
// Direct integration of extracted wiki data
@Inject private Client client;

// Load wiki data extracted via: python wiki_tool.py source "Module:SlayerConsts"  
private final Map<Integer, SlayerTask> taskData = loadWikiExtraction("slayer_tasks.json");

public void updateSlayerOverlay() {
    int currentTask = client.getSlayerTaskId();
    SlayerTask task = taskData.get(currentTask);
    overlay.setTaskInfo(task.getName(), task.getWeight(), task.getRequirements());
}
```

#### Web Application Data Loading:
```javascript
// Load extracted category data for item search
fetch('/data/categories/Items.json')
  .then(response => response.json())  
  .then(items => {
    // Populate searchable item database
    itemDatabase.loadWikiData(items.pages);
    searchIndex.build(items.pages.map(p => p.title));
  });
```

#### Database Analytics Pipeline:
```sql
-- Load extracted calculator data for analysis
CREATE TABLE wiki_calculators AS 
SELECT * FROM read_csv_auto('data/calculators/Calculator_*.csv');

-- Analyze calculator usage patterns  
SELECT category, COUNT(*) as page_count, 
       AVG(content_length) as avg_size
FROM wiki_calculators 
GROUP BY category;
```

### Production Deployment Features:
- **Automated Batch Processing**: Schedule regular extractions for data freshness
- **API Rate Compliance**: Built-in throttling for production-scale usage
- **Error Recovery**: Automatic retry logic for network issues and API limits  
- **Data Validation**: Schema validation for output format consistency
- **Incremental Updates**: Only extract modified pages for efficient processing

### Example Production Usage:
```bash
# Complete dataset extraction for application deployment
python wiki_tool.py category "Items" --format json --save --data-dir /app/data/
python wiki_tool.py category "Monsters" --format json --save --data-dir /app/data/
python wiki_tool.py source "Module:SlayerConsts/MasterTables" --format json --save

# Verify data completeness for deployment
ls -la /app/data/categories/  # Check category extractions  
ls -la /app/data/modules/     # Check module extractions
ls -la /app/data/calculators/ # Check calculator extractions
```