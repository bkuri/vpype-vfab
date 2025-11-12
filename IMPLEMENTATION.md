# vpype-plotty Implementation Plan

## Overview

**vpype-plotty** is a vpype plugin that bridges creative tools (vsketch, vpype) with ploTTY's production plotter management system. It enables seamless workflow from generative art creation to professional plotter job management.

## Repository Structure

```
vpype-plotty/
├── .github/
│   └── workflows/
│       └── ci.yml
├── vpype_plotty/
│   ├── __init__.py
│   ├── commands.py          # Main vpype commands
│   ├── config.py            # ploTTY config detection
│   ├── database.py          # ploTTY DB integration
│   ├── utils.py             # Shared utilities
│   └── exceptions.py       # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_commands.py
│   ├── test_config.py
│   ├── test_database.py
│   └── fixtures/
│       └── test_svg.svg
├── examples/
│   ├── vsketch_integration.py
│   ├── batch_processing.py
│   └── standalone_usage.py
├── docs/
│   ├── installation.md
│   ├── usage.md
│   └── examples.md
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── .gitignore
```

## Core Commands

### 1. `plotty-add` - Add document to ploTTY

```python
@click.command()
@click.option('--name', '-n', help='Job name (defaults to auto-generated)')
@click.option('--preset', '-p', default='fast', 
              type=click.Choice(['fast', 'default', 'hq']),
              help='Optimization preset')
@click.option('--paper', default='A4', help='Paper size')
@click.option('--queue/--no-queue', default=False, 
              help='Automatically queue job after adding')
@click.option('--workspace', help='ploTTY workspace path')
@vpype_cli.global_processor
def plotty_add(document, name, preset, paper, queue, workspace):
    """Add current document to ploTTY job queue."""
    pass
```

**Features:**
- Auto-generate job name from document metadata or timestamp
- Detect ploTTY configuration automatically
- Create job using ploTTY's FSM system
- Support for both ploTTY-integrated and standalone modes
- Return job ID for reference

### 2. `plotty-queue` - Queue existing job

```python
@click.command()
@click.option('--name', '-n', required=True, help='Job name to queue')
@click.option('--priority', default=1, help='Job priority')
@click.option('--interactive/--no-interactive', default=True,
              help='Interactive pen mapping for multi-pen designs')
@vpype_cli.global_processor  
def plotty_queue(document, name, priority, interactive):
    """Queue existing ploTTY job for plotting."""
    try:
        # Initialize ploTTY integration
        plotty = PlottyIntegration()
        
        # Queue the job with specified priority
        plotty.queue_job(name, priority)
        
        click.echo(f"✓ Queued job '{name}' with priority {priority}")
        
        # Interactive pen mapping for multi-pen designs
        if interactive and len(document.layers) > 1:
            _interactive_pen_mapping(document, name)
            
        return document
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.ClickException(str(e))


def _interactive_pen_mapping(document: Document, job_name: str) -> None:
    """Interactive pen mapping for multi-pen designs."""
    plotty = PlottyIntegration()
    
    click.echo(f"\n🖊️  Interactive Pen Mapping for '{job_name}'")
    click.echo(f"Found {len(document.layers)} layers with {len(document.layer_ids)} unique pens")
    
    # Get current pen assignments from document
    current_pens = {}
    for layer_id in document.layer_ids:
        layer = document.layers[layer_id]
        pen_color = layer.properties.get("pen_color", "black")
        current_pens[layer_id] = pen_color
    
    # Display current mapping
    click.echo("\nCurrent pen assignments:")
    for layer_id, pen_color in current_pens.items():
        click.echo(f"  Layer {layer_id}: {pen_color}")
    
    # Interactive mapping
    click.echo("\nAvailable pen colors: black, red, blue, green, yellow")
    click.echo("Enter new pen color for each layer (press Enter to keep current):")
    
    new_pens = {}
    for layer_id in document.layer_ids:
        current = current_pens.get(layer_id, "black")
        new_color = click.prompt(f"Layer {layer_id} pen", default=current, 
                                type=click.Choice(['black', 'red', 'blue', 'green', 'yellow']))
        new_pens[layer_id] = new_color
        
        # Update layer property
        layer = document.layers[layer_id]
        layer.properties["pen_color"] = new_color
    
    # Save updated pen mapping
    pen_mapping_path = plotty.workspace / f"{job_name}_pen_mapping.yaml"
    import yaml
    with open(pen_mapping_path, 'w') as f:
        yaml.dump(new_pens, f)
    
    click.echo(f"\n✓ Pen mapping saved to {pen_mapping_path}")
```

