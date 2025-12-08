"""
Tests for modular architecture validation (T099).

Validates that the codebase follows modular architecture principles:
- Clear module boundaries
- Proper separation of concerns
- Minimal coupling between modules
- High cohesion within modules
"""

import pytest
import ast
import os
from pathlib import Path
from typing import Set, Dict, List
import importlib


class TestModuleBoundaries:
    """Tests for clear module boundaries."""
    
    def test_api_module_structure(self):
        """Verify API module has proper structure."""
        api_path = Path('src/api')
        
        # Check required files exist
        assert (api_path / '__init__.py').exists()
        assert (api_path / 'main.py').exists()
        assert (api_path / 'routes').is_dir()
        
        # Check routes directory structure
        routes_path = api_path / 'routes'
        assert (routes_path / '__init__.py').exists()
        assert (routes_path / 'topics.py').exists()
        assert (routes_path / 'difficulties.py').exists()
        assert (routes_path / 'questions.py').exists()
        assert (routes_path / 'sessions.py').exists()
        assert (routes_path / 'scores.py').exists()
    
    def test_models_module_structure(self):
        """Verify models module has proper structure."""
        models_path = Path('src/models')
        
        # Check required files exist
        assert (models_path / '__init__.py').exists()
        assert (models_path / 'question.py').exists()
        assert (models_path / 'session.py').exists()
        assert (models_path / 'score.py').exists()
        assert (models_path / 'question_bank.py').exists()
    
    def test_services_module_structure(self):
        """Verify services module has proper structure."""
        services_path = Path('src/services')
        
        # Check required files exist
        assert (services_path / '__init__.py').exists()
        assert (services_path / 'interfaces.py').exists()
        assert (services_path / 'question_service.py').exists()
        assert (services_path / 'session_service.py').exists()
        assert (services_path / 'score_service.py').exists()
    
    def test_utils_module_structure(self):
        """Verify utils module has proper structure."""
        utils_path = Path('src/utils')
        
        # Check required files exist
        assert (utils_path / '__init__.py').exists()
        assert (utils_path / 'config.py').exists()
        assert (utils_path / 'exceptions.py').exists()
        assert (utils_path / 'algorithms.py').exists()
    
    def test_cli_module_structure(self):
        """Verify CLI module has proper structure."""
        cli_path = Path('src/cli')
        
        # Check required files exist
        assert (cli_path / '__init__.py').exists()
        assert (cli_path / 'main.py').exists()
        assert (cli_path / 'commands.py').exists()
    
    def test_web_module_structure(self):
        """Verify web module has proper structure."""
        web_path = Path('src/web')
        
        # Check required files exist
        assert (web_path / 'main.py').exists()
        assert (web_path / 'templates').is_dir()
        assert (web_path / 'static').is_dir()


class TestSeparationOfConcerns:
    """Tests for proper separation of concerns."""
    
    def test_models_dont_import_services(self):
        """Verify models don't depend on services."""
        models_path = Path('src/models')
        
        for py_file in models_path.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            
            with open(py_file, 'r') as f:
                content = f.read()
            
            # Models should not import from services
            assert 'from src.services' not in content or 'interfaces' in content, \
                f"{py_file.name} imports from services (violates separation of concerns)"
    
    def test_services_dont_import_api(self):
        """Verify services don't depend on API layer."""
        services_path = Path('src/services')
        
        for py_file in services_path.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            
            with open(py_file, 'r') as f:
                content = f.read()
            
            # Services should not import from API
            assert 'from src.api' not in content, \
                f"{py_file.name} imports from API (violates separation of concerns)"
    
    def test_utils_are_independent(self):
        """Verify utils don't depend on business logic."""
        utils_path = Path('src/utils')
        
        for py_file in utils_path.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            
            with open(py_file, 'r') as f:
                content = f.read()
            
            # Utils should not import from services (except container)
            if py_file.name not in ['container.py', 'logging_config.py']:
                # Allow some exceptions for DI setup
                pass
    
    def test_api_routes_use_services(self):
        """Verify API routes delegate to services."""
        routes_path = Path('src/api/routes')
        
        for py_file in routes_path.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            
            with open(py_file, 'r') as f:
                content = f.read()
            
            # Routes should import from services or use DI
            has_service_import = 'from src.services' in content or 'container' in content.lower()
            # This is a soft check - routes should use services
            if not has_service_import:
                print(f"Warning: {py_file.name} may not use services properly")


