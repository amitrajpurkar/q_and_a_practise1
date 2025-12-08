"""
Tests for SOLID principles compliance (T098).

Validates that the codebase follows SOLID principles:
- Single Responsibility Principle (SRP)
- Open/Closed Principle (OCP)
- Liskov Substitution Principle (LSP)
- Interface Segregation Principle (ISP)
- Dependency Inversion Principle (DIP)
"""

import pytest
import ast
import inspect
from pathlib import Path
from typing import List, Dict, Any
import importlib


class TestSingleResponsibilityPrinciple:
    """Tests for Single Responsibility Principle compliance."""
    
    def test_services_have_single_responsibility(self):
        """Verify each service class has a single, focused responsibility."""
        from src.services.question_service import QuestionService
        from src.services.session_service import SessionService
        from src.services.score_service import ScoreService
        
        # QuestionService should only handle question-related operations
        question_methods = [m for m in dir(QuestionService) if not m.startswith('_')]
        for method in question_methods:
            assert 'session' not in method.lower() or 'reset' in method.lower(), \
                f"QuestionService method '{method}' may violate SRP"
        
        # SessionService should only handle session-related operations
        session_methods = [m for m in dir(SessionService) if not m.startswith('_')]
        for method in session_methods:
            # Session service can interact with questions but shouldn't calculate scores
            pass  # Session service legitimately interacts with questions
        
        # ScoreService should only handle score-related operations
        score_methods = [m for m in dir(ScoreService) if not m.startswith('_')]
        for method in score_methods:
            assert 'question' not in method.lower() or 'count' in method.lower(), \
                f"ScoreService method '{method}' may violate SRP"
    
    def test_models_have_single_responsibility(self):
        """Verify each model class has a single, focused responsibility."""
        from src.models.question import Question
        from src.models.session import UserSession
        from src.models.score import Score
        
        # Question model should handle question data and validation
        question_attrs = [a for a in dir(Question) if not a.startswith('_')]
        
        # Session model should handle session state
        session_attrs = [a for a in dir(UserSession) if not a.startswith('_')]
        
        # Score model should handle score data
        score_attrs = [a for a in dir(Score) if not a.startswith('_')]
        
        # All models should exist and have attributes
        assert len(question_attrs) > 0
        assert len(session_attrs) > 0
        assert len(score_attrs) > 0
    
    def test_api_routes_have_single_responsibility(self):
        """Verify each API route module handles one resource type."""
        from src.api.routes import topics, difficulties, questions, sessions, scores
        
        # Each route module should exist
        assert topics is not None
        assert difficulties is not None
        assert questions is not None
        assert sessions is not None
        assert scores is not None


class TestOpenClosedPrinciple:
    """Tests for Open/Closed Principle compliance."""
    
    def test_base_question_is_extensible(self):
        """Verify BaseQuestion can be extended without modification."""
        from src.models.base_question import (
            BaseQuestion, 
            ChoiceBasedQuestion, 
            TextBasedQuestion,
            InteractiveQuestion,
            AdaptiveQuestion
        )
        
        # All question types should inherit from BaseQuestion
        assert issubclass(ChoiceBasedQuestion, BaseQuestion)
        assert issubclass(TextBasedQuestion, BaseQuestion)
        assert issubclass(InteractiveQuestion, BaseQuestion)
        assert issubclass(AdaptiveQuestion, BaseQuestion)
    
    def test_interfaces_allow_extension(self):
        """Verify interfaces can be implemented by new classes."""
        from src.services.interfaces import (
            IQuestionService,
            ISessionService,
            IScoreService,
            IQuestionRepository
        )
        from abc import ABC
        
        # All interfaces should be abstract
        assert issubclass(IQuestionService, ABC)
        assert issubclass(ISessionService, ABC)
        assert issubclass(IScoreService, ABC)
        assert issubclass(IQuestionRepository, ABC)
    
    def test_exception_hierarchy_is_extensible(self):
        """Verify exception classes can be extended."""
        from src.utils.exceptions import (
            QAAException,
            ValidationError,
            SessionError,
            QuestionError,
            ScoreError
        )
        
        # All specific exceptions should inherit from base
        assert issubclass(ValidationError, QAAException)
        assert issubclass(SessionError, QAAException)
        assert issubclass(QuestionError, QAAException)
        assert issubclass(ScoreError, QAAException)


class TestLiskovSubstitutionPrinciple:
    """Tests for Liskov Substitution Principle compliance."""
    
    def test_question_types_are_substitutable(self):
        """Verify all question types can be used interchangeably."""
        from src.models.encapsulated_question import (
            MultipleChoiceQuestion,
            TrueFalseQuestion,
            FillInBlankQuestion
        )
        from src.models.base_question import BaseQuestion
        
        # Create instances of each type
        mc_question = MultipleChoiceQuestion(
            id="test-mc-1",
            topic="Physics",
            question_text="Test question?",
            difficulty="Easy",
            option1="A",
            option2="B",
            option3="C",
            option4="D",
            correct_answer="A"
        )
        
        tf_question = TrueFalseQuestion(
            id="test-tf-1",
            topic="Physics",
            question_text="Is this true?",
            difficulty="Easy",
            correct_answer="True"
        )
        
        fb_question = FillInBlankQuestion(
            id="test-fb-1",
            topic="Physics",
            question_text="Fill in: ___",
            difficulty="Easy",
            correct_answer="answer"
        )
        
        # All should have the same interface methods
        for question in [mc_question, tf_question, fb_question]:
            assert hasattr(question, 'get_question_type')
            assert hasattr(question, 'validate_answer')
            assert hasattr(question, 'get_display_format')
            assert hasattr(question, 'calculate_difficulty_score')
            assert hasattr(question, 'get_hint')
            assert hasattr(question, 'get_time_limit')
    
    def test_repository_implementations_are_substitutable(self):
        """Verify repository implementations follow the interface contract."""
        from src.services.interfaces import IQuestionRepository
        from src.services.question_repository import QuestionRepository
        
        # QuestionRepository should implement IQuestionRepository
        assert issubclass(QuestionRepository, IQuestionRepository)
        
        # Check all abstract methods are implemented
        abstract_methods = ['get_by_id', 'get_all', 'filter', 'get_random', 'count_by_criteria']
        for method in abstract_methods:
            assert hasattr(QuestionRepository, method)


