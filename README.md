# vpype-plotty

[![PyPI version](https://img.shields.io/pypi/v/vpype-plotty.svg)](https://pypi.org/project/vpype-plotty/)
[![Python versions](https://img.shields.io/pypi/pyversions/vpype-plotty.svg)](https://pypi.org/project/vpype-plotty/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**vpype-plotty** is a vpype plugin that bridges creative tools (vsketch, vpype) with [ploTTY](https://github.com/bkuri/plotty)'s production plotter management system. It enables seamless workflow from generative art creation to professional plotter job management.

## Features

- 🎨 **Seamless Integration**: Works directly with vpype and vsketch workflows
- 🚀 **Quick Job Creation**: Add documents to ploTTY with a single command
- 📊 **Job Management**: Queue, monitor, and list plotter jobs
- 🎯 **Optimization Presets**: Fast, default, and high-quality optimization settings
- 📄 **Multiple Formats**: Support for various paper sizes and output formats
- 🔧 **Standalone Mode**: Works with or without ploTTY installation
- 📈 **Status Tracking**: Real-time job status and queue position monitoring

## Installation

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
git clone https://github.com/bkuri/vpype-plotty.git
cd vpype-plotty

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Quick Start

### Basic Usage

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

## Commands

### `plotty-add` - Add document to ploTTY

```bash
vpype plotty-add [OPTIONS]
```

**Options:**
- `--name, -n`: Job name (defaults to auto-generated)
- `--preset, -p`: Optimization preset (fast, default, hq)
- `--paper`: Paper size (default: A4)
- `--queue/--no-queue`: Automatically queue job after adding
- `--workspace`: ploTTY workspace path

**Example:**
```bash
vpype read design.svg plotty-add --name my_design --preset hq --queue
```

### `plotty-queue` - Queue existing job

```bash
vpype plotty-queue [OPTIONS]
```

**Options:**
- `--name, -n`: Job name to queue (required)
- `--priority`: Job priority (default: 1)
- `--interactive/--no-interactive`: Interactive pen mapping
- `--workspace`: ploTTY workspace path

**Example:**
```bash
vpype plotty-queue --name my_design --priority 2
```

### `plotty-status` - Check job status

```bash
vpype plotty-status [OPTIONS]
```

**Options:**
- `--name, -n`: Specific job name (shows all if omitted)
- `--format`: Output format (table, json, simple)
- `--workspace`: ploTTY workspace path

**Example:**
```bash
vpype plotty-status --name my_design --format json
```

### `plotty-list` - List ploTTY jobs

```bash
vpype plotty-list [OPTIONS]
```

**Options:**
- `--state`: Filter by job state
- `--format`: Output format (table, json, csv)
- `--limit`: Limit number of jobs
- `--workspace`: ploTTY workspace path

**Example:**
```bash
vpype plotty-list --state queued --format table --limit 10
```

## Configuration

vpype-plotty automatically detects ploTTY workspace locations in the following order:

1. Explicit `--workspace` parameter
2. `./plotty-workspace` (current directory)
3. `~/plotty-workspace` (home directory)
4. XDG data directory (`~/.local/share/plotty`)

If no workspace is found, a default one is created in `~/plotty-workspace`.

### Default Configuration

```yaml
workspace: "/home/user/plotty-workspace"
vpype:
  preset: "fast"
  presets_file: "/home/user/plotty-workspace/vpype-presets.yaml"
paper:
  default_size: "A4"
  default_margin_mm: 10.0
```

## Optimization Presets

- **fast**: Quick optimization for testing and drafts
- **default**: Balanced optimization for general use
- **hq**: High-quality optimization for final output

## ploTTY Integration

vpype-plotty works seamlessly with [ploTTY](https://github.com/bkuri/plotty), the professional plotter management system:

- **Full Integration**: When ploTTY is installed, uses its FSM and database
- **Standalone Mode**: Works without ploTTY for basic job management
- **Job Metadata**: Preserves creation info, presets, and optimization settings
- **Queue Management**: Integrates with ploTTY's priority-based queuing system

## Examples

### Batch Processing

```python
# Batch processing script
import subprocess

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
    
    return job_ids

# Generate and queue 10 variants
job_ids = generate_and_queue_sketches(range(10), "my_sketch")
print(f"Queued jobs: {', '.join(job_ids)}")
```

### Multi-Pen Workflow

```bash
# Create design with multiple layers
vpype read layer1.svg read layer2.svg \
    linemerge linesimplify reloop linesort \
    plotty-add --name multi_pen_design --preset hq

# Queue with interactive pen mapping
vpype plotty-queue --name multi_pen_design --interactive
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vpype_plotty --cov-report=html

# Run specific test
pytest tests/test_commands.py::test_plotty_add_basic
```

### Code Quality

```bash
# Format code
black .
ruff format .

# Lint code
ruff check .
mypy vpype_plotty/
```

## Contributing

1. **Code Style**: Follow Black and Ruff conventions
2. **Testing**: Maintain >90% test coverage
3. **Documentation**: Update docs for all new features
4. **Compatibility**: Support ploTTY 1.0+ and vpype 1.14+
5. **Issues**: Use GitHub issues with clear reproduction steps

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [vpype-plotty Repository](https://github.com/bkuri/vpype-plotty)
- [ploTTY Plotter Management](https://github.com/bkuri/plotty)
- [vpype Vector Graphics Pipeline](https://github.com/abey79/vpype)
- [vsketch Generative Art Framework](https://github.com/abey79/vsketch)

## Changelog

### v0.1.0 (Initial Release)
- Basic `plotty-add` command
- ploTTY detection and configuration
- Standalone mode support
- Core documentation and examples