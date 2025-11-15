# Getting Started Guide

This guide expands on the [Quick Start](../QUICKSTART.md) with more detail on core concepts and basic workflows.

## Table of Contents

1. [Installation Details](#installation-details)
2. [Understanding vfab](#understanding-plotty)
3. [Core Concepts](#core-concepts)
4. [Basic Workflows](#basic-workflows)
5. [Command Reference](#command-reference)
6. [Next Steps](#next-steps)

## Installation Details

### Prerequisites

- **Python 3.11+**: Required for all features
- **vpype 1.14+**: For vector graphics processing
- **vfab 1.0+**: Optional, for full integration

### Installation Methods

#### Method 1: pipx (Recommended)
```bash
# For vpype users
pipx inject vpype vpype-vfab

# For vsketch users  
pipx inject vsketch vpype-vfab
```

#### Method 2: pip (Alternative)
```bash
# Install directly
pip install vpype-vfab

# Or for development
pip install -e ".[dev]"
```

#### Method 3: From Source
```bash
git clone https://github.com/bkuri/vpype-vfab.git
cd vpype-vfab
pip install -e ".[dev]"
```

### Verification

```bash
# Check plugin is installed
vpype --help | grep plotty

# Test basic functionality
vpype circle --radius 1cm vfab-add --name test
```

## Understanding vfab

### What is vfab?

[vfab](https://github.com/bkuri/vfab) is a professional plotter management system that provides:

- **Job Queue Management**: Priority-based job scheduling
- **Plotter Control**: Direct hardware interface
- **State Management**: Track job progress and plotter status
- **Resource Optimization**: Efficient resource allocation

### vfab vs Standalone Mode

**vfab Integration** (Recommended):
- Full job management features
- Real-time status updates
- Resource optimization
- Multi-plotter support

**Standalone Mode** (Fallback):
- Basic job creation and queuing
- Works without vfab installation
- Limited to local file management

### Workspace Structure

```
~/vfab-workspace/
├── jobs/           # Job files and metadata
├── config.yaml     # vfab configuration
├── logs/          # Operation logs
└── state/         # vfab state files
```

## Core Concepts

### Jobs

A **job** represents a single plotting task with:
- **Name**: Unique identifier
- **Design**: SVG/vector data
- **Metadata**: Presets, paper size, creation info
- **State**: queued, running, completed, failed

### Presets

Optimization presets control how designs are processed:

| Preset | Speed | Quality | Use Case |
|--------|-------|---------|----------|
| `fast` | ⚡ Fast | Good | Testing, drafts, iterations |
| `default` | 🚀 Moderate | Better | General use, balanced |
| `hq` | 🐢 Slow | Best | Final output, client work |

### Paper Sizes

Standard paper sizes are supported:
- **Metric**: A4, A3, A2, A1
- **US**: Letter, Tabloid, Legal
- **Custom**: `297x420mm`, `11x17in`, etc.

## Basic Workflows

### Workflow 1: Simple Design → Plot

```bash
# 1. Create or load design
vpype circle --radius 5cm

# 2. Optimize for plotting
vpype linemerge linesimplify reloop linesort

# 3. Add to vfab
vpype vfab-add --name simple_circle --preset default --queue

# 4. Check status
vpype vfab-status --name simple_circle
```

### Workflow 2: Load Existing SVG

```bash
# 1. Load SVG file
vpype read my_design.svg

# 2. Validate design
vpype validate --min-path-length 0.5mm

# 3. Add with custom settings
vpype vfab-add --name my_design --preset hq --paper A3 --queue

# 4. Monitor progress
vpype vfab-status
```

### Workflow 3: Batch Processing

```bash
# Process multiple files
for file in designs/*.svg; do
    name=$(basename "$file" .svg)
    vpype read "$file" vfab-add --name "$name" --preset fast --queue
done

# Check all jobs
vpype vfab-list --format table
```

### Workflow 4: Iterative Design

```bash
# Create design variant
vpype rand --seed 123 vfab-add --name variant_123 --preset fast --queue

# Test plot
vpype vfab-status --name variant_123

# If good, create high-quality version
vpype rand --seed 123 vfab-add --name final_123 --preset hq --queue
```

## Command Reference

### vfab-add

Add current document to vfab job system.

```bash
vpype vfab-add [OPTIONS]
```

**Options:**
- `--name, -n`: Job name (auto-generated if omitted)
- `--preset, -p`: Optimization preset (fast, default, hq)
- `--paper`: Paper size (A4, A3, Letter, etc.)
- `--queue/--no-queue`: Auto-queue after adding
- `--workspace`: vfab workspace path

**Examples:**
```bash
# Basic usage
vpype vfab-add --name my_design

# With preset and auto-queue
vpype vfab-add --name test --preset hq --queue

# Custom paper size
vpype vfab-add --name large --paper A3 --preset default
```

### vfab-queue

Queue existing job for plotting.

```bash
vpype vfab-queue [OPTIONS]
```

**Options:**
- `--name, -n`: Job name to queue (required)
- `--priority`: Job priority (higher = more important)
- `--interactive/--no-interactive`: Multi-pen mapping
- `--workspace`: vfab workspace path

**Examples:**
```bash
# Queue with default priority
vpype vfab-queue --name my_design

# High priority job
vpype vfab-queue --name urgent --priority 10

# Multi-pen design
vpype vfab-queue --name colorful --interactive
```

### vfab-status

Check job status and details.

```bash
vpype vfab-status [OPTIONS]
```

**Options:**
- `--name, -n`: Specific job name (shows all if omitted)
- `--format`: Output format (table, json, simple)
- `--workspace`: vfab workspace path

**Examples:**
```bash
# Show all jobs
vpype vfab-status

# Specific job details
vpype vfab-status --name my_design

# JSON output for scripts
vpype vfab-status --name my_design --format json
```

### vfab-list

List vfab jobs with filtering.

```bash
vpype vfab-list [OPTIONS]
```

**Options:**
- `--state`: Filter by job state (queued, running, completed, failed)
- `--format`: Output format (table, json, csv)
- `--limit`: Maximum number of jobs to show
- `--workspace`: vfab workspace path

**Examples:**
```bash
# All jobs in table format
vpype vfab-list --format table

# Only queued jobs
vpype vfab-list --state queued

# Export to CSV
vpype vfab-list --format csv > jobs.csv

# Recent jobs only
vpype vfab-list --limit 10
```

## Next Steps

Now that you understand the basics, explore more advanced features:

- 🎨 **[vsketch Integration](vsketch-integration.md)** - Generative art workflows
- 🚀 **[Advanced Features](advanced-features.md)** - Multi-pen, batch processing
- 🔧 **[Configuration](configuration.md)** - Workspace and preset customization
- 🏭 **[Production Workflow](production-workflow.md)** - Professional use cases

## Troubleshooting

If you encounter issues:

1. **Check Installation**: `vpype --help | grep plotty`
2. **Verify vfab**: `vfab --version` (if using vfab)
3. **Test Workspace**: `vpype vfab-list`
4. **Enable Debug**: `vpype --debug vfab-add --name test`

For more help, see the [Troubleshooting Guide](troubleshooting.md).

---

**← [Quick Start](quickstart.md) | [vsketch Integration](vsketch-integration.md) →**