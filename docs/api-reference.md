# API Reference

This document provides technical reference for vpype-plotty commands, functions, and configuration options.

## Table of Contents

1. [Commands](#commands)
2. [Configuration Options](#configuration-options)
3. [Exception Types](#exception-types)
4. [Data Structures](#data-structures)
5. [Environment Variables](#environment-variables)

## Commands

### plotty-add

Add current vpype document to ploTTY job system.

#### Syntax
```bash
vpype plotty-add [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|-------|---------|-------------|
| `--name` | `-n` | string | auto-generated | Job name |
| `--preset` | `-p` | choice | `default` | Optimization preset (`fast`, `default`, `hq`) |
| `--paper` | | string | `A4` | Paper size (A4, A3, Letter, or custom) |
| `--queue` | | flag | `False` | Automatically queue job after adding |
| `--no-queue` | | flag | `True` | Don't automatically queue job |
| `--workspace` | | path | auto-detected | ploTTY workspace path |

#### Examples
```bash
# Basic usage
vpype plotty-add --name my_design

# With preset and auto-queue
vpype plotty-add --name test --preset hq --queue

# Custom paper size
vpype plotty-add --name large --paper A3 --preset default

# Custom workspace
vpype --workspace /path/to/workspace plotty-add --name test
```

#### Return Values

**Success**: Returns job name and metadata
```
✓ Added job 'my_design' to ploTTY
Job ID: my_design
Preset: default
Paper: A4
Created: 2025-11-12T10:30:00Z
```

**Error**: Returns descriptive error message with recovery hint
```
✗ Error: ploTTY installation or workspace not found
Recovery: Install ploTTY or specify --workspace /path/to/workspace
```

### plotty-queue

Queue existing ploTTY job for plotting.

#### Syntax
```bash
vpype plotty-queue [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|-------|---------|-------------|
| `--name` | `-n` | string | **required** | Job name to queue |
| `--priority` | | integer | `1` | Job priority (1-10, higher = more urgent) |
| `--interactive` | | flag | `True` | Enable interactive pen mapping |
| `--no-interactive` | | flag | `False` | Disable interactive pen mapping |
| `--workspace` | | path | auto-detected | ploTTY workspace path |

#### Examples
```bash
# Queue with default priority
vpype plotty-queue --name my_design

# High priority job
vpype plotty-queue --name urgent --priority 10

# Multi-pen design with interactive mapping
vpype plotty-queue --name colorful --interactive
```

#### Interactive Pen Mapping

When `--interactive` is enabled and design has multiple layers:

```
🖊️  Interactive Pen Mapping for 'colorful_design'

Layer 1 (background): 15 paths, black
Available pens: 1 (black), 2 (red), 3 (blue), 4 (green)
Enter pen number for layer 1 [1]: 1

Layer 2 (foreground): 8 paths, red  
Available pens: 1 (black), 2 (red), 3 (blue), 4 (green)
Enter pen number for layer 2 [2]: 3

✅ Pen mapping saved to colorful_design_pen_mapping.yaml
✅ Queued job 'colorful_design' with priority 1
```

### plotty-status

Check job status and details.

#### Syntax
```bash
vpype plotty-status [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|-------|---------|-------------|
| `--name` | `-n` | string | `None` | Specific job name (shows all if omitted) |
| `--format` | | choice | `table` | Output format (`table`, `json`, `simple`) |
| `--workspace` | | path | auto-detected | ploTTY workspace path |

#### Output Formats

**Table Format** (default):
```
┌─────────────────┬─────────┬──────────┬─────────────┬────────────┐
│ Name           │ State   │ Priority │ Created     │ Duration   │
├─────────────────┼─────────┼──────────┼─────────────┼────────────┤
│ my_design      │ queued  │ 1        │ 2m ago      │ -          │
│ test_circle    │ running │ 5        │ 5m ago      │ 3m 15s     │
│ completed_job  │ completed│ 1        │ 1h ago      │ 12m 30s    │
└─────────────────┴─────────┴──────────┴─────────────┴────────────┘
```

**JSON Format**:
```json
{
  "name": "my_design",
  "state": "queued",
  "priority": 1,
  "created_at": "2025-11-12T10:30:00Z",
  "started_at": null,
  "completed_at": null,
  "duration_seconds": null,
  "metadata": {
    "preset": "hq",
    "paper": "A4",
    "path_count": 42,
    "layer_count": 3,
    "file_size_bytes": 15420
  }
}
```

**Simple Format**:
```
my_design: queued (priority 1, created 2m ago)
test_circle: running (priority 5, created 5m ago, duration 3m 15s)
```

### plotty-list

List ploTTY jobs with filtering and sorting options.

#### Syntax
```bash
vpype plotty-list [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|-------|---------|-------------|
| `--state` | | string | `None` | Filter by job state (`queued`, `running`, `completed`, `failed`) |
| `--format` | | choice | `table` | Output format (`table`, `json`, `csv`) |
| `--limit` | | integer | `None` | Maximum number of jobs to show |
| `--workspace` | | path | auto-detected | ploTTY workspace path |

#### Filtering Examples

```bash
# Only queued jobs
vpype plotty-list --state queued

# Only completed jobs from today
vpype plotty-list --state completed --limit 10

# Export to CSV
vpype plotty-list --format csv > jobs_backup.csv

# JSON for scripts
vpype plotty-list --format json | jq '.[] | select(.state == "failed")'
```

## Configuration Options

### Workspace Configuration

Located at `<workspace>/config.yaml`:

```yaml
# ploTTY workspace configuration
workspace: "/home/user/plotty-workspace"

# Plotter hardware settings
plotter:
  type: "axidraw"           # Plotter type
  port: "/dev/ttyUSB0"       # Device port
  speed: 50                  # Drawing speed (1-100)
  acceleration: 75           # Acceleration (1-100)
  pen_height_up: 60           # Pen up height
  pen_height_down: 40        # Pen down height

# Job management settings
jobs:
  default_priority: 1         # Default job priority
  max_concurrent: 1          # Max concurrent jobs
  auto_cleanup: true          # Auto-cleanup old jobs
  cleanup_after_days: 30      # Cleanup jobs older than
  keep_states: ["completed", "failed"]  # States to keep

# Logging configuration
logging:
  level: "INFO"              # Log level (DEBUG, INFO, WARNING, ERROR)
  file: "logs/plotty.log"    # Log file path
  max_size: "10MB"          # Max log file size
  backup_count: 5            # Number of backup logs
```

### vpype-plotty Configuration

```yaml
# vpype-plotty specific settings
vpype:
  default_preset: "default"           # Default optimization preset
  presets_file: "vpype-presets.yaml" # Custom presets file
  auto_optimize: true                 # Auto-optimize designs
  
paper:
  default_size: "A4"                 # Default paper size
  default_margin_mm: 10.0            # Default margin in mm
  custom_sizes:                      # Custom paper size aliases
    postcard: "148x105mm"
    business_card: "90x54mm"
    banner: "1200x300mm"

# Pen mapping settings
pen_mapping:
  auto_save: true                    # Auto-save pen mappings
  default_colors:                    # Default pen colors
    - "black"
    - "red" 
    - "blue"
    - "green"
    - "yellow"
  mapping_file: "pen_mapping.yaml"   # Default mapping file
```

### Custom Presets

Located at `<workspace>/vpype-presets.yaml`:

```yaml
presets:
  preset_name:
    linemerge:
      tolerance: "0.05mm"           # Merge tolerance
      max_distance: "1.0mm"         # Max merge distance
    linesimplify:
      tolerance: "0.02mm"           # Simplification tolerance
      preserve_topology: true         # Preserve path topology
    reloop: true                    # Ensure closed loops
    linesort: true                   # Optimize path order
    filter_small_paths:
      enabled: true                  # Filter tiny paths
      min_length: "0.3mm"          # Minimum path length
    reduce_lifts:
      enabled: true                  # Reduce pen lifts
      max_lift_distance: "2.0mm"    # Max distance without lift
```

## Exception Types

### Base Exception

```python
class PlottyError(Exception):
    """Base exception for vpype-plotty."""
    
    def __init__(self, message: str, recovery_hint: Optional[str] = None, retry_after: Optional[float] = None):
        super().__init__(message)
        self.recovery_hint = recovery_hint
        self.retry_after = retry_after
```

### Specific Exceptions

#### PlottyNotFoundError
```python
class PlottyNotFoundError(PlottyError):
    """ploTTY installation or workspace not found."""
    
    def __init__(self, message: str, workspace_path: Optional[str] = None):
        recovery_hint = f"Check ploTTY installation at {workspace_path}" if workspace_path else "Verify ploTTY is properly installed"
        super().__init__(message, recovery_hint)
```

#### PlottyConnectionError
```python
class PlottyConnectionError(PlottyError):
    """Connection or communication error with ploTTY."""
    
    def __init__(self, message: str, retry_after: float = 5.0):
        super().__init__(message, "Check ploTTY is running and accessible", retry_after)
```

#### PlottyTimeoutError
```python
class PlottyTimeoutError(PlottyError):
    """Operation timeout error."""
    
    def __init__(self, message: str, timeout_seconds: float):
        super().__init__(message, f"Increase timeout or check ploTTY performance", timeout_seconds)
```

#### PlottyJobError
```python
class PlottyJobError(PlottyError):
    """Job creation or management error."""
    
    def __init__(self, message: str, job_id: Optional[str] = None):
        recovery_hint = f"Check job status with: plotty-status {job_id}" if job_id else "Verify job parameters and ploTTY status"
        super().__init__(message, recovery_hint)
```

## Data Structures

### Job Metadata

```python
@dataclass
class JobMetadata:
    name: str                           # Job name
    state: JobState                      # Current state
    priority: int                       # Priority level (1-10)
    created_at: datetime                 # Creation timestamp
    started_at: Optional[datetime]       # Start timestamp
    completed_at: Optional[datetime]      # Completion timestamp
    duration_seconds: Optional[float]      # Duration in seconds
    
    # Design metadata
    preset: str                         # Optimization preset used
    paper: str                         # Paper size
    path_count: int                     # Number of paths
    layer_count: int                    # Number of layers
    file_size_bytes: int                 # File size in bytes
    
    # ploTTY metadata
    plotter_id: Optional[str]           # Assigned plotter
    queue_position: Optional[int]         # Position in queue
    error_message: Optional[str]         # Error message if failed
```

### Job States

```python
class JobState(Enum):
    CREATED = "created"         # Job created in system
    QUEUED = "queued"          # Ready to plot
    RUNNING = "running"        # Currently plotting
    COMPLETED = "completed"    # Successfully plotted
    FAILED = "failed"          # Error during plotting
    CANCELLED = "cancelled"    # Cancelled by user
```

### Pen Mapping

```python
@dataclass
class PenMapping:
    job_name: str                      # Job name
    layers: List[LayerMapping]          # Layer mappings
    created_at: datetime                # Creation timestamp
    file_path: str                     # Mapping file path

@dataclass
class LayerMapping:
    layer_index: int                   # Layer index
    layer_name: str                   # Layer name
    pen_number: int                   # Assigned pen (1-based)
    color: Optional[str]               # Detected color
    path_count: int                   # Number of paths in layer
```

## Environment Variables

### ploTTY Variables

```bash
# Workspace location
export PLOTTY_WORKSPACE=~/my-plotty-workspace

# Configuration file
export PLOTTY_CONFIG=~/my-config.yaml

# Log level
export PLOTTY_LOG_LEVEL=DEBUG
```

### vpype-plotty Variables

```bash
# Debug mode
export VPYPE_PLOTTY_DEBUG=1

# Custom config file
export VPYPE_PLOTTY_CONFIG=~/vpype-plotty-config.yaml

# Log level
export VPYPE_PLOTTY_LOG_LEVEL=DEBUG

# Default workspace
export VPYPE_PLOTTY_WORKSPACE=~/default-workspace
```

### Shell Aliases

```bash
# Common aliases
alias pp-add='vpype plotty-add'
alias pp-queue='vpype plotty-queue'
alias pp-status='vpype plotty-status'
alias pp-list='vpype plotty-list --format table'

# Development aliases
alias pp-test='vpype --debug plotty-add --name test'
alias pp-jobs='vpype plotty-list --format json | jq .'
```

## Error Codes

### Exit Codes

| Code | Meaning | Description |
|-------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | General Error | Generic error occurred |
| 2 | Usage Error | Invalid command line arguments |
| 3 | Configuration Error | Invalid configuration |
| 4 | Connection Error | Cannot connect to ploTTY |
| 5 | Job Error | Job operation failed |
| 6 | Timeout Error | Operation timed out |
| 7 | Permission Error | Insufficient permissions |
| 8 | Resource Error | Resource exhaustion |

### Recovery Actions

Each error includes suggested recovery action:

```bash
# Example error with recovery
Error: Job 'my_design' not found
Recovery: Check job name with: vpype plotty-list
Exit code: 5

# Example timeout with retry
Error: Connection timeout after 30 seconds
Recovery: Check ploTTY is running and accessible
Retry after: 5.0 seconds
Exit code: 6
```

---

**← [Troubleshooting](troubleshooting.md) | [Configuration](configuration.md) →**