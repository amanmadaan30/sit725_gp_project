import ast
import autopep8
import re

def analyze_code(code, language='python'):
    if language == 'python':
        return analyze_python_code(code)
    elif language == 'java':
        return analyze_java_code(code)
    elif language == 'javascript':
        return analyze_js_code(code)
    return ["Unsupported language"]

def refactor_code(code, language='python'):
    if language == 'python':
        return refactor_python_code(code)
    elif language == 'java':
        return refactor_java_code(code)
    elif language == 'javascript':
        return refactor_js_code(code)
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
            if len(node.body) > 5:  # Long function
                issues.append(f"Function '{node.name}' is too long at line {node.lineno}")
            if '_' in node.name:  # Non-camelCase function name
                issues.append(f"Function '{node.name}' is not camelCase at line {node.lineno}")
            if isinstance(node.returns, ast.Constant) and node.returns is None:  # Missing return type
                issues.append(f"Function '{node.name}' is missing a return type at line {node.lineno}")
        if isinstance(node, ast.If):
            # Nested If-Else blocks check
            if isinstance(node.body[0], ast.If):
                issues.append(f"Nested If statement found at line {node.lineno}")

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
    refactored_code = split_long_methods(refactored_code)
    refactored_code = flatten_nested_if_else(refactored_code)
    
    return refactored_code

# Java analysis
def analyze_java_code(code):
    issues = []
    
    # Check for long methods
    method_pattern = r'public\s+\w+\s+(\w+)\(.*\)\s*\{([\s\S]+?)\}'
    methods = re.findall(method_pattern, code)
    
    for method_name, method_body in methods:
        if len(method_body.split('\n')) > 6:
            issues.append(f"Method '{method_name}' is too long.")
        if '_' in method_name:
            issues.append(f"Method '{method_name}' is not camelCase.")
    
    # Check for nested if-else
    nested_if_pattern = r'if\s*\(.*\)\s*\{[^{}]*if\s*\(.*\)\s*\{'
    if re.search(nested_if_pattern, code):
        issues.append("Nested if-else blocks found.")

    # Check for missing return type
    missing_return_pattern = r'public\s+void\s+\w+\s*\(.*\)\s*\{'
    if re.search(missing_return_pattern, code):
        issues.append("Some methods are missing return types.")

    return issues

def refactor_java_code(code):
    # Refactor camelCase
    code = re.sub(r'_(\w)', lambda m: m.group(1).upper(), code)
    
    # Eliminate switch statements
    code = re.sub(r'switch\s*\(.*\)\s*\{[\s\S]+?\}', 'if-else equivalent', code)
    
    # Flatten nested if-else
    code = re.sub(r'if\s*\((.*)\)\s*\{\s*if\s*\((.*)\)\s*\{', r'if (\1 && \2) {', code)
    
    return code

# JavaScript analysis
def analyze_js_code(code):
    issues = []
    
    # Check for long functions
    function_pattern = r'function\s+(\w+)\s*\(.*\)\s*\{([\s\S]+?)\}'
    functions = re.findall(function_pattern, code)
    
    for func_name, func_body in functions:
        if len(func_body.split('\n')) > 6:
            issues.append(f"Function '{func_name}' is too long.")
        if '_' in func_name:
            issues.append(f"Function '{func_name}' is not camelCase.")
    
    # Check for nested if-else
    nested_if_pattern = r'if\s*\(.*\)\s*\{[^{}]*if\s*\(.*\)\s*\{'
    if re.search(nested_if_pattern, code):
        issues.append("Nested if-else blocks found.")

    return issues

def refactor_js_code(code):
    # Refactor camelCase
    code = re.sub(r'_(\w)', lambda m: m.group(1).upper(), code)
    
    # Eliminate switch statements
    code = re.sub(r'switch\s*\(.*\)\s*\{[\s\S]+?\}', 'if-else equivalent', code)
    
    # Flatten nested if-else
    code = re.sub(r'if\s*\((.*)\)\s*\{\s*if\s*\((.*)\)\s*\{', r'if (\1 && \2) {', code)
    
    return code

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

def split_long_methods(code):
    # Detect long methods and split them into smaller ones
    def split_method(match):
        func_name = match.group(1)
        method_body = match.group(2)
        lines = method_body.split('\n')
        
        if len(lines) > 6:
            new_func_name = func_name + '_part1'
            helper_method = f'def {new_func_name}(...):\n    ' + '\n    '.join(lines[:3]) + '\n'
            new_body = f'{helper_method}\n    {new_func_name}()' + '\n    ' + '\n    '.join(lines[3:])
            return f'def {func_name}(...):\n    {new_body}'
        return match.group(0)

    method_pattern = r'def\s+(\w+)\(.*\):\n(.*?)(?=\ndef|\Z)'
    return re.sub(method_pattern, split_method, code, flags=re.DOTALL)

def flatten_nested_if_else(code):
    nested_if_pattern = r'if\s+(.+):\n\s+if\s+(.+):\n\s+(.+)'
    
    def flatten(match):
        condition1 = match.group(1)
        condition2 = match.group(2)
        statement = match.group(3)
        return f'if {condition1} and {condition2}:\n    {statement}'
    
    return re.sub(nested_if_pattern, flatten, code)
