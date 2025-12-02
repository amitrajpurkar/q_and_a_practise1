# Implementation Plan: Q&A Practice Application

**Branch**: `001-qa-app` | **Date**: 2025-12-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-qa-app/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Standalone Q&A practice application with dual interfaces (CLI and web) using Python 3.12, UV package manager, pandas for CSV processing, FastAPI backend services, and Jinja2/HTMX frontend. Application loads questions from CSV, allows topic/difficulty selection, provides randomized questions with immediate feedback, tracks scores, and generates session summaries. Architecture follows SOLID principles with 90% test coverage requirement and implementation of 15+ programming concepts.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, pandas, Jinja2, HTMX, pytest, uvicorn  
**Storage**: CSV file for question bank (question-bank.csv)  
**Testing**: pytest with pytest-cov for 90% coverage requirement  
**Target Platform**: Cross-platform desktop (Windows, macOS, Linux)  
**Project Type**: Web application with CLI interface  
**Performance Goals**: <2s CSV parsing for 200+ questions, <200ms UI response time  
**Constraints**: <100MB memory usage, standalone operation, 90% test coverage  
**Scale/Scope**: Single-user sessions, 200+ questions, 3 topics × 3 difficulties

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### SOLID Principles Compliance
- [x] Single Responsibility: Each module has one reason to change - Service layer separation
- [x] Open/Closed: Classes open for extension, closed for modification - Abstract interfaces
- [x] Liskov Substitution: Child classes substitutable for parents - Base question classes
- [x] Interface Segregation: No fat interfaces, clients depend only on used methods - Specific service interfaces
- [x] Dependency Inversion: High-level modules don't depend on low-level modules - Repository pattern with DI

### Test Coverage Requirements
- [x] 90% minimum test coverage planned - pytest with pytest-cov configured
- [x] TDD approach ( test-first development) - Test structure defined in plan
- [x] Unit tests for all business logic - Comprehensive unit test structure
- [x] Integration tests for service interactions - API endpoint and workflow tests
- [x] End-to-end tests for user journeys - CLI and web interface tests

### Modular Architecture Requirements
- [x] Clear backend/frontend separation - FastAPI backend + Jinja2/HTMX frontend + CLI
- [x] Service layer abstractions - Defined service interfaces and implementations
- [x] Independent module deployability - Separate modules with clear boundaries
- [x] No direct data access from presentation layer - Repository pattern abstraction

### Programming Concepts Implementation
- [x] Arrays and data structures - Python lists, dictionaries for question storage
- [x] User-defined objects and records - Question, UserSession, Score dataclasses
- [x] Simple and complex selection ( if/else, nested if, switch) - Answer validation logic
- [x] Loops and nested loops - Question processing and filtering algorithms
- [x] User-defined methods with parameters and return values - Service methods
- [x] Sorting algorithms - Question organization by difficulty
- [x] Searching algorithms - Question filtering and lookup
- [x] File I/O operations - CSV parsing with pandas
- [x] Sentinels/flags for control flow - Session state management
- [x] Recursion where appropriate - Complex data structure operations
- [x] Merging sorted data structures - Question bank organization
- [x] Polymorphism implementation - Different question type handling
- [x] Inheritance hierarchies - Base classes for entities
- [x] Encapsulation practices - Private methods and data protection
- [x] Text file parsing capabilities - CSV processing with error handling

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── __init__.py
│   ├── question.py
│   ├── session.py
│   └── score.py
├── services/
│   ├── __init__.py
│   ├── question_service.py
│   ├── session_service.py
│   └── csv_parser.py
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── questions.py
│   │   └── sessions.py
│   └── dependencies.py
├── cli/
│   ├── __init__.py
│   ├── main.py
│   └── commands.py
├── web/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── quiz.html
│       └── results.html
└── utils/
    ├── __init__.py
    ├── validators.py
    └── exceptions.py

tests/
├── unit/
│   ├── test_models/
│   ├── test_services/
│   ├── test_api/
│   └── test_cli/
├── integration/
│   ├── test_api_endpoints.py
│   └── test_cli_workflows.py
└── contract/
    └── test_api_contracts.py

pyproject.toml
README.md
requirements.txt
src/main/resources/question-bank.csv
```

**Structure Decision**: Modular architecture with clear separation of concerns. Backend services in `src/api/` with FastAPI, CLI interface in `src/cli/`, web frontend in `src/web/` using Jinja2/HTMX, shared models and services, comprehensive test structure for 90% coverage requirement.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
