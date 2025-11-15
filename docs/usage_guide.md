# vpype-vfab Usage Guide

This guide provides detailed tutorials and examples for using vpype-vfab effectively in your creative workflow.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Workflow](#basic-workflow)
3. [Advanced Features](#advanced-features)
4. [vsketch Integration](#vsketch-integration)
5. [Batch Processing](#batch-processing)
6. [Multi-Pen Designs](#multi-pen-designs)
7. [Production Workflow](#production-workflow)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- **vpype** (v1.14+): Vector graphics pipeline
- **vsketch** (optional): Generative art framework
- **vfab** (optional): Professional plotter management

### Installation

```bash
# Install into vpype
pipx inject vpype vpype-vfab

# Or into vsketch
pipx inject vsketch vpype-vfab

# Verify installation
vpype --help | grep plotty
```

### First Test

```bash
# Create a simple test design
vpype circle --radius 5cm vfab-add --name test_circle --queue

# Check if it worked
vpype vfab-list
```

## Basic Workflow

### 1. Create or Load a Design

```bash
# Generate a random design
vpype rand --seed 123 --layers 3

# Load an existing SVG
vpype read my_design.svg

# Create geometric patterns
vpype rect --width 10cm --height 15cm circle --radius 3cm
```

### 2. Optimize for Plotting

```bash
# Standard optimization pipeline
vpype linemerge linesimplify reloop linesort

# Custom optimization
vpype linemerge --tolerance 0.1mm linesimplify --tolerance 0.05mm
```

### 3. Add to vfab

```bash
# Basic addition
vpype vfab-add --name my_design

# With preset and auto-queue
vpype vfab-add --name my_design --preset hq --queue

# Custom paper size
vpype vfab-add --name my_design --paper A3 --preset default
```

### 4. Manage Jobs

```bash
# Queue the job
vpype vfab-queue --name my_design --priority 1

# Check status
vpype vfab-status --name my_design

# List all jobs
vpype vfab-list --format table
```

## Advanced Features

### Optimization Presets

#### Fast Preset (Drafts & Testing)
```bash
vpype vfab-add --name draft --preset fast --queue
```
- Quick optimization
- Minimal processing time
- Good for testing and iterations

#### Default Preset (General Use)
```bash
vpype vfab-add --name final --preset default --queue
```
- Balanced optimization
- Good quality/time ratio
- Suitable for most designs

#### High-Quality Preset (Final Output)
```bash
vpype vfab-add --name masterpiece --preset hq --queue
```
- Maximum optimization
- Best possible quality
- Longer processing time

### Custom Paper Sizes

```bash
# Standard sizes
vpype vfab-add --name design --paper A4
vpype vfab-add --name design --paper A3
vpype vfab-add --name design --paper US_Letter

# Custom sizes
vpype vfab-add --name design --paper 297x420mm
vpype vfab-add --name design --paper 11x17in
```

### Workspace Management

```bash
# Use specific workspace
vpype --workspace /path/to/project vfab-add --name design

# Create project-specific workspace
mkdir my_project_workspace
vpype --workspace ./my_project_workspace vfab-add --name design
```

## vsketch Integration

### Basic vsketch Workflow

```python
import vsketch

class MySketch(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")
        
        # Create generative art
        for i in range(20):
            x = vsk.random(0, 20)
            y = vsk.random(0, 30)
            r = vsk.random(0.5, 2.5)
            vsk.circle(x, y, radius=r)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        # Standard optimization
        vsk.vpype("linemerge linesimplify reloop linesort")
        
        # Add to vfab
        vsk.vpype("vfab-add --name generative_circles --preset hq --queue")

if __name__ == "__main__":
    MySketch().display()
```

### Advanced vsketch with Parameters

```python
import vsketch
import click

class ParametricSketch(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4")
        vsk.scale("cm")
        
        # Get parameters
        count = vsk.param("count", 50)
        max_radius = vsk.param("max_radius", 3.0)
        
        # Generate based on parameters
        for i in range(count):
            x = vsk.random(0, 20)
            y = vsk.random(0, 30)
            r = vsk.random(0.1, max_radius)
            vsk.circle(x, y, radius=r)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        # Get preset from parameter
        preset = vsk.param("preset", "default")
        
        # Optimize and add to vfab
        vsk.vpype(f"linemerge linesimplify reloop linesort vfab-add --name parametric_art --preset {preset}")

if __name__ == "__main__":
    ParametricSketch().display()
```

## Batch Processing

### Generate Multiple Variants

```python
#!/usr/bin/env python3
"""Batch processing script for generating multiple design variants."""

import subprocess
import sys
from pathlib import Path

def generate_variant(seed: int, name: str) -> bool:
    """Generate a single variant and add to vfab."""
    try:
        # Generate the sketch
        cmd = f"vsk run --seed {seed} my_sketch.py --save-only"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to generate variant {seed}: {result.stderr}")
            return False
        
        # Add to vfab
        svg_file = f"output/{name}_{seed}.svg"
        cmd = f"vpype read {svg_file} vfab-add --name {name}_{seed} --preset hq --queue"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Generated and queued {name}_{seed}")
            return True
        else:
            print(f"❌ Failed to queue {name}_{seed}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing variant {seed}: {e}")
        return False

def main():
    """Generate multiple variants."""
    if len(sys.argv) < 3:
        print("Usage: python batch_generate.py <base_name> <count>")
        sys.exit(1)
    
    base_name = sys.argv[1]
    count = int(sys.argv[2])
    
    print(f"Generating {count} variants of {base_name}...")
    
    successful = 0
    for seed in range(count):
        if generate_variant(seed, base_name):
            successful += 1
    
    print(f"\n📊 Summary: {successful}/{count} variants generated successfully")
    
    # Show vfab status
    subprocess.run("vpype vfab-list --format table", shell=True)

if __name__ == "__main__":
    main()
```

### Usage

```bash
# Generate 10 variants
python batch_generate.py my_design 10

# Check what was queued
vpype vfab-list --state queued

# Monitor progress
vpype vfab-status
```

## Multi-Pen Designs

### Creating Multi-Layer Designs

```bash
# Create design with separate layers
vpype read background.svg \
    read foreground.svg \
    read details.svg \
    vfab-add --name multi_layer_design --preset hq
```

### Interactive Pen Mapping

```bash
# Queue with interactive pen mapping
vpype vfab-queue --name multi_layer_design --interactive
```

This will prompt you to assign pens to each layer:

```
🖊️  Interactive Pen Mapping for 'multi_layer_design'

Layer 1 (background): 15 paths, black
Available pens: 1 (black), 2 (red), 3 (blue), 4 (green)
Enter pen number for layer 1 [1]: 1

Layer 2 (foreground): 8 paths, red  
Available pens: 1 (black), 2 (red), 3 (blue), 4 (green)
Enter pen number for layer 2 [2]: 3

Layer 3 (details): 23 paths, blue
Available pens: 1 (black), 2 (red), 3 (blue), 4 (green)  
Enter pen number for layer 3 [3]: 2

✅ Pen mapping saved to multi_layer_design_pen_mapping.yaml
✅ Queued job 'multi_layer_design' with priority 1
```

### Reusing Pen Mappings

```bash
# Use saved mapping for future jobs
vpype vfab-queue --name similar_design --interactive --load-pen-mapping multi_layer_design_pen_mapping.yaml
```

## Production Workflow

### Professional Setup

```bash
# 1. Create dedicated workspace
mkdir /home/user/production_workspace
cd /home/user/production_workspace

# 2. Set up project structure
mkdir -p designs/{clients,internal,tests}
mkdir -p output/{final,proofs,drafts}
mkdir -p archive

# 3. Configure vfab workspace
vfab init --workspace .
```

### Quality Control Pipeline

```bash
#!/bin/bash
# production_pipeline.sh - Quality control for production jobs

set -e

DESIGN_NAME="$1"
PRESET="${2:-hq}"
PAPER="${3:-A4}"

if [ -z "$DESIGN_NAME" ]; then
    echo "Usage: $0 <design_name> [preset] [paper_size]"
    exit 1
fi

echo "🎨 Processing design: $DESIGN_NAME"
echo "📋 Preset: $PRESET, Paper: $PAPER"

# 1. Load and validate design
echo "📖 Loading design..."
vpype read "designs/clients/$DESIGN_NAME.svg" \
    validate --min-path-length 1mm \
    stats

# 2. Optimize for production
echo "⚡ Optimizing for production..."
vpype linemerge --tolerance 0.05mm \
    linesimplify --tolerance 0.02mm \
    reloop \
    linesort \
    vfab-add --name "$DESIGN_NAME" --preset "$PRESET" --paper "$PAPER"

# 3. Create proof
echo "📋 Creating proof..."
vpype read "designs/clients/$DESIGN_NAME.svg" \
    scale --factor 0.5 \
    write "output/proofs/${DESIGN_NAME}_proof.svg"

# 4. Queue for production
echo "🚀 Queuing for production..."
vpype vfab-queue --name "$DESIGN_NAME" --priority 2

# 5. Generate report
echo "📊 Generating status report..."
vpype vfab-status --name "$DESIGN_NAME" --format json > "output/${DESIGN_NAME}_status.json"

echo "✅ Production pipeline complete for $DESIGN_NAME"
```

### Monitoring Production Jobs

```bash
# Monitor all production jobs
watch -n 5 'vpype vfab-list --state queued,running --format table'

# Get detailed status for specific job
vpype vfab-status --name important_client_job --format json

# Export job list for reporting
vpype vfab-list --format csv > production_jobs_$(date +%Y%m%d).csv
```

## Troubleshooting

### Common Issues and Solutions

#### Design Not Plotting Correctly

```bash
# Check design complexity
vpype read design.svg stats

# Validate paths
vpype read design.svg validate --min-path-length 0.5mm

# Check for overlapping lines
vpype read design.svg stats --details
```

#### vfab Connection Issues

```bash
# Check vfab status
vfab status

# Verify workspace
vpype --workspace /path/to/workspace vfab-list

# Test with simple design
vpype circle --radius 5cm vfab-add --name test --queue
```

#### Performance Issues

```bash
# Use fast preset for testing
vpype vfab-add --name test --preset fast --queue

# Simplify complex designs
vpype read complex_design.svg linesimplify --tolerance 0.1mm vfab-add --name simplified

# Break large jobs into smaller pieces
vpype read large_design.svg split --max-paths 1000 vfab-add --name part1
```

### Debug Mode

```bash
# Enable verbose output
vpype --debug vfab-add --name debug_test input.svg

# Check vfab integration
vpype vfab-status --format json | jq .
```

### Getting Help

```bash
# Get help for any command
vpype vfab-add --help
vpype vfab-queue --help
vpype vfab-status --help
vpype vfab-list --help

# Check version and compatibility
vpype --version
vpype-vfab --version  # if available
```

## Best Practices

1. **Always test with fast preset first** before using hq for final output
2. **Use meaningful job names** for easy identification
3. **Save pen mappings** for consistent multi-pen designs
4. **Monitor job progress** regularly for production work
5. **Keep workspace organized** with proper directory structure
6. **Validate designs** before adding to production queue
7. **Use version control** for design files and configurations

## Next Steps

- Explore vfab documentation for advanced plotter management
- Check vpype documentation for optimization techniques
- Look at vsketch examples for generative art inspiration
- Join the community for support and inspiration