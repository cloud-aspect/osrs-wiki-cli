#!/usr/bin/env python3
"""
OSRS Wiki CLI Tool

A command-line interface for extracting data from the Old School RuneScape Wiki
using the MediaWiki API. Supports on-demand data extraction with modular subcommands.
"""

import time
import json
import csv
import sys
from typing import Optional, Dict, Any, List
from pathlib import Path

import typer
import requests
from bs4 import BeautifulSoup


# Global configuration
DEFAULT_WIKI_URL = "https://oldschool.runescape.wiki/api.php"
USER_AGENT = "OSRSWikiTool/1.0 (https://github.com/user/osrs-wiki-cli-tool)"
REQUEST_DELAY = 1  # seconds between requests (60 req/min limit)

# Initialize Typer app with explicit configuration for better compatibility
app = typer.Typer(
    help="Extract data from the Old School RuneScape Wiki",
    add_completion=False,  # Disable completion to avoid compatibility issues
    rich_markup_mode=None  # Disable rich formatting for better compatibility
)


class WikiAPIError(Exception):
    """Custom exception for MediaWiki API errors"""
    def __init__(self, error_code: str, error_info: str):
        self.error_code = error_code
        self.error_info = error_info
        super().__init__(f"MediaWiki API Error [{error_code}]: {error_info}")


class WikiAPIClient:
    """MediaWiki API client with rate limiting and error handling"""
    
    def __init__(self, wiki_url: str = DEFAULT_WIKI_URL):
        self.wiki_url = wiki_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def _handle_api_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MediaWiki API response and check for errors"""
        if 'error' in response_data:
            error = response_data['error']
            error_code = error.get('code', 'unknown')
            error_info = error.get('info', 'Unknown error occurred')
            
            if error_code == 'ratelimited':
                typer.echo("Rate limited. Implementing exponential backoff...", err=True)
                time.sleep(5)  # Wait 5 seconds for rate limit
                raise WikiAPIError(error_code, error_info)
            elif error_code == 'missingtitle':
                raise WikiAPIError(error_code, f"Page not found: {error_info}")
            elif error_code == 'readonly':
                raise WikiAPIError(error_code, "Wiki is in maintenance mode")
            else:
                raise WikiAPIError(error_code, error_info)
        
        return response_data
    
    def make_request(self, params: Dict[str, Any], retries: int = 3) -> Dict[str, Any]:
        """Make a request to the MediaWiki API with retry logic"""
        self._rate_limit()
        
        # Add required parameters
        params.setdefault('format', 'json')
        
        for attempt in range(retries):
            try:
                response = self.session.get(self.wiki_url, params=params, timeout=30)
                response.raise_for_status()
                
                response_data = response.json()
                return self._handle_api_response(response_data)
                
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    raise typer.Exit(f"Network error after {retries} attempts: {e}")
                typer.echo(f"Request failed (attempt {attempt + 1}/{retries}): {e}", err=True)
                time.sleep(2 ** attempt)  # Exponential backoff
            except WikiAPIError as e:
                if e.error_code == 'ratelimited' and attempt < retries - 1:
                    time.sleep(5 * (attempt + 1))  # Longer wait for rate limiting
                    continue
                raise typer.Exit(str(e))
        
        raise typer.Exit("Max retries exceeded")


def format_output_data(data: Any, output_format: str) -> str:
    """Format data for output - renamed to avoid shadowing built-in format()"""
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
    # Fallback to JSON
    return json.dumps(data, indent=2, ensure_ascii=False)


@app.command()
def page(
    page_title: str,
    format: str = typer.Option("json", "--format", "-f"),
    section: str = typer.Option(None, "--section", "-s")
):
    """Extract data from a wiki page"""
    client = WikiAPIClient()
    
    # Parameters for the parse API
    params = {
        'action': 'parse',
        'page': page_title,
        'prop': 'text|sections',
        'disablelimitreport': '1'
    }
    
    # Removed section parameter for simplicity
    
    try:
        response_data = client.make_request(params)
        
        if 'parse' not in response_data:
            raise typer.Exit("Invalid API response: missing 'parse' data")
        
        parse_data = response_data['parse']
        html_content = parse_data.get('text', {}).get('*', '')
        
        if not html_content:
            raise typer.Exit(f"No content found for page: {page_title}")
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract different types of content
        extracted_data = {
            'page_title': parse_data.get('title', page_title),
            'page_id': parse_data.get('pageid'),
            'sections': parse_data.get('sections', []),
            'tables': extract_tables(soup),
            'paragraphs': extract_paragraphs(soup),
            'links': extract_links(soup)
        }
        
        output = format_output_data(extracted_data, "json")
        typer.echo(output)
        
    except typer.Exit:
        raise
    except Exception as e:
        raise typer.Exit(f"Error processing page '{page_title}': {e}")


@app.command("category")
def list_category(
    category: str,
    output_format: str = typer.Option("json", "--format", "-f"),
    limit: int = typer.Option(10, "--limit", "-l")
):
    """List pages in a category"""
    client = WikiAPIClient()
    
    all_pages = []
    continue_token = None
    while len(all_pages) < limit:
        # Parameters for the query API
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': f'Category:{category}',
            'cmlimit': min(500, limit - len(all_pages)),  # API max is 500
            'cmprop': 'ids|title|type|timestamp'
        }
        
        if continue_token:
            params.update(continue_token)
        
        try:
            response_data = client.make_request(params)
            
            if 'query' not in response_data:
                raise typer.Exit("Invalid API response: missing 'query' data")
            
            category_members = response_data['query'].get('categorymembers', [])
            all_pages.extend(category_members)
            
            # Check for continuation
            if 'continue' in response_data and len(all_pages) < limit:
                continue_token = response_data['continue']
                typer.echo(f"Retrieved {len(all_pages)} pages, continuing...", err=True)
            else:
                break
                
        except typer.Exit:
            raise
        except Exception as e:
            raise typer.Exit(f"Error retrieving category '{category}': {e}")
    
    result_data = {
        'category': category,
        'total_pages': len(all_pages),
        'pages': all_pages[:limit]
    }
    
    output = format_output_data(result_data, output_format)
    typer.echo(output)


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
        
        # Extract all rows
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data:  # Only add non-empty rows
                table_data['rows'].append(row_data)
        
        tables.append(table_data)
    
    return tables


def extract_paragraphs(soup: BeautifulSoup) -> List[str]:
    """Extract paragraph text from HTML content"""
    paragraphs = soup.find_all('p')
    return [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]


def extract_links(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract internal and external links from HTML content"""
    links = []
    
    # Internal wiki links
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.get_text(strip=True)
        
        if href.startswith('/wiki/'):
            links.append({
                'type': 'internal',
                'title': text,
                'url': href,
                'page': href[6:]  # Remove '/wiki/' prefix
            })
        elif href.startswith('http'):
            links.append({
                'type': 'external',
                'title': text,
                'url': href
            })
    
    return links


def main():
    """Main entry point with error handling"""
    try:
        app()
    except KeyboardInterrupt:
        typer.echo("\nOperation cancelled", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()