**Features:**
- Queue existing ploTTY jobs by name
- **Interactive pen mapping for multi-layer designs** with color selection
- Priority-based queuing with validation
- Status feedback and time estimation
- Pen mapping persistence in YAML format

### 3. `plotty-status` - Check job status

```python
@click.command()
@click.option('--name', '-n', help='Specific job name (shows all if omitted)')
@click.option('--format', 'output_format', default='table',
              type=click.Choice(['table', 'json', 'simple']),
              help='Output format')
@vpype_cli.global_processor
def plotty_status(document, name, output_format):
    """Check ploTTY job status."""
    pass
```

**Features:**
- Show status for specific job or all jobs
- Multiple output formats (table, JSON, simple)
- Queue position and estimated time
- Real-time updates

### 4. `plotty-list` - List ploTTY jobs

```python
@click.command()
@click.option('--state', help='Filter by job state')
@click.option('--format', 'output_format', default='table',
              type=click.Choice(['table', 'json', 'csv']),
              help='Output format')
@click.option('--limit', type=int, help='Limit number of jobs')
@vpype_cli.global_processor
def plotty_list(document, state, output_format, limit):
    """List ploTTY jobs."""
    pass
```

**Features:**
- Filter by job state (queued, ready, plotting, completed)
- Multiple output formats
- Pagination support
- Sorting options

## Implementation Details

### ploTTY Integration (`database.py`)

```python
class PlottyIntegration:
    """Handles integration with ploTTY system."""
    
    def __init__(self, workspace_path=None):
        self.workspace = self._detect_workspace(workspace_path)
        self.config = self._load_config()
        self.db_session = None
        
    def _detect_workspace(self, workspace_path):
        """Detect ploTTY workspace directory."""
        if workspace_path:
            return Path(workspace_path)
            
        # Check XDG directories
        from platformdirs import user_data_dir
        xdg_path = Path(user_data_dir("plotty"))
        if xdg_path.exists():
            return xdg_path
            
        # Check current directory
        current = Path.cwd() / "plotty-workspace"
        if current.exists():
            return current
            
        # Check home directory
        home = Path.home() / "plotty-workspace"
        if home.exists():
            return home
            
        raise PlottyNotFoundError("ploTTY workspace not found")
    
    def _load_config(self):
        """Load ploTTY configuration."""
        try:
            from plotty.config import load_config
            return load_config(self.workspace)
        except ImportError:
            # ploTTY not installed, use defaults
            return self._default_config()
    
    def add_job(self, document, name, preset, paper):
        """Add job to ploTTY system."""
        if self._plotty_available():
            return self._add_job_plotty(document, name, preset, paper)
        else:
            return self._add_job_standalone(document, name, preset, paper)
    
    def _plotty_available(self):
        """Check if ploTTY is available."""
        try:
            import plotty
            import plotty.fsm
            import plotty.models
            return True
        except ImportError:
            return False
            
    def delete_job(self, name: str) -> None:
        """Delete a job from ploTTY system."""
        job_path = self.jobs_dir / name
        if job_path.exists():
            import shutil
            shutil.rmtree(job_path)
        else:
            raise PlottyJobError(f"Job '{name}' not found")
            
    def queue_job(self, name: str, priority: int = 1) -> None:
        """Queue an existing job for plotting."""
        job_data = self.get_job_status(name)
        if job_data:
            job_data["state"] = "QUEUED"
            job_data["priority"] = priority
            job_data["queued_at"] = datetime.now(timezone.utc).isoformat()
            self._save_job_metadata(name, job_data)
        else:
            raise PlottyJobError(f"Job '{name}' not found")
            
    def _save_job_metadata(self, name: str, job_data: dict) -> None:
        """Save job metadata to JSON file."""
        job_path = self.jobs_dir / name
        job_json_path = job_path / "job.json"
        with open(job_json_path, "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=2)
```

### Configuration Detection (`config.py`)

```python
class PlottyConfig:
    """ploTTY configuration detection and management."""
    
    def __init__(self, workspace_path=None):
        self.workspace_path = self._find_workspace(workspace_path)
        self.config_path = self.workspace_path / "config.yaml"
        self.vpype_presets_path = self.workspace_path / "vpype-presets.yaml"
        
    def _find_workspace(self, workspace_path):
        """Find ploTTY workspace using multiple strategies."""
        candidates = [
            Path(workspace_path) if workspace_path else None,
            Path.cwd() / "plotty-workspace",
            Path.home() / "plotty-workspace",
            Path.home() / ".local" / "share" / "plotty",
        ]
        
        for candidate in candidates:
            if candidate and candidate.exists():
                return candidate
                
        # Create default workspace if none found
        default = Path.home() / "plotty-workspace"
        default.mkdir(parents=True, exist_ok=True)
        return default
    
    def load_config(self):
        """Load ploTTY configuration."""
        if self.config_path.exists():
            import yaml
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return self._default_config()
    
    def _default_config(self):
        """Default ploTTY configuration."""
        return {
            "workspace": str(self.workspace_path),
            "vpype": {
                "preset": "fast",
                "presets_file": str(self.vpype_presets_path)
            },
            "paper": {
                "default_size": "A4",
                "default_margin_mm": 10.0
            }
        }
```

