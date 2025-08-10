#!/usr/bin/env python3
"""
Example usage scripts for the Java Development Agent

This file demonstrates how to use the agent for various Java development tasks.
"""

import asyncio
import logging
from pathlib import Path
from java_agent import agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def example_1_agent_status():
    """Example 1: Check agent status"""
    print("=== Example 1: Agent Status ===")
    
    try:
        status = agent.get_status()
        print(f"Agent Name: {status['agent_name']}")
        print(f"Version: {status['version']}")
        print(f"Initialized: {status['initialized']}")
        print(f"Model: {status.get('model_info', {}).get('model_name', 'N/A')}")
        print(f"Database Stats: {status.get('database_stats', {})}")
    except Exception as e:
        print(f"Error getting status: {e}")
    print()

def example_2_code_generation():
    """Example 2: Generate Java code"""
    print("=== Example 2: Code Generation ===")
    
    try:
        # Simple code generation request
        request = "Create a Java class called Calculator with methods for add, subtract, multiply, and divide"
        
        result = agent.generate_code(request)
        
        print(f"Request: {result['request']}")
        print(f"Status: {result['status']}")
        print("Generated Code:")
        print("-" * 50)
        print(result['generated_code'])
        print("-" * 50)
        
        # Print analysis if available
        if 'analysis' in result and result['analysis']:
            print("Code Analysis:")
            print(result['analysis']['analysis'])
        
    except Exception as e:
        print(f"Error generating code: {e}")
    print()

def example_3_code_improvement():
    """Example 3: Suggest code improvements"""
    print("=== Example 3: Code Improvement Suggestions ===")
    
    sample_code = """
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int divide(int a, int b) {
        return a / b;  // No zero check!
    }
}
"""
    
    try:
        result = agent.suggest_improvements(sample_code)
        
        print("Original Code:")
        print("-" * 30)
        print(sample_code)
        print("-" * 30)
        
        print(f"Status: {result['status']}")
        print("Improvement Suggestions:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"{i}. {suggestion}")
        
        if 'detailed_analysis' in result:
            print("\nDetailed Analysis:")
            print(result['detailed_analysis']['analysis'])
            
    except Exception as e:
        print(f"Error suggesting improvements: {e}")
    print()

def example_4_project_analysis():
    """Example 4: Analyze a Java project"""
    print("=== Example 4: Project Analysis ===")
    
    # Create a sample Java file for testing
    sample_project_dir = Path("./sample_java_project")
    sample_project_dir.mkdir(exist_ok=True)
    
    sample_java_file = sample_project_dir / "TestClass.java"
    sample_java_content = """
package com.example;

import java.util.List;
import java.util.ArrayList;

/**
 * A sample test class for demonstration
 */
public class TestClass {
    private String name;
    private List<String> items;
    
    public TestClass(String name) {
        this.name = name;
        this.items = new ArrayList<>();
    }
    
    /**
     * Add an item to the list
     */
    public void addItem(String item) {
        items.add(item);
    }
    
    /**
     * Get all items
     */
    public List<String> getItems() {
        return new ArrayList<>(items);
    }
    
    public String getName() {
        return name;
    }
}
"""
    
    try:
        # Write sample Java file
        with open(sample_java_file, 'w') as f:
            f.write(sample_java_content)
        
        print(f"Created sample project at: {sample_project_dir}")
        print("Analyzing project...")
        
        result = agent.analyze_project(str(sample_project_dir))
        
        print(f"Status: {result['status']}")
        if result['status'] == 'completed':
            stats = result['parsing_stats']
            print(f"Files parsed: {stats['files_parsed']}")
            print(f"Files failed: {stats['files_failed']}")
            print(f"Classes found: {stats['classes_found']}")
            print(f"Interfaces found: {stats['interfaces_found']}")
            print(f"Enums found: {stats['enums_found']}")
            
            storage_stats = result.get('storage_stats', {})
            print(f"Classes stored: {storage_stats.get('classes_stored', 0)}")
            print(f"Methods stored: {storage_stats.get('methods_stored', 0)}")
            print(f"Dependencies created: {storage_stats.get('dependencies_created', 0)}")
        else:
            print(f"Analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error analyzing project: {e}")
    print()

def example_5_codebase_query():
    """Example 5: Query the codebase"""
    print("=== Example 5: Codebase Query ===")
    
    try:
        queries = [
            "What classes are in the codebase?",
            "Find TestClass",
            "Show me methods in TestClass"
        ]
        
        for query in queries:
            print(f"Query: {query}")
            result = agent.query_codebase(query)
            
            print(f"Status: {result['status']}")
            if result['status'] == 'success':
                print(f"Results found: {len(result['results'])}")
                for res in result['results'][:3]:  # Show first 3 results
                    print(f"  - {res}")
                
                if 'llm_response' in result:
                    print(f"AI Response: {result['llm_response'][:200]}...")
            else:
                print(f"Query failed: {result.get('error', 'Unknown error')}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error querying codebase: {e}")
    print()

def example_6_contextual_generation():
    """Example 6: Generate code with context"""
    print("=== Example 6: Contextual Code Generation ===")
    
    try:
        # Generate code with context about existing classes
        request = "Create a service class that uses TestClass to manage a collection of items"
        context = {
            "class_name": "TestClass",
            "package": "com.example"
        }
        
        result = agent.generate_code(request, context)
        
        print(f"Request: {request}")
        print(f"Context: {context}")
        print(f"Status: {result['status']}")
        print("Generated Code:")
        print("-" * 50)
        print(result.get('generated_code', 'No code generated'))
        print("-" * 50)
        
        if 'context_used' in result:
            context_used = result['context_used']
            if 'related_classes' in context_used:
                print(f"Related classes found: {len(context_used['related_classes'])}")
            if 'methods' in context_used:
                print(f"Existing methods found: {len(context_used['methods'])}")
        
    except Exception as e:
        print(f"Error with contextual generation: {e}")
    print()

def run_all_examples():
    """Run all examples in sequence"""
    print("Java Development Agent - Example Usage")
    print("=" * 60)
    
    try:
        # Initialize the agent
        if not agent.initialized:
            print("Initializing agent...")
            agent.initialize()
            print("Agent initialized successfully!")
            print()
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        print("Some examples may not work properly.")
        print()
    
    # Run examples
    example_1_agent_status()
    example_2_code_generation()
    example_3_code_improvement()
    example_4_project_analysis()
    example_5_codebase_query()
    example_6_contextual_generation()
    
    print("All examples completed!")

if __name__ == "__main__":
    run_all_examples()