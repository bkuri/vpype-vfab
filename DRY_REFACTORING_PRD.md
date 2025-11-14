# vpype-plotty DRY Refactoring PRD
## Product Requirements Document

**Version**: 1.0  
**Date**: 2025-01-13  
**Status**: Ready for Implementation  
**Owner**: Development Team  

---

## 📋 **Executive Summary**

vpype-plotty codebase currently has significant DRY (Don't Repeat Yourself) violations, with **commands.py (95%)**, **utils.py (85%)**, and **database.py (65%)** showing high duplication potential. This PRD outlines a systematic refactoring approach to:

- **Reduce test complexity by 35-40%**
- **Increase overall coverage from 30% to 65%+**
- **Eliminate 200+ lines of duplicated code**
- **Improve maintainability and consistency**

### **Current State Analysis**
- **Overall Coverage**: 30% (target: 65%+)
- **Test Count**: 55 tests (target: 35 tests)
- **Code Duplication**: ~60% across core modules
- **Lines of Code**: 526 statements in vpype_plotty/

### **Success Metrics**
- **Code Reduction**: 200+ lines eliminated (15% reduction)
- **Coverage Increase**: 30% → 65%+ (116% improvement)
- **Test Efficiency**: 55 → 35 tests (36% reduction)
- **Development Velocity**: 40% faster feature development

---

## 🎯 **Phase 1: commands.py Abstraction (HIGHEST IMPACT)**

### **Problem Statement**
The commands module contains 6 commands with ~40 lines of duplicated scaffolding each, resulting in 240 lines of repetitive code including:
- Identical error handling patterns
- Repeated click options (`--workspace` in 5/6 commands)
- Same initialization logic (`StreamlinedPlottyCommand(workspace)`)
- Duplicated try/catch blocks

### **Proposed Solution: Command Decorator System**

#### **Technical Requirements**
1. Create `vpype_plotty/decorators.py` with `@plotty_command` decorator
2. Decorator must handle:
   - Standard option injection (`--workspace`)
   - Custom option support
   - Automatic error handling
   - Command initialization
   - vpype_cli integration

3. Refactor all 6 commands to use new decorator
4. Maintain backward compatibility with existing CLI interface

#### **Implementation Details**

```python
# New file: vpype_plotty/decorators.py
def plotty_command(*options, requires_workspace=True, error_context=None):
    """Universal ploTTY command decorator."""
    def decorator(func):
        # Add standard options
        if requires_workspace:
            func = click.option("--workspace", help="ploTTY workspace path")(func)
        
        # Add any custom options
        for opt in reversed(options):
            func = opt(func)
        
        # Apply vpype_cli decorator
        func = vpype_cli.global_processor(func)
        
        # Wrap with error handling
        @wraps(func)
        def wrapper(document, *args, **kwargs):
            workspace = kwargs.get('workspace')
            cmd = StreamlinedPlottyCommand(workspace)
            try:
                return func(cmd, document, *args, **kwargs)
            except Exception as e:
                cmd.handle_error(e, error_context or func.__name__)
        
        return wrapper
    return decorator
```

#### **Refactoring Example**

**Before (45 lines)**:
```python
@click.command()
@click.option("--name", help="Job name")
@click.option("--workspace", help="ploTTY workspace path")
@vpype_cli.global_processor
def plotty_add(document, name, workspace):
    try:
        cmd = StreamlinedPlottyCommand(workspace)
        # ... 30+ lines of logic
    except Exception as e:
        cmd.handle_error(e, "job creation")
```

**After (12 lines)**:
```python
@plotty_command(
    click.option("--name", help="Job name"),
    error_context="job creation"
)
def plotty_add(cmd, document, name):
    # ... just core logic, no scaffolding
```

#### **Acceptance Criteria**
- [ ] All 6 commands refactored to use decorator
- [ ] Commands module coverage increases from 33% to 55%+
- [ ] Test count reduces from 25 to 15 (40% reduction)
- [ ] All existing CLI functionality preserved
- [ ] No breaking changes to public API

#### **Implementation Timeline**
- **Days 1-2**: Create decorator system and test infrastructure
- **Days 3-4**: Refactor 3 commands (add, queue, status)
- **Days 5-7**: Refactor remaining 3 commands + update tests

---

## 🎯 **Phase 2: utils.py Formatting Unification**

### **Problem Statement**
The utils module has 70% code duplication between `format_job_status()` and `format_job_list()` functions:
- Identical JSON handling patterns
- Repeated format switching logic
- Similar field access with defaults
- Duplicated table formatting logic

### **Proposed Solution: Unified Formatter Class**

#### **Technical Requirements**
1. Create `JobFormatter` class in utils.py
2. Consolidate all formatting logic into single class
3. Maintain backward compatibility with existing function signatures
4. Support all existing output formats (table, json, simple, csv)

#### **Implementation Details**

```python
class JobFormatter:
    """Unified job and list formatting with consistent output."""
    
    def __init__(self):
        self.state_colors = {
            "pending": "🟡", "queued": "🔵", "running": "🟢",
            "completed": "✅", "failed": "❌", "cancelled": "⏹️"
        }
    
    def format(self, data, output_format="table", data_type="single"):
        """Unified formatting for jobs and lists."""
        if output_format == "json":
            return json.dumps(data, indent=2)
        
        elif output_format == "simple" and data_type == "single":
            return f"{data['name']}: {data['state']}"
        
        elif output_format == "csv" and data_type == "list":
            return self._format_csv(data)
        
        else:  # table format
            return self._format_table(data, data_type)
```

#### **Refactoring Strategy**
1. Create `JobFormatter` class with unified logic
2. Refactor existing functions to use formatter class
3. Keep thin wrapper functions for backward compatibility
4. Consolidate tests to focus on formatter class

#### **Acceptance Criteria**
- [ ] `JobFormatter` class implemented with unified logic
- [ ] Existing function signatures preserved
- [ ] All output formats (table, json, simple, csv) working
- [ ] Test count reduces from 8 to 4 (50% reduction)
- [ ] No breaking changes to function APIs

#### **Implementation Timeline**
- **Days 1-3**: Create unified formatter class
- **Days 4-5**: Refactor existing functions
- **Days 6-7**: Consolidate tests and validate

---

## 🎯 **Phase 3: database.py File Operations Abstraction**

### **Problem Statement**
The database module has repeated JSON file operations in 4 methods:
- Same read/write pattern with identical error handling
- Duplicated path construction logic
- Repeated try/catch blocks with `PlottyJobError`

### **Proposed Solution: Generic File Operations**

#### **Technical Requirements**
1. Create generic `_load_json_file()` and `_save_json_file()` methods
2. Standardize error handling for all file operations
3. Consolidate path construction logic
4. Maintain all existing method signatures

#### **Implementation Details**

```python
def _load_json_file(self, name: str, file_type: str = "job") -> Dict[str, Any]:
    """Generic JSON file loader with error handling."""
    file_path = self._get_file_path(name, file_type)
    
    if not file_path.exists():
        raise PlottyJobError(f"{file_type.title()} '{name}' not found")
    
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise PlottyJobError(f"Failed to load {file_type} '{name}': {e}")

def _save_json_file(self, name: str, data: Dict[str, Any], file_type: str = "job") -> None:
    """Generic JSON file saver with error handling."""
    file_path = self._get_file_path(name, file_type)
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except (OSError, json.JSONDecodeError) as e:
        raise PlottyJobError(f"Failed to save {file_type} '{name}': {e}")
```

#### **Refactoring Strategy**
1. Add generic file operation methods to `StreamlinedPlottyIntegration`
2. Refactor existing methods one by one to use generics
3. Consolidate file operation tests
4. Add comprehensive tests for generic operations

#### **Acceptance Criteria**
- [ ] Generic file operations implemented
- [ ] All existing methods refactored to use generics
- [ ] Database module coverage increases from 23% to 45%+
- [ ] Test count reduces from 12 to 6 (50% reduction)
- [ ] All file operations maintain existing behavior

#### **Implementation Timeline**
- **Days 1-4**: Create generic file operations
- **Days 5-6**: Refactor existing methods
- **Day 7**: Update tests and validate

---

## 🎯 **Phase 4: monitor.py Status Formatting (Optional Cleanup)**

### **Problem Statement**
The monitor module has similar formatting logic for jobs and devices:
- Duplicated status icon mapping
- Similar string formatting patterns
- Repeated field access logic

### **Proposed Solution: Unified Status Formatter**

#### **Technical Requirements**
1. Create `StatusFormatter` class in monitor.py
2. Unify job and device formatting logic
3. Consolidate status icon mappings
4. Maintain all existing functionality

#### **Acceptance Criteria**
- [ ] `StatusFormatter` class implemented
- [ ] Job and device formatting unified
- [ ] All existing display functionality preserved
- [ ] Monitor module coverage improves

---

## 📊 **Overall Implementation Timeline**

### **Week 1: Phase 1 - commands.py**
- **Days 1-2**: Create decorator system
- **Days 3-4**: Refactor 3 commands (add, queue, status)
- **Days 5-7**: Refactor remaining 3 commands + update tests
- **Expected Coverage Gain**: 30% → 45% overall

### **Week 2: Phase 2 - utils.py**
- **Days 1-3**: Create unified formatter class
- **Days 4-5**: Refactor existing functions
- **Days 6-7**: Consolidate tests
- **Expected Coverage Gain**: 45% → 52% overall

### **Week 3: Phase 3 - database.py**
- **Days 1-4**: Create generic file operations
- **Days 5-6**: Refactor existing methods
- **Day 7**: Update tests
- **Expected Coverage Gain**: 52% → 58% overall

### **Week 4: Phase 4 - monitor.py & Final Polish**
- **Days 1-2**: Unify status formatting
- **Days 3-4**: Final test consolidation
- **Days 5-7**: Documentation and cleanup
- **Expected Final Coverage**: 58% → 65%+ overall

---

## 🎯 **Success Metrics & KPIs**

### **Code Quality Metrics**
| Metric | Current | Target | Improvement |
|---------|----------|--------|-------------|
| Lines of Code | 526 | 426 | 19% reduction |
| Code Duplication | 60% | 20% | 67% reduction |
| Cyclomatic Complexity | High | Medium | 30% reduction |

### **Testing Metrics**
| Metric | Current | Target | Improvement |
|---------|----------|--------|-------------|
| Overall Coverage | 30% | 65% | 116% improvement |
| Test Count | 55 | 35 | 36% reduction |
| Test Maintenance Effort | High | Low | 50% reduction |

### **Development Efficiency Metrics**
| Metric | Current | Target | Improvement |
|---------|----------|--------|-------------|
| New Feature Time | 100% | 60% | 40% faster |
| Bug Fix Time | 100% | 50% | 50% faster |
| Code Review Time | 100% | 70% | 30% faster |

---

## 🚦 **Go/No-Go Decision Points**

### **Phase 1 Gate (commands.py)**
**Go Criteria:**
- Commands module coverage >50%
- All 6 commands refactored
- Tests passing with 40% reduction
- No breaking changes to CLI

**No-Go Criteria:**
- Commands module coverage <40%
- Any command functionality broken
- CLI interface changes

### **Phase 2 Gate (utils.py)**
**Go Criteria:**
- Overall coverage >52%
- Formatter class working
- All output formats preserved
- Backward compatibility maintained

**No-Go Criteria:**
- Overall coverage <48%
- Breaking changes to function APIs
- Output format regressions

### **Phase 3 Gate (database.py)**
**Go Criteria:**
- Overall coverage >58%
- All file operations working
- Database functionality preserved
- Generic operations tested

**No-Go Criteria:**
- Overall coverage <55%
- Data loss or corruption
- Breaking changes to database API

### **Final Gate (Project Complete)**
**Go Criteria:**
- Overall coverage >60%
- All acceptance criteria met
- Documentation updated
- Performance maintained

**No-Go Criteria:**
- Overall coverage <55%
- Any module regression
- Performance degradation

---

## 🔧 **Technical Implementation Guidelines**

### **Code Standards**
- Follow existing code style (Black, Ruff)
- Maintain type hints throughout
- Add comprehensive docstrings
- Use existing error handling patterns

### **Testing Strategy**
- Focus on testing core logic, not scaffolding
- Use existing direct import pattern
- Maintain test coverage during refactoring
- Add tests for new abstraction layers

### **Backward Compatibility**
- All public APIs must remain unchanged
- CLI interface must be preserved
- Configuration files must remain compatible
- Database schema must remain stable

### **Performance Requirements**
- No performance degradation
- Memory usage must not increase
- File I/O operations must remain efficient
- CLI response time must be maintained

---

## 📋 **Risks & Mitigations**

### **High Risk Areas**
1. **Command Decorator Complexity**
   - **Risk**: Breaking CLI functionality
   - **Mitigation**: Incremental refactoring with comprehensive testing

2. **Formatter Class Changes**
   - **Risk**: Output format changes
   - **Mitigation**: Maintain exact output formatting with wrapper functions

3. **Database File Operations**
   - **Risk**: Data loss or corruption
   - **Mitigation**: Extensive testing and backup procedures

### **Medium Risk Areas**
1. **Test Coverage Regression**
   - **Risk**: Coverage decreases during refactoring
   - **Mitigation**: Continuous coverage monitoring

2. **Performance Degradation**
   - **Risk**: Abstraction layers slow down operations
   - **Mitigation**: Performance testing at each phase

### **Low Risk Areas**
1. **Code Style Inconsistencies**
   - **Risk**: Inconsistent formatting
   - **Mitigation**: Automated linting and formatting

---

## 📚 **Documentation Requirements**

### **Code Documentation**
- All new classes and methods must have docstrings
- Type hints required for all function signatures
- Examples provided for complex abstractions

### **Testing Documentation**
- Test strategy documented for each phase
- Coverage targets and measurements tracked
- Test data and fixtures documented

### **User Documentation**
- CLI usage examples updated if needed
- Configuration changes documented
- Migration guides for any breaking changes

---

## 🚀 **Deployment Strategy**

### **Phase-Based Deployment**
1. **Phase 1**: Deploy commands.py changes
2. **Phase 2**: Deploy utils.py changes
3. **Phase 3**: Deploy database.py changes
4. **Phase 4**: Deploy monitor.py changes and final polish

### **Rollback Strategy**
- Each phase can be rolled back independently
- Git branches for each phase
- Automated testing before each merge
- Feature flags for critical changes

### **Monitoring & Validation**
- Continuous coverage monitoring
- Automated testing on each commit
- Performance benchmarking
- User feedback collection

---

## 📞 **Stakeholder Communication**

### **Development Team**
- Daily progress updates
- Technical decision documentation
- Code review requirements
- Testing status updates

### **Project Management**
- Weekly progress reports
- Gate decision documentation
- Risk assessment updates
- Timeline adjustments

### **End Users**
- Release notes for each phase
- Documentation updates
- Breaking change notifications
- Support channel updates

---

## 📄 **Appendix**

### **A. Current Code Analysis**
- **commands.py**: 155 statements, 33% coverage, 95% DRY potential
- **utils.py**: 67 statements, 100% coverage, 85% DRY potential
- **database.py**: 95 statements, 23% coverage, 65% DRY potential
- **monitor.py**: 90 statements, 0% coverage, 60% DRY potential
- **config.py**: 44 statements, 30% coverage, 35% DRY potential
- **exceptions.py**: 71 statements, 0% coverage, 15% DRY potential

### **B. Test Coverage Breakdown**
- **test_utils_direct.py**: 30 tests, 100% utils coverage
- **test_commands_direct.py**: 25 tests, 33% commands coverage
- **test_monitor_direct.py**: 17 tests, 89% monitor coverage
- **Overall**: 55 tests, 30% project coverage

### **C. Technical Debt Assessment**
- **High Priority**: commands.py, utils.py, database.py
- **Medium Priority**: monitor.py, config.py
- **Low Priority**: exceptions.py

---

**Document Status**: Ready for Implementation  
**Next Review**: After Phase 1 completion  
**Approval**: Development Team Lead