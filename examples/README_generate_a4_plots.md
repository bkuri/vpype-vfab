# Configurable Plot Generation Script

This script generates configurable-sized plots using vsketch + vpype-vfab + plotty workflow.

## Usage

### Basic Usage
```bash
python examples/generate_vsketch_plots.py
```

### With Custom Parameters
```bash
python examples/generate_vsketch_plots.py \
  -n 5 \
  -s a3 \
  -W ~/custom-vfab-workspace \
  --preset hq \
  -C cat,dog,house \
  -O ./my_plots \
  --queue
```

### Generate Single Plot
```bash
python examples/generate_vsketch_plots.py -n 1 -s letter
```

### Generate Plots Without Queuing (Default)
```bash
# Generate plots but don't queue them (creates NEW jobs)
python examples/generate_vsketch_plots.py -n 3 -s a4
```

### Generate and Queue Plots
```bash
# Generate plots and queue them immediately (creates QUEUED jobs)
python examples/generate_vsketch_plots.py -n 3 -s a4 --queue
python examples/generate_vsketch_plots.py -n 3 -s a4 -Q  # short version
```

### Generate Many Plots with Different Page Sizes
```bash
# A3 plots for larger format
python examples/generate_vsketch_plots.py -n 10 -s a3 --preset fast --queue

# Letter size plots for US standard
python examples/generate_vsketch_plots.py -n 3 -s letter

# A5 plots for smaller format
python examples/generate_vsketch_plots.py -n 5 -s a5
```

### With Verbose Output
```bash
python examples/generate_vsketch_plots.py -V -n 1 --queue
```

### Using Short Options
```bash
# Quick and concise with all short options
python examples/generate_vsketch_plots.py -n 3 -s a4 -C "cat,dog,tree" -F "0.5,1.0" -V -O ./plots -Q
```

## Generated Plots

The script creates multiple generative art pieces in a rotating pattern:

1. **QuickDraw Plot** - Grid of Google Quick Draw dataset images
2. **Schotter Plot** - Georg Nees' generative art with random square distortions  
3. **RandomFlower Plot** - Noise-based generative flower patterns

The pattern repeats if you request more than 3 plots, cycling through these types with different parameters.

## Command Line Options

### Core Options
- `-n, --num-plots`: Number of plots to generate (min: 1, default: 1)
- `-s, --page-size`: Page size for plots (default: a4, e.g., a3, a4, a5, letter, legal)
- `-W, --workspace`: vfab workspace path (default: `~/vfab-workspace`)
- `-O, --output-dir`: Directory to save SVG files (default: `/tmp/vsketch_plots_<timestamp>`)

### Plot Configuration
- `-C, --quickdraw-categories`: QuickDraw categories (comma-separated, default: `cat,dog,house`)
- `-F, --schotter-fuzziness`: Schotter fuzziness levels (comma-separated, default: `0.5,1.0,1.5`)
- `--preset`: vfab preset - `fast`, `default`, or `hq` (default: `fast`)
- `-Q, --queue`: Queue jobs for plotting (default: jobs are created in NEW state)

### Utility Options
- `-V, --verbose`: Show vsketch/vpype/plotty commands being executed
- `-v, --version`: Show program version number
- `-h, --help`: Show help message

## Requirements

- `vsketch` - For generative art creation
- `vpype-vfab` - For vfab integration
- `vfab` - For plotter management (optional, script works in standalone mode)

## Example Output

```
🚀 Starting Plot Generation Workflow
==================================================
📁 Workspace: /home/bk/vfab-workspace
📁 Output directory: /tmp/vsketch_plots_1763232252
⚙️  Preset: fast
📋 Auto-queue: True
📊 Number of plots: 1
📄 Page size: a4

📐 Plot 1/1: quickdraw_cat_1

🎨 Generating QuickDraw plot: cat
🔧 Executing vpype command: linemerge linesimplify reloop linesort
💾 Saved SVG: /tmp/vsketch_plots_1763232252/quickdraw_cat_1.svg
🔧 Executing vfab command: vfab-add --name quickdraw_cat_1 --preset fast --workspace workspace --queue
✅ Added to vfab: quickdraw_cat_1 (preset: fast, queued: True)

==================================================
📊 Generation Summary:
✅ Successful: 1 jobs
   - quickdraw_cat_1
```

### Verbose Output Example

When using `--verbose`, you'll see the actual commands being executed:

```
🔧 Executing vpype command: linemerge linesimplify reloop linesort
🔧 Executing vfab command: vfab-add --name quickdraw_cat_1 --preset fast --workspace /home/bk/vfab-workspace
```

### Job States

The script creates jobs in different vfab states:

- **NEW state** (default): Jobs are created but not queued for plotting
- **QUEUED state** (with `--queue`): Jobs are automatically queued for plotting

Use `--queue` when you want to start plotting immediately, or omit it to review jobs first and queue them later with `vpype plotty-queue`.

## Verification

After running the script, you can check the vfab queue with:

```bash
vpype plotty-list --format table
```

And monitor job progress with:

```bash
vpype plotty-monitor --follow
```