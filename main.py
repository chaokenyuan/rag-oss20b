#!/usr/bin/env python3
"""
Java Development Agent
======================

A powerful Java development assistant powered by GPT-OSS-20B LLM and Neo4j knowledge graph.

This agent can:
- Analyze existing Java codebases and store structure in Neo4j
- Generate new Java code based on natural language descriptions
- Suggest improvements and refactoring for existing code
- Answer questions about code structure and relationships
- Provide contextual code generation using knowledge graph

Usage:
------
1. Direct usage: python main.py
2. API server: python api.py
3. Examples: python examples.py
"""

import sys
import logging
from pathlib import Path
from java_agent import agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    Java Development Agent                    ║
║              GPT-OSS-20B + Neo4j Integration                ║
╚══════════════════════════════════════════════════════════════╝

A sophisticated Java development assistant that combines:
• GPT-OSS-20B Large Language Model for code generation
• Neo4j Knowledge Graph for code structure analysis
• Advanced Java code parsing and dependency tracking
• RESTful API interface for integration
"""
    print(banner)

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    # neo4j dependency removed - using NetworkX-based in-memory database instead
    
    try:
        import transformers
    except ImportError:
        missing_deps.append("transformers")
        
    try:
        import torch
    except ImportError:
        missing_deps.append("torch")
        
    try:
        import javalang
    except ImportError:
        missing_deps.append("javalang")
    
    return missing_deps

def interactive_mode():
    """Run the agent in interactive mode"""
    print("\n🚀 Starting Interactive Mode")
    print("Commands:")
    print("  status     - Show agent status")
    print("  generate   - Generate Java code")
    print("  analyze    - Analyze Java project")
    print("  improve    - Suggest code improvements")
    print("  query      - Query codebase")
    print("  help       - Show this help")
    print("  quit       - Exit")
    print()
    
    try:
        agent.initialize()
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    while True:
        try:
            command = input("\njavagen> ").strip().lower()
            
            if command == 'quit' or command == 'exit':
                break
            elif command == 'status':
                handle_status_command()
            elif command == 'generate':
                handle_generate_command()
            elif command == 'analyze':
                handle_analyze_command()
            elif command == 'improve':
                handle_improve_command()
            elif command == 'query':
                handle_query_command()
            elif command == 'help':
                print("\nAvailable commands:")
                print("  status, generate, analyze, improve, query, help, quit")
            elif command == '':
                continue
            else:
                print(f"Unknown command: {command}. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def handle_status_command():
    """Handle status command"""
    try:
        status = agent.get_status()
        print(f"\n📊 Agent Status:")
        print(f"   Name: {status['agent_name']}")
        print(f"   Version: {status['version']}")
        print(f"   Initialized: {status['initialized']}")
        
        db_stats = status.get('database_stats', {})
        print(f"   Database: {db_stats.get('classes', 0)} classes, {db_stats.get('methods', 0)} methods")
        
        model_info = status.get('model_info', {})
        print(f"   Model: {model_info.get('model_name', 'N/A')}")
    except Exception as e:
        print(f"Error getting status: {e}")

def handle_generate_command():
    """Handle code generation command"""
    try:
        request = input("Enter code generation request: ").strip()
        if not request:
            print("No request provided.")
            return
        
        print("🔄 Generating code...")
        result = agent.generate_code(request)
        
        if result['status'] == 'success':
            print("\n✅ Generated Code:")
            print("-" * 60)
            print(result['generated_code'])
            print("-" * 60)
        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error generating code: {e}")

def handle_analyze_command():
    """Handle project analysis command"""
    try:
        project_path = input("Enter Java project path: ").strip()
        if not project_path:
            print("No path provided.")
            return
        
        if not Path(project_path).exists():
            print("Path does not exist.")
            return
        
        print("🔄 Analyzing project...")
        result = agent.analyze_project(project_path)
        
        if result['status'] == 'completed':
            stats = result['parsing_stats']
            print(f"\n✅ Analysis Complete:")
            print(f"   Files parsed: {stats['files_parsed']}")
            print(f"   Classes found: {stats['classes_found']}")
            print(f"   Interfaces: {stats['interfaces_found']}")
            print(f"   Enums: {stats['enums_found']}")
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error analyzing project: {e}")

def handle_improve_command():
    """Handle code improvement command"""
    try:
        print("Enter Java code to improve (end with empty line):")
        code_lines = []
        while True:
            line = input()
            if line == "":
                break
            code_lines.append(line)
        
        code = "\n".join(code_lines)
        if not code.strip():
            print("No code provided.")
            return
        
        print("🔄 Analyzing code for improvements...")
        result = agent.suggest_improvements(code)
        
        if result['status'] == 'success':
            print(f"\n✅ Found {len(result['suggestions'])} suggestions:")
            for i, suggestion in enumerate(result['suggestions'], 1):
                print(f"   {i}. {suggestion}")
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error suggesting improvements: {e}")

def handle_query_command():
    """Handle codebase query command"""
    try:
        query = input("Enter codebase query: ").strip()
        if not query:
            print("No query provided.")
            return
        
        print("🔄 Processing query...")
        result = agent.query_codebase(query)
        
        if result['status'] == 'success':
            print(f"\n✅ Query Results:")
            print(f"   Found {len(result['results'])} results")
            if 'llm_response' in result:
                print(f"   AI Response: {result['llm_response']}")
        else:
            print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error processing query: {e}")

def show_help():
    """Show help information"""
    help_text = """
Usage: python main.py [command]

Commands:
  interactive  - Start interactive mode (default)
  examples     - Run example usage scenarios
  api          - Start REST API server
  help         - Show this help message

Dependencies:
  Install required packages with: pip install -r requirements.txt
  
  Required services:
  - Neo4j database running on bolt://localhost:7687
  - GPT-OSS-20B model (configure path in config.py)

Configuration:
  - Copy .env.example to .env and configure settings
  - Update config.py with your Neo4j and model settings

For more information, see README.md
"""
    print(help_text)

def main():
    """Main entry point"""
    print_banner()
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("   Install with: pip install -r requirements.txt")
        print()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'help' or command == '-h' or command == '--help':
            show_help()
        elif command == 'examples':
            print("🚀 Running examples...")
            from examples import run_all_examples
            run_all_examples()
        elif command == 'api':
            print("🚀 Starting API server...")
            import uvicorn
            from api import app
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        elif command == 'interactive':
            interactive_mode()
        else:
            print(f"Unknown command: {command}")
            print("Use 'python main.py help' for available commands.")
    else:
        # Default to interactive mode
        interactive_mode()

if __name__ == '__main__':
    main()
