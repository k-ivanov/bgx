#!/usr/bin/env python3
"""
Script to aggregate race results from all CSVs in final_results folder.
Sums points for each unique rider (RaceNumber + FirstName + LastName)
and outputs grouped results by category.
"""

import csv
import os
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple


def parse_csv_file(file_path: Path) -> List[Dict]:
    """Parse a single CSV file and return list of rider data."""
    riders = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    riders.append({
                        'RaceNumber': row.get('RaceNumber', '').strip(),
                        'FirstName': row.get('FirstName', '').strip(),
                        'LastName': row.get('LastName', '').strip(),
                        'Position': int(row.get('Position', 0)),
                        'Points': float(row.get('Points', 0))
                    })
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid row in {file_path}: {row} - {e}")
                    continue
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return riders


def aggregate_results(final_results_dir: Path, skip_worst: bool = False) -> Tuple[Dict[str, Dict[Tuple, Dict]], Dict[str, List[str]]]:
    """
    Walk through all CSVs in final_results directory and aggregate by category.
    
    Args:
        final_results_dir: Path to the directory containing race results
        skip_worst: If True, remove worst result for riders with 7+ races
    
    Returns:
        Tuple of:
        - Dict with category name as key, and dict of riders as value
        - Dict with category name as key, and list of race names as value
    """
    # Dictionary: category_name -> {(race_num, first, last): {data}}
    category_results = defaultdict(lambda: defaultdict(lambda: {
        'RaceNumber': '',
        'FirstName': '',
        'LastName': '',
        'TotalPoints': 0.0,
        'RacesParticipated': 0,
        'BestPosition': float('inf'),
        'RaceResults': [],  # Track individual race results
        'RacePointsMap': {}  # Map: race_name -> points
    }))
    
    # Track all race names per category
    category_races = defaultdict(set)
    
    # Walk through all subdirectories
    for race_dir in final_results_dir.iterdir():
        if not race_dir.is_dir():
            continue
        
        race_name = race_dir.name
        print(f"\nProcessing race: {race_name}")
        
        # Process all CSV files in this race directory
        for csv_file in race_dir.glob('*.csv'):
            category = csv_file.stem  # e.g., 'expert', 'profi', etc.
            print(f"  - Category: {category}")
            
            riders = parse_csv_file(csv_file)
            
            # Track this race for this category
            category_races[category].add(race_name)
            
            for rider in riders:
                # Create unique key for rider
                rider_key = (
                    rider['RaceNumber'],
                    rider['FirstName'],
                    rider['LastName']
                )
                
                # Update aggregated data
                agg = category_results[category][rider_key]
                agg['RaceNumber'] = rider['RaceNumber']
                agg['FirstName'] = rider['FirstName']
                agg['LastName'] = rider['LastName']
                agg['TotalPoints'] += rider['Points']
                agg['RacesParticipated'] += 1
                agg['BestPosition'] = min(agg['BestPosition'], rider['Position'])
                agg['RaceResults'].append({
                    'race': race_name,
                    'points': rider['Points'],
                    'position': rider['Position']
                })
                # Track points for this specific race
                agg['RacePointsMap'][race_name] = rider['Points']
    
    # Apply skip-worst-result logic if enabled
    if skip_worst:
        print(f"\n{'='*60}")
        print("Applying 'skip-worst-result' logic...")
        print('='*60)
        
        for category, riders_dict in category_results.items():
            for rider_key, rider_data in riders_dict.items():
                if rider_data['RacesParticipated'] >= 7:
                    # Find worst result (lowest points)
                    race_results = rider_data['RaceResults']
                    worst_result = min(race_results, key=lambda x: x['points'])
                    
                    # Recalculate total without worst result
                    rider_data['TotalPoints'] -= worst_result['points']
                    rider_data['WorstResultDropped'] = worst_result['points']
                    rider_data['WorstRace'] = worst_result['race']
                    
                    print(f"  {rider_data['FirstName']} {rider_data['LastName']}: "
                          f"Dropped {worst_result['points']} pts from {worst_result['race']}")
                else:
                    rider_data['WorstResultDropped'] = None
                    rider_data['WorstRace'] = None
    
    # Convert race sets to sorted lists
    category_races_list = {cat: sorted(races) for cat, races in category_races.items()}
    
    return category_results, category_races_list


