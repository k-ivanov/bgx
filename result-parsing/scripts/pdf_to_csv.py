#!/usr/bin/env python3
"""
PDF to CSV Converter for Navigation Race Results
This script extracts race numbers, competitor names, and points from PDF files.
"""

import os
import sys
from pathlib import Path
import re
import argparse
import PyPDF2
import pandas as pd

def clean_text(text):
    """Clean and normalize text from PDF"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def extract_data_from_pdf(pdf_path):
    """
    Extract race numbers, names and position from a PDF file.
    Groups data by sections starting with 'Навигация - '.
    Format: number + string + number (e.g., "112Станислав  КИРИЛОВ1")
    Args:
        pdf_path (str): Path to the PDF file
    Returns:
        dict: Dictionary where keys are section names and values are lists of data
    """
    grouped_data = {}
    current_section = None
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Pattern to match: number + text + number
            # Example: 112Станислав  КИРИЛОВ1
            pattern = r'^(\d+)([А-Яа-яA-Za-z\s]+?)(\d+)$'
            
            # Pattern to match section headers with flexible spacing
            # Example: "Навигация  ДЕН 2"
            section_pattern = r'^Навигация\s+ДЕН\s+2'
            
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Process text line by line
                lines = text.split('\n')
                
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    # print(f"LINE: {line}")
                    # Check if this is a section header
                    section_match = re.match(section_pattern, line)
                    
                    if section_match:
                        print(f"SECTION MATCH: {section_match}")
                        # The next line should contain the section name (e.g., "ПРОФИ", "ЕКСПЕРТ")
                        section_name = lines[i].strip()[:30]
                        grouped_data[current_section] = []
                        current_section = section_name
                        print(f"SECTION NAME: {section_name}")
                        i += 2
                        continue
                    
                    # Try to match the data pattern
                    match = re.match(pattern, line)
                    if match and current_section:
                        race_number = match.group(1)
                        name = match.group(2).strip()
                        name_split = name.split(' ')
                        first_name = name_split[0]
                        last_name = name_split[1] if len(name_split[1]) > 1 else name_split[2]
                        position = match.group(3)
                        
                        # Extract RaceTeam from next line
                        race_team = ""
                        if i + 1 < len(lines):
                            race_team = lines[i + 1].strip()
                        
                        # Extract Points from the line after that (number after space)
                        points = ""
                        if i + 2 < len(lines):
                            points_line = lines[i + 2].strip()
                            # Extract number after space
                            points_match = re.search(r'\s+(\d+)$', points_line)
                            if points_match:
                                points = points_match.group(1)
                        
                        grouped_data[current_section].append({
                            'RaceNumber': race_number,
                            'FirstName': first_name,
                            'LastName': last_name,
                            'Position': position,
                            # 'RaceTeam': race_team,
                            'Points': points
                        })
                        print(f"Extracted: RaceNumber={race_number}, Name={name}, Position={position}, Team={race_team}, Points={points} -> {current_section}")
                        
                        # Skip the next 2 lines as we've already processed them
                        i += 3
                        continue
                    
                    i += 1
                
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        sys.exit(1)
    
    return grouped_data

def save_grouped_data_to_csvs(grouped_data, output_dir, skip_mapping=False):
    """
    Save grouped data to separate CSV files.
    Args:
        grouped_data (dict): Dictionary where keys are section names and values are lists of data
        output_dir (Path): Directory where CSV files should be saved
        skip_mapping (bool): If True, skip filename mapping and use original section names
    """
    if not grouped_data:
        print("No data was extracted from the PDF.")
        return
    
    # Mapping for cleaner filenames
    filename_mapping = { 
        'ЕКСПЕРТ': 'expert',
        'ПРОФИ': 'profi',
        'ЖЕНИ': 'women',
        'СЕНЬОРИ_40': 'seniors_40',
        'СЕНЬОРИ_50': 'seniors_50',
        'СТАНДАРТ_ДЖУНИ': 'standard_junior',
        'СТАНДАРТ': 'standard'
    }
    
    total_entries = 0
    for section_name, data in grouped_data.items():
        if not data:
            print(f"No data for section: {section_name}")
            continue
        
        try:
            # Create a safe filename from the section name
            safe_filename = re.sub(r'[^\w\s-]', '', section_name)
            safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
            print(f"SAFE FILENAME: {section_name}")
            
            # Check if section name starts with any key in the mapping
            csv_filename = safe_filename
            if not skip_mapping:
                for key, value in filename_mapping.items():
                    if safe_filename.startswith(key):
                        csv_filename = value
                        break
            
            output_path = output_dir / f'{csv_filename}.csv'
            
            df = pd.DataFrame(data)
            # Ensure columns are in the desired order
            df = df[['RaceNumber', 'FirstName', 'LastName', 'Position', 'Points']]
            df.to_csv(output_path, index=False, encoding='utf-8')
            print(f"Saved {len(data)} entries to {output_path}")
            total_entries += len(data)
        except Exception as e:
            print(f"Error saving CSV for section '{section_name}': {str(e)}")
    
    print(f"\nTotal: Extracted {total_entries} entries across {len(grouped_data)} sections")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract data from navigation race PDF files to CSV')
    parser.add_argument('--skip-mapping', action='store_true', 
                        help='Skip filename mapping and use original section names')
    args = parser.parse_args()
    
    # Get the absolute path to the PDF directory
    base_dir = Path(__file__).parent.parent
    pdf_dir = base_dir / 'pdfs'
    output_base_dir = base_dir / 'output'
    
    # Create output directory if it doesn't exist
    output_base_dir.mkdir(exist_ok=True)
    
    # Find all PDF files in the pdfs directory
    pdf_files = list(pdf_dir.glob('*.pdf'))
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    if args.skip_mapping:
        print("Filename mapping: DISABLED (using original section names)\n")
    else:
        print("Filename mapping: ENABLED\n")
    
    # Process each PDF file
    for pdf_path in pdf_files:
        print(f"{'='*60}")
        print(f"Processing PDF: {pdf_path.name}")
        print(f"{'='*60}")
        
        # Create a subfolder with the PDF name (without extension)
        pdf_name = pdf_path.stem  # Gets filename without extension
        output_dir = output_base_dir / pdf_name
        output_dir.mkdir(exist_ok=True)
        
        print(f"Output directory: {output_dir}")
        
        try:
            grouped_data = extract_data_from_pdf(pdf_path)
            
            if not grouped_data:
                print(f"Warning: No data was extracted from {pdf_path.name}")
                continue
                
            save_grouped_data_to_csvs(grouped_data, output_dir, skip_mapping=args.skip_mapping)
            print(f"✓ Successfully processed {pdf_path.name}\n")
            
        except Exception as e:
            print(f"✗ Error processing {pdf_path.name}: {str(e)}\n")
            continue
    
    print(f"{'='*60}")
    print("Processing complete!")

if __name__ == "__main__":
    main()