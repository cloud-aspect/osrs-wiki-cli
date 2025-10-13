# Frequently Asked Questions

Common questions and solutions for using the OSRS Wiki Page Tool.

## General Usage

### Q: What is this tool designed for?

**A:** This tool is specifically designed for extracting structured data from the Old School RuneScape Wiki using the MediaWiki API. The primary use case is extracting slayer task weight data from complex calculator pages, but it works for any wiki content.

### Q: Why not use web scraping instead of the API?

**A:** The MediaWiki API provides:
- Clean, structured JSON responses
- Better reliability and performance  
- No HTML parsing complexity
- Rate limiting compliance
- Access to raw wikitext and templates

### Q: Can I use this for other MediaWiki sites?

**A:** Yes, but you'll need to modify the base URL and possibly the User-Agent header. The tool is currently configured specifically for the OSRS Wiki.

## Installation & Setup

### Q: What are the minimum requirements?

**A:** 
- Python 3.8 or higher
- `requests` library (>=2.31.0)
- `beautifulsoup4` library (>=4.12.2)
- Internet connection for API access

### Q: Why did you choose argparse over other CLI frameworks?

**A:** After testing with Typer and encountering compatibility issues, we migrated to argparse for:
- Zero external dependencies
- 100% Python compatibility
- Rock-solid reliability
- Full-featured CLI capabilities

### Q: Can I run this without installing dependencies?

**A:** No, you need `requests` and `beautifulsoup4`. However, these are the only external dependencies required.

## Commands & Usage

### Q: How do I find the exact page title to use?

**A:** 
1. Go to the wiki page in your browser
2. Copy the title from the URL or page header
3. Include the namespace prefix (e.g., `Module:`, `Template:`, `Calculator:`)
4. Use quotes around titles with spaces: `"Calculator:Slayer/Slayer task weight"`

### Q: What's the difference between the output formats?

**A:**
- **JSON:** Complete structured data with metadata
- **Text:** Raw content only (wikitext for source, titles for list)
- **CSV:** Tabular format suitable for spreadsheets

### Q: Why am I getting "Page not found" errors?

**A:** Common causes:
- Incorrect page title spelling or capitalization
- Missing namespace prefix (`Module:`, `Template:`, etc.)
- Page doesn't exist or has been moved
- Using display name instead of actual page title

### Q: How do I handle pages with special characters?

**A:** Use quotes and the exact title as it appears on the wiki:
```bash
python wiki_tool.py source "Calculator:Slayer/Slayer task weight"
python wiki_tool.py source "Monkey Madness I"
```

## Rate Limiting & Performance

### Q: How fast can I make requests?

**A:** The tool includes automatic 1-second delays between requests to respect MediaWiki guidelines. Don't run multiple instances simultaneously.

### Q: What happens if I hit rate limits?

**A:** The tool implements exponential backoff and will automatically retry after rate limit errors. You'll see a brief pause before retrying.

### Q: Can I speed up bulk operations?

**A:** No, please respect the rate limits. For large datasets:
- Use specific queries instead of broad category scans
- Process data in smaller chunks
- Cache results to avoid repeat requests

## Data & Output

### Q: How do I extract slayer task weights?

**A:** Use this three-step process:
```bash
# 1. Get calculator configuration
python wiki_tool.py source "Calculator:Slayer/Slayer task weight" --templates --format text

# 2. Get weight tables  
python wiki_tool.py source "Module:SlayerConsts/MasterTables" --format text

# 3. Get calculation logic
python wiki_tool.py source "Module:Slayer weight calculator" --format text
```

### Q: The output is too large. How do I limit it?

**A:** 
- Use `--limit` with the `list` command
- Use `--format text` for content-only output
- Redirect output to files: `python wiki_tool.py ... > output.txt`
- Process specific pages instead of entire categories

### Q: How do I work with the Lua code output?

**A:** The Lua code contains structured data in tables. You can:
- Parse it programmatically with a Lua parser
- Extract data manually using text processing
- Convert to JSON/CSV for easier analysis
- Use tools like `sqlite-utils` for database import

### Q: Can I get only template names without content?

**A:** Yes, use the `--templates` flag with source command and parse the JSON output:
```bash
python wiki_tool.py source "Page Name" --templates --format json | jq '.templates'
```

## Troubleshooting

### Q: I'm getting network timeout errors. What should I do?

**A:**
1. Check your internet connection
2. Try again in a few minutes (server may be busy)
3. Verify the OSRS Wiki is accessible in your browser
4. Check if you're behind a firewall blocking API access

### Q: The tool returns empty results for a page I know exists.

**A:**
- Verify the exact page title (check capitalization and spelling)
- Ensure you're including the proper namespace prefix
- Try accessing the page directly in your browser first
- Some pages may be redirects - use the final destination title

### Q: How do I report bugs or request features?

**A:** 
1. Check existing issues in the repository
2. Provide the exact command that failed
3. Include the full error message
4. Specify your Python version and operating system
5. Include expected vs actual behavior

### Q: The JSON output is malformed.

**A:** This usually indicates:
- API response parsing error
- Network connection issues
- Invalid page content (very rare)

Try the same command with `--format text` to see if the issue is with JSON formatting.

### Q: Can I use this tool offline?

**A:** No, the tool requires internet access to query the MediaWiki API. However, you can cache results locally for offline analysis.

## Advanced Usage

### Q: How do I integrate this with other tools?

**A:** The tool works well with:
- **sqlite-utils:** `python wiki_tool.py list "Category:Items" --format csv | sqlite-utils insert items.db items -`
- **jq:** `python wiki_tool.py source "Module:Data" --format json | jq '.wikitext'`  
- **pandas:** Save CSV output and load with `pd.read_csv()`

### Q: Can I modify the User-Agent or other headers?

**A:** Currently not configurable via CLI options. You would need to modify the `USER_AGENT` constant in the source code.

### Q: How do I handle large category listings?

**A:** 
1. Use `--limit` to control batch size
2. Process results incrementally  
3. Save intermediate results to files
4. Use specific subcategories instead of broad parent categories

### Q: Is there a way to get historical page versions?

**A:** The current tool only gets the latest version. Historical versions would require additional MediaWiki API parameters not currently implemented.

---

**Need more help?** Check the [User Guide](README.md) or [open an issue](https://github.com/cloud-aspect/osrs-wiki-cli/issues/new) for support.