#!/usr/bin/env python3
"""
OSRS Wiki CLI Tool - Argparse Implementation
Extract data from the Old School RuneScape Wiki using the MediaWiki API.
"""

import argparse
import sys
import time
import json
import csv
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup

# Import data organizer if available
try:
    from data_organizer import DataOrganizer
    ORGANIZER_AVAILABLE = True
except ImportError:
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
            
            # Check for API errors
            if 'error' in data:
                error_code = data['error'].get('code', 'unknown')
                error_info = data['error'].get('info', 'Unknown error')
                raise Exception(f"API Error [{error_code}]: {error_info}")
            
            return data
            
        except requests.RequestException as e:
            raise Exception(f"Network error: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")

    def get_wikitext(self, title: str) -> str:
        """Get the raw wikitext (revision content) for a page via API"""
        params = {
            'action': 'query',
            'prop': 'revisions',
            'titles': title,
            'rvslots': '*',
            'rvprop': 'content'
        }
        data = self.make_request(params)
        pages = data.get('query', {}).get('pages', {})
        for _, page in pages.items():
            revs = page.get('revisions')
            if revs:
                slots = revs[0].get('slots', {})
                # prefer main slot, fallback to first slot
                if 'main' in slots and '*' in slots['main']:
                    return slots['main']['*']
                for slot in slots.values():
                    if '*' in slot:
                        return slot['*']
        return ''

    def get_templates_and_modules(self, title: str) -> Dict[str, List[str]]:
        """List templates and modules used by a page"""
        params = {
            'action': 'parse',
            'page': title,
            'prop': 'templates|modules'
        }
        data = self.make_request(params)
        parse_data = data.get('parse', {})
        templates = [t.get('*') for t in parse_data.get('templates', []) if t.get('*')]
        modules = parse_data.get('modules', []) or []
        return {'templates': templates, 'modules': modules}

    def expand_page_wikitext(self, title: str) -> str:
        """Return expanded wikitext for a page by transcluding it in expandtemplates"""
        # Transclude the page content as wikitext; ':' ensures normal page transclusion
        transclusion = f"{{{{:{title}}}}}"
        params = {
            'action': 'expandtemplates',
            'title': title,
            'text': transclusion,
            'prop': 'wikitext'
        }
        data = self.make_request(params)
        return data.get('expandtemplates', {}).get('wikitext', '')


def format_output_data(data: Any, output_format: str) -> str:
    """Format data for output"""
    if output_format.lower() == 'json':
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif output_format.lower() == 'csv' and isinstance(data, list) and data:
        if isinstance(data[0], dict):
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()
    elif output_format.lower() == 'text':
        if isinstance(data, dict):
            return '\n'.join(f"{k}: {v}" for k, v in data.items())
        elif isinstance(data, list):
            return '\n'.join(str(item) for item in data)
        else:
            return str(data)
    # Fallback to JSON
    return json.dumps(data, indent=2, ensure_ascii=False)


