# vpype-vfab Documentation

Welcome to the vpype-vfab documentation hub. This guide helps you find the right documentation for your needs.

## 🚀 Quick Start (New Users)

**New to vpype-vfab? Start here:**

1. **[Quick Start](quickstart.md)** - 5-minute getting started guide
2. **[Getting Started](getting-started.md)** - Detailed installation and basic concepts
3. **[Basic Usage](basic-usage.md)** - Core commands and everyday workflows

## 📚 Core Documentation

### Essential Guides
- **[Getting Started](getting-started.md)** - Installation, setup, and basic concepts
- **[Basic Usage](basic-usage.md)** - Core commands and common workflows
- **[Configuration](configuration.md)** - Workspace setup and customization

### Advanced Features
- **[Advanced Features](advanced-features.md)** - Multi-pen designs, batch processing
- **[vsketch Integration](vsketch-integration.md)** - Generative art workflows
- **[Production Workflow](production-workflow.md)** - Professional and production use

### Reference & Support
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[API Reference](api-reference.md)** - Technical documentation

## 🎯 Learning Paths

### Path 1: Quick Start (5 minutes)
```
quickstart.md → Basic Usage → Your First Plot
```

### Path 2: Complete Beginner (30 minutes)
```
quickstart.md → Getting Started → Basic Usage → Configuration
```

### Path 3: vsketch User (20 minutes)
```
quickstart.md → vsketch Integration → Advanced Features
```

### Path 4: Professional User (45 minutes)
```
Getting Started → Basic Usage → Advanced Features → Production Workflow
```

## 📖 Documentation by Topic

### Installation & Setup
- **[Quick Start - Installation](quickstart.md#installation)** - 2-command install
- **[Getting Started - Installation Details](getting-started.md#installation-details)** - Complete setup guide
- **[Configuration - Workspace Setup](configuration.md#workspace-setup)** - Workspace management

### Core Commands
- **[Basic Usage - Essential Commands](basic-usage.md#essential-commands)** - Daily use commands
- **[Getting Started - Command Reference](getting-started.md#command-reference)** - All basic commands
- **[API Reference](api-reference.md)** - Complete technical reference

### Workflows & Techniques
- **[Basic Usage - Common Workflows](basic-usage.md#common-workflows)** - Everyday patterns
- **[Advanced Features - Batch Processing](advanced-features.md#batch-processing)** - Automation
- **[Production Workflow](production-workflow.md)** - Professional processes

### Specialized Topics
- **[Advanced Features - Multi-Pen Designs](advanced-features.md#multi-pen-designs)** - Color plotting
- **[vsketch Integration](vsketch-integration.md)** - Generative art
- **[Configuration - Advanced Setup](configuration.md#advanced-configuration)** - Power user settings

### Problem Solving
- **[Troubleshooting](troubleshooting.md)** - Complete problem resolution
- **[Basic Usage - Troubleshooting](basic-usage.md#troubleshooting-common-issues)** - Quick fixes
- **[Configuration - Validation](configuration.md#configuration-validation)** - Debug setup

## 🔍 Quick Reference

### Command Cheat Sheet

| Command | Purpose | Quick Example |
|---------|---------|---------------|
| `vfab-add` | Add design to vfab | `vpype vfab-add --name test --queue` |
| `vfab-queue` | Queue existing job | `vpype vfab-queue --name test --priority 5` |
| `vfab-status` | Check job status | `vpype vfab-status --name test` |
| `vfab-list` | List all jobs | `vpype vfab-list --format table` |

### Common Options

| Option | Purpose | Values |
|--------|---------|--------|
| `--name` | Job name | Any string |
| `--preset` | Optimization level | `fast`, `default`, `hq` |
| `--paper` | Paper size | `A4`, `A3`, `Letter`, custom |
| `--queue` | Auto-queue job | Flag |
| `--priority` | Job priority | 1-10 (higher = more urgent) |
| `--format` | Output format | `table`, `json`, `csv` |

### Preset Guide

| Preset | Speed | Quality | Best For |
|--------|-------|---------|-----------|
| `fast` | ⚡ Very Fast | Good | Testing, drafts |
| `default` | 🚀 Moderate | Better | General use |
| `hq` | 🐢 Slow | Best | Final output |

## 🆘 Getting Help

### Self-Service
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions
- **[Quick Start - Need Help](quickstart.md#-need-help)** - Basic help commands
- **[Configuration - Common Issues](configuration.md#common-issues)** - Setup problems

### Command Line Help
```bash
# Get help for any command
vpype vfab-add --help
vpype vfab-queue --help
vpype vfab-status --help
vpype vfab-list --help

# Check versions
vpype --version
python --version
```

### Community Support
- **GitHub Issues**: [Report bugs and request features](https://github.com/bkuri/vpype-vfab/issues)
- **Discussions**: [Community questions and discussions](https://github.com/bkuri/vpype-vfab/discussions)

## 📝 Documentation Structure

```
vpype-vfab/
├── README.md                  # Project overview and features
├── CHANGELOG.md              # Version history
└── docs/
    ├── index.md              # This page - documentation hub
    ├── quickstart.md         # 5-minute getting started
    ├── getting-started.md    # Detailed setup and basics
    ├── basic-usage.md       # Core commands and workflows
    ├── configuration.md      # Setup and customization
    ├── advanced-features.md # Multi-pen, batch processing
    ├── vsketch-integration.md # Generative art workflows
    ├── production-workflow.md # Professional use
    ├── troubleshooting.md    # Problem resolution
    └── api-reference.md     # Technical reference
```

## 🚀 Navigation Tips

### For New Users
1. Start with **[Quick Start](quickstart.md)**
2. Read **[Getting Started](getting-started.md)** for details
3. Use **[Basic Usage](basic-usage.md)** for everyday tasks

### For vsketch Users
1. **[Quick Start](quickstart.md)** for installation
2. **[vsketch Integration](vsketch-integration.md)** for workflows
3. **[Advanced Features](advanced-features.md)** for power features

### For Professionals
1. **[Getting Started](getting-started.md)** for setup
2. **[Production Workflow](production-workflow.md)** for best practices
3. **[Configuration](configuration.md)** for customization

### For Troubleshooting
1. **[Troubleshooting](troubleshooting.md)** for comprehensive help
2. **[Configuration - Validation](configuration.md#configuration-validation)** for setup issues
3. **[Basic Usage - Troubleshooting](basic-usage.md#troubleshooting-common-issues)** for quick fixes

---

**🎯 Not sure where to start? Begin with [Quick Start](quickstart.md)!**