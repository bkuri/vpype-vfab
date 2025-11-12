# vpype-plotty Agent Guidelines

## Build & Test Commands
- **Install**: `pip install -e ".[dev]"`
- **Lint**: `ruff check .` and `black --check .`
- **Format**: `ruff format .` and `black .`
- **Type check**: `mypy vpype_plotty/`
- **Run tests**: `pytest`
- **Single test**: `pytest tests/test_commands.py::test_function_name`
- **Coverage**: `pytest --cov=vpype_plotty --cov-report=html`

## Code Style Guidelines
- **Python**: 3.11+ with type hints required
- **Formatting**: Black (88 char line), Ruff for linting
- **Imports**: Group stdlib, third-party, local imports; use `isort` style
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error handling**: Use custom exceptions from `vpype_plotty.exceptions`
- **Documentation**: Docstrings for all public functions/classes
- **Testing**: pytest with >90% coverage, mock external dependencies
- **Dependencies**: Use pyproject.toml, follow vpype plugin conventions