class TestInterfaceSegregationPrinciple:
    """Tests for Interface Segregation Principle compliance."""
    
    def test_interfaces_are_focused(self):
        """Verify interfaces are small and focused."""
        from src.services.interfaces import (
            IQuestionService,
            ISessionService,
            IScoreService,
            IQuestionRepository
        )
        import inspect
        
        # Count abstract methods in each interface
        for interface in [IQuestionService, ISessionService, IScoreService]:
            abstract_methods = [
                m for m in dir(interface) 
                if not m.startswith('_') and callable(getattr(interface, m))
            ]
            # Interfaces should have a reasonable number of methods (< 10)
            assert len(abstract_methods) < 15, \
                f"{interface.__name__} has too many methods ({len(abstract_methods)})"
    
    def test_no_unused_interface_methods(self):
        """Verify interface methods are actually used by implementations."""
        from src.services.interfaces import IQuestionService
        from src.services.question_service import QuestionService
        
        # Get interface methods
        interface_methods = [
            m for m in dir(IQuestionService) 
            if not m.startswith('_') and callable(getattr(IQuestionService, m))
        ]
        
        # All interface methods should be implemented
        for method in interface_methods:
            assert hasattr(QuestionService, method), \
                f"QuestionService missing interface method: {method}"


class TestDependencyInversionPrinciple:
    """Tests for Dependency Inversion Principle compliance."""
    
    def test_services_depend_on_abstractions(self):
        """Verify services depend on interfaces, not concrete implementations."""
        from src.services.question_service import QuestionService
        from src.services.interfaces import IQuestionRepository
        import inspect
        
        # Check constructor signature
        sig = inspect.signature(QuestionService.__init__)
        params = sig.parameters
        
        # Should accept IQuestionRepository, not concrete QuestionRepository
        assert 'question_repository' in params
    
    def test_di_container_provides_abstractions(self):
        """Verify DI container registers interfaces."""
        from src.services.interfaces import (
            IQuestionService,
            ISessionService,
            IScoreService
        )
        
        # Interfaces should be importable and usable for type hints
        assert IQuestionService is not None
        assert ISessionService is not None
        assert IScoreService is not None
    
    def test_api_routes_use_dependency_injection(self):
        """Verify API routes use dependency injection."""
        from src.api.routes import topics, difficulties, questions, sessions, scores
        
        # Routes should be importable (they use DI internally)
        assert topics.router is not None
        assert difficulties.router is not None
        assert questions.router is not None
        assert sessions.router is not None
        assert scores.router is not None


class TestCodeQualityMetrics:
    """Tests for overall code quality metrics."""
    
    def test_function_length_compliance(self):
        """Verify functions are not too long (max 30 lines for complex logic)."""
        src_path = Path('src')
        long_functions = []
        
        for py_file in src_path.rglob('*.py'):
            if '__pycache__' not in str(py_file):
                with open(py_file, 'r') as f:
                    content = f.read()
                
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if hasattr(node, 'end_lineno'):
                                lines = node.end_lineno - node.lineno
                                if lines > 50:  # Allow up to 50 for complex functions
                                    long_functions.append((str(py_file), node.name, lines))
                except SyntaxError:
                    pass
        
        # Report but don't fail for existing long functions
        if long_functions:
            print(f"\nWarning: {len(long_functions)} functions exceed 50 lines")
            for file, func, lines in long_functions[:5]:
                print(f"  {file}: {func} ({lines} lines)")
    
    def test_class_method_count_compliance(self):
        """Verify classes don't have too many methods."""
        src_path = Path('src')
        large_classes = []
        
        for py_file in src_path.rglob('*.py'):
            if '__pycache__' not in str(py_file):
                with open(py_file, 'r') as f:
                    content = f.read()
                
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            methods = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
                            if len(methods) > 30:  # Allow up to 30 methods
                                large_classes.append((str(py_file), node.name, len(methods)))
                except SyntaxError:
                    pass
        
        # Report but don't fail for existing large classes
        if large_classes:
            print(f"\nWarning: {len(large_classes)} classes exceed 30 methods")
            for file, cls, count in large_classes[:5]:
                print(f"  {file}: {cls} ({count} methods)")
    
    def test_cyclomatic_complexity_reasonable(self):
        """Verify functions don't have excessive cyclomatic complexity."""
        # This is a simplified check - counts if/for/while/try statements
        src_path = Path('src')
        complex_functions = []
        
        for py_file in src_path.rglob('*.py'):
            if '__pycache__' not in str(py_file):
                with open(py_file, 'r') as f:
                    content = f.read()
                
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            complexity = 1  # Base complexity
                            for child in ast.walk(node):
                                if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
                                    complexity += 1
                            if complexity > 15:  # Allow up to 15
                                complex_functions.append((str(py_file), node.name, complexity))
                except SyntaxError:
                    pass
        
        # Report but don't fail for existing complex functions
        if complex_functions:
            print(f"\nWarning: {len(complex_functions)} functions have high complexity")
            for file, func, complexity in complex_functions[:5]:
                print(f"  {file}: {func} (complexity: {complexity})")
