#!/usr/bin/env python3
"""
OSRS Wiki CLI Tool - Argparse Implementation
Extract data from the Old School RuneScape Wiki using the MediaWiki API.
"""

import argparse
import csv
import json
import sys
import time
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# Import data organizer if available
try:
    from data_organizer import DataOrganizer
    ORGANIZER_AVAILABLE = True
except ImportError:
    print("Data organizer not available.")
    ORGANIZER_AVAILABLE = False


class WikiAPIClient:
    """Client for interacting with the OSRS Wiki MediaWiki API"""
    
    def __init__(self):
        self.base_url = "https://oldschool.runescape.wiki/api.php"
        self.headers = {
            'User-Agent': 'osrs-wiki-cli/1.0 (https://github.com/cloud-aspect/osrs-wiki-cli)'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with rate limiting"""
        params.setdefault('format', 'json')
        
        try:
            time.sleep(1)  # Rate limiting: 60 requests per minute
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()

            if "error" in data:
                error_code = data["error"].get("code", "unknown")
                error_info = data["error"].get("info", "Unknown error")
                raise Exception(f"API Error [{error_code}]: {error_info}")

            return data

        except requests.RequestException as e:
            raise Exception(f"Network error: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")

    def get_wikitext(self, title: str) -> str:
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": title,
            "rvslots": "*",
            "rvprop": "content",
        }
        data = self.make_request(params)
        pages = data.get("query", {}).get("pages", {})
        for _, page in pages.items():
            revs = page.get("revisions")
            if revs:
                slots = revs[0].get("slots", {})
                if "main" in slots and "*" in slots["main"]:
                    return slots["main"]["*"]
                for slot in slots.values():
                    if "*" in slot:
                        return slot["*"]
        return ""

    def get_templates_and_modules(self, title: str) -> Dict[str, List[str]]:
        params = {"action": "parse", "page": title, "prop": "templates|modules"}
        data = self.make_request(params)
        parse_data = data.get("parse", {})
        templates = [t.get("*") for t in parse_data.get("templates", []) if t.get("*")]
        modules = parse_data.get("modules", []) or []
        return {"templates": templates, "modules": modules}

    def expand_page_wikitext(self, title: str) -> str:
        transclusion = f"{{{{:{title}}}}}"
        params = {
            "action": "expandtemplates",
            "title": title,
            "text": transclusion,
            "prop": "wikitext",
        }
        data = self.make_request(params)
        return data.get("expandtemplates", {}).get("wikitext", "")


def format_output_data(data: Any, output_format: str) -> str:
    """Format data for output"""
    if output_format.lower() == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif output_format.lower() == "csv" and isinstance(data, list) and data:
        if isinstance(data[0], dict):
            import io

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()
    elif output_format.lower() == "text":
        if isinstance(data, dict):
            return "\n".join(f"{k}: {v}" for k, v in data.items())
        elif isinstance(data, list):
            return "\n".join(str(item) for item in data)
        else:
            return str(data)
    return json.dumps(data, indent=2, ensure_ascii=False)

def format_markdown_table(table_data: Dict[str, Any]) -> str:
    """Helper function to convert extracted table data to flattened Markdown format"""
    lines = []
    headers = table_data.get("headers", [])
    rows = table_data.get("rows", [])

    # Determine the maximum number of columns
    max_cols = 0
    for r in headers + rows:
        max_cols = max(max_cols, len(r))

    if max_cols == 0:
        return ""

    def clean_cell(cell):
        # Escape markdown pipes and remove hard line breaks
        if not cell:
            return ""
        return str(cell).replace("\n", " ").replace("|", "\\|").strip()

    def pad_row(row):
        return [clean_cell(c) for c in row] + [""] * (max_cols - len(row))

    # Pad all rows first to ensure uniform width
    padded_headers = [pad_row(h) for h in headers]
    padded_rows = [pad_row(r) for r in rows]

    # --- UPDATED: Filter empty columns by evaluating DATA rows only ---
    non_empty_cols = []
    for c in range(max_cols):
        has_data = False

        for r in padded_rows:
            if r[c].strip():  # If there is any text in the data rows
                has_data = True
                break

        # Fallback: if the table has headers but strictly zero data rows
        if not has_data and not padded_rows:
            for h in padded_headers:
                if h[c].strip():
                    has_data = True
                    break

        if has_data:
            non_empty_cols.append(c)

    if not non_empty_cols:
        return ""

    # Rebuild headers and rows keeping only the columns containing data
    filtered_headers = [[r[c] for c in non_empty_cols] for r in padded_headers]
    filtered_rows = [[r[c] for c in non_empty_cols] for r in padded_rows]
    final_cols_count = len(non_empty_cols)
    # -----------------------------------------------------------------

    if filtered_headers:
        flat_headers = []

        # Flatten multiple header rows into a single row
        for c in range(final_cols_count):
            col_texts = []
            last_text = None
            for r in range(len(filtered_headers)):
                txt = filtered_headers[r][c]
                # Append if it has text and isn't a direct vertical repeat
                if txt and txt != last_text:
                    col_texts.append(txt)
                    last_text = txt

            # Join the flattened column headers with a space
            flat_headers.append(" ".join(col_texts))

        lines.append("| " + " | ".join(flat_headers) + " |")
        lines.append("|" + "|".join(["---"] * final_cols_count) + "|")
    elif filtered_rows:
        # Fallback if a table has no headers but has rows
        lines.append("| " + " | ".join([""] * final_cols_count) + " |")
        lines.append("|" + "|".join(["---"] * final_cols_count) + "|")

    for row in filtered_rows:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)

def extract_tables(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract tables from HTML content using a 2D matrix for colspans/rowspans"""
    tables = []
    # New line (Ignores infoboxes)
    wiki_tables = soup.find_all("table", class_=["wikitable", "calc-table"])

    for i, table in enumerate(wiki_tables):
        table_data = {
            "table_id": i,
            "classes": table.get("class", []),
            "headers": [],
            "rows": [],
        }

        matrix = []

        for r, row in enumerate(table.find_all("tr")):
            cells = row.find_all(["th", "td"])
            if not cells:
                continue

            while len(matrix) <= r:
                matrix.append([])

            c = 0
            for cell in cells:
                while c < len(matrix[r]) and matrix[r][c] is not None:
                    c += 1

                is_header = cell.name == "th"
                text = cell.get_text(separator=" ", strip=True)

                try:
                    colspan = int(cell.get("colspan", 1))
                except ValueError:
                    colspan = 1

                try:
                    rowspan = int(cell.get("rowspan", 1))
                except ValueError:
                    rowspan = 1

                for row_offset in range(rowspan):
                    for col_offset in range(colspan):
                        target_r = r + row_offset
                        target_c = c + col_offset

                        while len(matrix) <= target_r:
                            matrix.append([])
                        while len(matrix[target_r]) <= target_c:
                            matrix[target_r].append(None)

                        matrix[target_r][target_c] = {
                            "text": text,
                            "is_header": is_header,
                        }

        # Populate formatted rows from the resolved grid
        for row in matrix:
            if not row:
                continue
            header_count = sum(1 for cell in row if cell and cell.get("is_header"))
            data_count = len(row) - header_count
            is_header_row = header_count > 0 and header_count >= data_count

            row_text = [cell["text"] if cell else "" for cell in row]

            if is_header_row:
                table_data["headers"].append(row_text)
            else:
                table_data["rows"].append(row_text)

        tables.append(table_data)

    return tables


def extract_paragraphs(soup: BeautifulSoup) -> List[str]:
    paragraphs = []
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if text:
            paragraphs.append(text)
    return paragraphs


def extract_links(soup: BeautifulSoup) -> List[Dict[str, str]]:
    links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = link.get_text(strip=True)
        if href.startswith("/w/") or "oldschool.runescape.wiki" in href:
            links.append(
                {
                    "text": text,
                    "url": href,
                    "full_url": f"https://oldschool.runescape.wiki{href}"
                    if href.startswith("/")
                    else href,
                }
            )
    return links


def cmd_page(args):
    """Extract data from a specific wiki page"""
    try:
        client = WikiAPIClient()

        params = {
            'action': 'parse',
            'page': args.page_title,
            'prop': 'text|sections',
            'disablelimitreport': '1'
        }
        
        response_data = client.make_request(params)
        
        if 'parse' not in response_data:
            print("Error: Invalid API response - missing 'parse' data", file=sys.stderr)
            sys.exit(1)
        
        parse_data = response_data['parse']
        html_content = parse_data.get('text', {}).get('*', '')
        
        if not html_content:
            print(f"Error: No content found for page: {args.page_title}", file=sys.stderr)
            sys.exit(1)

        soup = BeautifulSoup(html_content, "html.parser")

        extracted_data = {
            "page_title": parse_data.get("title", args.page_title),
            "page_id": parse_data.get("pageid"),
            "sections": parse_data.get("sections", []),
            "tables": extract_tables(soup),
            "paragraphs": extract_paragraphs(soup),
            "links": extract_links(soup),
        }

        if args.save and ORGANIZER_AVAILABLE:
            organizer = DataOrganizer(args.data_dir)
            organizer.save_raw_data(args.page_title, extracted_data, "page")
            print(f"✓ Data saved to {args.data_dir}/", file=sys.stderr)
        elif args.save and not ORGANIZER_AVAILABLE:
            print("Warning: --save option requires data_organizer.py", file=sys.stderr)

        # Determine output strategy (Tables-only filter vs standard output)
        if args.tables:
            tables = extracted_data.get("tables", [])
            if not tables:
                print("No tables found on this page.", file=sys.stderr)
            else:
                print(f"# Tables extracted from: {extracted_data['page_title']}\n")
                for i, table in enumerate(tables):
                    print(f"## Table {i + 1}")
                    if table.get("classes"):
                        print(f"**Classes:** {', '.join(table['classes'])}\n")
                    print(format_markdown_table(table))
                    print("\n")
        else:
            output = format_output_data(extracted_data, args.format)
            print(output)

    except Exception as e:
        print(f"Error processing page '{args.page_title}': {e}", file=sys.stderr)
        sys.exit(1)


def cmd_category(args):
    # Category code remains unchanged...
    try:
        client = WikiAPIClient()
        all_pages = []
        continue_token = None

        while len(all_pages) < args.limit:
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{args.category}",
                "cmlimit": min(500, args.limit - len(all_pages)),
                "cmprop": "ids|title|type|timestamp",
            }
            if continue_token:
                params.update(continue_token)

            response_data = client.make_request(params)
            if "query" not in response_data:
                print("Error: Invalid API response", file=sys.stderr)
                sys.exit(1)

            all_pages.extend(response_data["query"].get("categorymembers", []))

            if "continue" in response_data and len(all_pages) < args.limit:
                continue_token = response_data["continue"]
            else:
                break

        result_data = {
            "category": args.category,
            "total_pages": len(all_pages),
            "pages": all_pages[: args.limit],
        }

        if args.save and ORGANIZER_AVAILABLE:
            organizer = DataOrganizer(args.data_dir)
            organizer.save_raw_data(
                f"Category:{args.category}", result_data, "category"
            )

        print(format_output_data(result_data, args.format))
    except Exception as e:
        print(f"Error retrieving category '{args.category}': {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point using argparse"""
    parser = argparse.ArgumentParser(
        description="Extract data from the Old School RuneScape Wiki",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Page command
    page_parser = subparsers.add_parser('page', help='Extract data from a specific wiki page')
    page_parser.add_argument('page_title', help='Wiki page title to extract data from')
    page_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "csv", "text"],
        default="json",
        help="Output format (default: json)",
    )
    page_parser.add_argument(
        "--tables",
        action="store_true",
        help="Filter output to strictly display extracted tables rendered in Markdown",
    )
    page_parser.add_argument('--save', '-s', action='store_true', help='Save extracted data using data organizer')
    page_parser.add_argument('--data-dir', default='data', help='Directory for organized data storage (default: data)')
    
    # Category command
    category_parser = subparsers.add_parser('category', help='List pages in a category')
    category_parser.add_argument('category', help='Category name (without "Category:" prefix)')
    category_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=10,
        help="Maximum number of pages to retrieve (default: 10)",
    )
    category_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "csv", "text"],
        default="json",
        help="Output format",
    )
    category_parser.add_argument('--save', '-s', action='store_true', help='Save extracted data using data organizer')
    category_parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory for organized data (default: data)",
    )

    # Source command
    source_parser = subparsers.add_parser('source', help='Get raw wikitext and template/module info for a page')
    source_parser.add_argument('page_title', help='Page title to fetch source for')
    source_parser.add_argument('--templates', action='store_true', help='Include templates and modules used by the page')
    source_parser.add_argument('--expand', action='store_true', help='Also return expanded wikitext (templates expanded)')
    source_parser.add_argument('--format', '-f', choices=['json', 'text'], default='json', help='Output format (default: json)')
    source_parser.add_argument('--save', '-s', action='store_true', help='Save extracted data using data organizer')
    source_parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory for organized data (default: data)",
    )

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'page':
        cmd_page(args)
    elif args.command == 'category':
        cmd_category(args)
    elif args.command == 'source':
        try:
            client = WikiAPIClient()
            result: Dict[str, Any] = {
                'page_title': args.page_title,
                'wikitext': client.get_wikitext(args.page_title)
            }
            if args.templates:
                result.update(client.get_templates_and_modules(args.page_title))
            if args.expand:
                result["expanded_wikitext"] = client.expand_page_wikitext(
                    args.page_title
                )

            if args.save and ORGANIZER_AVAILABLE:
                organizer = DataOrganizer(args.data_dir)
                organizer.save_raw_data(args.page_title, result, "source")
                if 'wikitext' in result and result['wikitext']:
                    content_type = "lua" if args.page_title.startswith("Module:") else "wikitext"
                    organizer.save_text_content(
                        args.page_title, result["wikitext"], content_type
                    )

            print(format_output_data(result, args.format))
        except Exception as e:
            print(f"Error retrieving source for '{args.page_title}': {e}", file=sys.stderr)
            sys.exit(1)

def cli():
    main()

if __name__ == '__main__':
    cli()