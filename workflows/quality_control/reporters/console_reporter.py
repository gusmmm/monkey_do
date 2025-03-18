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
    
    def report_birth_analysis(self, results: Dict[str, Any]) -> None:
        """Format birth date analysis results for console."""
        print("\n" + "="*80)
        print("👶 BIRTH DATE ANALYSIS")
        print("="*80)
        
        # Report missing dates
        missing = results.get('missing', {})
        print("\n🔍 Missing Birth Date Analysis:")
        if missing.get('count', 0) == 0:
            print("   ✅ No missing birth dates found")
        else:
            print(f"   ⚠️ Found {missing['count']} missing birth dates ({missing['percentage']:.2%} of total records)")
            self._print_row_list(missing.get('rows', []))
        
        # Report date format
        format_results = results.get('format', {})
        print("\n📋 Date Format Analysis:")
        if format_results.get('invalid_count', 0) == 0:
            print("   ✅ All birth dates follow the expected format (dd-mm-yyyy)")
        else:
            print(f"   ⚠️ Found {format_results['invalid_count']} birth dates with unexpected format")
            print("\n   Records with invalid date formats:")
            
            for i, example in enumerate(format_results.get('invalid_examples', []), 1):
                print(f"   {i}. ID '{example['id']}' has birth date '{example['date']}' at row {example['row'] + 2}")
        
        # Report date validity
        validity = results.get('validity', {})
        print("\n🔎 Birth Date Validity Check:")
        
        if 'error' in validity:
            print(f"   ⚠️ Error analyzing date validity: {validity['error']}")
        else:
            too_old_count = validity.get('too_old_count', 0)
            future_count = validity.get('future_count', 0)
            
            if too_old_count == 0 and future_count == 0:
                print("   ✅ All birth dates are within reasonable ranges (1900 to present)")
            else:
                if too_old_count > 0:
                    print(f"   ⚠️ Found {too_old_count} birth dates before 1900")
                    print("\n   Examples of unusually old birth dates:")
                    for i, example in enumerate(validity.get('too_old_examples', []), 1):
                        print(f"   {i}. ID '{example['id']}' has birth date '{example['date']}' (year {example['year']}) at row {example['row'] + 2}")
                
                if future_count > 0:
                    print(f"   ⚠️ Found {future_count} birth dates in the future")
                    print("\n   Examples of future birth dates:")
                    for i, example in enumerate(validity.get('future_examples', []), 1):
                        print(f"   {i}. ID '{example['id']}' has birth date '{example['date']}' (year {example['year']}) at row {example['row'] + 2}")
        
        # Report age statistics
        age_stats = results.get('age', {})
        print("\n📊 Patient Age Statistics:")
        
        if 'error' in age_stats:
            if age_stats['error'] == 'Admission date column not found':
                print("   ⚠️ Cannot calculate patient age: admission date column not found")
            elif age_stats['error'] == 'No records with both admission and birth dates':
                print("   ℹ️ No records with both admission and birth dates found")
            elif age_stats['error'] == 'No records with valid date formats':
                print("   ⚠️ No records with valid date formats found")
            else:
                print(f"   ⚠️ Error calculating age statistics: {age_stats['error']}")
        elif age_stats.get('count', 0) == 0:
            print("   ℹ️ No data available for age statistics")
        else:
            print(f"   Records analyzed: {age_stats['count']}")
            print(f"   Average age: {age_stats['mean_age']:.1f} years")
            print(f"   Median age: {age_stats['median_age']:.1f} years")
            print(f"   Youngest patient: {age_stats['min_age']:.1f} years")
            print(f"   Oldest patient: {age_stats['max_age']:.1f} years")
            
            # Display age distribution
            distribution = age_stats.get('age_distribution', {})
            if distribution:
                print("\n   Age Distribution:")
                for age_range, count in sorted(distribution.items()):
                    percentage = count / age_stats['count'] * 100
                    bar_length = int(percentage / 2)  # Scale to reasonable bar length
                    bar = "█" * bar_length
                    print(f"   {age_range} years: {count:3d} patients ({percentage:5.1f}%) {bar}")
            
            # Report unusual ages
            unusual = age_stats.get('unusual_ages', {})
            
            if unusual:
                # Very young patients
                very_young_count = unusual.get('very_young_count', 0)
                if very_young_count > 0:
                    print(f"\n   ⚠️ Found {very_young_count} very young patients (under 5 years old)")
                    for i, example in enumerate(unusual.get('very_young', []), 1):
                        print(f"   {i}. ID '{example['id']}' age: {example['age']:.1f} years (birth: {example['birth_date']}, admission: {example['admission_date']}) - row {example['row'] + 2}")
                
                # Very old patients
                very_old_count = unusual.get('very_old_count', 0)
                if very_old_count > 0:
                    print(f"\n   ⚠️ Found {very_old_count} very old patients (over 100 years old)")
                    for i, example in enumerate(unusual.get('very_old', []), 1):
                        print(f"   {i}. ID '{example['id']}' age: {example['age']:.1f} years (birth: {example['birth_date']}, admission: {example['admission_date']}) - row {example['row'] + 2}")
                
                # Negative ages
                negative_count = unusual.get('negative_count', 0)
                if negative_count > 0:
                    print(f"\n   ⚠️ Found {negative_count} patients with negative ages (admission before birth!)")
                    for i, example in enumerate(unusual.get('negative', []), 1):
                        print(f"   {i}. ID '{example['id']}' age: {example['age']:.1f} years (birth: {example['birth_date']}, admission: {example['admission_date']}) - row {example['row'] + 2}")
        
        print("\n" + "="*80)
    
    def _print_row_list(self, rows: List[int], limit: int = 10) -> None:
        """Helper to print a list of row numbers with limit."""
        if not rows:
            return
            
        # Convert all entries to integers explicitly
        try:
            row_nums = [int(r) + 2 for r in rows if isinstance(r, (int, float))]
        except Exception:
            print("   Warning: Unable to parse row numbers properly")
            return
        
        if len(row_nums) <= limit:
            rows_display = ", ".join(str(row) for row in row_nums)
        else:
            first_rows = ", ".join(str(row) for row in row_nums[:limit])
            rows_display = f"{first_rows}, ... ({len(row_nums) - limit} more)"
                
        print(f"   Rows with issues: {rows_display}")

    def report_processo_analysis(self, results: Dict[str, Any]) -> None:
        """Format processo column analysis results for console."""
        print("\n" + "="*80)
        print("📝 PROCESSO (MEDICAL RECORD) ANALYSIS")
        print("="*80)
        
        # Report missing values
        missing = results.get('missing', {})
        print("\n🔍 Missing Values Analysis:")
        if missing.get('count', 0) == 0:
            print("   ✅ No missing processo values found")
        else:
            print(f"   ⚠️ Found {missing['count']} missing processo values ({missing['percentage']:.2%} of total records)")
            print("\n   Examples of records with missing processo:")
            
            for i, example in enumerate(missing.get('examples', []), 1):
                print(f"   {i}. ID '{example['id']}' at row {example['row'] + 2}")
        
        # Report invalid values
        invalid = results.get('invalid', {})
        print("\n🔢 Non-numeric Values Analysis:")
        if invalid.get('count', 0) == 0:
            print("   ✅ All processo values are numeric")
        else:
            print(f"   ⚠️ Found {invalid['count']} non-numeric processo values ({invalid['percentage']:.2%} of non-missing values)")
            print("\n   Examples of records with non-numeric processo values:")
            
            for i, example in enumerate(invalid.get('examples', []), 1):
                print(f"   {i}. ID '{example['id']}' has '{example['value']}' at row {example['row'] + 2}")
        
        print("\n" + "="*80)

    def report_nome_analysis(self, results: Dict[str, Any]) -> None:
        """Format nome column analysis results for console."""
        print("\n" + "="*80)
        print("👤 PATIENT NAME ANALYSIS")
        print("="*80)
        
        # Report missing values
        missing = results.get('missing', {})
        print("\n🔍 Missing Names Analysis:")
        if missing.get('count', 0) == 0:
            print("   ✅ No missing patient names found")
        else:
            print(f"   ⚠️ Found {missing['count']} missing patient names ({missing['percentage']:.2%} of total records)")
            print("\n   Records with missing names:")
            
            for i, example in enumerate(missing.get('examples', []), 1):
                print(f"   {i}. ID '{example['id']}' at row {example['row'] + 2}")
        
        print("\n" + "="*80)

    def report_categorical_analysis(self, results: Dict[str, Any], column_name: str, title: str) -> None:
        """Format categorical column analysis results for console."""
        print("\n" + "="*80)
        print(f"{title}")
        print("="*80)
        
        # Report missing values
        missing = results.get('missing', {})
        print(f"\n🔍 Missing {column_name.capitalize()} Analysis:")
        if missing.get('count', 0) == 0:
            print(f"   ✅ No missing {column_name} values found")
        else:
            print(f"   ⚠️ Found {missing['count']} missing {column_name} values ({missing['percentage']:.2%} of total records)")
            print(f"\n   Records with missing {column_name}:")
            
            for i, example in enumerate(missing.get('examples', []), 1):
                print(f"   {i}. ID '{example['id']}' at row {example['row'] + 2}")
        
        # Report value frequencies
        frequencies = results.get('frequency', {})
        print(f"\n📊 {column_name.capitalize()} Value Distribution:")
        
        if frequencies.get('unique_count', 0) == 0:
            print(f"   ℹ️ No {column_name} values found (all missing)")
        else:
            print(f"   Found {frequencies['unique_count']} unique {column_name} values")
            print(f"\n   Frequency breakdown:")
            
            # Sort by frequency (descending)
            sorted_values = sorted(
                frequencies.get('frequencies', {}).items(),
                key=lambda x: x[1]['count'], 
                reverse=True
            )
            
            for value, details in sorted_values:
                count = details['count']
                percentage = details['percentage']
                bar_length = int(percentage * 40)  # Scale for reasonable bar length
                bar = "█" * bar_length
                print(f"   {value:15} : {count:4d} ({percentage:6.2%}) {bar}")
        
        # Report unexpected values if applicable
        unexpected = results.get('unexpected', {})
        if unexpected is not None and 'count' in unexpected:
            print(f"\n⚠️ Unexpected {column_name.capitalize()} Values:")
            
            if unexpected.get('count', 0) == 0:
                print(f"   ✅ All {column_name} values match expected format")
            else:
                print(f"   ⚠️ Found {unexpected['count']} unexpected {column_name} values ({unexpected['percentage']:.2%} of non-missing values)")
                print(f"\n   Examples of unexpected values:")
                
                for i, example in enumerate(unexpected.get('examples', []), 1):
                    print(f"   {i}. ID '{example['id']}' has '{example['value']}' at row {example['row'] + 2}")
        
        print("\n" + "="*80)

    def report_sexo_analysis(self, results: Dict[str, Any]) -> None:
        """Format sexo column analysis results for console."""
        self.report_categorical_analysis(results, "sexo", "👫 PATIENT SEX/GENDER ANALYSIS")

    def report_destino_analysis(self, results: Dict[str, Any]) -> None:
        """Format destino column analysis results for console."""
        self.report_categorical_analysis(results, "destino", "🏥 PATIENT DESTINATION ANALYSIS")

    def report_origem_analysis(self, results: Dict[str, Any]) -> None:
        """Format origem column analysis results for console."""
        self.report_categorical_analysis(results, "origem", "🚑 PATIENT ORIGIN ANALYSIS")