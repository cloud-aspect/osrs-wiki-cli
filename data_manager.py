#!/usr/bin/env python3
"""
OSRS Wiki Data Manager
Command-line interface for managing organized wiki data
"""

import argparse
import json
import sys
from pathlib import Path
from data_organizer import DataOrganizer


def cmd_organize(args):
    """Organize existing JSON files"""
    organizer = DataOrganizer(args.data_dir)
    
    if not Path(args.file).exists():
        print(f"Error: File {args.file} not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract page title from data or use filename
        if isinstance(data, dict) and 'page_title' in data:
            page_title = data['page_title']
        else:
            page_title = Path(args.file).stem
        
        # Save organized data
        organizer.save_raw_data(page_title, data, args.type)
        
        # Save text content if it's wikitext
        if isinstance(data, dict) and 'wikitext' in data and data['wikitext']:
            content_type = "lua" if page_title.startswith("Module:") else "wikitext"
            organizer.save_text_content(page_title, data['wikitext'], content_type)
        
        print(f"✓ Organized {args.file} into {args.data_dir}/")
        
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error processing {args.file}: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args):
    """List organized data files"""
    organizer = DataOrganizer(args.data_dir)
    saved_data = organizer.list_saved_data(args.category)
    
    if not saved_data:
        print("No organized data found.")
        return
    
    total_files = 0
    for category, files in saved_data.items():
        print(f"\n📁 {category}/ ({len(files)} files)")
        total_files += len(files)
        
        for file_path in files:
            size = file_path.stat().st_size if file_path.exists() else 0
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            print(f"  • {file_path.name} ({size_str})")
    
    print(f"\nTotal: {total_files} files across {len(saved_data)} categories")


def cmd_extract(args):
    """Extract specific content from organized files"""
    organizer = DataOrganizer(args.data_dir)
    
    # Find files matching the pattern
    search_pattern = f"*{args.pattern}*"
    matching_files = []
    
    for category_dir in organizer.data_dir.iterdir():
        if category_dir.is_dir():
            matching_files.extend(category_dir.glob(search_pattern))
    
    if not matching_files:
        print(f"No files found matching pattern: {args.pattern}")
        return
    
    print(f"Found {len(matching_files)} matching files:")
    
    for file_path in matching_files:
        print(f"\n📄 {file_path}")
        
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Show key information
                if isinstance(data, dict):
                    if 'extraction_metadata' in data:
                        metadata = data['extraction_metadata']
                        print(f"   Page: {metadata.get('page_title', 'Unknown')}")
                        print(f"   Type: {metadata.get('data_type', 'Unknown')}")
                        print(f"   Date: {metadata.get('extraction_timestamp', 'Unknown')}")
                    
                    if 'data' in data and isinstance(data['data'], dict):
                        content = data['data']
                        if 'wikitext' in content:
                            lines = content['wikitext'].count('\n') + 1
                            print(f"   Wikitext: {lines} lines")
                        if 'templates' in content:
                            print(f"   Templates: {len(content['templates'])}")
                        if 'modules' in content:
                            print(f"   Modules: {len(content['modules'])}")
            
            elif file_path.suffix in ['.lua', '.wiki', '.txt']:
                size = file_path.stat().st_size
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = sum(1 for _ in f)
                print(f"   Size: {size:,} bytes, {lines} lines")
                
        except Exception as e:
            print(f"   Error reading file: {e}")


def cmd_export(args):
    """Export organized data to different formats"""
    organizer = DataOrganizer(args.data_dir)
    
    # Find the requested file
    target_file = None
    for category_dir in organizer.data_dir.iterdir():
        if category_dir.is_dir():
            potential_files = list(category_dir.glob(f"*{args.file}*"))
            if potential_files:
                target_file = potential_files[0]
                break
    
    if not target_file:
        print(f"File not found: {args.file}")
        return
    
    try:
        if target_file.suffix == '.json':
            with open(target_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract the main content
            if isinstance(data, dict) and 'data' in data:
                content = data['data']
            else:
                content = data
            
            # Export based on format
            if args.format == 'wikitext' and 'wikitext' in content:
                print(content['wikitext'])
            elif args.format == 'json':
                print(json.dumps(content, indent=2, ensure_ascii=False))
            elif args.format == 'summary':
                if isinstance(content, dict):
                    print(f"Content type: {type(content).__name__}")
                    for key, value in content.items():
                        if isinstance(value, str):
                            print(f"{key}: {len(value)} characters")
                        elif isinstance(value, list):
                            print(f"{key}: {len(value)} items")
                        elif isinstance(value, dict):
                            print(f"{key}: {len(value)} keys")
                        else:
                            print(f"{key}: {type(value).__name__}")
        
        elif target_file.suffix in ['.lua', '.wiki', '.txt']:
            with open(target_file, 'r', encoding='utf-8') as f:
                print(f.read())
                
    except Exception as e:
        print(f"Error exporting {target_file}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Manage and organize OSRS Wiki extracted data",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--data-dir', default='data', 
                       help='Data directory path (default: data)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Organize command
    organize_parser = subparsers.add_parser('organize', 
                                          help='Organize an existing JSON file')
    organize_parser.add_argument('file', help='JSON file to organize')
    organize_parser.add_argument('--type', default='unknown', 
                                help='Data type for categorization')
    
    # List command  
    list_parser = subparsers.add_parser('list', help='List organized data files')
    list_parser.add_argument('--category', help='Filter by category')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', 
                                         help='Extract info from organized files')
    extract_parser.add_argument('pattern', help='File name pattern to search for')
    
    # Export command
    export_parser = subparsers.add_parser('export', 
                                        help='Export file content in different formats')
    export_parser.add_argument('file', help='File name pattern to export')
    export_parser.add_argument('--format', choices=['json', 'wikitext', 'summary'],
                              default='summary', help='Export format')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate command handler
    if args.command == 'organize':
        cmd_organize(args)
    elif args.command == 'list':
        cmd_list(args)
    elif args.command == 'extract':
        cmd_extract(args)
    elif args.command == 'export':
        cmd_export(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()