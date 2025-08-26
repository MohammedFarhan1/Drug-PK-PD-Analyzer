#!/usr/bin/env python3
"""
Drug PK/PD Analyzer - Command Line Interface
"""

import sys
import argparse
from core import DrugAnalyzer, DRUG_DATABASE

def main():
    parser = argparse.ArgumentParser(description='Drug PK/PD Analysis CLI')
    parser.add_argument('drug_name', help='Name of the drug to analyze')
    parser.add_argument('--type', choices=['comprehensive', 'comparison', 'clinical'], 
                       default='comprehensive', help='Analysis type')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', choices=['text', 'excel', 'pdf'], 
                       default='text', help='Output format')
    parser.add_argument('--list-drugs', action='store_true', help='List available drugs')
    
    args = parser.parse_args()
    
    if args.list_drugs:
        print("Available drugs in database:")
        for i, drug in enumerate(DRUG_DATABASE, 1):
            print(f"{i:2d}. {drug}")
        return 0
    
    try:
        analyzer = DrugAnalyzer()
        
        print(f"🔬 Analyzing {args.drug_name}...")
        result = analyzer.generate_analysis(args.drug_name, args.type)
        
        if not result['success']:
            print(f"❌ Error: {result['error']}")
            return 1
        
        if args.format == 'text':
            output_content = result['content']
        elif args.format == 'excel':
            # Save as Excel file
            import pandas as pd
            df = pd.DataFrame(result['table_data']['structured_data'][1:], 
                            columns=result['table_data']['structured_data'][0])
            output_file = args.output or f"{args.drug_name.replace(' ', '_')}_pk_pd.xlsx"
            df.to_excel(output_file, index=False)
            print(f"✅ Excel file saved to {output_file}")
            return 0
        elif args.format == 'pdf':
            print("❌ PDF export from CLI not implemented. Use web interface.")
            return 1
        else:
            output_content = result['content']
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"✅ Results saved to {args.output}")
        else:
            print("\n" + "="*60)
            print(f"Analysis Results: {args.drug_name}")
            print("="*60)
            print(output_content)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())