#!/usr/bin/env python3
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
        "Calculator:Agility",
        "Calculator:Barrows"
    ]
    
    extracted_pages = []
    
    print("🔍 Starting batch extraction...")
    
    # Extract slayer data
    print("\n📊 Extracting slayer data...")
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
    print("\n🧮 Extracting calculator data...")
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
    
    print(f"\n✅ Extraction complete! {len(extracted_pages)} pages processed.")
    print("\n📁 Data organization:")
    
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
