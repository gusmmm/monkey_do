from typing import Dict, Any, List, Optional

class ConsoleReporter:
    """Console reporting for analysis results."""
    
    def report_file_analysis(self, results: Dict[str, Any]) -> None:
        """Format file analysis results for console."""
        print("\n" + "="*80)
        print(f"📊 FILE ANALYSIS: {results['file_name']}")
        print("="*80)
        
        print(f"\n📍 File Location:")
        print(f"   {results['file_path']}")
        
        # Size information
        print(f"\n💾 File Size: {results['file_size_kb']:.2f} KB")
        
        # Column information
        print(f"\n📋 Column Information:")
        print(f"   Total Columns: {results['column_count']}")
        print("\n   Column Names:")
        
        # Format column names in multiple rows for readability
        columns = results['columns']
        col_width = max(len(col) for col in columns) + 2
        cols_per_row = max(1, 80 // col_width)
        
        for i in range(0, len(columns), cols_per_row):
            cols_chunk = columns[i:i+cols_per_row]
            print("   " + "  ".join(f"{col:{col_width}}" for col in cols_chunk))
        
        # Row information
        print(f"\n🔢 Row Information:")
        print(f"   Total Rows: {results['row_count']}")
        
        print("\n" + "="*80)
    
    def report_id_analysis(self, results: Dict[str, Any]) -> None:
        """Format ID analysis results for console."""
        print("\n" + "="*80)
        print("🔍 ID COLUMN ANALYSIS")
        print("="*80)
        
        # Report missing IDs
        missing = results.get('missing', {})
        print("\n📑 Missing ID Analysis:")
        if missing.get('count', 0) == 0:
            print("   ✅ No missing IDs found")
        else:
            print(f"   ⚠️ Found {missing['count']} missing IDs ({missing['percentage']:.2%} of total records)")
            self._print_row_list(missing.get('rows', []))
        
        # Report duplicates
        duplicates = results.get('duplicates', {})
        print("\n🔄 Duplicate ID Analysis:")
        if duplicates.get('count', 0) == 0:
            print("   ✅ No duplicate IDs found")
        else:
            print(f"   ⚠️ Found {duplicates['count']} rows with duplicate IDs ({duplicates['percentage']:.2%} of total records)")
            
            # Group and display duplicate values
            if duplicates.get('duplicates'):
                print(f"\n   Duplicated ID values ({len(duplicates['duplicates'])} unique values):")
                
                # Display each duplicated ID with its row numbers
                for i, dup_info in enumerate(duplicates['duplicates'][:10], 1):
                    # Find rows with this ID
                    rows_str = ", ".join(str(row + 2) for row in dup_info['rows'])  # +2 for 1-indexing and header
                    print(f"   {i}. ID '{dup_info['id']}' found in rows: {rows_str}")
                
                # If more than 10 duplicate IDs, show ellipsis
                if len(duplicates['duplicates']) > 10:
                    print(f"   ... and {len(duplicates['duplicates']) - 10} more duplicated IDs")
        
        # Report sequence analysis
        sequences = results.get('sequences', {})
        if sequences:
            print("\n" + "="*80)
            print("🔢 ID SEQUENCE ANALYSIS BY YEAR")
            print("="*80)
            
            print("\n📊 ID Analysis by Year:")
            print("   Year  Count  Min Serial  Max Serial  Missing Values")
            print("   ----  -----  ----------  ----------  --------------")
            
            for year_data in sorted(sequences.get('years', []), key=lambda x: x['year'], reverse=True):
                year = year_data['year']
                count = year_data['count']
                
                if not year_data.get('valid', True):
                    print(f"   {year}    {count:4d}  {year_data.get('error', 'Invalid data')}")
                    continue
                
                min_serial = year_data['min_serial']
                max_serial = year_data['max_serial']
                missing_count = year_data['missing_count']
                missing_pct = year_data['missing_percentage']
                
                # Format the missing value count
                missing_display = f"{missing_count} ({missing_pct:.1%})" if missing_count > 0 else "0"
                
                # Print row
                print(f"   {year}    {count:4d}  {min_serial:10d}  {max_serial:10d}  {missing_display}")
                
                # If missing values, show details
                if missing_count > 0:
                    missing_serials = year_data['missing_serials']
                    if len(missing_serials) <= 5:
                        missing_serials_display = ", ".join(str(s) for s in missing_serials)
                    else:
                        first_five = ", ".join(str(s) for s in missing_serials[:5])
                        missing_serials_display = f"{first_five}, ... ({len(missing_serials) - 5} more)"
                        
                    print(f"      Missing in {year}: {missing_serials_display}")
        
        # Report pattern consistency
        pattern = results.get('pattern', {})
        if pattern:
            print("\n" + "="*80)
            print("🔍 ID PATTERN CONSISTENCY CHECK")
            print("="*80)
            
            # Check if all values follow the pattern
            if pattern.get('invalid_count', 0) == 0:
                print("\n✅ All ID values follow the expected format (YYXXX)")
            else:
                invalid_count = pattern.get('invalid_count', 0)
                print(f"\n⚠️ Found {invalid_count} ID values with unexpected format")
                
                # Display examples of invalid IDs
                if pattern.get('invalid_examples'):
                    print("\n   Examples of invalid ID formats:")
                    for i, invalid in enumerate(pattern['invalid_examples'], 1):
                        print(f"   {i}. '{invalid['id']}' at row {invalid['row'] + 2}")  # +2 for 1-indexing and header
            
            # Check year patterns
            years = pattern.get('years', [])
            if years:
                print(f"\n📅 Years found in ID prefixes: {', '.join(sorted(years))}")
            
            # Check for unusual patterns
            future_years = pattern.get('future_years', [])
            if future_years:
                print(f"\n⚠️ Warning: Found IDs with future years: {', '.join(future_years)}")
            
            very_old_years = pattern.get('very_old_years', [])
            if very_old_years:
                print(f"\n⚠️ Warning: Found IDs with potentially old years: {', '.join(very_old_years)}")
        
        print("\n" + "="*80)
    
    def report_admission_analysis(self, results: Dict[str, Any]) -> None:
        """Format admission date analysis results for console."""
        print("\n" + "="*80)
        print("📅 ADMISSION DATE ANALYSIS")
        print("="*80)
        
        # Report missing dates
        missing = results.get('missing', {})
        print("\n🔍 Missing Date Analysis:")
        if missing.get('count', 0) == 0:
            print("   ✅ No missing admission dates found")
        else:
            print(f"   ⚠️ Found {missing['count']} missing admission dates ({missing['percentage']:.2%} of total records)")
            self._print_row_list(missing.get('rows', []))
        
        # Report date format
        format_results = results.get('format', {})
        print("\n📋 Date Format Analysis:")
        if format_results.get('invalid_count', 0) == 0:
            print("   ✅ All dates follow the expected format (dd-mm-yyyy)")
        else:
            print(f"   ⚠️ Found {format_results['invalid_count']} dates with unexpected format")
            print("\n   Records with invalid date formats:")
            
            for i, example in enumerate(format_results.get('invalid_examples', []), 1):
                print(f"   {i}. ID '{example['id']}' has date '{example['date']}' at row {example['row'] + 2}")
        
        # Report year consistency
        consistency = results.get('year_consistency', {})
        print("\n🔄 Year Consistency Check:")
        
        if 'error' in consistency:
            print(f"   ⚠️ Error analyzing date consistency: {consistency['error']}")
        elif consistency.get('inconsistent_count', 0) == 0:
            print("   ✅ All IDs match their admission year (first 2 digits of ID = last 2 digits of year)")
        else:
            print(f"   ⚠️ Found {consistency['inconsistent_count']} IDs that don't match their admission year")
            print("\n   ID vs. Year inconsistencies:")
            
            for i, example in enumerate(consistency.get('inconsistent_examples', []), 1):
                print(f"   {i}. ID '{example['id']}' (prefix '{example['id_prefix']}') has date '{example['date']}' (year '{example['year']}') at row {example['row'] + 2}")
        
        print("\n" + "="*80)
    
    def report_discharge_analysis(self, results: Dict[str, Any]) -> None:
        """Format discharge date analysis results for console."""
        print("\n" + "="*80)
        print("📤 DISCHARGE DATE ANALYSIS")
        print("="*80)
        
        # Report date format
        format_results = results.get('format', {})
        print("\n📋 Date Format Analysis:")
        
        total_count = format_results.get('total_count', 0)
        if total_count == 0:
            print("   ℹ️ No discharge dates found in the dataset")
        elif format_results.get('invalid_count', 0) == 0:
            print("   ✅ All discharge dates follow the expected format (dd-mm-yyyy)")
        else:
            print(f"   ⚠️ Found {format_results['invalid_count']} discharge dates with unexpected format")
            print("\n   Records with invalid date formats:")
            
            for i, example in enumerate(format_results.get('invalid_examples', []), 1):
                print(f"   {i}. ID '{example['id']}' has discharge date '{example['date']}' at row {example['row'] + 2}")
        
        # Report chronology check
        chronology = results.get('chronology', {})
        print("\n🔄 Chronology Check (discharge date >= admission date):")
        
        if 'error' in chronology and chronology['error'] == 'Admission date column not found':
            print("   ⚠️ Cannot verify date chronology: admission date column not found")
        elif chronology.get('valid_pairs_count', 0) == 0:
            print("   ℹ️ No records with both admission and discharge dates found")
        elif chronology.get('error_count', 0) == 0:
            print("   ✅ All discharge dates are on or after their corresponding admission dates")
        else:
            print(f"   ⚠️ Found {chronology['error_count']} records where discharge date is before admission date")
            print("\n   Chronology errors:")
            
            for i, error in enumerate(chronology.get('chronology_errors', []), 1):
                print(f"   {i}. ID '{error['id']}': admission date '{error['admission_date']}' occurs AFTER discharge date '{error['discharge_date']}' (row {error['row'] + 2})")
        
        # Report duration statistics
        duration = results.get('duration', {})
        print("\n📊 Hospitalization Duration Statistics:")
        
        if 'error' in duration:
            if duration['error'] == 'Admission date column not found':
                print("   ⚠️ Cannot calculate stay duration: admission date column not found")
            elif duration['error'] == 'No records with both admission and discharge dates':
                print("   ℹ️ No records with both admission and discharge dates found")
            elif duration['error'] == 'No records with valid date formats':
                print("   ⚠️ No records with valid date formats found")
            else:
                print(f"   ⚠️ Error calculating duration statistics: {duration['error']}")
        elif duration.get('count', 0) == 0:
            print("   ℹ️ No data available for duration statistics")
        else:
            print(f"   Records analyzed: {duration['count']}")
            print(f"   Average stay: {duration['mean_days']:.1f} days")
            print(f"   Median stay: {duration['median_days']:.1f} days")
            print(f"   Shortest stay: {duration['min_days']} days")
            print(f"   Longest stay: {duration['max_days']} days")
            
            # Show extremely long stays (potential errors)
            if duration.get('long_stays_count', 0) > 0:
                print("\n⚠️ Potentially unusual long stays (> 60 days):")
                
                for i, stay in enumerate(duration.get('long_stays', []), 1):
                    print(f"   {i}. ID '{stay['id']}': {stay['days']} days (admitted: {stay['admission_date']}, discharged: {stay['discharge_date']}) - row {stay['row'] + 2}")
                    
                if duration['long_stays_count'] > len(duration.get('long_stays', [])):
                    print(f"      ... and {duration['long_stays_count'] - len(duration.get('long_stays', []))} more")
        
        print("\n" + "="*80)
    
    def _print_row_list(self, rows: List[int], limit: int = 10) -> None:
        """Helper to print a list of row numbers with limit."""
        # Add 2 to row index (1 for 0-indexing, 1 for header row in CSV)
        row_nums = [r + 2 for r in rows]
        
        if len(row_nums) <= limit:
            rows_display = ", ".join(str(row) for row in row_nums)
        else:
            first_rows = ", ".join(str(row) for row in row_nums[:limit])
            rows_display = f"{first_rows}, ... ({len(row_nums) - limit} more)"
            
        print(f"   Rows with issues: {rows_display}")