import javalang
from typing import Dict, List, Any, Optional
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class JavaCodeParser:
    def __init__(self):
        self.parsed_files = {}
    
    def parse_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse a single Java file and extract structural information"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse the Java code
            tree = javalang.parse.parse(content)
            
            result = {
                'file_path': file_path,
                'package': tree.package.name if tree.package else '',
                'imports': [imp.path for imp in tree.imports] if tree.imports else [],
                'classes': [],
                'interfaces': [],
                'enums': []
            }
            
            # Extract classes, interfaces, and enums
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_info = self._extract_class_info(node, file_path, result['package'])
                result['classes'].append(class_info)
            
            for path, node in tree.filter(javalang.tree.InterfaceDeclaration):
                interface_info = self._extract_interface_info(node, file_path, result['package'])
                result['interfaces'].append(interface_info)
            
            for path, node in tree.filter(javalang.tree.EnumDeclaration):
                enum_info = self._extract_enum_info(node, file_path, result['package'])
                result['enums'].append(enum_info)
            
            self.parsed_files[file_path] = result
            return result
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return None
    
    def _extract_class_info(self, node: javalang.tree.ClassDeclaration, 
                           file_path: str, package: str) -> Dict[str, Any]:
        """Extract detailed information about a class"""
        class_info = {
            'name': node.name,
            'package': package,
            'file_path': file_path,
            'modifiers': node.modifiers if node.modifiers else [],
            'extends': node.extends.name if node.extends else None,
            'implements': [impl.name for impl in node.implements] if node.implements else [],
            'methods': [],
            'fields': [],
            'constructors': [],
            'documentation': node.documentation if hasattr(node, 'documentation') else None
        }
        
        # Extract methods
        for method in node.body:
            if isinstance(method, javalang.tree.MethodDeclaration):
                method_info = self._extract_method_info(method, node.name, package)
                class_info['methods'].append(method_info)
            elif isinstance(method, javalang.tree.ConstructorDeclaration):
                constructor_info = self._extract_constructor_info(method, node.name, package)
                class_info['constructors'].append(constructor_info)
            elif isinstance(method, javalang.tree.FieldDeclaration):
                for declarator in method.declarators:
                    field_info = self._extract_field_info(method, declarator, node.name, package)
                    class_info['fields'].append(field_info)
        
        return class_info
    
    def _extract_method_info(self, method: javalang.tree.MethodDeclaration,
                            class_name: str, package: str) -> Dict[str, Any]:
        """Extract detailed information about a method"""
        parameters = []
        if method.parameters:
            for param in method.parameters:
                param_info = {
                    'name': param.name,
                    'type': param.type.name if hasattr(param.type, 'name') else str(param.type),
                    'modifiers': param.modifiers if param.modifiers else []
                }
                parameters.append(param_info)
        
        return {
            'name': method.name,
            'class_name': class_name,
            'package': package,
            'return_type': method.return_type.name if method.return_type and hasattr(method.return_type, 'name') else 'void',
            'parameters': parameters,
            'modifiers': method.modifiers if method.modifiers else [],
            'throws': [throw.name for throw in method.throws] if method.throws else [],
            'documentation': method.documentation if hasattr(method, 'documentation') else None,
            'body': str(method.body) if method.body else None
        }
    
    def _extract_constructor_info(self, constructor: javalang.tree.ConstructorDeclaration,
                                 class_name: str, package: str) -> Dict[str, Any]:
        """Extract information about a constructor"""
        parameters = []
        if constructor.parameters:
            for param in constructor.parameters:
                param_info = {
                    'name': param.name,
                    'type': param.type.name if hasattr(param.type, 'name') else str(param.type),
                    'modifiers': param.modifiers if param.modifiers else []
                }
                parameters.append(param_info)
        
        return {
            'name': constructor.name,
            'class_name': class_name,
            'package': package,
            'parameters': parameters,
            'modifiers': constructor.modifiers if constructor.modifiers else [],
            'throws': [throw.name for throw in constructor.throws] if constructor.throws else [],
            'documentation': constructor.documentation if hasattr(constructor, 'documentation') else None
        }
    
    def _extract_field_info(self, field: javalang.tree.FieldDeclaration,
                           declarator: javalang.tree.VariableDeclarator,
                           class_name: str, package: str) -> Dict[str, Any]:
        """Extract information about a field"""
        return {
            'name': declarator.name,
            'class_name': class_name,
            'package': package,
            'type': field.type.name if hasattr(field.type, 'name') else str(field.type),
            'modifiers': field.modifiers if field.modifiers else [],
            'initializer': str(declarator.initializer) if declarator.initializer else None
        }
    
    def _extract_interface_info(self, node: javalang.tree.InterfaceDeclaration,
                               file_path: str, package: str) -> Dict[str, Any]:
        """Extract information about an interface"""
        interface_info = {
            'name': node.name,
            'package': package,
            'file_path': file_path,
            'modifiers': node.modifiers if node.modifiers else [],
            'extends': [ext.name for ext in node.extends] if node.extends else [],
            'methods': [],
            'documentation': node.documentation if hasattr(node, 'documentation') else None
        }
        
        # Extract methods
        for method in node.body:
            if isinstance(method, javalang.tree.MethodDeclaration):
                method_info = self._extract_method_info(method, node.name, package)
                interface_info['methods'].append(method_info)
        
        return interface_info
    
    def _extract_enum_info(self, node: javalang.tree.EnumDeclaration,
                          file_path: str, package: str) -> Dict[str, Any]:
        """Extract information about an enum"""
        return {
            'name': node.name,
            'package': package,
            'file_path': file_path,
            'modifiers': node.modifiers if node.modifiers else [],
            'implements': [impl.name for impl in node.implements] if node.implements else [],
            'constants': [const.name for const in node.body.constants] if node.body and node.body.constants else [],
            'documentation': node.documentation if hasattr(node, 'documentation') else None
        }
    
    def parse_project(self, project_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse all Java files in a project directory"""
        project_path = Path(project_path)
        java_files = list(project_path.rglob("*.java"))
        
        results = {
            'classes': [],
            'interfaces': [],
            'enums': [],
            'files_parsed': 0,
            'files_failed': 0
        }
        
        logger.info(f"Found {len(java_files)} Java files to parse")
        
        for java_file in java_files:
            try:
                file_result = self.parse_file(str(java_file))
                if file_result:
                    results['classes'].extend(file_result['classes'])
                    results['interfaces'].extend(file_result['interfaces'])
                    results['enums'].extend(file_result['enums'])
                    results['files_parsed'] += 1
                else:
                    results['files_failed'] += 1
            except Exception as e:
                logger.error(f"Failed to parse {java_file}: {e}")
                results['files_failed'] += 1
        
        logger.info(f"Parsing complete. Success: {results['files_parsed']}, Failed: {results['files_failed']}")
        return results
    
    def find_dependencies(self, class_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Find dependencies for a given class"""
        dependencies = []
        
        # Dependencies from extends
        if class_info.get('extends'):
            dependencies.append({
                'from': class_info['name'],
                'to': class_info['extends'],
                'type': 'inheritance',
                'package_from': class_info['package'],
                'package_to': ''  # Would need import analysis to determine
            })
        
        # Dependencies from implements
        for interface in class_info.get('implements', []):
            dependencies.append({
                'from': class_info['name'],
                'to': interface,
                'type': 'implementation',
                'package_from': class_info['package'],
                'package_to': ''
            })
        
        # Dependencies from method parameters and return types
        for method in class_info.get('methods', []):
            # Return type dependency
            if method['return_type'] and method['return_type'] != 'void':
                if not self._is_primitive_type(method['return_type']):
                    dependencies.append({
                        'from': class_info['name'],
                        'to': method['return_type'],
                        'type': 'usage',
                        'package_from': class_info['package'],
                        'package_to': ''
                    })
            
            # Parameter dependencies
            for param in method.get('parameters', []):
                if not self._is_primitive_type(param['type']):
                    dependencies.append({
                        'from': class_info['name'],
                        'to': param['type'],
                        'type': 'usage',
                        'package_from': class_info['package'],
                        'package_to': ''
                    })
        
        return dependencies
    
    def _is_primitive_type(self, type_name: str) -> bool:
        """Check if a type is a Java primitive type"""
        primitive_types = {
            'boolean', 'byte', 'char', 'short', 'int', 'long', 
            'float', 'double', 'void', 'String'
        }
        return type_name in primitive_types


# Global parser instance
java_parser = JavaCodeParser()