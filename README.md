# vpype-vfab

[![PyPI version](https://img.shields.io/pypi/v/vpype-vfab.svg)](https://pypi.org/project/vpype-vfab/)
[![Python versions](https://img.shields.io/pypi/pyversions/vpype-vfab.svg)](https://pypi.org/project/vpype-vfab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](tests/)

**vpype-vfab** bridges creative tools (vsketch, vpype) with [vfab](https://github.com/bkuri/vfab)'s professional plotter management system. Go from generative art to plotter jobs in seconds.

## ✨ Key Features

- 🎨 **Seamless Integration**: Works directly with vpype and vsketch workflows
- 🚀 **Quick Job Creation**: Add documents to vfab with a single command  
- 📊 **Job Management**: Queue, monitor, and list plotter jobs
- 🎯 **Optimization Presets**: Fast, default, and high-quality settings
- 🖊️ **Multi-Pen Support**: Interactive pen mapping with YAML persistence
- 🛡️ **Error Recovery**: Automatic retry logic and user-friendly error messages
- 🔧 **Standalone Mode**: Works with or without vfab installation

## 🚀 Quick Start

### Install (2 commands)

```bash
pipx inject vpype vpype-vfab
vpype circle --radius 5cm vfab-add --name test --queue
```

### Your First Plot (3 commands)

```bash
# Create design
vpype rand --seed 123

# Add to vfab
vpype vfab-add --name my_first_plot

# Check status  
vpype vfab-status
```

📖 **[→ Full Quick Start Guide](docs/quickstart.md)** (5 minutes to first plot)

## 📚 Documentation

### Getting Started
- 📖 **[Quick Start](docs/quickstart.md)** - 5-minute getting started guide
- 📖 **[Basic Usage](docs/basic-usage.md)** - Core commands and simple workflows
- 🔧 **[Configuration](docs/configuration.md)** - Workspace setup and presets

### Advanced Features  
- 🎨 **[vsketch Integration](docs/vsketch-integration.md)** - Generative art workflows
- 🚀 **[Advanced Features](docs/advanced-features.md)** - Multi-pen, batch processing, production
- 🏭 **[Production Workflow](docs/production-workflow.md)** - Professional/production use

### Reference & Support
- 🚨 **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- 📋 **[API Reference](docs/api-reference.md)** - Technical documentation
- 📖 **[Documentation Index](docs/index.md)** - Complete documentation overview

## 💻 Core Commands

| Command | What it does | Example |
|---------|--------------|---------|
| `vfab-add` | Add design to vfab | `vpype vfab-add --name test --queue` |
| `vfab-queue` | Queue existing job | `vpype vfab-queue --name test --priority 2` |
| `vfab-status` | Check job status | `vpype vfab-status --name test --format json` |
| `vfab-list` | List all jobs | `vpype vfab-list --state queued --format table` |

## 🎯 Common Workflows

### Basic Design → Plot
```bash
vpype read design.svg vfab-add --name my_design --preset hq --queue
```

### vsketch Integration
```python
import vsketch

class MySketch(vsketch.SketchClass):
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("vfab-add --name my_sketch --preset hq --queue")
```

### Batch Processing
```bash
for seed in {1..10}; do
    vpype rand --seed $seed vfab-add --name variant_$seed --queue
done
```

## 📦 Installation

### For vpype Users
```bash
pipx inject vpype vpype-vfab
```

### For vsketch Users  
```bash
pipx inject vsketch vpype-vfab
```

### Development Installation
```bash
git clone https://github.com/bkuri/vpype-vfab.git
cd vpype-vfab
pip install -e ".[dev]"
```

## 🔧 Requirements

- **Python**: 3.11+
- **vpype**: 1.14+ (for vpype users)
- **vsketch**: 1.0+ (for vsketch users)  
- **vfab**: 1.0+ (optional, for full integration)

## 🏗️ Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
black . && ruff check . && mypy vpype_plotty/
```

### Contributing
1. Follow Black and Ruff conventions
2. Maintain >90% test coverage
3. Update documentation for new features
4. Use GitHub issues with clear reproduction steps

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: [github.com/bkuri/vpype-vfab](https://github.com/bkuri/vpype-vfab)
- **vfab**: [github.com/bkuri/plotty](https://github.com/bkuri/vfab)  
- **vpype**: [github.com/abey79/vpype](https://github.com/abey79/vpype)
- **vsketch**: [github.com/abey79/vsketch](https://github.com/abey79/vsketch)

## 📈 Changelog

### [v0.3.0] - 2025-11-12 (Current)
- ✨ **Documentation Restructure**: Quick start, modular docs, progressive disclosure
- 🛡️ **Advanced Error Handling**: Retry logic, recovery hints, user-friendly messages
- 📚 **Production Documentation**: Comprehensive guides and troubleshooting
- 🚀 **Publishing Pipeline**: Automated PyPI and GitHub release workflows

### [v0.2.0] - 2025-11-12
- ✨ **Interactive Pen Mapping**: Multi-pen designs with YAML persistence
- 🔧 **Complete Database Methods**: Full CRUD operations for job management
- 📊 **Enhanced vfab-queue**: Interactive features and priority support

### [v0.1.0] - 2025-11-12
- 🎉 **Initial Release**: Core commands and basic vfab integration

---

**Ready to start? Begin with the [Quick Start Guide](docs/quickstart.md)! 🚀**