### Utilities (`utils.py`)

```python
def save_document_for_plotty(document, job_path, name):
    """Save vpype document as ploTTY-compatible job."""
    # Ensure job directory exists
    job_path.mkdir(parents=True, exist_ok=True)
    
    # Save optimized SVG
    svg_path = job_path / "src.svg"
    document.save(svg_path)
    
    # Create job metadata
    job_data = {
        "id": name,
        "name": name,
        "paper": "A4",
        "state": "NEW",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "created_by": "vpype-plotty",
            "source": "vpype document"
        }
    }
    
    # Save job.json
    job_json_path = job_path / "job.json"
    with open(job_json_path, 'w') as f:
        json.dump(job_data, f, indent=2)
    
    return svg_path, job_json_path

def generate_job_name(document, fallback_name=None):
    """Generate job name from document metadata."""
    # Try to extract name from document properties
    if hasattr(document, 'properties') and 'name' in document.properties:
        return document.properties['name']
    
    # Use fallback name or generate timestamp-based name
    if fallback_name:
        return fallback_name
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"vpype_job_{timestamp}"

def validate_preset(preset):
    """Validate optimization preset."""
    valid_presets = ['fast', 'default', 'hq']
    if preset not in valid_presets:
        raise click.BadParameter(
            f"Invalid preset '{preset}'. Valid options: {', '.join(valid_presets)}"
        )
    return preset
```

### Custom Exceptions (`exceptions.py`)

```python
class PlottyError(Exception):
    """Base exception for vpype-plotty."""
    pass

class PlottyNotFoundError(PlottyError):
    """ploTTY installation or workspace not found."""
    pass

class PlottyConfigError(PlottyError):
    """ploTTY configuration error."""
    pass

class PlottyJobError(PlottyError):
    """Job creation or management error."""
    pass
```

## Installation Configuration

### `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=75", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "vpype-plotty"
version = "0.1.0"
description = "vpype plugin for ploTTY plotter management integration"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [
    {name = "ploTTY Contributors", email = "plotty@example.com"}
]
keywords = ["plotter", "vpype", "plotty", "axidraw", "generative-art"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Artistic",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Artistic Software",
    "Topic :: Multimedia :: Graphics",
]

dependencies = [
    "vpype>=1.14.0",
    "click>=8.0.0",
    "pydantic>=2.0",
    "platformdirs>=4.0.0",
    "pyyaml>=6.0.2",
]

