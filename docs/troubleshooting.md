# vpype-vfab Troubleshooting Guide

This guide covers common issues, error messages, and solutions for vpype-vfab.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Connection Problems](#connection-problems)
3. [Job Management Issues](#job-management-issues)
4. [Design and Optimization Problems](#design-and-optimization-problems)
5. [Performance Issues](#performance-issues)
6. [Workspace and Configuration](#workspace-and-configuration)
7. [Error Messages Reference](#error-messages-reference)
8. [Debug Mode and Diagnostics](#debug-mode-and-diagnostics)

## Installation Issues

### Plugin Not Found

**Error**: `vpype: command not found` or `vfab-add: command not found`

**Causes**:
- vpype not installed
- Plugin not properly injected
- PATH issues

**Solutions**:

```bash
# Check vpype installation
which vpype
vpype --version

# Reinstall plugin
pipx inject vpype vpype-vfab

# Alternative: install directly
pip install vpype-vfab

# Verify installation
vpype --help | grep plotty
```

### Python Version Compatibility

**Error**: `Python 3.11+ required` or package conflicts

**Solutions**:

```bash
# Check Python version
python --version

# Upgrade if needed
pip install --upgrade python

# Use specific version
python3.11 -m pip install vpype-vfab
```

### Permission Issues

**Error**: `Permission denied` during installation

**Solutions**:

```bash
# Use user installation
pip install --user vpype-vfab

# Or use pipx (recommended)
pipx install vpype
pipx inject vpype vpype-vfab

# Fix permissions
sudo chown -R $USER ~/.local
```

## Connection Problems

### vfab Not Found

**Error**: `vfab installation or workspace not found`

**Causes**:
- vfab not installed
- Workspace not configured
- Incorrect workspace path

**Solutions**:

```bash
# Install vfab
pip install plotty

# Check vfab installation
vfab --version

# Create workspace
vfab init --workspace ~/vfab-workspace

# Specify workspace explicitly
vpype --workspace ~/vfab-workspace vfab-add --name test input.svg

# Check workspace detection
vpype --debug vfab-list
```

### Connection Timeout

**Error**: `Failed to connect to vfab` or `Connection timeout`

**Causes**:
- vfab not running
- Network issues
- Workspace corruption

**Solutions**:

```bash
# Check if vfab is running
ps aux | grep plotty

# Start vfab if needed
vfab start --daemon

# Check workspace integrity
vfab check --workspace ~/vfab-workspace

# Test with simple design
vpype circle --radius 5cm vfab-add --name test --queue

# Use debug mode
vpype --debug vfab-status
```

### Workspace Corruption

**Error**: `Invalid workspace` or `Database corrupted`

**Solutions**:

```bash
# Check workspace
vfab check --workspace ~/vfab-workspace

# Repair workspace
vfab repair --workspace ~/vfab-workspace

# Create new workspace (last resort)
mkdir ~/new-vfab-workspace
vfab init --workspace ~/new-vfab-workspace
vpype --workspace ~/new-vfab-workspace vfab-add --name test input.svg
```

## Job Management Issues

### Job Not Found

**Error**: `Job 'my_design' not found`

**Causes**:
- Job name typo
- Job deleted
- Wrong workspace

**Solutions**:

```bash
# List all jobs
vpype vfab-list

# Search for similar names
vpype vfab-list --format csv | grep my

# Check different workspace
vpype --workspace ~/other-workspace vfab-list

# Use exact name from list
vpype vfab-status --name exact_job_name
```

### Job Stuck in Queue

**Error**: Job not progressing from `queued` state

**Causes**:
- vfab not running
- Plotter offline
- Resource conflicts

**Solutions**:

```bash
# Check vfab status
vfab status

# Check plotter status
vfab plotter status

# Check job details
vpype vfab-status --name stuck_job --format json

# Restart vfab
vfab restart

# Check system resources
df -h  # disk space
free -h  # memory
```

### Job Creation Failed

**Error**: `Failed to create job` or `Job creation error`

**Causes**:
- Invalid design
- Permission issues
- Disk space

**Solutions**:

```bash
# Validate design
vpype read input.svg validate

# Check permissions
ls -la ~/vfab-workspace/
chmod -R u+rw ~/vfab-workspace/

# Check disk space
df -h ~/vfab-workspace/

# Try with simple design
vpype circle --radius 5cm vfab-add --name test
```

## Design and Optimization Problems

### Invalid SVG Format

**Error**: `Invalid SVG` or `Cannot parse design`

**Causes**:
- Corrupted SVG file
- Unsupported features
- Encoding issues

**Solutions**:

```bash
# Validate SVG
xmllint --noout input.svg

# Check SVG content
head -20 input.svg

# Convert with vpype
vpype read input.svg write output.svg

# Simplify design
vpype read input.svg linemerge linesimplify write simplified.svg
```

### Optimization Taking Too Long

**Error**: Very slow processing with `hq` preset

**Causes**:
- Complex design
- Many small paths
- Large file size

**Solutions**:

```bash
# Use faster preset
vpype vfab-add --name design --preset fast

# Simplify first
vpype read input.svg linesimplify --tolerance 0.1mm vfab-add --name simplified

# Check complexity
vpype read input.svg stats

# Split large design
vpype read input.svg split --max-paths 1000 vfab-add --name part1
```

### Poor Plotting Quality

**Issue**: Lines don't connect, gaps, or poor quality

**Solutions**:

```bash
# Use higher quality preset
vpype vfab-add --name design --preset hq

# Manual optimization
vpype read input.svg \
    linemerge --tolerance 0.05mm \
    linesimplify --tolerance 0.02mm \
    reloop \
    linesort \
    vfab-add --name optimized

# Check path continuity
vpype read input.svg stats --details
```

## Performance Issues

### Slow Job Processing

**Causes**:
- Large designs
- Complex optimization
- System resources

**Solutions**:

```bash
# Monitor system resources
htop
iotop

# Use faster preset
vpype vfab-add --name design --preset fast

# Process in batches
vpype read large_design.svg split --max-paths 500

# Optimize system
# - Close other applications
# - Ensure sufficient RAM
# - Use SSD for workspace
```

### Memory Issues

**Error**: `MemoryError` or system becomes unresponsive

**Solutions**:

```bash
# Check memory usage
free -h

# Use simpler optimization
vpype read input.svg linesimplify --tolerance 0.2mm

# Process smaller chunks
vpype read input.svg split --max-size 10MB

# Restart vfab to clear memory
vfab restart
```

## Workspace and Configuration

### Workspace Detection Issues

**Issue**: Wrong workspace being used

**Solutions**:

```bash
# Check current workspace
vpype --debug vfab-list

# Specify workspace explicitly
vpype --workspace /correct/path vfab-add --name test input.svg

# Set environment variable
export PLOTTY_WORKSPACE=/correct/path
vpype vfab-add --name test input.svg

# Create workspace symlink
ln -s /correct/path ~/vfab-workspace
```

### Configuration Issues

**Error**: `Invalid configuration` or `Config file corrupted`

**Solutions**:

```bash
# Check configuration
vfab config --show

# Reset configuration
vfab config --reset

# Edit configuration manually
nano ~/vfab-workspace/config.yaml

# Validate configuration
vfab config --validate
```

## Error Messages Reference

### Common Error Types

#### `PlottyNotFoundError`
- **Meaning**: vfab installation or workspace not found
- **Action**: Install vfab or specify correct workspace
- **Command**: `pip install plotty` or `--workspace /path`

#### `PlottyConnectionError`
- **Meaning**: Cannot connect to running vfab instance
- **Action**: Start vfab or check network connectivity
- **Command**: `vfab start --daemon`

#### `PlottyJobError`
- **Meaning**: Job creation or management failed
- **Action**: Check job name, permissions, and design validity
- **Command**: `vpype vfab-list` to verify

#### `PlottyConfigError`
- **Meaning**: Configuration file issues
- **Action**: Check or reset vfab configuration
- **Command**: `vfab config --reset`

#### `PlottyTimeoutError`
- **Meaning**: Operation took too long
- **Action**: Use faster preset or simplify design
- **Command**: `--preset fast` or `linesimplify`

### Recovery Hints

Most error messages include recovery hints:

```bash
# Example error with hint
Error: Job 'my_design' not found
Recovery: Check job name with: vpype vfab-list

# Example with retry suggestion
Error: Connection timeout
Recovery: Check vfab is running and accessible
Retry after: 5.0s
```

## Debug Mode and Diagnostics

### Enable Debug Mode

```bash
# Global debug mode
vpype --debug vfab-add --name test input.svg

# Command-specific debug
vpype vfab-add --name test input.svg --verbose

# Check vfab debug
vfab --debug status
```

### Diagnostic Commands

```bash
# System information
vpype --version
vfab --version
python --version

# Workspace diagnostics
vpype --debug vfab-list
vfab check --workspace ~/vfab-workspace

# Job diagnostics
vpype vfab-status --format json
vpype vfab-list --format csv

# Design validation
vpype read input.svg validate --min-path-length 0.5mm
vpype read input.svg stats --details
```

### Log Files

```bash
# Check vfab logs
tail -f ~/vfab-workspace/logs/plotty.log

# Check system logs
journalctl -u plotty

# Check vpype logs (if configured)
tail -f ~/.local/share/vpype/logs/vpype.log
```

### Performance Profiling

```bash
# Time operations
time vpype read input.svg vfab-add --name test

# Profile with Python
python -m cProfile -o profile.stats \
    -c "import vpype; vpype.run('read input.svg vfab-add --name test')"

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"
```

## Getting Help

### Built-in Help

```bash
# General help
vpype --help

# Command-specific help
vpype vfab-add --help
vpype vfab-queue --help
vpype vfab-status --help
vpype vfab-list --help
```

### Community Support

- **GitHub Issues**: [vpype-vfab issues](https://github.com/bkuri/vpype-vfab/issues)
- **vfab Documentation**: [vfab docs](https://github.com/bkuri/vfab)
- **vpype Documentation**: [vpype docs](https://github.com/abey79/vpype)

### Reporting Issues

When reporting issues, include:

1. **System Information**:
   ```bash
   vpype --version
   vfab --version
   python --version
   uname -a
   ```

2. **Error Message**: Full error output

3. **Steps to Reproduce**: Exact commands used

4. **Debug Output**: Use `--debug` flag

5. **Design File**: If possible, provide the SVG file

### Quick Diagnostic Script

```bash
#!/bin/bash
# quick_diagnostic.sh - Quick system diagnostic

echo "=== vpype-vfab Diagnostic ==="
echo "Date: $(date)"
echo "System: $(uname -a)"
echo ""

echo "=== Versions ==="
echo "Python: $(python --version)"
echo "vpype: $(vpype --version 2>/dev/null || echo 'Not found')"
echo "vfab: $(vfab --version 2>/dev/null || echo 'Not found')"
echo ""

echo "=== Installation Check ==="
echo "vpype location: $(which vpype 2>/dev/null || echo 'Not found')"
echo "vfab location: $(which vfab 2>/dev/null || echo 'Not found')"
echo ""

echo "=== Plugin Check ==="
vpype --help | grep -A 5 "plotty" || echo "Plugin not found"
echo ""

echo "=== Workspace Check ==="
if [ -d ~/vfab-workspace ]; then
    echo "Workspace exists: ~/vfab-workspace"
    ls -la ~/vfab-workspace/
else
    echo "Workspace not found: ~/vfab-workspace"
fi
echo ""

echo "=== Quick Test ==="
vpype circle --radius 1cm vfab-add --name diagnostic_test 2>&1 || echo "Test failed"
echo ""

echo "=== End Diagnostic ==="
```

Run this script to quickly diagnose most common issues:

```bash
chmod +x quick_diagnostic.sh
./quickagnostic.sh
```

## Prevention Tips

1. **Regular Updates**: Keep vpype, vfab, and vpype-vfab updated
2. **Workspace Backup**: Regular backup of vfab workspace
3. **Design Validation**: Validate designs before adding to queue
4. **Resource Monitoring**: Monitor system resources during large jobs
5. **Test with Fast Preset**: Always test with fast preset first
6. **Meaningful Names**: Use descriptive job names for easy tracking
7. **Regular Cleanup**: Remove old completed jobs to free space