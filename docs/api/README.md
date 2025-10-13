# API Reference

Complete command-line interface reference for the OSRS Wiki Page Tool.

## Table of Contents

- [Global Options](#global-options)
- [Commands](#commands)
  - [source](#source-command)
  - [category](#category-command)
- [Output Formats](#output-formats)
- [Error Codes](#error-codes)

## Global Options

These options are available for all commands:

### `--format FORMAT`

Specify the output format for results.

**Choices:** `json` (default), `csv`, `text`

**Example:**
```bash
python wiki_tool.py source "Module:SlayerConsts/MasterTables" --format json
```

### `--help`

Show help information for the command.

**Example:**
```bash
python wiki_tool.py --help
python wiki_tool.py source --help
```

## Commands

### `source` Command

Extract raw wikitext and template information from a wiki page.

```
Usage: python wiki_tool.py source PAGE_TITLE [OPTIONS]

Extract wikitext source and template information from a wiki page

Arguments:
  PAGE_TITLE  The exact title of the wiki page to extract

Options:
  --templates         Include list of templates used on the page
  --format FORMAT     Output format: json (default), csv, text
  --help              Show this help message and exit
```

**Arguments:**

- `PAGE_TITLE` - The exact title of the wiki page to extract. Must match the wiki page title exactly, including namespace prefixes.

**Options:**

- `--templates` - When specified, includes a list of all templates referenced on the page in the output
- `--format FORMAT` - Output format (json, csv, text)

**Examples:**

```bash
# Extract Lua module source
python wiki_tool.py source "Module:SlayerConsts/MasterTables"

# Get calculator page with template list
python wiki_tool.py source "Calculator:Slayer/Slayer task weight" --templates

# Get wikitext as plain text
python wiki_tool.py source "Template:Infobox Monster" --format text
```

**Output Structure (JSON):**

```json
{
  "page_title": "string",
  "wikitext": "string", 
  "templates": ["string", ...],  // only if --templates specified
  "modules": ["string", ...]     // only if --templates specified
}
```

### `category` Command

List pages in a category with pagination support.

```
Usage: python wiki_tool.py category CATEGORY_NAME [OPTIONS]

List pages in a wiki category

Arguments:
  CATEGORY_NAME  The name of the category to list (with or without 'Category:' prefix)

Options:
  --limit INTEGER     Maximum number of pages to return (default: 50)
  --format FORMAT     Output format: json (default), csv, text  
  --help              Show this help message and exit
```

**Arguments:**

- `CATEGORY_NAME` - The name of the category to list. Can include the `Category:` prefix or not.

**Options:**

- `--limit INTEGER` - Maximum number of pages to return. Default is 50. Maximum allowed is 500 per MediaWiki API limits.
- `--format FORMAT` - Output format (json, csv, text)

**Examples:**

```bash
# List calculator pages
python wiki_tool.py category "Calculators" --format json

# List modules without category prefix
python wiki_tool.py category "Modules" --limit 100

# Get CSV output
python wiki_tool.py category "Templates" --format csv --limit 25
```

**Output Structure (JSON):**

```json
{
  "category": "string",
  "total_pages": integer,
  "pages": [
    {
      "pageid": integer,
      "ns": integer,
      "title": "string",
      "type": "page|subcat",
      "timestamp": "string"
    },
    ...
  ]
}
```

## Output Formats

### JSON Format

The default structured format with complete metadata:

```json
{
  "page_title": "Calculator:Slayer/Slayer task weight",
  "wikitext": "{{external|rs=calculator:Slayer}}{{Calc use|Calculator:Slayer/Slayer task weight/Template}}...",
  "templates": [
    "Template:External", 
    "Template:Calc use",
    "Template:JSCalculator"
  ],
  "modules": [
    "Calculator:Slayer/Slayer task weight/Template"
  ]
}
```

### CSV Format

Tabular format suitable for spreadsheet import. Structure varies by command:

**Source command:**
```csv
page_title,wikitext_length,templates_count,modules_count
"Module:SlayerConsts/MasterTables",12486,1,0
```

**Category command:**
```csv
title,pageid,ns
"Calculator:Combat level",12345,0
"Calculator:Experience table",12346,0
```

### Text Format

Plain text output of the primary content:

**Source command:** Returns raw wikitext only
**Category command:** Returns page titles only, one per line

## Error Codes

The tool uses standard exit codes:

- **0** - Success
- **1** - General error (network, parsing, etc.)
- **2** - Invalid arguments or usage
- **3** - MediaWiki API error (rate limit, missing page, etc.)

## MediaWiki API Integration

### Rate Limiting

The tool automatically implements rate limiting:
- 1 second delay between requests
- Respectful request patterns
- Exponential backoff on errors

### User Agent

All requests include a descriptive User-Agent header:
```
OSRSWikiTool/1.0 (Python CLI tool for OSRS Wiki data extraction)
```

### Error Handling

The tool handles common MediaWiki API errors:

- **Missing pages** - Returns appropriate error message
- **Rate limiting** - Automatically retries with backoff
- **Network errors** - Retries with exponential backoff
- **Malformed responses** - Clear error reporting

### API Endpoints Used

- **Page content:** `action=parse&prop=wikitext&page=<title>`
- **Category members:** `action=query&list=categorymembers&cmtitle=<category>`
- **Templates/modules:** `action=parse&prop=templates&modules&page=<title>`

---

**Next:** [Development Guide](../development/README.md) | **Previous:** [User Guide](../usage/README.md)