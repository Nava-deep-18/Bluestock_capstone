import os
import glob
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(filepath)
    changed = False

    # 1. Add module docstring if missing
    if not content.lstrip().startswith('\"\"\"'):
        docstring = f'\"\"\"\nModule: {filename}\nDescription: Component of the Bluestock Mutual Fund Analytics Capstone.\n\"\"\"\n\n'
        # If there's a shebang or encoding comment, it should ideally go after it, but for our simple scripts this is fine
        content = docstring + content
        changed = True

    # 2. Remove specific debug prints (mostly from data_ingestion.py and others)
    # We will remove prints that output Shape, Dtypes, Head, or Dataset, or simple status prints like "--- Data Ingestion ---"
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.strip()
        is_debug_print = False
        
        # Check for typical debug prints we found in our grep
        if stripped.startswith('print('):
            if any(term in stripped for term in ['Shape:', 'Dtypes:', 'Head:', 'Dataset:', '--- Data Ingestion ---', 'Successfully generated']):
                is_debug_print = True
            elif stripped == 'print(f"\\n======================================")':
                is_debug_print = True
                
        if not is_debug_print:
            new_lines.append(line)
        else:
            changed = True

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        print(f"Cleaned {filename}")

if __name__ == '__main__':
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Target directories
    targets = [
        os.path.join(project_dir, 'run_pipeline.py'),
        os.path.join(project_dir, 'dashboard', 'app.py'),
        os.path.join(project_dir, 'dashboard', 'pages', '*.py'),
        os.path.join(project_dir, 'scripts', '*.py')
    ]
    
    for target in targets:
        for filepath in glob.glob(target):
            # Exclude this cleaning script itself
            if os.path.basename(filepath) != 'clean_codebase.py':
                process_file(filepath)