def extract_tables(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract tables from HTML content"""
    tables = []
    
    # Find all wiki tables
    wiki_tables = soup.find_all('table', class_=['wikitable', 'infobox', 'calc-table'])
    
    for i, table in enumerate(wiki_tables):
        table_data = {
            'table_id': i,
            'classes': table.get('class', []),
            'headers': [],
            'rows': []
        }
        
        # Extract headers
        header_row = table.find('tr')
        if header_row:
            headers = header_row.find_all(['th', 'td'])
            table_data['headers'] = [h.get_text(strip=True) for h in headers]
        
        # Extract data rows
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data:  # Skip empty rows
                table_data['rows'].append(row_data)
        
        tables.append(table_data)
    
    return tables


def extract_paragraphs(soup: BeautifulSoup) -> List[str]:
    """Extract paragraph content from HTML"""
    paragraphs = []
    
    # Extract text from paragraphs
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if text:  # Skip empty paragraphs
            paragraphs.append(text)
    
    return paragraphs


def extract_links(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract links from HTML content"""
    links = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.get_text(strip=True)
        
        # Filter for wiki links
        if href.startswith('/w/') or 'oldschool.runescape.wiki' in href:
            links.append({
                'text': text,
                'url': href,
                'full_url': f"https://oldschool.runescape.wiki{href}" if href.startswith('/') else href
            })
    
    return links


def cmd_page(args):
    """Extract data from a specific wiki page"""
    try:
        client = WikiAPIClient()
        
        # Parameters for the parse API
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
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract different types of content
        extracted_data = {
            'page_title': parse_data.get('title', args.page_title),
            'page_id': parse_data.get('pageid'),
            'sections': parse_data.get('sections', []),
            'tables': extract_tables(soup),
            'paragraphs': extract_paragraphs(soup),
            'links': extract_links(soup)
        }
        
        # Save data if requested
        if args.save and ORGANIZER_AVAILABLE:
            organizer = DataOrganizer(args.data_dir)
            organizer.save_raw_data(args.page_title, extracted_data, "page")
            print(f"✓ Data saved to {args.data_dir}/", file=sys.stderr)
        elif args.save and not ORGANIZER_AVAILABLE:
            print("Warning: --save option requires data_organizer.py", file=sys.stderr)
        
        output = format_output_data(extracted_data, args.format)
        print(output)
        
    except Exception as e:
        print(f"Error processing page '{args.page_title}': {e}", file=sys.stderr)
        sys.exit(1)


def cmd_category(args):
    """List pages in a category"""
    try:
        client = WikiAPIClient()
        
        all_pages = []
        continue_token = None
        
        while len(all_pages) < args.limit:
            # Parameters for the query API
            params = {
                'action': 'query',
                'list': 'categorymembers',
                'cmtitle': f'Category:{args.category}',
                'cmlimit': min(500, args.limit - len(all_pages)),  # API max is 500
                'cmprop': 'ids|title|type|timestamp'
            }
            
            if continue_token:
                params.update(continue_token)
            
            response_data = client.make_request(params)
            
            if 'query' not in response_data:
                print("Error: Invalid API response - missing 'query' data", file=sys.stderr)
                sys.exit(1)
            
            category_members = response_data['query'].get('categorymembers', [])
            all_pages.extend(category_members)
            
            # Check for continuation
            if 'continue' in response_data and len(all_pages) < args.limit:
                continue_token = response_data['continue']
                print(f"Retrieved {len(all_pages)} pages, continuing...", file=sys.stderr)
            else:
                break
        
        result_data = {
            'category': args.category,
            'total_pages': len(all_pages),
            'pages': all_pages[:args.limit]
        }
        
        # Save data if requested
        if args.save and ORGANIZER_AVAILABLE:
            organizer = DataOrganizer(args.data_dir)
            organizer.save_raw_data(f"Category:{args.category}", result_data, "category")
            print(f"✓ Data saved to {args.data_dir}/", file=sys.stderr)
        elif args.save and not ORGANIZER_AVAILABLE:
            print("Warning: --save option requires data_organizer.py", file=sys.stderr)
        
        output = format_output_data(result_data, args.format)
        print(output)
        
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
    page_parser.add_argument('--format', '-f', choices=['json', 'csv', 'text'], 
                           default='json', help='Output format (default: json)')
    page_parser.add_argument('--save', '-s', action='store_true', help='Save extracted data using data organizer')
    page_parser.add_argument('--data-dir', default='data', help='Directory for organized data storage (default: data)')
    
    # Category command
    category_parser = subparsers.add_parser('category', help='List pages in a category')
    category_parser.add_argument('category', help='Category name (without "Category:" prefix)')
    category_parser.add_argument('--limit', '-l', type=int, default=10, 
                                help='Maximum number of pages to retrieve (default: 10)')
    category_parser.add_argument('--format', '-f', choices=['json', 'csv', 'text'], 
                                default='json', help='Output format (default: json)')
    category_parser.add_argument('--save', '-s', action='store_true', help='Save extracted data using data organizer')
    category_parser.add_argument('--data-dir', default='data', help='Directory for organized data storage (default: data)')

    # Source command (raw wikitext/templates)
    source_parser = subparsers.add_parser('source', help='Get raw wikitext and template/module info for a page')
    source_parser.add_argument('page_title', help='Page title to fetch source for')
    source_parser.add_argument('--templates', action='store_true', help='Include templates and modules used by the page')
    source_parser.add_argument('--expand', action='store_true', help='Also return expanded wikitext (templates expanded)')
    source_parser.add_argument('--format', '-f', choices=['json', 'text'], default='json', help='Output format (default: json)')
    source_parser.add_argument('--save', '-s', action='store_true', help='Save extracted data using data organizer')
    source_parser.add_argument('--data-dir', default='data', help='Directory for organized data storage (default: data)')
    
    args = parser.parse_args()
    
    # Handle no command provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate command handler
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
                result['expanded_wikitext'] = client.expand_page_wikitext(args.page_title)
            
            # Save data if requested
            if args.save and ORGANIZER_AVAILABLE:
                organizer = DataOrganizer(args.data_dir)
                organizer.save_raw_data(args.page_title, result, "source")
                if 'wikitext' in result and result['wikitext']:
                    content_type = "lua" if args.page_title.startswith("Module:") else "wikitext"
                    organizer.save_text_content(args.page_title, result['wikitext'], content_type)
                print(f"✓ Data saved to {args.data_dir}/", file=sys.stderr)
            elif args.save and not ORGANIZER_AVAILABLE:
                print("Warning: --save option requires data_organizer.py", file=sys.stderr)
            
            output = format_output_data(result, args.format)
            print(output)
        except Exception as e:
            print(f"Error retrieving source for '{args.page_title}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


def cli():
    """Entry point for osrs-wiki-cli command."""
    main()

if __name__ == '__main__':
    cli()