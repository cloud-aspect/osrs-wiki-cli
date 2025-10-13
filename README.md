# osrs-wiki-cli

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/v/release/cloud-aspect/osrs-wiki-cli?include_prereleases)](https://github.com/cloud-aspect/osrs-wiki-cli/releases)

A modern CLI utility for extracting structured data from the Old School RuneScape Wiki. Built for developers who need clean, programmatically accessible data formats for RuneLite plugins, web applications, and data analysis workflows.

## Features

- 🔌 **Plugin-Ready Data Formats** - JSON and CSV outputs optimized for RuneLite plugins and external tools
- 📊 **Structured Data Extraction** - Clean API responses suitable for databases and spreadsheet analysis  
- 🔍 **MediaWiki API Integration** - Direct JSON access without HTML parsing dependencies
- 📄 **Multiple Output Formats** - JSON, CSV, and raw text formats for different integration needs
- 🏗️ **Modular Commands** - Composable subcommands for specific data extraction tasks
- 🛡️ **Developer-Friendly** - Rate limiting, error handling, and batch processing support

## Quick Start

```bash
# Extract Lua module data for plugin development  
osrs-wiki-cli source "Module:SlayerConsts/MasterTables" --format json

# Get calculator configurations with dependencies
osrs-wiki-cli source "Calculator:Agility" --templates --format text

# List all items in a category for data analysis
osrs-wiki-cli category "Items" --format csv --limit 50

# Extract template structure for parsing
osrs-wiki-cli source "Template:Infobox Item" --format text
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/cloud-aspect/osrs-wiki-cli.git
   cd osrs-wiki-cli
   ```

2. **Install osrs-wiki-cli:**
   ```bash
   # Option 1: Install from PyPI (recommended)
   pip install osrs-wiki-cli
   
   # Option 2: Install from source
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/macOS
   pip install requests beautifulsoup4
   ```

## Usage

The tool provides commands designed for different integration workflows:

### Commands

- **`source`** - Extract raw source code, templates, and dependencies for custom parsing
- **`category`** - Generate complete page lists for building indexes and data catalogs  
- **`page`** (planned) - Extract parsed tables and infoboxes in structured formats
- **`search`** (planned) - Search wiki content with filtering for targeted data discovery

### Integration Examples

```bash
# Extract all items for a trading application database
osrs-wiki-cli category "Items" --format csv --save

# Get monster data for combat calculator development  
osrs-wiki-cli category "Monsters" --format json --limit 100

# Extract Lua modules for game logic integration
osrs-wiki-cli source "Module:SlayerConsts/MasterTables" --format text
```

## Data Integration Examples

### RuneLite Plugin Development
```java
// Using extracted JSON data in a RuneLite plugin
@Slf4j
public class WikiDataPlugin extends Plugin {
    private Map<String, ItemInfo> itemDatabase;
    
    @Override
    protected void startUp() {
        // Load extracted wiki data: python wiki_tool.py category "Items" --format json
        itemDatabase = loadWikiItemData("data/categories/Items.json");
        log.info("Loaded {} items from wiki extraction", itemDatabase.size());
    }
}
```

### Web Application Integration
```javascript
// Load extracted category data for web app
async function loadGameData() {
    // Data from: python wiki_tool.py category "Calculators" --format json --save
    const calculators = await fetch('/data/categories/Calculators.json').then(r => r.json());
    
    // Build searchable calculator index
    const searchIndex = calculators.pages.map(calc => ({
        name: calc.title.replace('Calculator:', ''),
        url: calc.title,
        lastUpdated: calc.timestamp
    }));
    
    return { calculators: searchIndex };
}
```

### Database Loading
```python
# Load extracted CSV data into pandas/SQLite
import pandas as pd
import sqlite3

# Load data from: osrs-wiki-cli category "Items" --format csv --save  
df = pd.read_csv('data/categories/Items.csv')

# Create searchable database
conn = sqlite3.connect('osrs_data.db')
df.to_sql('wiki_items', conn, if_exists='replace', index=False)

# Query for item lookup
items = pd.read_sql("SELECT * FROM wiki_items WHERE title LIKE '%sword%'", conn)
print(f"Found {len(items)} sword items")
```

For detailed usage instructions, see the [User Guide](docs/usage/README.md).

## Documentation

- **[User Guide](docs/usage/README.md)** - Complete usage instructions and examples
- **[API Reference](docs/api/README.md)** - Command-line interface documentation
- **[Developer Guide](docs/development/README.md)** - Contributing and development setup
- **[Data Examples](docs/examples/README.md)** - Sample outputs and use cases

## Project Background

This tool provides developers and data analysts with programmatic access to the OSRS Wiki's extensive structured content, including:

- **Lua Modules**: Complete game logic and data tables for plugin integration
- **Calculator Configurations**: JavaScript and template-based calculators with parameters
- **Category Systems**: Comprehensive lists for building complete datasets  
- **Template Structures**: Underlying data formats for custom parsing solutions

The extracted data formats are designed for seamless integration into RuneLite plugins, web applications, mobile apps, databases, and custom analysis tools.

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/development/contributing.md) for details on:

- Setting up the development environment  
- Code style and standards
- Submitting pull requests
- Reporting issues

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Old School RuneScape Wiki](https://oldschool.runescape.wiki/) for providing comprehensive game data
- [MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page) for reliable programmatic access
- The OSRS community for maintaining accurate wiki content

## Related Projects

- [sqlite-utils](https://github.com/simonw/sqlite-utils) - CLI tool and library for SQLite databases
- [osrs-cli](https://github.com/LucasPickering/osrs-cli) - Command line tools for OSRS calculations
- [RuneLite](https://github.com/runelite/runelite) - Open source OSRS client with extensive APIs

---

**Need help?** Check out the [FAQ](docs/usage/faq.md) or [open an issue](https://github.com/cloud-aspect/osrs-wiki-cli/issues/new).