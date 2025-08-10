#!/usr/bin/env python3
"""
Script to reproduce the ModuleNotFoundError: No module named 'neo4j'
"""

print("Testing neo4j import...")
try:
    import main
    print("SUCCESS: main module imported without errors")
except ModuleNotFoundError as e:
    print(f"ERROR: {e}")
    print("This confirms the ModuleNotFoundError issue")
except Exception as e:
    print(f"OTHER ERROR: {e}")