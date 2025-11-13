# Basic Usage Guide

This guide covers core vpype-plotty functionality for everyday use. Perfect for users who understand the basics and want to master essential workflows.

## Table of Contents

1. [Essential Commands](#essential-commands)
2. [Design Optimization](#design-optimization)
3. [Job Management](#job-management)
4. [Common Workflows](#common-workflows)
5. [Output Formats](#output-formats)
6. [Best Practices](#best-practices)

## Essential Commands

### Adding Jobs

The most common operation - add your current vpype document to ploTTY:

```bash
# Basic addition
vpype plotty-add --name my_design

# With preset and auto-queue
vpype plotty-add --name my_design --preset hq --queue

# Custom paper size
vpype plotty-add --name large_design --paper A3 --preset default
```

**Pro Tips:**
- Use descriptive names for easy identification
- Start with `fast` preset for testing
- Use `--queue` to immediately add to plotting queue

### Managing Jobs

```bash
# Queue existing job
vpype plotty-queue --name my_design --priority 1

# Check specific job
vpype plotty-status --name my_design

# List all jobs
vpype plotty-list --format table

# Filter by state
vpype plotty-list --state queued
```

**Priority Levels:**
- `1-3`: Low priority (background jobs)
- `4-7`: Normal priority (regular work)
- `8-10`: High priority (urgent jobs)

## Design Optimization

### Optimization Pipeline

Always optimize designs before plotting:

```bash
# Standard optimization
vpype linemerge linesimplify reloop linesort

# Add to ploTTY
vpype plotty-add --name optimized_design --preset hq
```

### Optimization Levels

#### Fast Optimization (Testing)
```bash
vpype linemerge --tolerance 0.1mm linesimplify --tolerance 0.05mm
vpype plotty-add --name test --preset fast --queue
```

#### High-Quality Optimization (Final)
```bash
vpype linemerge --tolerance 0.02mm linesimplify --tolerance 0.01mm
vpype plotty-add --name final --preset hq --queue
```

### Validation

Always validate designs before plotting:

```bash
# Check for issues
vpype validate --min-path-length 0.5mm

# Get design statistics
vpype stats --details

# Check layer information
vpype info
```

## Job Management

### Job States

Jobs progress through these states:

1. **created**: Job added to system
2. **queued**: Ready to plot
3. **running**: Currently plotting
4. **completed**: Successfully plotted
5. **failed**: Error during plotting

### Monitoring Jobs

```bash
# Quick status overview
vpype plotty-status

# Detailed job information
vpype plotty-status --name my_design --format json

# Watch job progress
watch -n 2 'vpype plotty-status --name my_design'
```

### Job Operations

```bash
# Queue with priority
vpype plotty-queue --name important_job --priority 8

# List recent jobs
vpype plotty-list --limit 10 --format table

# Export job list
vpype plotty-list --format csv > jobs_backup.csv
```

## Common Workflows

### Workflow 1: Design → Test → Final

```bash
# 1. Create design
vpype read my_design.svg

# 2. Quick test with fast preset
vpype plotty-add --name test_design --preset fast --queue

# 3. Check test result
vpype plotty-status --name test_design

# 4. Create final version
vpype plotty-add --name final_design --preset hq --queue
```

### Workflow 2: Batch Processing

```bash
# Process multiple designs
for file in designs/*.svg; do
    name=$(basename "$file" .svg)
    vpype read "$file" \
        linemerge linesimplify reloop linesort \
        plotty-add --name "$name" --preset default --queue
done

# Check all jobs
vpype plotty-list --format table
```

### Workflow 3: Iterative Design

```bash
# Create variations
for seed in {1..5}; do
    vpype rand --seed $seed \
        plotty-add --name variant_$seed --preset fast --queue
done

# Review results
vpype plotty-list --state completed

# Create final version of best variant
vpype rand --seed 3 \
    plotty-add --name final_variant --preset hq --queue
```

### Workflow 4: Large Design Management

```bash
# Split large design into manageable parts
vpype read large_design.svg \
    split --max-paths 1000 \
    plotty-add --name large_part1 --preset default

# Process parts sequentially
vpype plotty-queue --name large_part1
vpype plotty-status --name large_part1

# Continue with next part when first completes
vpype plotty-queue --name large_part2
```

## Output Formats

### Table Format (Default)

```bash
vpype plotty-list --format table
```

```
┌─────────────────┬─────────┬──────────┬─────────────┐
│ Name           │ State   │ Priority │ Created     │
├─────────────────┼─────────┼──────────┼─────────────┤
│ my_design      │ queued  │ 1        │ 2m ago      │
│ test_circle    │ running │ 5        │ 5m ago      │
│ completed_job  │ completed│ 1        │ 1h ago      │
└─────────────────┴─────────┴──────────┴─────────────┘
```

### JSON Format (Scripts)

```bash
vpype plotty-status --name my_design --format json
```

```json
{
  "name": "my_design",
  "state": "queued",
  "priority": 1,
  "created_at": "2025-11-12T10:30:00Z",
  "metadata": {
    "preset": "hq",
    "paper": "A4",
    "path_count": 42
  }
}
```

### CSV Format (Export)

```bash
vpype plotty-list --format csv > jobs.csv
```

```csv
name,state,priority,created_at,preset,paper
my_design,queued,1,2025-11-12T10:30:00Z,hq,A4
test_circle,running,5,2025-11-12T10:25:00Z,fast,A4
```

## Best Practices

### Naming Conventions

Use consistent, descriptive names:

```bash
# Good names
vpype plotty-add --name client_logo_final --preset hq
vpype plotty-add --name test_pattern_v3 --preset fast
vpype plotty-add --name batch_poster_01 --preset default

# Avoid
vpype plotty-add --name test
vpype plotty-add --name thing
vpype plotty-add --name 1
```

### Preset Selection

Choose presets based on use case:

```bash
# Development/Testing
vpype plotty-add --name prototype --preset fast --queue

# Regular Work
vpype plotty-add --name standard_design --preset default --queue

# Client Work/Final Output
vpype plotty-add --name client_delivery --preset hq --queue
```

### Paper Size Management

```bash
# Standard sizes
vpype plotty-add --name a4_design --paper A4
vpype plotty-add --name large_poster --paper A3

# Custom sizes
vpype plotty-add --name custom --paper 297x420mm
vpype plotty-add --name us_letter --paper 8.5x11in
```

### Queue Management

```bash
# Low priority background jobs
vpype plotty-queue --name background_task --priority 1

# Normal work
vpype plotty-queue --name regular_job --priority 5

# Urgent jobs
vpype plotty-queue --name urgent_fix --priority 10
```

### Error Prevention

```bash
# Always validate before plotting
vpype read design.svg validate --min-path-length 0.5mm

# Test with fast preset first
vpype plotty-add --name test --preset fast --queue

# Check status before creating final version
vpype plotty-status --name test

# Create final version only after test succeeds
vpype plotty-add --name final --preset hq --queue
```

### Performance Tips

```bash
# For complex designs, use simpler optimization first
vpype read complex.svg linesimplify --tolerance 0.1mm

# Split very large designs
vpype read huge.svg split --max-paths 500

# Use appropriate presets
vpype plotty-add --name draft --preset fast      # Quick testing
vpype plotty-add --name final --preset hq        # Final output
```

## Troubleshooting Common Issues

### Job Not Appearing

```bash
# Check if job was created
vpype plotty-list --format table

# Check specific job
vpype plotty-status --name my_design

# Verify workspace
vpype --debug plotty-list
```

### Long Processing Times

```bash
# Use faster preset
vpype plotty-add --name design --preset fast

# Simplify design
vpype read design.svg linesimplify --tolerance 0.1mm

# Split large design
vpype read design.svg split --max-paths 1000
```

### Quality Issues

```bash
# Use higher quality preset
vpype plotty-add --name design --preset hq

# Manual optimization
vpype read design.svg \
    linemerge --tolerance 0.02mm \
    linesimplify --tolerance 0.01mm \
    reloop \
    linesort
```

---

**← [Getting Started](getting-started.md) | [Advanced Features](advanced-features.md) →**