"""
Main script for processing invoices using the Donut model.
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from invoice_processor import InvoiceProcessor


def main():
    """Main entry point for the invoice processing application."""
    parser = argparse.ArgumentParser(
        description='Process invoices using Donut transformer model'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='./invoices',
        help='Path to input directory containing invoice images or a single invoice image'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./output',
        help='Path to output directory for JSON results'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--single',
        action='store_true',
        help='Process a single invoice file instead of a directory'
    )
    
    args = parser.parse_args()
    
    # Initialize the processor
    print("Initializing Invoice Processor...")
    processor = InvoiceProcessor(config_path=args.config)
    
    # Process invoices
    if args.single:
        # Process single file
        if not os.path.exists(args.input):
            print(f"Error: File not found: {args.input}")
            sys.exit(1)
        
        print(f"\nProcessing single invoice: {args.input}")
        result = processor.process_invoice(args.input)
        
        # Create output directory
        os.makedirs(args.output, exist_ok=True)
        
        # Save result
        output_file = os.path.join(args.output, f"{Path(args.input).stem}_output.json")
        processor.save_results([result], output_file)
        
        if result['status'] == 'success':
            print("\n✓ Invoice processed successfully!")
        else:
            print(f"\n✗ Error processing invoice: {result.get('error', 'Unknown error')}")
    else:
        # Process directory
        if not os.path.isdir(args.input):
            print(f"Error: Directory not found: {args.input}")
            print("Use --single flag to process a single file instead.")
            sys.exit(1)
        
        print(f"\nProcessing invoices from directory: {args.input}")
        results = processor.process_directory(args.input, args.output)
        
        # Save combined results
        output_file = os.path.join(args.output, "all_results.json")
        processor.save_results(results, output_file)
        
        # Print summary
        success_count = sum(1 for r in results if r['status'] == 'success')
        error_count = len(results) - success_count
        
        print("\n" + "="*50)
        print(f"Processing complete!")
        print(f"Total: {len(results)} | Success: {success_count} | Errors: {error_count}")
        print("="*50)


if __name__ == "__main__":
    main()
