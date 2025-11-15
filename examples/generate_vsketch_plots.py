#!/usr/bin/env python3
"""
Generate configurable-sized plots using vsketch + vpype-plotty + plotty workflow.

This script creates multiple generative art pieces using vsketch examples,
optimizes them for plotting, and adds them to ploTTY queue automatically.
Supports various page sizes (A3, A4, A5, letter, legal, etc.).

The --categories parameter specifies which Google Quick Draw dataset categories to use
for QuickDraw plots (e.g., cat, dog, house, tree, etc.).
"""

import argparse
import sys
import time
from pathlib import Path
import subprocess

# Add vsketch examples to path
vsketch_path = Path(__file__).parent.parent / "sandbox" / "vsketch"
if vsketch_path.exists():
    sys.path.insert(0, str(vsketch_path))
    sys.path.insert(0, str(vsketch_path / "examples" / "quick_draw"))
    sys.path.insert(0, str(vsketch_path / "examples" / "schotter"))
    sys.path.insert(0, str(vsketch_path / "examples" / "random_flower"))

try:
    import vsketch
except ImportError:
    print("❌ vsketch not found. Please install it with: pip install vsketch")
    sys.exit(1)

try:
    from sketch_quick_draw import QuickDrawSketch
except ImportError:
    print("⚠️  QuickDraw sketch not found, will skip it")
    QuickDrawSketch = None

try:
    from sketch_schotter import SchotterSketch
except ImportError:
    print("⚠️  Schotter sketch not found, will skip it")
    SchotterSketch = None

try:
    from sketch_random_flower import RandomFlowerSketch
except ImportError:
    print("⚠️  RandomFlower sketch not found, will skip it")
    RandomFlowerSketch = None


def setup_workspace(workspace_path: str) -> str:
    """Setup and verify ploTTY workspace."""
    workspace = Path(workspace_path).expanduser()

    if not workspace.exists():
        print(f"📁 Creating ploTTY workspace: {workspace}")
        workspace.mkdir(parents=True, exist_ok=True)

    return str(workspace)


