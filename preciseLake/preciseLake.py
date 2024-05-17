# preciseLake.py

import ast
import time
import tracemalloc
import pyflakes.api
import pyflakes.messages
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog
import networkx as nx
import matplotlib.pyplot as plt
import importlib.util
import inspect
from matplotlib import cm

def estimate_memory_usage(code):
    tracemalloc.start()
    try:
        exec(code)
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        total_memory = sum(stat.size for stat in top_stats)
        return total_memory / (1024 * 1024)
    finally:
        tracemalloc.stop()

def write_memory_usage_to_file(code, output_file, execution_time):
    memory_usage = estimate_memory_usage(code)
    with open(output_file, 'a+') as file:
        file.write(f"Memory Usage: {memory_usage} MB\t")
        file.write(f"Execution Time: {execution_time} seconds\n\n")

def analyze_code(code):
    tree = ast.parse(code)
    unused_variables = set()
    all_variables = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if isinstance(node.targets[0], ast.Name):
                all_variables.update(target.id for target in node.targets)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            all_variables.add(node.id)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            all_variables.discard(node.id)
    unused_variables = all_variables.copy()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            unused_variables.discard(node.id)
    inefficient_patterns = []
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.For):
                        inefficient_patterns.append((subnode.lineno, "Nested loops detected", subnode))
                        break
    return unused_variables, inefficient_patterns

def find_unused_code(code):
    tree = ast.parse(code)
    used_functions = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            used_functions.add(node.func.id)
    unused_functions = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if node.name not in used_functions:
                unused_functions.add(node.name)
    return unused_functions

def find_non_terminating_functions(code):
    tree = ast.parse(code)
    non_terminating_functions = set()
    def has_non_terminating_constructs(node):
        if isinstance(node, ast.While):
            non_terminating_functions.add(node)
        for child_node in ast.iter_child_nodes(node):
            has_non_terminating_constructs(child_node)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for child_node in ast.iter_child_nodes(node):
                has_non_terminating_constructs(child_node)
    return non_terminating_functions, tree

def find_method_overrides(file_path):
    with open(file_path, 'r') as file:
        code = file.read()
    tree = ast.parse(code)
    class_definitions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_definitions[node.name] = node
    overridden_methods = {}
    for class_name, class_node in class_definitions.items():
        base_classes = [base.id for base in class_node.bases if isinstance(base, ast.Name)]
        for base_class in base_classes:
            if (base_class in class_definitions):
                base_class_node = class_definitions[base_class]
                for base_method in base_class_node.body:
                    if isinstance(base_method, ast.FunctionDef):
                        for method in class_node.body:
                            if isinstance(method, ast.FunctionDef) and method.name == base_method.name:
                                overridden_methods[method.name] = (base_class, class_name)
    return overridden_methods

def extract_source_lines(node):
    if hasattr(node, 'lineno'):
        return node.lineno
    elif hasattr(node, 'body'):
        return [extract_source_lines(child) for child in node.body]
    else:
        return None

def visit_BinOp(node, calculations, redundant_calculations):
    if isinstance(node.op, ast.Add) or isinstance(node.op, ast.Sub) or isinstance(node.op, ast.Mult) or isinstance(node.op, ast.Div):
        expr_hash = hash(ast.dump(node))
        if expr_hash in calculations:
            redundant_calculations.append((node, calculations[expr_hash]))
        else:
            calculations[expr_hash] = node

def detect_redundant_calculations(code, i):
    calculations = {}
    redundant_calculations = []
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):
            visit_BinOp(node, calculations, redundant_calculations)
    if redundant_calculations:
        i += 1
        print(str(i) + ". Redundant calculations detected:")
        for expr1, expr2 in redundant_calculations:
            line1 = extract_source_lines(expr1)
            line2 = extract_source_lines(expr2)
            print(f"Redundant calculation at line {line1}: {ast.dump(expr1)}")
            print(f"Same calculation found at line {line2}: {ast.dump(expr2)}")
            print()
            print("==============================================")
            print()
    return i

def detect_unused_imports(code):
    try:
        result = pyflakes.api.check(code, '')
        if isinstance(result, int):
            return []
        unused_imports = [issue.message for issue in result if isinstance(issue, pyflakes.messages.UnusedImport)]
        return unused_imports
    except Exception as e:
        print(f"Error occurred during analysis: {e}")
        return []

