import os
import json
import re
import sys
import argparse

def extract_data_files_from_notebook(notebook_path):
    """Extract data file references from notebook output cells"""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        data_files = []
        
        for cell in notebook.get('cells', []):
            # Look in output cells for the print pattern
            if cell.get('cell_type') == 'code' and 'outputs' in cell:
                for output in cell['outputs']:
                    if 'text' in output:
                        # Handle both string and list formats for text output
                        text_content = output['text']
                        if isinstance(text_content, list):
                            text_content = ''.join(text_content)
                        
                        # Look for the specific pattern: ... open file: filename
                        pattern = r'\.\.\.\ open\ file:\ (.+)'
                        matches = re.findall(pattern, text_content)
                        data_files.extend(matches)
                    
                    # Also check stdout output
                    if 'name' in output and output['name'] == 'stdout' and 'text' in output:
                        text_content = output['text']
                        if isinstance(text_content, list):
                            text_content = ''.join(text_content)
                        
                        pattern = r'\.\.\.\ open\ file:\ (.+)'
                        matches = re.findall(pattern, text_content)
                        data_files.extend(matches)
        
        return list(set(data_files))  # Remove duplicates
        
    except Exception as e:
        return [f"Error reading notebook: {e}"]

def check_data_files():
    """Check and list data files used in all notebooks"""
    nbooks_dir = "/home/b/b380352/pub/2025-08_hurricane-centric-paper/nbooks"
    
    if not os.path.exists(nbooks_dir):
        print(f"Error: Notebooks directory not found: {nbooks_dir}")
        return
    
    notebooks = [f for f in os.listdir(nbooks_dir) if f.endswith('.ipynb')]
    notebooks.sort()
    
    if not notebooks:
        print("No notebook files found in the nbooks directory.")
        return
    
    # Extract data files from each notebook
    notebook_data_files = {}
    for notebook in notebooks:
        notebook_path = os.path.join(nbooks_dir, notebook)
        data_files = extract_data_files_from_notebook(notebook_path)
        notebook_data_files[notebook] = data_files
    
    # Print results
    for notebook, files in notebook_data_files.items():
        print(f"\n{notebook}:")
        if files:
            for file in sorted(files):
                print(f"  - {file}")
        else:
            print("  - No data files found")

def pack_data_files():
    """Pack data files to target directory using rsync"""
    import subprocess
    from pathlib import Path
    
    target_dir = "/scratch/b/b380352/paulette"
    
    # Directory prefixes to remove
    prefixes_to_remove = [
        "/work/bb1376/data/",
        "/home/b/b380352/proj/2025-05_hurricane-centric-setup-tools/",
        "/home/b/b380352/pub/2025-08_hurricane-centric-paper/data/"
    ]
    
    print(f"Packing data files to: {target_dir}")
    
    # First get all data files from notebooks
    nbooks_dir = "/home/b/b380352/pub/2025-08_hurricane-centric-paper/nbooks"
    
    if not os.path.exists(nbooks_dir):
        print(f"Error: Notebooks directory not found: {nbooks_dir}")
        return
    
    notebooks = [f for f in os.listdir(nbooks_dir) if f.endswith('.ipynb')]
    notebooks.sort()
    
    if not notebooks:
        print("No notebook files found in the nbooks directory.")
        return
    
    # Collect all unique data files
    all_data_files = set()
    for notebook in notebooks:
        notebook_path = os.path.join(nbooks_dir, notebook)
        data_files = extract_data_files_from_notebook(notebook_path)
        all_data_files.update([f for f in data_files if not f.startswith("Error")])
    
    if not all_data_files:
        print("No data files found to pack.")
        return
    
    print(f"Found {len(all_data_files)} unique data files to pack.")
    
    # Create target directory
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    
    # Process each file
    successful_copies = 0
    failed_copies = 0
    
    for file_path in sorted(all_data_files):
        # Determine target path by removing prefixes
        target_path = None
        source_path = file_path.strip()
        
        for prefix in prefixes_to_remove:
            if source_path.startswith(prefix):
                relative_path = source_path[len(prefix):]
                target_path = os.path.join(target_dir, relative_path)
                break
        
        if not target_path:
            print(f"Warning: No matching prefix for {source_path}, skipping...")
            failed_copies += 1
            continue
        
        # Check if source file exists
        if not os.path.exists(source_path):
            print(f"Warning: Source file not found: {source_path}")
            failed_copies += 1
            continue
        
        # Create target directory structure
        target_parent = os.path.dirname(target_path)
        Path(target_parent).mkdir(parents=True, exist_ok=True)
        
        # Use rsync with archive options
        try:
            cmd = [
                "rsync", 
                "-av",  # archive mode, verbose
                "--update",  # skip files that are newer on target
                source_path, 
                target_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ {source_path} -> {target_path}")
            successful_copies += 1
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to copy {source_path}: {e}")
            failed_copies += 1
        except Exception as e:
            print(f"✗ Error copying {source_path}: {e}")
            failed_copies += 1
    
    print(f"\nPacking complete:")
    print(f"  Successful copies: {successful_copies}")
    print(f"  Failed copies: {failed_copies}")
    print(f"  Target directory: {target_dir}")

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="Data utility for hurricane-centric paper notebooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python data_util.py check    # Check data files in notebooks
  python data_util.py pack     # Pack data files (future functionality)
        """
    )
    
    parser.add_argument(
        'action', 
        choices=['check', 'pack'],
        help='Action to perform: "check" to analyze data files, "pack" to package them'
    )
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    if args.action == 'check':
        print("Checking data files in notebooks...")
        check_data_files()
    elif args.action == 'pack':
        print("Packing data files...")
        pack_data_files()

if __name__ == "__main__":
    main()