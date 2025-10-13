#!/usr/bin/env python3
"""
OSRS Wiki Data Organizer
Portable file writing and organization system for extracted wiki data.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import re


class DataOrganizer:
    """Organizes and stores wiki data in a structured file system"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize data organizer
        
        Args:
            data_dir: Base directory for organized data storage
        """
        self.data_dir = Path(data_dir)
        self.ensure_directory_structure()
    
    def ensure_directory_structure(self):
        """Create the standard data directory structure"""
        directories = [
            self.data_dir,
            self.data_dir / "raw",           # Raw wikitext/JSON dumps
            self.data_dir / "processed",     # Cleaned and parsed data
            self.data_dir / "slayer",        # Slayer-specific data
            self.data_dir / "calculators",   # Calculator page data
            self.data_dir / "modules",       # Lua module exports
            self.data_dir / "templates",     # Template data
            self.data_dir / "metadata",      # Extraction metadata and logs
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def sanitize_filename(self, filename: str) -> str:
        """Convert wiki page titles to safe filenames"""
        # Remove/replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Remove multiple consecutive underscores
        filename = re.sub(r'_+', '_', filename)
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        return filename
    
    def save_raw_data(self, page_title: str, data: Dict[str, Any], 
                     data_type: str = "page") -> Path:
        """
        Save raw extracted data with metadata
        
        Args:
            page_title: Original wiki page title
            data: Raw extracted data dictionary
            data_type: Type of data (page, category, source, etc.)
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.datetime.now().isoformat()
        safe_filename = self.sanitize_filename(page_title)
        
        # Add extraction metadata
        enriched_data = {
            "extraction_metadata": {
                "page_title": page_title,
                "data_type": data_type,
                "extraction_timestamp": timestamp,
                "tool_version": "1.0",
            },
            "data": data
        }
        
        # Save to appropriate subdirectory based on content type
        if "slayer" in page_title.lower():
            subdir = self.data_dir / "slayer"
        elif "calculator" in page_title.lower():
            subdir = self.data_dir / "calculators"
        elif page_title.startswith("Module:"):
            subdir = self.data_dir / "modules"
        elif page_title.startswith("Template:"):
            subdir = self.data_dir / "templates"
        else:
            subdir = self.data_dir / "raw"
        
        filepath = subdir / f"{safe_filename}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved raw data: {filepath}")
        return filepath
    
    def save_text_content(self, page_title: str, content: str, 
                         content_type: str = "wikitext") -> Path:
        """
        Save text content (wikitext, code, etc.) to plain text files
        
        Args:
            page_title: Original wiki page title
            content: Text content to save
            content_type: Type of content (wikitext, lua, javascript, etc.)
            
        Returns:
            Path to saved file
        """
        safe_filename = self.sanitize_filename(page_title)
        
        # Determine file extension based on content type
        extensions = {
            "wikitext": ".wiki",
            "lua": ".lua", 
            "javascript": ".js",
            "css": ".css",
            "html": ".html",
            "text": ".txt"
        }
        
        ext = extensions.get(content_type.lower(), ".txt")
        
        # Choose subdirectory
        if page_title.startswith("Module:"):
            subdir = self.data_dir / "modules"
        elif page_title.startswith("Template:"):
            subdir = self.data_dir / "templates"
        elif "calculator" in page_title.lower():
            subdir = self.data_dir / "calculators"
        else:
            subdir = self.data_dir / "processed"
        
        filepath = subdir / f"{safe_filename}{ext}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Saved {content_type}: {filepath}")
        return filepath
    
    def save_processed_data(self, name: str, data: Union[Dict, List], 
                           category: str = "general") -> Path:
        """
        Save processed/parsed data structures
        
        Args:
            name: Descriptive name for the dataset
            data: Processed data (dict or list)
            category: Data category (slayer, items, quests, etc.)
            
        Returns:
            Path to saved file
        """
        safe_filename = self.sanitize_filename(name)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        subdir = self.data_dir / "processed" / category
        subdir.mkdir(parents=True, exist_ok=True)
        
        filepath = subdir / f"{safe_filename}_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved processed data: {filepath}")
        return filepath
    
    def create_extraction_log(self, pages: List[str], notes: str = "") -> Path:
        """
        Create a log of extraction session
        
        Args:
            pages: List of pages extracted
            notes: Additional notes about the extraction
            
        Returns:
            Path to log file
        """
        timestamp = datetime.datetime.now()
        log_data = {
            "extraction_session": {
                "timestamp": timestamp.isoformat(),
                "pages_extracted": pages,
                "total_pages": len(pages),
                "notes": notes
            }
        }
        
        log_filename = f"extraction_log_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        log_path = self.data_dir / "metadata" / log_filename
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Created extraction log: {log_path}")
        return log_path
    
    def list_saved_data(self, category: Optional[str] = None) -> Dict[str, List[Path]]:
        """
        List all saved data files, optionally filtered by category
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary mapping categories to file lists
        """
        categories = {}
        
        if category:
            search_dirs = [self.data_dir / category] if (self.data_dir / category).exists() else []
        else:
            search_dirs = [d for d in self.data_dir.iterdir() if d.is_dir()]
        
        for dir_path in search_dirs:
            category_name = dir_path.name
            files = list(dir_path.glob("*.json")) + list(dir_path.glob("*.lua")) + \
                   list(dir_path.glob("*.wiki")) + list(dir_path.glob("*.txt"))
            
            if files:
                categories[category_name] = sorted(files)
        
        return categories


