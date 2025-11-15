# Configuration Guide

This guide covers vpype-vfab configuration, workspace management, and customization options.

## Table of Contents

1. [Workspace Setup](#workspace-setup)
2. [vfab Configuration](#plotty-configuration)
3. [Presets and Optimization](#presets-and-optimization)
4. [Paper Sizes](#paper-sizes)
5. [Environment Variables](#environment-variables)
6. [Advanced Configuration](#advanced-configuration)

## Workspace Setup

### Automatic Workspace Detection

vpype-vfab automatically detects vfab workspaces in this order:

1. **Explicit `--workspace` parameter**
2. `./vfab-workspace` (current directory)
3. `~/vfab-workspace` (home directory)
4. XDG data directory (`~/.local/share/plotty`)

### Creating a Workspace

```bash
# Method 1: Use vfab (recommended)
vfab init --workspace ~/my-vfab-workspace

# Method 2: Manual creation
mkdir ~/my-vfab-workspace
cd ~/my-vfab-workspace
mkdir jobs logs state

# Method 3: Let vpype-vfab create it
vpype --workspace ~/new-workspace vfab-add --name test
```

### Workspace Structure

```
~/vfab-workspace/
├── jobs/                    # Job files and metadata
│   ├── job_name/
│   │   ├── design.svg       # Original design
│   │   ├── optimized.svg    # Optimized version
│   │   ├── job.json        # Job metadata
│   │   └── pen_mapping.yaml # Pen assignments (if multi-pen)
├── config.yaml             # vfab configuration
├── logs/                   # Operation logs
│   ├── plotty.log
│   └── jobs.log
└── state/                  # vfab state files
    ├── queue.json
    └── plotter_state.json
```

### Using Multiple Workspaces

```bash
# Project-specific workspace
vpype --workspace ./project-workspace vfab-add --name project_design

# Temporary workspace
vpype --workspace /tmp/test-workspace vfab-add --name test

# Environment variable
export PLOTTY_WORKSPACE=~/client-workspace
vpype vfab-add --name client_design
```

## vfab Configuration

### Basic Configuration

vfab uses `config.yaml` in the workspace root:

```yaml
# vfab configuration
workspace: "/home/user/vfab-workspace"

# Plotter settings
plotter:
  type: "axidraw"
  port: "/dev/ttyUSB0"
  speed: 50
  acceleration: 75

# Job settings
jobs:
  default_priority: 1
  max_concurrent: 1
  auto_cleanup: true
  cleanup_after_days: 30

# Logging
logging:
  level: "INFO"
  file: "logs/plotty.log"
  max_size: "10MB"
  backup_count: 5
```

### vpype-vfab Specific Settings

Add vpype-vfab configuration to the same file:

```yaml
# vpype-vfab configuration
vpype:
  default_preset: "default"
  presets_file: "vpype-presets.yaml"
  auto_optimize: true
  
paper:
  default_size: "A4"
  default_margin_mm: 10.0
  custom_sizes:
    postcard: "148x105mm"
    banner: "1200x300mm"

# Pen mapping settings
pen_mapping:
  auto_save: true
  default_colors:
    - "black"
    - "red" 
    - "blue"
    - "green"
    - "yellow"
```

### Creating Custom Presets

Create `vpype-presets.yaml` in your workspace:

```yaml
# Custom optimization presets
presets:
  # Ultra-fast for testing
  ultra_fast:
    linemerge:
      tolerance: "0.2mm"
    linesimplify:
      tolerance: "0.1mm"
    reloop: true
    linesort: true
    
  # Detailed for complex art
  detailed:
    linemerge:
      tolerance: "0.01mm"
    linesimplify:
      tolerance: "0.005mm"
    reloop: true
    linesort: true
    filter_small_paths:
      min_length: "0.5mm"
      
  # Heavy paper optimization
  heavy_paper:
    linemerge:
      tolerance: "0.05mm"
    linesimplify:
      tolerance: "0.02mm"
    reloop: true
    linesort: true
    reduce_lifts: true
    
  # Draft mode (maximum speed)
  draft:
    linemerge:
      tolerance: "0.5mm"
    linesimplify:
      tolerance: "0.3mm"
    reloop: false
    linesort: false
```

Use custom presets:

```bash
vpype vfab-add --name design --preset ultra_fast
vpype vfab-add --name detailed_art --preset detailed
```

## Presets and Optimization

### Built-in Presets

#### Fast Preset
```yaml
fast:
  linemerge:
    tolerance: "0.1mm"
  linesimplify:
    tolerance: "0.05mm"
  reloop: true
  linesort: true
```
**Use Case**: Testing, drafts, iterations
**Speed**: ⚡ Very Fast
**Quality**: Good

#### Default Preset
```yaml
default:
  linemerge:
    tolerance: "0.05mm"
  linesimplify:
    tolerance: "0.02mm"
  reloop: true
  linesort: true
```
**Use Case**: General use, balanced approach
**Speed**: 🚀 Moderate
**Quality**: Better

#### High-Quality Preset
```yaml
hq:
  linemerge:
    tolerance: "0.02mm"
  linesimplify:
    tolerance: "0.01mm"
  reloop: true
  linesort: true
  filter_small_paths:
    min_length: "0.3mm"
```
**Use Case**: Final output, client work
**Speed**: 🐢 Slow
**Quality**: Best

### Optimization Parameters

#### linemerge
- **tolerance**: Maximum distance to merge paths (smaller = more precise)
- **Recommended**: 0.02mm - 0.2mm

#### linesimplify
- **tolerance**: Maximum deviation for simplification (smaller = more detail)
- **Recommended**: 0.01mm - 0.1mm

#### reloop
- **Purpose**: Ensure paths are closed loops
- **Recommended**: Always true for plotting

#### linesort
- **Purpose**: Optimize path order to reduce travel
- **Recommended**: Always true for efficiency

### Creating Your Own Preset

1. **Determine your needs**:
   - Speed vs quality tradeoff
   - Paper type
   - Design complexity

2. **Start with a base preset**:
   ```yaml
   my_preset:
     linemerge:
       tolerance: "0.03mm"  # Adjust based on needs
     linesimplify:
       tolerance: "0.015mm" # Adjust based on needs
     reloop: true
     linesort: true
   ```

3. **Test and refine**:
   ```bash
   vpype vfab-add --name test --preset my_preset
   vpype vfab-status --name test
   ```

## Paper Sizes

### Standard Paper Sizes

#### Metric (ISO 216)
```bash
vpype vfab-add --name design --paper A4    # 210x297mm
vpype vfab-add --name design --paper A3    # 297x420mm
vpype vfab-add --name design --paper A2    # 420x594mm
vpype vfab-add --name design --paper A1    # 594x841mm
```

#### US (ANSI)
```bash
vpype vfab-add --name design --paper Letter    # 8.5x11in
vpype vfab-add --name design --paper Tabloid   # 11x17in
vpype vfab-add --name design --paper Legal     # 8.5x14in
```

### Custom Paper Sizes

#### Format: `WIDTHxHEIGHT` with unit

```bash
# Metric
vpype vfab-add --name design --paper 297x420mm
vpype vfab-add --name design --paper 100x200mm

# Imperial
vpype vfab-add --name design --paper 8.5x11in
vpype vfab-add --name design --paper 12x18in

# Mixed (not recommended but supported)
vpype vfab-add --name design --paper 8.5x297mm
```

### Custom Size Aliases

Add to `config.yaml`:

```yaml
paper:
  custom_sizes:
    postcard: "148x105mm"
    business_card: "90x54mm"
    banner: "1200x300mm"
    square_large: "300x300mm"
```

Use aliases:

```bash
vpype vfab-add --name design --paper postcard
vpype vfab-add --name design --paper banner
```

### Paper Margins

Configure default margins in `config.yaml`:

```yaml
paper:
  default_margin_mm: 10.0  # 1cm margin
  margins:
    A4: 15.0               # 1.5cm for A4
    A3: 20.0               # 2cm for A3
    custom_size: 5.0        # 5mm for custom sizes
```

## Environment Variables

### vfab Workspace

```bash
# Set default workspace
export PLOTTY_WORKSPACE=~/my-vfab-workspace

# Temporary override
PLOTTY_WORKSPACE=/tmp/test-workspace vpype vfab-add --name test

# Project-specific
export PLOTTY_WORKSPACE=./project-workspace
```

### vpype-vfab Settings

```bash
# Debug mode
export VPYPE_PLOTTY_DEBUG=1

# Custom config file
export VPYPE_PLOTTY_CONFIG=~/my-config.yaml

# Log level
export VPYPE_PLOTTY_LOG_LEVEL=DEBUG
```

### Shell Configuration

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# vfab workspace
export PLOTTY_WORKSPACE=~/vfab-workspace

# vpype-vfab settings
export VPYPE_PLOTTY_LOG_LEVEL=INFO

# Aliases for convenience
alias pp-status='vpype vfab-status'
alias pp-list='vpype vfab-list --format table'
alias pp-queue='vpype vfab-queue'
```

## Advanced Configuration

### Multiple Plotter Setup

```yaml
# config.yaml
plotters:
  main_plotter:
    type: "axidraw"
    port: "/dev/ttyUSB0"
    speed: 50
    acceleration: 75
    
  backup_plotter:
    type: "axidraw"
    port: "/dev/ttyUSB1"
    speed: 40
    acceleration: 60

default_plotter: "main_plotter"
```

### Job Priorities

```yaml
# Priority levels
priorities:
  urgent: 10      # Client deadlines
  high: 7         # Important work
  normal: 5       # Regular work
  low: 3          # Background tasks
  batch: 1        # Batch processing
```

Use priorities:

```bash
vpype vfab-queue --name urgent_job --priority 10
vpype vfab-queue --name background_task --priority 1
```

### Automation Settings

```yaml
# Automatic job management
automation:
  # Auto-cleanup old jobs
  cleanup:
    enabled: true
    after_days: 30
    keep_states: ["completed", "failed"]
    
  # Auto-queue based on name patterns
  auto_queue:
    enabled: true
    patterns:
      - "test_*"      # Auto-queue test jobs
      - "draft_*"     # Auto-queue drafts
      - "final_*"      # Auto-queue finals with high priority
      
  # Notifications
  notifications:
    enabled: true
    on_complete: true
    on_error: true
    method: "email"  # or "slack", "webhook"
```

### Performance Tuning

```yaml
# Performance settings
performance:
  # Memory usage
  max_memory_mb: 512
  
  # Processing threads
  worker_threads: 2
  
  # Cache settings
  cache:
    enabled: true
    max_size_mb: 100
    ttl_hours: 24
    
  # Optimization timeouts
  timeouts:
    linemerge: 30    # seconds
    linesimplify: 60  # seconds
    total: 300       # seconds
```

### Integration Settings

```yaml
# External integrations
integrations:
  # Cloud storage
  cloud_storage:
    enabled: false
    provider: "s3"  # or "gcs", "azure"
    bucket: "plotter-jobs"
    
  # Version control
  git:
    enabled: true
    auto_commit: true
    commit_message: "Add vfab job: {job_name}"
    
  # API access
  api:
    enabled: true
    port: 8080
    auth_required: true
```

## Configuration Validation

### Check Configuration

```bash
# Validate vfab configuration
vfab config --validate

# Check workspace
vfab check --workspace ~/my-workspace

# Test vpype-vfab settings
vpype --debug vfab-add --name config_test
```

### Common Issues

#### Workspace Not Found
```bash
# Error: vfab workspace not found
# Solution: Create or specify workspace
vpype --workspace ~/correct/path vfab-add --name test
```

#### Invalid Preset
```bash
# Error: Unknown preset 'my_preset'
# Solution: Check preset file
cat ~/vfab-workspace/vpype-presets.yaml
```

#### Permission Issues
```bash
# Error: Permission denied
# Solution: Fix permissions
chmod -R u+rw ~/vfab-workspace/
```

---

**← [Basic Usage](basic-usage.md) | [Advanced Features](advanced-features.md) →**