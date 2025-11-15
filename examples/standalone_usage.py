"""Standalone usage example."""

import subprocess
import sys


def run_command(cmd, description):
    """Run a command and handle the result."""
    print(f"\n{'=' * 50}")
    print(f"Example: {description}")
    print(f"Command: {cmd}")
    print("=" * 50)

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print("✓ Success!")
        if result.stdout:
            print(result.stdout)
    else:
        print("✗ Error!")
        if result.stderr:
            print(result.stderr)

    return result.returncode == 0


def main():
    """Demonstrate standalone vpype-plotty usage."""
    print("vpype-plotty Standalone Usage Examples")
    print("=====================================")

    # Check if vpype-plotty is available
    if not run_command(
        "vpype --help | grep plotty", "Checking vpype-plotty installation"
    ):
        print("\n❌ vpype-plotty not found. Please install it first:")
        print("pipx inject vpype vpype-plotty")
        sys.exit(1)

    # Example 1: Create simple generative art and add to vfab
    run_command(
        "vpype rand --seed 42 linemerge linesimplify reloop linesort vfab-add --name example_1 --preset fast",
        "Create random art and add to vfab",
    )

    # Example 2: Create more complex art with high-quality preset
    run_command(
        "vpype rand --seed 123 repeat 3 transform rotate 120 linemerge linesimplify reloop linesort vfab-add --name example_2 --preset hq --queue",
        "Create complex art with high-quality preset and auto-queue",
    )

    # Example 3: Check job status
    run_command("vpype plotty-status", "Check all job statuses")

    # Example 4: List queued jobs
    run_command(
        "vpype vfab-list --state QUEUED --format table",
        "List queued jobs in table format",
    )

    # Example 5: Check specific job
    run_command(
        "vpype plotty-status --name example_1 --format json",
        "Check specific job status in JSON format",
    )

    # Example 6: Queue a job manually
    run_command(
        "vpype plotty-queue --name example_1 --priority 2", "Queue job with priority 2"
    )

    # Example 7: List all jobs with limit
    run_command(
        "vpype vfab-list --limit 5 --format table",
        "List up to 5 jobs in table format",
    )

    print(f"\n{'=' * 50}")
    print("Examples complete!")
    print("Check your vfab workspace for the created jobs.")
    print("Default workspace: ~/vfab-workspace")
    print("=" * 50)


if __name__ == "__main__":
    main()
