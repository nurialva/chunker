#!/usr/bin/env python3
"""
Split JSONL file into chunks of N lines (default: 1000)
Usage: python split_jsonl.py input.jsonl [chunk_size]
"""

import os
import sys
from pathlib import Path

def split_jsonl(input_file, chunk_size=50):
    """
    Split JSONL file into multiple files, each with chunk_size lines.
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ Error: File '{input_file}' not found!")
        return
    
    if not input_path.suffix == '.jsonl':
        print(f"⚠️  Warning: File extension is not .jsonl, but continuing...")
    
    # Create output directory
    output_dir = input_path.parent / f"{input_path.stem}_split"
    output_dir.mkdir(exist_ok=True)
    
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Splitting '{input_file}' into chunks of {chunk_size} lines...")
    
    total_lines = 0
    file_count = 0
    current_lines = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            current_lines.append(line)
            total_lines += 1
            
            if len(current_lines) >= chunk_size:
                file_count += 1
                output_file = output_dir / f"part_{file_count:04d}.jsonl"
                with open(output_file, 'w', encoding='utf-8') as out:
                    out.write('\n'.join(current_lines))
                print(f"  ✅ Created {output_file.name} ({len(current_lines)} lines)")
                current_lines = []
        
        # Write remaining lines
        if current_lines:
            file_count += 1
            output_file = output_dir / f"part_{file_count:04d}.jsonl"
            with open(output_file, 'w', encoding='utf-8') as out:
                out.write('\n'.join(current_lines))
            print(f"  ✅ Created {output_file.name} ({len(current_lines)} lines)")
    
    print(f"\n✅ Done! Split {total_lines} lines into {file_count} files.")
    print(f"📁 Files saved in: {output_dir}")

def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python split_jsonl.py <input.jsonl> [chunk_size]")
        print("Example: python split_jsonl.py pages.jsonl 1000")
        print("         python split_jsonl.py pages.jsonl 500")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Default chunk size 1000, or from argument
    chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    split_jsonl(input_file, chunk_size)

if __name__ == "__main__":
    main()
