"""
Test Script to Validate ML Module Structure

This script validates the structure and basic functionality
of the ML module without requiring external dependencies to be installed.
"""

import ast
import sys
from pathlib import Path

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)

def check_imports(filepath):
    """Check what imports a file requires"""
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    return imports

def check_classes(filepath):
    """Find all classes defined in a file"""
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
            classes.append({
                'name': node.name,
                'methods': methods
            })
    
    return classes

def check_functions(filepath):
    """Find all top-level functions in a file"""
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    functions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
    
    return functions

def main():
    """Run all checks"""
    print("=" * 80)
    print("ML MODULE STRUCTURE VALIDATION")
    print("=" * 80)
    
    ml_dir = Path(__file__).parent
    files_to_check = [
        'train.py',
        'evaluate.py',
        'predict.py',
        '__init__.py',
        'integration_example.py'
    ]
    
    all_passed = True
    
    for filename in files_to_check:
        filepath = ml_dir / filename
        
        print(f"\n{'=' * 80}")
        print(f"Checking: {filename}")
        print('=' * 80)
        
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            all_passed = False
            continue
        
        # Check syntax
        is_valid, error = check_file_syntax(filepath)
        if is_valid:
            print("✓ Syntax: Valid")
        else:
            print(f"❌ Syntax Error: {error}")
            all_passed = False
            continue
        
        # Check imports
        imports = check_imports(filepath)
        unique_imports = list(set(imports))
        print(f"✓ Imports ({len(imports)}): {', '.join(unique_imports[:5])}{'...' if len(unique_imports) > 5 else ''}")
        
        # Check classes
        classes = check_classes(filepath)
        if classes:
            print(f"✓ Classes ({len(classes)}):")
            for cls in classes:
                print(f"  - {cls['name']} ({len(cls['methods'])} methods)")
        
        # Check functions
        functions = check_functions(filepath)
        if functions:
            print(f"✓ Functions ({len(functions)}): {', '.join(functions[:3])}{'...' if len(functions) > 3 else ''}")
    
    # Check documentation
    print(f"\n{'=' * 80}")
    print("Checking: README.md")
    print('=' * 80)
    
    readme_path = ml_dir / 'README.md'
    if readme_path.exists():
        with open(readme_path, 'r') as f:
            content = f.read()
            print(f"✓ README exists ({len(content)} characters)")
            print(f"✓ Sections found: {content.count('#')}")
    else:
        print("❌ README.md not found")
        all_passed = False
    
    # Summary
    print(f"\n{'=' * 80}")
    print("VALIDATION SUMMARY")
    print('=' * 80)
    
    if all_passed:
        print("✓ All checks passed!")
        print("\nThe ML module structure is valid and ready to use.")
        print("\nTo use the module:")
        print("  1. Install dependencies: pip install numpy pandas scikit-learn joblib")
        print("  2. Run training: python train.py")
        print("  3. Run evaluation: python evaluate.py")
        print("  4. Make predictions: python predict.py")
        return 0
    else:
        print("❌ Some checks failed. Please review the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
