# vpype-plotty Quick Start

Get up and running with vpype-plotty in 5 minutes. This guide gets you from installation to your first plot.

## 🚀 Installation (2 commands)

```bash
# Install the plugin
pipx inject vpype vpype-plotty

# Verify installation
vpype --help | grep plotty
```

> **Note**: If you use vsketch instead of vpype:
> ```bash
> pipx inject vsketch vpype-plotty
> ```

## 🎨 Your First Plot (3 commands)

```bash
# 1. Create a simple test design
vpype circle --radius 5cm

# 2. Add to ploTTY queue
vpype plotty-add --name my_first_plot --queue

# 3. Check the status
vpype plotty-status
```

That's it! Your design is now in the ploTTY queue and ready to plot.

## 📊 What Just Happened?

1. **Created Design**: Made a 5cm circle
2. **Added to Queue**: Sent it to ploTTY with auto-generated name
3. **Checked Status**: Verified it's in the queue

## 🔄 Next Steps

### Try Different Designs

```bash
# Random generative art
vpype rand --seed 123 plotty-add --name random_art --queue

# Load existing SVG
vpype read my_design.svg plotty-add --name my_design --queue

# Geometric pattern
vpype rect --width 10cm --height 15cm plotty-add --name rectangle --queue
```

### Common Options

```bash
# Specify job name
vpype plotty-add --name my_custom_name

# Use high-quality preset
vpype plotty-add --name detailed --preset hq

# Different paper size
vpype plotty-add --name large --paper A3

# Don't auto-queue (just add)
vpype plotty-add --name draft --no-queue
```

### Job Management

```bash
# List all jobs
vpype plotty-list

# Queue an existing job
vpype plotty-queue --name my_design

# Check specific job
vpype plotty-status --name my_design
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
| `plotty-add` | Add design to ploTTY | `vpype plotty-add --name test --queue` |
| `plotty-queue` | Queue existing job | `vpype plotty-queue --name test` |
| `plotty-status` | Check job status | `vpype plotty-status --name test` |
| `plotty-list` | List all jobs | `vpype plotty-list --format table` |

## 🆘 Need Help?

```bash
# Get help for any command
vpype plotty-add --help
vpype plotty-queue --help
vpype plotty-status --help
vpype plotty-list --help

# Check versions
vpype --version
python --version
```

## ✅ Success!

You've successfully:
- ✅ Installed vpype-plotty
- ✅ Created your first design
- ✅ Added it to ploTTY
- ✅ Checked its status

Ready for more? Start with the [Basic Usage Guide](docs/basic-usage.md).

---

**Happy plotting! 🎉**