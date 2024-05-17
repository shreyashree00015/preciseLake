# __init__.py

from .preciseLake import main, analyze_code, estimate_memory_usage, write_memory_usage_to_file, find_unused_code, find_non_terminating_functions, find_method_overrides, detect_redundant_calculations, detect_unused_imports, high_memory_components, code_to_graph

__all__ = [
    'main',
    'analyze_code',
    'estimate_memory_usage',
    'write_memory_usage_to_file',
    'find_unused_code',
    'find_non_terminating_functions',
    'find_method_overrides',
    'detect_redundant_calculations',
    'detect_unused_imports',
    'high_memory_components',
    'code_to_graph'
]
