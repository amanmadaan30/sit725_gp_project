import ast 
import autopep8
import re

def analyze_code(code, language='python'):
    if language == 'python':
        return analyze_python_code(code)
    return ["Unsupported language"]

def refactor_code(code, language='python'):
    if language == 'python':
        return refactor_python_code(code)
    return "Unsupported language"

# Python analysis
def analyze_python_code(code):
    issues = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ["SyntaxError: Invalid Python code provided"]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if len(node.name) > 20:  # Long function name
                issues.append(f"Function name '{node.name}' exceeds 20 characters at line {node.lineno}")
            if '_' in node.name:  # Non-camelCase function name
                issues.append(f"Function '{node.name}' is not camelCase at line {node.lineno}")
            # Check for missing return statements
            if not any(isinstance(n, ast.Return) for n in node.body):
                issues.append(f"Function '{node.name}' is missing a return statement at line {node.lineno}")
        # Nested If-Else blocks check
        if isinstance(node, ast.If):
            if isinstance(node.body[0], ast.If):
                issues.append(f"Nested If statement found at line {node.lineno}")
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            # Check for unused imports
            issues.extend(find_unused_imports(code))

    return issues

def refactor_python_code(code):
    try:
        refactored_code = autopep8.fix_code(code)  # First, auto-format the code
        tree = ast.parse(refactored_code)
    except SyntaxError:
        return "SyntaxError: Invalid Python code provided"
    
    # Handle function renaming (camelCase)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            node.name = convert_to_camel_case(node.name)

    # Apply more specific refactoring rules
    refactored_code = ast.unparse(tree)
    refactored_code = add_return_type_annotations(refactored_code)
    refactored_code = remove_unused_imports(refactored_code)
    refactored_code = remove_unused_variables(refactored_code)
    refactored_code = eliminate_long_switch_statements(refactored_code)
    refactored_code = flatten_nested_if_else(refactored_code)
    
    return refactored_code

# New feature: Removing unused imports
def find_unused_imports(code):
    issues = []
    tree = ast.parse(code)
    imported_names = [name.name for node in ast.walk(tree) if isinstance(node, ast.Import) for name in node.names]
    used_names = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]

    for import_name in imported_names:
        if import_name not in used_names:
            issues.append(f"Unnecessary import '{import_name}' found")
    return issues

def remove_unused_imports(code):
    tree = ast.parse(code)
    used_names = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]

    def filter_imports(node):
        if isinstance(node, ast.Import):
            node.names = [name for name in node.names if name.name in used_names]
        return node

    new_tree = ast.fix_missing_locations(ast.NodeTransformer().visit(tree))
    return ast.unparse(new_tree)

# New feature: Removing unused variables
def remove_unused_variables(code):
    tree = ast.parse(code)
    assigned_vars = [node.targets[0].id for node in ast.walk(tree) if isinstance(node, ast.Assign)]
    used_vars = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]

    def remove_var(node):
        if isinstance(node, ast.Assign):
            target = node.targets[0].id
            if target not in used_vars:
                return None
        return node

    new_tree = ast.fix_missing_locations(ast.NodeTransformer().visit(tree))
    return ast.unparse(new_tree)

# New feature: Eliminating long switch-like statements (if-elif chains)
def eliminate_long_switch_statements(code):
    if_pattern = r'if\s+(.*?)\s*:\n\s+(.*?)elif\s+(.*?)\s*:\n\s+(.*?)'
    
    def switch_to_dict(match):
        key1, action1, key2, action2 = match.groups()
        return f"actions = {{\n    {key1}: {action1},\n    {key2}: {action2}\n}}\nresult = actions.get(key, default_action)"
    
    return re.sub(if_pattern, switch_to_dict, code)

# Utility functions for refactoring

def convert_to_camel_case(name):
    parts = name.split('_')
    return parts[0] + ''.join(part.capitalize() for part in parts[1:])

def add_return_type_annotations(code):
    # Add return type annotations to Python functions (as an example)
    function_pattern = r'def\s+(\w+)\(.*\):\n'
    return_pattern = r'return\s'
    
    def add_annotation(match):
        func_name = match.group(1)
        if re.search(f'{func_name}.*{return_pattern}', code):  # If function contains return statement
            return f'def {func_name}(...) -> Any:\n'
        return match.group(0)

    return re.sub(function_pattern, add_annotation, code)

def flatten_nested_if_else(code):
    nested_if_pattern = r'if\s+(.+):\n\s+if\s+(.+):\n\s+(.+)'
    
    def flatten(match):
        condition1 = match.group(1)
        condition2 = match.group(2)
        statement = match.group(3)
        return f'if {condition1} and {condition2}:\n    {statement}'
    
    return re.sub(nested_if_pattern, flatten, code)