def create_batch_extraction_script():
    """Create a helper script for batch data extraction and organization"""
    
    script_content = '''#!/usr/bin/env python3
"""
Batch Data Extraction Script
Automates extraction and organization of OSRS Wiki data
"""

import subprocess
import json
import sys
from pathlib import Path
from data_organizer import DataOrganizer


def run_extraction(page_title, command_args=None):
    """Run wiki_tool.py extraction and organize results"""
    if command_args is None:
        command_args = ["source", "--templates", "--format", "json"]
    
    cmd = ["python", "wiki_tool.py"] + command_args + [page_title]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error extracting {page_title}: {e}")
        return None


def main():
    """Main batch extraction workflow"""
    organizer = DataOrganizer()
    
    # Define common extraction targets
    slayer_pages = [
        "Module:SlayerConsts/MasterTables",
        "Module:Slayer weight calculator", 
        "Module:Slayer task library",
        "Calculator:Slayer/Slayer task weight"
    ]
    
    calculator_pages = [
        "Calculator:Combat level",
        "Calculator:Skill calculators/Hitpoints",
        "Calculator:Skill calculators/Attack"
    ]
    
    extracted_pages = []
    
    print("🔍 Starting batch extraction...")
    
    # Extract slayer data
    print("\\n📊 Extracting slayer data...")
    for page in slayer_pages:
        print(f"  → {page}")
        data = run_extraction(page)
        if data:
            # Save raw data
            organizer.save_raw_data(page, data, "source")
            
            # Save wikitext if available
            if 'wikitext' in data:
                organizer.save_text_content(
                    page, 
                    data['wikitext'], 
                    "lua" if page.startswith("Module:") else "wikitext"
                )
            
            extracted_pages.append(page)
    
    # Extract calculator data
    print("\\n🧮 Extracting calculator data...")
    for page in calculator_pages:
        print(f"  → {page}")
        data = run_extraction(page)
        if data:
            organizer.save_raw_data(page, data, "source")
            if 'wikitext' in data:
                organizer.save_text_content(page, data['wikitext'], "wikitext")
            extracted_pages.append(page)
    
    # Create extraction log
    organizer.create_extraction_log(
        extracted_pages, 
        "Batch extraction of slayer and calculator data"
    )
    
    print(f"\\n✅ Extraction complete! {len(extracted_pages)} pages processed.")
    print("\\n📁 Data organization:")
    
    # Show organized data
    saved_data = organizer.list_saved_data()
    for category, files in saved_data.items():
        print(f"  {category}/: {len(files)} files")
        for file_path in files[:3]:  # Show first 3 files
            print(f"    - {file_path.name}")
        if len(files) > 3:
            print(f"    ... and {len(files) - 3} more")


if __name__ == "__main__":
    main()
'''
    
    with open("batch_extract.py", 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✓ Created batch extraction script: batch_extract.py")


if __name__ == "__main__":
    # Demo usage
    print("🗂️  OSRS Wiki Data Organizer")
    print("=" * 40)
    
    organizer = DataOrganizer()
    print("✓ Directory structure created")
    
    # Example usage with existing data
    if Path("calc_source.json").exists():
        print("\n📄 Organizing existing calc_source.json...")
        
        with open("calc_source.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Save as organized data
        page_title = data.get('page_title', 'Unknown_Page')
        organizer.save_raw_data(page_title, data, "source")
        
        # Save wikitext separately
        if 'wikitext' in data:
            organizer.save_text_content(page_title, data['wikitext'], "wikitext")
    
    print("\n📋 Available organization methods:")
    print("  • organizer.save_raw_data(title, data, type)")
    print("  • organizer.save_text_content(title, content, type)")
    print("  • organizer.save_processed_data(name, data, category)")
    print("  • organizer.create_extraction_log(pages, notes)")
    print("  • organizer.list_saved_data(category)")
    
    create_batch_extraction_script()
    
    print("\n🚀 Ready to organize your wiki data!")