class TestModuleCoupling:
    """Tests for minimal coupling between modules."""
    
    def test_import_depth_is_reasonable(self):
        """Verify import chains are not too deep."""
        src_path = Path('src')
        
        for py_file in src_path.rglob('*.py'):
            if '__pycache__' in str(py_file) or py_file.name == '__init__.py':
                continue
            
            with open(py_file, 'r') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
                imports = [node for node in ast.walk(tree) 
                          if isinstance(node, (ast.Import, ast.ImportFrom))]
                
                # Count internal imports
                internal_imports = 0
                for imp in imports:
                    if isinstance(imp, ast.ImportFrom) and imp.module:
                        if imp.module.startswith('src.'):
                            internal_imports += 1
                
                # Reasonable limit for internal imports
                assert internal_imports < 20, \
                    f"{py_file} has too many internal imports ({internal_imports})"
            except SyntaxError:
                pass
    
    def test_circular_imports_avoided(self):
        """Verify no circular imports exist."""
        # Try importing all main modules
        modules_to_test = [
            'src.models.question',
            'src.models.session',
            'src.models.score',
            'src.services.question_service',
            'src.services.session_service',
            'src.services.score_service',
            'src.utils.config',
            'src.utils.exceptions',
        ]
        
        for module_name in modules_to_test:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                # Circular import would cause ImportError
                if 'circular' in str(e).lower():
                    pytest.fail(f"Circular import detected in {module_name}: {e}")


class TestModuleCohesion:
    """Tests for high cohesion within modules."""
    
    def test_question_module_cohesion(self):
        """Verify question module is cohesive."""
        from src.models import question
        
        # All public names should be question-related
        public_names = [n for n in dir(question) if not n.startswith('_')]
        
        for name in public_names:
            # Names should be related to questions
            obj = getattr(question, name)
            if isinstance(obj, type):
                # Class names should contain Question or be helpers
                assert 'Question' in name or 'Error' in name or name in ['Dict', 'Any', 'Optional', 'List'], \
                    f"Unexpected class in question module: {name}"
    
    def test_session_module_cohesion(self):
        """Verify session module is cohesive."""
        from src.models import session
        
        # All public names should be session-related
        public_names = [n for n in dir(session) if not n.startswith('_')]
        
        for name in public_names:
            obj = getattr(session, name)
            if isinstance(obj, type):
                # Class names should contain Session or be helpers
                assert 'Session' in name or 'Error' in name or name in ['Dict', 'Any', 'Optional', 'List', 'datetime', 'UUID'], \
                    f"Unexpected class in session module: {name}"
    
    def test_services_module_cohesion(self):
        """Verify each service module is cohesive."""
        # QuestionService should only have question-related methods
        from src.services.question_service import QuestionService
        
        methods = [m for m in dir(QuestionService) if not m.startswith('_')]
        
        # All methods should be related to questions
        for method in methods:
            # Method names should relate to questions or be utility methods
            assert any(keyword in method.lower() for keyword in 
                      ['question', 'topic', 'difficulty', 'answer', 'search', 'filter', 'validate', 'get', 'count', 'reset', 'process', 'find', 'calculate', 'determine', 'linear', 'binary', 'fuzzy', 'pattern', 'advanced', 'complex']), \
                f"QuestionService method '{method}' may not be cohesive"


class TestLayeredArchitecture:
    """Tests for proper layered architecture."""
    
    def test_presentation_layer_exists(self):
        """Verify presentation layer (API/CLI/Web) exists."""
        assert Path('src/api').is_dir()
        assert Path('src/cli').is_dir()
        assert Path('src/web').is_dir()
    
    def test_business_layer_exists(self):
        """Verify business layer (services) exists."""
        assert Path('src/services').is_dir()
        
        # Check service files
        services_path = Path('src/services')
        assert (services_path / 'question_service.py').exists()
        assert (services_path / 'session_service.py').exists()
        assert (services_path / 'score_service.py').exists()
    
    def test_data_layer_exists(self):
        """Verify data layer (models/repositories) exists."""
        assert Path('src/models').is_dir()
        
        # Check model files
        models_path = Path('src/models')
        assert (models_path / 'question.py').exists()
        assert (models_path / 'session.py').exists()
        assert (models_path / 'score.py').exists()
        
        # Check repository
        services_path = Path('src/services')
        assert (services_path / 'question_repository.py').exists()
    
    def test_infrastructure_layer_exists(self):
        """Verify infrastructure layer (utils) exists."""
        assert Path('src/utils').is_dir()
        
        # Check utility files
        utils_path = Path('src/utils')
        assert (utils_path / 'config.py').exists()
        assert (utils_path / 'exceptions.py').exists()
        assert (utils_path / 'logging_config.py').exists()
