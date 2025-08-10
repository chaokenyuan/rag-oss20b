from typing import Dict, List, Any, Optional
import logging
import os
from pathlib import Path

from database import db
from llm_client import llm_client
from java_parser import java_parser
from config import settings

logger = logging.getLogger(__name__)


class JavaDevelopmentAgent:
    """
    Java Development Agent powered by GPT-OSS-20B and Neo4j
    
    This agent can:
    - Analyze existing Java codebases
    - Generate new Java code
    - Suggest improvements and refactoring
    - Answer questions about code structure and relationships
    """
    
    def __init__(self):
        self.name = "Java Development Agent"
        self.version = "1.0.0"
        self.initialized = False
        
    def initialize(self):
        """Initialize the agent by setting up database indexes"""
        try:
            logger.info("Initializing Java Development Agent...")
            
            # Create database indexes
            db.create_indexes()
            
            self.initialized = True
            logger.info("Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """
        Analyze a Java project and store its structure in the knowledge graph
        
        Args:
            project_path: Path to the Java project directory
            
        Returns:
            Analysis results including parsing statistics and stored entities
        """
        if not self.initialized:
            self.initialize()
        
        logger.info(f"Analyzing Java project at: {project_path}")
        
        try:
            # Parse the project
            parse_results = java_parser.parse_project(project_path)
            
            # Store parsed information in Neo4j
            storage_results = self._store_project_data(parse_results)
            
            analysis_summary = {
                'project_path': project_path,
                'parsing_stats': {
                    'files_parsed': parse_results['files_parsed'],
                    'files_failed': parse_results['files_failed'],
                    'classes_found': len(parse_results['classes']),
                    'interfaces_found': len(parse_results['interfaces']),
                    'enums_found': len(parse_results['enums'])
                },
                'storage_stats': storage_results,
                'status': 'completed'
            }
            
            logger.info(f"Project analysis completed: {analysis_summary['parsing_stats']}")
            return analysis_summary
            
        except Exception as e:
            logger.error(f"Error analyzing project: {e}")
            return {
                'project_path': project_path,
                'status': 'failed',
                'error': str(e)
            }
    
    def _store_project_data(self, parse_results: Dict[str, Any]) -> Dict[str, int]:
        """Store parsed project data in Neo4j"""
        storage_stats = {
            'classes_stored': 0,
            'methods_stored': 0,
            'dependencies_created': 0
        }
        
        try:
            # Store classes
            for class_info in parse_results['classes']:
                if db.create_class_node(class_info):
                    storage_stats['classes_stored'] += 1
                    
                    # Store methods
                    for method in class_info['methods']:
                        method_data = {
                            'class_name': class_info['name'],
                            'package': class_info['package'],
                            'method_name': method['name'],
                            'return_type': method['return_type'],
                            'parameters': str(method['parameters']),
                            'modifiers': method['modifiers'],
                            'line_number': 0,  # Would need line number extraction
                            'documentation': method['documentation'],
                            'body': method['body']
                        }
                        if db.create_method_node(method_data):
                            storage_stats['methods_stored'] += 1
                
                # Create dependency relationships
                dependencies = java_parser.find_dependencies(class_info)
                for dep in dependencies:
                    if db.create_dependency_relationship(
                        dep['from'], dep['to'], dep['type'],
                        dep['package_from'], dep['package_to']
                    ):
                        storage_stats['dependencies_created'] += 1
            
            # Store interfaces (similar to classes)
            for interface_info in parse_results['interfaces']:
                if db.create_class_node(interface_info):  # Interfaces stored as special classes
                    storage_stats['classes_stored'] += 1
            
            logger.info(f"Storage completed: {storage_stats}")
            return storage_stats
            
        except Exception as e:
            logger.error(f"Error storing project data: {e}")
            return storage_stats
    
    def generate_code(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate Java code based on natural language request
        
        Args:
            request: Natural language description of what to generate
            context: Optional context including class names, packages, etc.
            
        Returns:
            Generated code and metadata
        """
        if not self.initialized:
            self.initialize()
        
        logger.info(f"Generating code for request: {request}")
        
        try:
            # Enhance context with related information from knowledge graph
            enhanced_context = self._build_context(context)
            
            # Generate code using LLM
            generated_code = llm_client.generate_code(request, enhanced_context)
            
            # Analyze the generated code
            analysis = llm_client.analyze_code(generated_code)
            
            result = {
                'request': request,
                'generated_code': generated_code,
                'analysis': analysis,
                'context_used': enhanced_context,
                'status': 'success' if generated_code else 'failed'
            }
            
            logger.info("Code generation completed")
            return result
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return {
                'request': request,
                'status': 'failed',
                'error': str(e)
            }
    
    def _build_context(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Build enhanced context using knowledge graph"""
        enhanced_context = context.copy() if context else {}
        
        try:
            # If a class name is provided, get related classes and methods
            if 'class_name' in enhanced_context:
                class_name = enhanced_context['class_name']
                package = enhanced_context.get('package', '')
                
                # Get related classes
                related_classes = db.find_related_classes(class_name)
                enhanced_context['related_classes'] = related_classes
                
                # Get existing methods
                methods = db.get_class_methods(class_name, package)
                enhanced_context['methods'] = methods
                
        except Exception as e:
            logger.warning(f"Error building context: {e}")
        
        return enhanced_context
    
    def suggest_improvements(self, code: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Suggest improvements for existing Java code
        
        Args:
            code: Java code to analyze and improve
            context: Optional context information
            
        Returns:
            Improvement suggestions and analysis
        """
        if not self.initialized:
            self.initialize()
        
        logger.info("Analyzing code for improvement suggestions")
        
        try:
            # Get suggestions from LLM
            suggestions = llm_client.suggest_improvements(code, context)
            
            # Perform detailed analysis
            analysis = llm_client.analyze_code(code)
            
            result = {
                'original_code': code,
                'suggestions': suggestions,
                'detailed_analysis': analysis,
                'context_used': context,
                'status': 'success'
            }
            
            logger.info(f"Generated {len(suggestions)} improvement suggestions")
            return result
            
        except Exception as e:
            logger.error(f"Error suggesting improvements: {e}")
            return {
                'original_code': code,
                'status': 'failed',
                'error': str(e)
            }
    
    def query_codebase(self, query: str) -> Dict[str, Any]:
        """
        Answer questions about the codebase using the knowledge graph
        
        Args:
            query: Natural language query about the code
            
        Returns:
            Query results and relevant information
        """
        if not self.initialized:
            self.initialize()
        
        logger.info(f"Processing codebase query: {query}")
        
        try:
            # Simple keyword-based query processing
            # In a more sophisticated implementation, you'd use NLP to understand the query
            
            results = {'query': query, 'results': [], 'status': 'success'}
            
            # Example: Find classes by name
            if 'class' in query.lower():
                # Extract potential class names from query
                words = query.split()
                for word in words:
                    if word.isalpha() and word[0].isupper():
                        # Try to find this as a class name
                        related = db.find_related_classes(word)
                        if related:
                            results['results'].extend(related)
            
            # Generate a natural language response using the LLM
            if results['results']:
                context = {'query_results': results['results']}
                response_prompt = f"Based on the following query results, provide a helpful answer to: {query}"
                llm_response = llm_client.generate_code(response_prompt, context)
                results['llm_response'] = llm_response
            else:
                results['llm_response'] = "I couldn't find specific information in the codebase for your query."
            
            logger.info("Query processed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'query': query,
                'status': 'failed',
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and statistics"""
        try:
            # Get some basic statistics from the database
            stats_query = """
            MATCH (c:Class) 
            OPTIONAL MATCH (c)-[:HAS_METHOD]->(m:Method)
            RETURN count(DISTINCT c) as classes, count(m) as methods
            """
            stats = db.execute_query(stats_query)
            
            return {
                'agent_name': self.name,
                'version': self.version,
                'initialized': self.initialized,
                'database_stats': stats[0] if stats else {'classes': 0, 'methods': 0},
                'model_info': {
                    'model_name': settings.model_name,
                    'device': str(llm_client.device) if hasattr(llm_client, 'device') else 'unknown'
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                'agent_name': self.name,
                'version': self.version,
                'initialized': self.initialized,
                'error': str(e)
            }


# Global agent instance
agent = JavaDevelopmentAgent()