def create_output_dir(output_dir: str) -> Path:
    """Create output directory for SVG files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def finalize_with_plotty(
    vsk: vsketch.Vsketch,
    job_name: str,
    workspace: str,
    preset: str,
    queue: bool,
    save_svg: bool = True,
    output_dir: Path | None = None,
    verbose: bool = False,
) -> None:
    """Apply vpype optimization and add to ploTTY."""
    # Standard vpype optimization
    vpype_cmd = "linemerge linesimplify reloop linesort"
    if verbose:
        print(f"🔧 Executing vpype command: {vpype_cmd}")
    vsk.vpype(vpype_cmd)

    # Save SVG if requested
    if save_svg and output_dir:
        svg_path = output_dir / f"{job_name}.svg"
        vsk.save(str(svg_path))
        print(f"💾 Saved SVG: {svg_path}")

    # Build plotty-add command
    cmd = f"plotty-add --name {job_name} --preset {preset}"
    if workspace:
        cmd += f" --workspace {workspace}"
    if queue:
        cmd += " --queue"

    # Add to ploTTY
    if verbose:
        print(f"🔧 Executing ploTTY command: {cmd}")
    vsk.vpype(cmd)
    print(f"✅ Added to ploTTY: {job_name} (preset: {preset}, queued: {queue})")


def generate_quickdraw_plot(
    category: str,
    job_name: str,
    workspace: str,
    preset: str,
    queue: bool,
    output_dir: Path,
    page_size: str = "a4",
    verbose: bool = False,
) -> bool:
    """Generate QuickDraw plot."""
    if QuickDrawSketch is None:
        print("❌ QuickDraw sketch not available")
        return False

    print(f"\n🎨 Generating QuickDraw plot: {category}")

    try:
        # Create sketch instance
        sketch = QuickDrawSketch()
        sketch.category = category
        sketch.page_size = page_size
        sketch.landscape = False
        sketch.columns = 6  # Smaller grid for A4
        sketch.rows = 8
        sketch.layer_count = 1
        sketch.scale_factor = 2.5

        # Create vsketch instance
        vsk = vsketch.Vsketch()

        # Generate the sketch
        sketch.draw(vsk)

        # Finalize and add to ploTTY
        finalize_with_plotty(
            vsk, job_name, workspace, preset, queue, True, output_dir, verbose
        )

        return True

    except Exception as e:
        print(f"❌ Failed to generate QuickDraw plot: {e}")
        return False


def generate_schotter_plot(
    fuzziness: float,
    job_name: str,
    workspace: str,
    preset: str,
    queue: bool,
    output_dir: Path,
    page_size: str = "a4",
    verbose: bool = False,
) -> bool:
    """Generate Schotter plot."""
    if SchotterSketch is None:
        print("❌ Schotter sketch not available")
        return False

    print(f"\n🎨 Generating Schotter plot: fuzziness={fuzziness}")

    try:
        # Create sketch instance
        sketch = SchotterSketch()
        sketch.columns = 12
        sketch.rows = 22
        sketch.fuzziness = fuzziness

        # Create vsketch instance and set page size
        vsk = vsketch.Vsketch()
        vsk.size(page_size, landscape=False)

        # Generate the sketch
        sketch.draw(vsk)

        # Finalize and add to ploTTY
        finalize_with_plotty(
            vsk, job_name, workspace, preset, queue, True, output_dir, verbose
        )

        return True

    except Exception as e:
        print(f"❌ Failed to generate Schotter plot: {e}")
        return False


def generate_randomflower_plot(
    job_name: str,
    workspace: str,
    preset: str,
    queue: bool,
    output_dir: Path,
    page_size: str = "a4",
    verbose: bool = False,
) -> bool:
    """Generate RandomFlower plot."""
    if RandomFlowerSketch is None:
        print("❌ RandomFlower sketch not available")
        return False

    print("\n🎨 Generating RandomFlower plot")

    try:
        # Create sketch instance
        sketch = RandomFlowerSketch()
        sketch.num_line = 150  # Fewer lines for cleaner plot
        sketch.point_per_line = 80
        sketch.rdir_range = 0.4  # Smaller range for tighter pattern

        # Create vsketch instance and set page size
        vsk = vsketch.Vsketch()
        vsk.size(page_size, landscape=True)  # RandomFlower uses landscape

        # Generate the sketch
        sketch.draw(vsk)

        # Finalize and add to ploTTY
        finalize_with_plotty(
            vsk, job_name, workspace, preset, queue, True, output_dir, verbose
        )

        return True

    except Exception as e:
        print(f"❌ Failed to generate RandomFlower plot: {e}")
        return False


def check_vpype_plotty():
    """Check if vpype-plotty is available."""
    try:
        result = subprocess.run(["vpype", "--help"], capture_output=True, text=True)
        if "plotty" in result.stdout:
            return True
        else:
            print("❌ vpype-plotty plugin not found in vpype")
            print("Install with: pipx inject vpype vpype-plotty")
            return False
    except FileNotFoundError:
        print("❌ vpype not found. Please install it with: pip install vpype")
        return False


def show_job_status(workspace: str):
    """Show current ploTTY job status."""
    print("\n📊 Current ploTTY job status:")
    try:
        cmd = ["vpype", "plotty-list"]
        if workspace:
            cmd.extend(["--workspace", workspace])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Could not retrieve job status")
    except Exception as e:
        print(f"Error checking job status: {e}")


def generate_plot_configs(
    num_plots: int, categories: list, fuzziness_values: list, page_size: str
) -> list:
    """Generate plot configurations based on number of plots requested."""
    configs = []
    plot_types = ["quickdraw", "schotter", "randomflower"]

    for i in range(num_plots):
        plot_type = plot_types[i % len(plot_types)]

        if plot_type == "quickdraw":
            category = categories[i % len(categories)] if categories else "cat"
            config = {
                "type": "quickdraw",
                "params": category,
                "name": f"quickdraw_{category}_{i + 1}",
            }
        elif plot_type == "schotter":
            fuzziness = (
                fuzziness_values[i % len(fuzziness_values)] if fuzziness_values else 0.8
            )
            config = {
                "type": "schotter",
                "params": fuzziness,
                "name": f"schotter_{fuzziness}_{i + 1}",
            }
        else:  # randomflower
            config = {
                "type": "randomflower",
                "params": None,
                "name": f"randomflower_a4_{i + 1}",
            }

        configs.append(config)

    return configs


def main():
    """Main function to generate A4 plots."""
    parser = argparse.ArgumentParser(
        description="Generate configurable-sized plots using vsketch + vpype-plotty + plotty"
    )
    parser.add_argument(
        "--workspace",
        "-W",
        default="~/plotty-workspace",
        help="ploTTY workspace path (default: ~/plotty-workspace)",
    )
    parser.add_argument(
        "--preset",
        choices=["fast", "default", "hq"],
        default="fast",
        help="ploTTY preset (default: fast)",
    )
    parser.add_argument(
        "--queue", "-Q", action="store_true", help="Queue jobs for plotting"
    )
    parser.add_argument(
        "--quickdraw-categories",
        "-C",
        default="cat,dog,house",
        help="QuickDraw categories (comma-separated, default: cat,dog,house)",
    )
    parser.add_argument(
        "--schotter-fuzziness",
        "-F",
        default="0.5,1.0,1.5",
        help="Schotter fuzziness levels (comma-separated, default: 0.5,1.0,1.5)",
    )
    parser.add_argument(
        "--num-plots",
        "-n",
        type=int,
        default=1,
        help="Number of plots to generate (min: 1, default: 1)",
    )
    parser.add_argument(
        "--page-size",
        "-s",
        default="a4",
        help="Page size for plots (default: a4, e.g., a3, a4, a5, letter, legal)",
    )
    parser.add_argument(
        "--output-dir",
        "-O",
        help="Directory to save SVG files (default: /tmp/vsketch_plots_<timestamp>)",
    )
    parser.add_argument(
        "--verbose",
        "-V",
        action="store_true",
        help="Show vsketch/vpype/plotty commands being executed",
    )
    parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0.0")

    args = parser.parse_args()

    # Validate num_plots
    if args.num_plots < 1:
        print("❌ Error: --num-plots must be at least 1")
        sys.exit(1)

    # Parse comma-separated values
    categories = [c.strip() for c in args.quickdraw_categories.split(",") if c.strip()]
    fuzziness_values = [
        float(f.strip()) for f in args.schotter_fuzziness.split(",") if f.strip()
    ]

    queue = args.queue

    print("🚀 Starting Plot Generation Workflow")
    print("=" * 50)

    # Check dependencies
    if not check_vpype_plotty():
        sys.exit(1)

    # Setup workspace and output directory
    workspace = setup_workspace(args.workspace)

    # Set default output directory with timestamp if not provided
    if args.output_dir is None:
        output_dir = create_output_dir(f"/tmp/vsketch_plots_{int(time.time())}")
    else:
        output_dir = create_output_dir(args.output_dir)

    print(f"📁 Workspace: {workspace}")
    print(f"📁 Output directory: {output_dir}")
    print(f"⚙️  Preset: {args.preset}")
    print(f"📋 Auto-queue: {queue}")
    print(f"📊 Number of plots: {args.num_plots}")
    print(f"📄 Page size: {args.page_size}")

    successful_jobs = []
    failed_jobs = []

    # Generate plot configurations
    plot_configs = generate_plot_configs(
        args.num_plots, categories, fuzziness_values, args.page_size
    )

    for i, config in enumerate(plot_configs, 1):
        print(f"\n📐 Plot {i}/{args.num_plots}: {config['name']}")

        if config["type"] == "quickdraw":
            success = generate_quickdraw_plot(
                config["params"],
                config["name"],
                workspace,
                args.preset,
                queue,
                output_dir,
                args.page_size,
                args.verbose,
            )
        elif config["type"] == "schotter":
            success = generate_schotter_plot(
                config["params"],
                config["name"],
                workspace,
                args.preset,
                queue,
                output_dir,
                args.page_size,
                args.verbose,
            )
        elif config["type"] == "randomflower":
            success = generate_randomflower_plot(
                config["name"],
                workspace,
                args.preset,
                queue,
                output_dir,
                args.page_size,
                args.verbose,
            )
        else:
            success = False

        if success:
            successful_jobs.append(config["name"])
        else:
            failed_jobs.append(config["name"])

    # Summary
    print("\n" + "=" * 50)
    print("📊 Generation Summary:")
    print(f"✅ Successful: {len(successful_jobs)} jobs")
    for job in successful_jobs:
        print(f"   - {job}")

    if failed_jobs:
        print(f"❌ Failed: {len(failed_jobs)} jobs")
        for job in failed_jobs:
            print(f"   - {job}")

    # Show job status
    if successful_jobs:
        show_job_status(workspace)

    print(f"\n🎉 Workflow complete! Check {output_dir} for SVG files.")
    print(f"📋 ploTTY workspace: {workspace}")


if __name__ == "__main__":
    main()
