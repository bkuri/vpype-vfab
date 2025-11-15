# vpype-vfab Quick Start

Get up and running with vpype-vfab in 5 minutes. This guide gets you from installation to your first plot.

## 🚀 Installation (2 commands)

```bash
# Install the plugin
pipx inject vpype vpype-vfab

# Verify installation
vpype --help | grep plotty
```

> **Note**: If you use vsketch instead of vpype:
> ```bash
> pipx inject vsketch vpype-vfab
> ```

## 🎨 Your First Plot (3 commands)

```bash
# 1. Create a simple test design
vpype circle --radius 5cm

# 2. Add to vfab queue
vpype vfab-add --name my_first_plot --queue

# 3. Check the status
vpype vfab-status
```

That's it! Your design is now in the vfab queue and ready to plot.

## 📊 What Just Happened?

1. **Created Design**: Made a 5cm circle
2. **Added to Queue**: Sent it to vfab with auto-generated name
3. **Checked Status**: Verified it's in the queue

## 🔄 Next Steps

### Try Different Designs

```bash
# Random generative art
vpype rand --seed 123 vfab-add --name random_art --queue

# Load existing SVG
vpype read my_design.svg vfab-add --name my_design --queue

# Geometric pattern
vpype rect --width 10cm --height 15cm vfab-add --name rectangle --queue
```

### Common Options

```bash
# Specify job name
vpype vfab-add --name my_custom_name

# Use high-quality preset
vpype vfab-add --name detailed --preset hq

# Different paper size
vpype vfab-add --name large --paper A3

# Don't auto-queue (just add)
vpype vfab-add --name draft --no-queue
```

### Job Management

```bash
# List all jobs
vpype vfab-list

# Queue an existing job
vpype vfab-queue --name my_design

# Check specific job
vpype vfab-status --name my_design
```

## 📚 Learn More

Now that you're up and running, dive deeper:

- 📖 **[Basic Usage Guide](basic-usage.md)** - Core commands and workflows
- 🎨 **[vsketch Integration](vsketch-integration.md)** - Generative art workflows
- 🔧 **[Configuration](configuration.md)** - Workspace and presets
- 🚨 **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## 🎯 Quick Reference

| Command | What it does | Example |
|---------|--------------|---------|
| `vfab-add` | Add design to vfab | `vpype vfab-add --name test --queue` |
| `vfab-queue` | Queue existing job | `vpype vfab-queue --name test` |
| `vfab-status` | Check job status | `vpype vfab-status --name test` |
| `vfab-list` | List all jobs | `vpype vfab-list --format table` |

## 🆘 Need Help?

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

## ✅ Success!

You've successfully:
- ✅ Installed vpype-vfab
- ✅ Created your first design
- ✅ Added it to vfab
- ✅ Checked its status

Ready for more? Start with the [Basic Usage Guide](docs/basic-usage.md).

---

**Happy plotting! 🎉**