#!/usr/bin/env python3
"""
Test script to reproduce the NetworkX import error.
This will help verify if networkx is properly installed.
"""

try:
    import networkx as nx
    print("✓ NetworkX imported successfully")
    print(f"NetworkX version: {nx.__version__}")
    
    # Test basic functionality
    G = nx.MultiDiGraph()
    G.add_node("test")
    print("✓ NetworkX MultiDiGraph created successfully")
    
except ImportError as e:
    print(f"✗ ModuleNotFoundError: {e}")
    print("NetworkX is not installed in the current environment")
    
except Exception as e:
    print(f"✗ Unexpected error: {e}")