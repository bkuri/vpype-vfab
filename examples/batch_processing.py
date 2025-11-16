"""Batch processing example."""

import subprocess
import time


def generate_and_queue_sketches(seeds, base_name):
    """Generate multiple sketches and queue them all."""
    job_ids = []

    for seed in seeds:
        print(f"Processing seed {seed}...")

        # Generate sketch using vpype
        cmd = f"vpype rand --seed {seed} linemerge linesimplify reloop linesort"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"✗ Failed to generate sketch for seed {seed}: {result.stderr}")
            continue

        # Add to vfab
        cmd = f'vpype rand --seed {seed} linemerge linesimplify reloop linesort vfab-add --name "{base_name}_{seed}" --preset fast --queue'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✓ Queued job for seed {seed}")
            job_ids.append(f"{base_name}_{seed}")
        else:
            print(f"✗ Failed to queue seed {seed}: {result.stderr}")

        # Small delay to avoid overwhelming the system
        time.sleep(0.1)

    return job_ids


def monitor_jobs(job_ids):
    """Monitor job status."""
    print(f"\nMonitoring {len(job_ids)} jobs...")

    while job_ids:
        completed_jobs = []

        for job_id in job_ids:
            # Check job status
            cmd = f"vpype plotty-status --name {job_id} --format simple"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                status = result.stdout.strip()
                print(f"  {job_id}: {status}")

                if "COMPLETED" in status:
                    completed_jobs.append(job_id)
            else:
                print(f"  {job_id}: Status check failed")

        # Remove completed jobs
        for job_id in completed_jobs:
            job_ids.remove(job_id)

        if job_ids:
            print(f"Waiting for {len(job_ids)} jobs...")
            time.sleep(5)


def main():
    """Main batch processing workflow."""
    print("=== vpype-vfab Batch Processing Example ===\n")

    # Configuration
    base_name = "batch_sketch"
    seed_count = 5

    print(f"Generating {seed_count} sketches with base name '{base_name}'...")

    # Generate and queue sketches
    job_ids = generate_and_queue_sketches(range(seed_count), base_name)

    if not job_ids:
        print("No jobs were successfully queued.")
        return

    print(f"\nSuccessfully queued {len(job_ids)} jobs:")
    for job_id in job_ids:
        print(f"  - {job_id}")

    # Show current queue status
    print("\nCurrent queue status:")
    cmd = "vpype vfab-list --state QUEUED --format table"
    subprocess.run(cmd, shell=True)

    # Monitor jobs (optional)
    if input("\nMonitor job completion? (y/n): ").lower() == "y":
        monitor_jobs(job_ids)

    print("\nBatch processing complete!")


if __name__ == "__main__":
    main()