# Optional ploTTY integration
[project.optional-dependencies]
plotty = ["plotty>=1.0.0"]
dev = [
    "pytest>=8.3.2",
    "pytest-cov>=4.0.0",
    "black>=24.10.0",
    "ruff>=0.6.8",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/your-org/vpype-plotty"
Documentation = "https://github.com/your-org/vpype-plotty/docs"
Repository = "https://github.com/your-org/vpype-plotty"
"Bug Tracker" = "https://github.com/your-org/vpype-plotty/issues"

[project.entry-points."vpype.plugins"]
plotty-add = "vpype_plotty.commands:plotty_add"
plotty-queue = "vpype_plotty.commands:plotty_queue"
plotty-status = "vpype_plotty.commands:plotty_status"
plotty-list = "vpype_plotty.commands:plotty_list"

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=vpype_plotty --cov-report=html --cov-report=term-missing"
```

## Usage Examples

### vsketch Integration

```python
import vsketch

class MySketch(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")
        
        # Your generative art code here
        for i in range(10):
            vsk.circle(i * 2, i * 2, radius=1)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        # Standard vpype optimization
        vsk.vpype("linemerge linesimplify reloop linesort")
        
        # Add to ploTTY with high-quality preset
        vsk.vpype("plotty-add --name my_design --preset hq --queue")

if __name__ == "__main__":
    MySketch().display()
```

### Standalone vpype Usage

```bash
# Create generative art and add to ploTTY
vpype rand --seed 123 plotty-add --name random_art --preset fast

# Add existing SVG to ploTTY
vpype read input.svg plotty-add --name existing_design --paper A3

# Queue existing job
vpype plotty-queue --name my_design --priority 2

# Check job status
vpype plotty-status --name my_design

# List all queued jobs
vpype plotty-list --state queued --format table
```

### Batch Processing

```python
# Batch processing script
import subprocess
import time

def generate_and_queue_sketches(seeds, base_name):
    """Generate multiple sketches and queue them all."""
    job_ids = []
    
    for seed in seeds:
        # Generate sketch
        cmd = f"vsk run --seed {seed} {base_name} --save-only"
        subprocess.run(cmd, shell=True)
        
        # Add to ploTTY
        cmd = f"vpype read output/{base_name}_{seed}.svg plotty-add --name {base_name}_{seed} --queue"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            job_id = result.stdout.strip()
            job_ids.append(job_id)
            print(f"✓ Queued job {job_id} for seed {seed}")
        else:
            print(f"✗ Failed to queue seed {seed}: {result.stderr}")
    
    return job_ids

# Generate and queue 10 variants
job_ids = generate_and_queue_sketches(range(10), "my_sketch")
print(f"Queued jobs: {', '.join(job_ids)}")
```

## Development Workflow

### Phase 1: Core Infrastructure (Week 1)
1. **Repository setup**
   - Create repository structure
   - Configure CI/CD pipeline
   - Set up development environment

2. **Basic integration**
   - Implement ploTTY detection
   - Create configuration management
   - Build utility functions

3. **First command**
   - Implement `plotty-add` basic functionality
   - Add standalone mode support
   - Create basic tests

### Phase 2: Full Command Set (Week 2)
1. **Complete command suite**
   - Implement `plotty-queue`
   - Implement `plotty-status`
   - Implement `plotty-list`

2. **Enhanced integration**
   - Full ploTTY FSM integration
   - Interactive pen mapping
   - Error handling and validation

3. **Testing**
   - Comprehensive test suite
   - Integration tests with ploTTY
   - Mock tests for standalone mode

### Phase 3: Polish and Documentation (Week 3)
1. **Documentation**
   - Complete README and usage docs
   - Add examples and tutorials
   - Create troubleshooting guide

2. **Release preparation**
   - Package configuration
   - Installation testing
   - Version tagging and release

## Testing Strategy

### Unit Tests
```python
# tests/test_config.py
def test_workspace_detection():
    """Test ploTTY workspace detection."""
    # Test various workspace configurations
    pass

def test_config_loading():
    """Test ploTTY configuration loading."""
    # Test config file parsing and defaults
    pass

# tests/test_commands.py
def test_plotty_add():
    """Test plotty-add command."""
    # Test with and without ploTTY integration
    pass
```

### Integration Tests
```python
# tests/test_integration.py
def test_full_workflow():
    """Test complete vsketch → ploTTY workflow."""
    # Create test vsketch document
    # Add to ploTTY via plugin
    # Verify job creation and queuing
    pass
```

### End-to-End Tests
```python
# tests/test_e2e.py
def test_vsketch_to_plotting():
    """Test complete workflow from vsketch to plotting."""
    # Requires actual ploTTY installation
    # Test with real AxiDraw hardware if available
    pass
```

## Release Plan

### Version 0.1.0 (MVP)
- Basic `plotty-add` command
- ploTTY detection and configuration
- Standalone mode support
- Core documentation

### Version 0.2.0 (Enhanced)
- Complete command suite (`queue`, `status`, `list`)
- Interactive pen mapping
- Batch processing support
- Comprehensive examples

### Version 0.3.0 (Polish)
- Advanced error handling
- Performance optimizations
- Full test coverage
- Integration with vsketch examples

## Installation Instructions

### For vsketch Users
```bash
# Install plugin into vsketch
pipx inject vsketch vpype-plotty

# Verify installation
vsk --help | grep plotty
```

### For vpype Users
```bash
# Install plugin into vpype
pipx inject vpype vpype-plotty

# Verify installation
vpype --help | grep plotty
```

### Development Installation
```bash
# Clone repository
git clone https://github.com/your-org/vpype-plotty.git
cd vpype-plotty

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Install into local vpype/vsketch for testing
pipx inject vpype -e .
```

## Contributing Guidelines

1. **Code Style**: Follow ploTTY's conventions (Black, Ruff)
2. **Testing**: Maintain >90% test coverage
3. **Documentation**: Update docs for all new features
4. **Compatibility**: Support ploTTY 1.0+ and vpype 1.14+
5. **Issues**: Use GitHub issues with clear reproduction steps

## Future Enhancements

### Version 0.4.0
- Real-time job monitoring
- Advanced pen mapping algorithms
- Integration with other creative tools
- Plugin configuration system

### Version 0.5.0
- Multi-workspace support
- Job templates and presets
- Performance analytics
- Cloud ploTTY integration

This implementation plan provides a solid foundation for creating the vpype-plotty plugin while maintaining flexibility for future enhancements and community contributions.