def high_memory_components(code):
    tree = ast.parse(code)
    memory_intensive_components = []
    for node in ast.walk(tree):
        if isinstance(node, ast.For) or isinstance(node, ast.While):
            nested_level = sum(1 for _ in ast.walk(node))
            if nested_level > 2:
                memory_intensive_components.append(('Loop', node.lineno))
        if isinstance(node, ast.Dict) or isinstance(node, ast.List) or isinstance(node, ast.Set):
            num_elements = len(node.elts) if hasattr(node, 'elts') else 0
            if num_elements > 100:
                memory_intensive_components.append(('Data Structure', node.lineno))
    return memory_intensive_components

def code_to_graph(file_path):
    try:
        module_name = file_path.split("/")[-1].split(".")[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        source_code = inspect.getsource(module)
        tree = ast.parse(source_code)
        G = nx.DiGraph()
        cmap = cm.get_cmap('tab20')

        def traverse(node, parent=None):
            if parent:
                G.add_edge(parent.__class__.__name__, node.__class__.__name__)
            nodes.append(node.__class__.__name__)
            color = cmap(len(nodes) / len(tree.body))
            G.add_node(node.__class__.__name__, color=color)
            for child in ast.iter_child_nodes(node):
                traverse(child, node)

        nodes = []
        traverse(tree)
        return G
    except (ImportError, FileNotFoundError) as e:
        print(f"Error: {e}")
        return None

def main():
    def select_file():
        app = QApplication(sys.argv)
        file_path, _ = QFileDialog.getOpenFileName(None, "Select a file")
        app.quit()
        return file_path

    file_path = select_file()
    
    with open(file_path, 'r') as file:
        code = file.read()

    start_time = time.time()
    unused_variables, inefficient_patterns = analyze_code(code)
    unused_functions = find_unused_code(code)
    non_terminating_functions, tree = find_non_terminating_functions(code)
    overridden_methods = find_method_overrides(file_path)
    components = high_memory_components(code)
    end_time = time.time()
    execution_time = end_time - start_time

    print("Precise Lake: Code Health Analysis and Optimisation Feedback Mechanism\n")
    print("Detected areas to optimize")
    i = 0
    i += 1
    if unused_variables:
        print(f"{i}. Unused variables: {unused_variables}")
        print()
        print("==============================================")
        print()

    i += 1
    if inefficient_patterns:
        print(f"{i}. Inefficient patterns:")
        for line, message, pattern in inefficient_patterns:
            print(f"{message} at line {line}")
            print(ast.dump(pattern))
            print()
            print("==============================================")
            print()
        
    i += 1
    if unused_functions:
        print(f"{i}. Unused functions: {unused_functions}")
        print()
        print("==============================================")
        print()

    i += 1
    if non_terminating_functions:
        print(f"{i}. Non-terminating functions: {non_terminating_functions}")
        print()
        print("==============================================")
        print()

    i += 1
    if overridden_methods:
        print(f"{i}. Overridden methods: {overridden_methods}")
        print()
        print("==============================================")
        print()

    i += 1
    if components:
        print(f"{i}. High memory components: {components}")
        print()
        print("==============================================")
        print()

    i = detect_redundant_calculations(code, i)
    i += 1
    if detect_unused_imports(code):
        print(f"{i}. Unused imports: {detect_unused_imports(code)}")
        print()
        print("==============================================")
        print()
        
    graph = code_to_graph(file_path)
    if graph:
        pos = nx.spring_layout(graph)
        plt.figure(figsize=(25, 15))
        nx.draw(graph, pos, with_labels=True, font_weight='bold', node_color=[c[1] for c in graph.nodes(data='color')])
        plt.show()
    
    output_file = "memory_usage.txt"
    write_memory_usage_to_file(code, output_file, execution_time)
    print(f'Find your memory usage and time taken in {output_file}')
    print(f"The number of issues detected: {len(unused_variables) + len(inefficient_patterns) + len(unused_functions) + len(non_terminating_functions) + len(overridden_methods) + len(components)}")

if __name__ == '__main__':
    main()