def write_category_results(output_dir: Path, category: str, riders_dict: Dict, 
                          race_names: List[str] = None, skip_worst: bool = False, 
                          full_report: bool = False):
    """Write aggregated results for a category to CSV."""
    output_file = output_dir / f"{category}.csv"
    
    # Convert to list and sort by TotalPoints (descending)
    riders_list = list(riders_dict.values())
    riders_list.sort(key=lambda x: (-x['TotalPoints'], x['BestPosition'], x['LastName']))
    
    # Assign final positions
    for position, rider in enumerate(riders_list, start=1):
        rider['FinalPosition'] = position
    
    # Write to CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'FinalPosition',
            'RaceNumber',
            'FirstName',
            'LastName',
            'TotalPoints',
            'RacesParticipated',
            'BestPosition'
        ]
        
        # Add skip-worst columns if enabled
        if skip_worst:
            fieldnames.extend(['WorstResultDropped', 'WorstRace'])
        
        # Add individual race columns if full report is enabled
        if full_report and race_names:
            # Add columns for each race
            for race_name in race_names:
                fieldnames.append(f'Race_{race_name}')
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for rider in riders_list:
            row_data = {
                'FinalPosition': rider['FinalPosition'],
                'RaceNumber': rider['RaceNumber'],
                'FirstName': rider['FirstName'],
                'LastName': rider['LastName'],
                'TotalPoints': rider['TotalPoints'],
                'RacesParticipated': rider['RacesParticipated'],
                'BestPosition': rider['BestPosition'] if rider['BestPosition'] != float('inf') else ''
            }
            
            if skip_worst:
                row_data['WorstResultDropped'] = rider.get('WorstResultDropped', '') or ''
                row_data['WorstRace'] = rider.get('WorstRace', '') or ''
            
            # Add individual race points if full report
            if full_report and race_names:
                race_points_map = rider.get('RacePointsMap', {})
                for race_name in race_names:
                    # Get points for this race, or 0 if rider didn't participate
                    row_data[f'Race_{race_name}'] = race_points_map.get(race_name, 0)
            
            writer.writerow(row_data)
    
    print(f"✓ Written {len(riders_list)} riders to {output_file}")


def main():
    """Main function to aggregate and output results."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Aggregate BGX racing results from all races'
    )
    parser.add_argument(
        '--skip-worst-result',
        action='store_true',
        help='For riders with 7+ races, drop the worst result from total points'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='bgx-result-2025',
        help='Output directory name (default: bgx-result-2025)'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Generate full report with individual race points columns'
    )
    
    args = parser.parse_args()
    
    # Get script directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Input directory
    final_results_dir = project_root / 'final_results'
    
    # Output directory
    output_dir = project_root / args.output_dir
    output_dir.mkdir(exist_ok=True)
    
    print("="*60)
    print("BGX Racing Results Aggregation")
    print("="*60)
    print(f"Input directory: {final_results_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Skip worst result: {'YES' if args.skip_worst_result else 'NO'}")
    print(f"Full report: {'YES' if args.full else 'NO'}")
    
    if not final_results_dir.exists():
        print(f"\nError: Directory not found: {final_results_dir}")
        return
    
    # Aggregate all results
    print("\n" + "="*60)
    print("Aggregating results from all races...")
    print("="*60)
    
    category_results, category_races = aggregate_results(final_results_dir, skip_worst=args.skip_worst_result)
    
    # Write results for each category
    print("\n" + "="*60)
    print("Writing aggregated results...")
    print("="*60)
    
    if not category_results:
        print("Warning: No results found!")
        return
    
    for category, riders_dict in sorted(category_results.items()):
        print(f"\nCategory: {category.upper()}")
        race_names = category_races.get(category, [])
        if args.full:
            print(f"  Races included: {', '.join(race_names)}")
        write_category_results(
            output_dir, category, riders_dict, 
            race_names=race_names,
            skip_worst=args.skip_worst_result,
            full_report=args.full
        )
    
    print("\n" + "="*60)
    print("✓ Aggregation complete!")
    print("="*60)
    print(f"\nResults saved to: {output_dir}")
    print(f"Categories processed: {', '.join(sorted(category_results.keys()))}")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("Summary Statistics:")
    print("="*60)
    for category in sorted(category_results.keys()):
        rider_count = len(category_results[category])
        print(f"  {category:20s}: {rider_count:4d} unique riders")


if __name__ == '__main__':
    main()

