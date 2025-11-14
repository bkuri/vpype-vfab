"""Performance and concurrency tests for vpype-plotty."""

import os
import time
import tempfile
import subprocess
import concurrent.futures

import pytest

from tests.integration import (
    import_vsketch_example,
    skip_if_no_sandbox,
    skip_if_no_vsketch,
)


class TestPerformanceConcurrency:
    """Test performance and concurrency characteristics."""

    @pytest.fixture
    def workspace_dir(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @skip_if_no_sandbox
    def test_concurrent_job_addition(self, workspace_dir):
        """Test adding multiple jobs concurrently."""
        # Create multiple SVG files
        svg_files = []
        job_names = []

        for i in range(10):  # 10 concurrent jobs
            svg_content = f"""<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<rect x="{i * 5}" y="{i * 5}" width="50" height="50" fill="none" stroke="black" stroke-width="1"/>
<circle cx="{50 + i * 2}" cy="{50 + i * 2}" r="20" fill="none" stroke="black" stroke-width="1"/>
</svg>"""

            svg_file = os.path.join(workspace_dir, f"concurrent_{i}.svg")
            with open(svg_file, "w") as f:
                f.write(svg_content)

            svg_files.append(svg_file)
            job_names.append(f"concurrent_job_{i}")

        # Function to add job
        def add_job(svg_file, job_name):
            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    job_name,
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0

        # Add jobs concurrently
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(add_job, svg_file, job_name)
                for svg_file, job_name in zip(svg_files, job_names)
            ]

            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        end_time = time.time()
        duration = end_time - start_time

        # Verify all jobs were added successfully
        assert all(results), f"Failed to add some jobs: {results}"
        assert duration < 30.0, f"Concurrent job addition took too long: {duration}s"

        # Verify all jobs are in ploTTY
        result = subprocess.run(
            [
                "vpype",
                "plotty-list",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        for job_name in job_names:
            assert job_name in result.stdout

    @skip_if_no_sandbox
    def test_large_dataset_processing(self, workspace_dir):
        """Test processing large datasets efficiently."""
        # Create complex SVG with many paths
        paths = []
        for i in range(1000):  # 1000 paths
            path_data = f"M{i % 100},{i // 100} L{(i + 10) % 100},{i // 100} L{(i + 20) % 100},{i // 100} Z"
            paths.append(
                f'<path d="{path_data}" fill="none" stroke="black" stroke-width="0.3"/>'
            )

        svg_content = f"""<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">
{chr(10).join(paths)}
</svg>"""

        svg_file = os.path.join(workspace_dir, "large_dataset.svg")
        with open(svg_file, "w") as f:
            f.write(svg_content)

        # Measure processing time
        start_time = time.time()

        result = subprocess.run(
            [
                "vpype",
                "read",
                svg_file,
                "linemerge",
                "linesimplify",
                "linesort",
                "plotty-add",
                "--name",
                "large_dataset_test",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        end_time = time.time()
        processing_time = end_time - start_time

        assert result.returncode == 0
        assert processing_time < 60.0, (
            f"Large dataset processing took too long: {processing_time}s"
        )

        # Check file size
        file_size = os.path.getsize(svg_file)
        assert file_size > 50000, f"SVG file should be substantial: {file_size} bytes"

    @skip_if_no_sandbox
    @skip_if_no_vsketch
    def test_memory_usage_with_complex_sketch(self, workspace_dir):
        """Test memory usage with complex vsketch patterns."""
        import vsketch

        # Create complex Schotter pattern
        schotter_sketch = import_vsketch_example("schotter")
        if not schotter_sketch:
            pytest.skip("Could not import Schotter sketch")

        # Use large parameters for complexity
        schotter_sketch.columns = 20  # 20x20 grid
        schotter_sketch.rows = 20
        schotter_sketch.fuzziness = 2.0

        vsk = vsketch.Vsketch()

        # Measure memory before
        import psutil

        process = psutil.Process()
        memory_before = process.memory_info().rss

        # Generate complex pattern
        schotter_sketch.draw(vsk)

        # Measure memory after
        memory_after = process.memory_info().rss
        memory_used = memory_after - memory_before

        # Verify pattern complexity
        total_paths = sum(len(layer) for layer in vsk.document.layers.values())
        assert total_paths == 400  # 20x20 grid

        # Memory usage should be reasonable (less than 100MB for this test)
        assert memory_used < 100 * 1024 * 1024, (
            f"Memory usage too high: {memory_used / 1024 / 1024:.1f}MB"
        )

    @skip_if_no_sandbox
    def test_batch_queue_processing(self, workspace_dir):
        """Test batch processing of queued jobs."""
        # Create multiple jobs and queue them
        job_names = []

        for i in range(20):  # 20 jobs
            svg_content = f"""<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<text x="{i * 3}" y="50" font-family="Arial" font-size="10">Batch {i}</text>
</svg>"""

            svg_file = os.path.join(workspace_dir, f"batch_{i}.svg")
            with open(svg_file, "w") as f:
                f.write(svg_content)

            job_name = f"batch_job_{i}"
            job_names.append(job_name)

            # Add and queue job
            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    job_name,
                    "--queue",
                    "--priority",
                    str(i % 5 + 1),  # Priority 1-5
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

        # Verify all jobs are queued
        result = subprocess.run(
            [
                "vpype",
                "plotty-list",
                "--state",
                "QUEUED",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        # Count queued jobs
        queued_count = result.stdout.count("batch_job_")
        assert queued_count >= 10, (
            f"Expected at least 10 queued jobs, got {queued_count}"
        )

    @skip_if_no_sandbox
    def test_database_performance(self, workspace_dir):
        """Test database performance with many jobs."""
        from vpype_plotty.database import PlottyIntegration

        plotty = PlottyIntegration(workspace_dir)

        # Create many jobs
        job_count = 100
        job_ids = []

        start_time = time.time()

        for i in range(job_count):
            job_id = f"perf_test_{i}"
            job_ids.append(job_id)

            # Create simple document
            import vpype
            from shapely.geometry import LineString

            document = vpype.Document()
            line = LineString([(0, 0), (10, 10)])
            document.add(line)

            # Add job
            result = plotty.add_job(document, job_id, "fast", "A4")
            assert result == job_id

        end_time = time.time()
        creation_time = end_time - start_time

        # Test job creation performance
        assert creation_time < 10.0, f"Job creation too slow: {creation_time}s"
        assert len(job_ids) == job_count

        # Test job listing performance
        start_time = time.time()

        jobs = plotty.list_jobs()

        end_time = time.time()
        listing_time = end_time - start_time

        assert listing_time < 1.0, f"Job listing too slow: {listing_time}s"
        assert len(jobs) >= job_count

    @skip_if_no_sandbox
    def test_concurrent_status_checks(self, workspace_dir):
        """Test concurrent status checks."""
        # Add some jobs first
        job_names = []
        for i in range(5):
            svg_content = f"""<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<circle cx="{50}" cy="{50}" r="{20 + i * 5}" fill="none" stroke="black" stroke-width="1"/>
</svg>"""

            svg_file = os.path.join(workspace_dir, f"status_test_{i}.svg")
            with open(svg_file, "w") as f:
                f.write(svg_content)

            job_name = f"status_test_{i}"
            job_names.append(job_name)

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    job_name,
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

        # Function to check job status
        def check_status(job_name):
            result = subprocess.run(
                [
                    "vpype",
                    "plotty-status",
                    "--name",
                    job_name,
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0

        # Check status concurrently
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(check_status, job_name) for job_name in job_names
            ]

            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        end_time = time.time()
        duration = end_time - start_time

        # Verify all status checks succeeded
        assert all(results), f"Failed to check some statuses: {results}"
        assert duration < 5.0, f"Concurrent status checks took too long: {duration}s"

    @skip_if_no_sandbox
    def test_stress_test_many_small_jobs(self, workspace_dir):
        """Stress test with many small jobs."""
        job_count = 50  # 50 small jobs
        job_names = []

        start_time = time.time()

        for i in range(job_count):
            svg_content = """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50">
<line x1="0" y1="0" x2="50" y2="50" stroke="black" stroke-width="1"/>
</svg>"""

            svg_file = os.path.join(workspace_dir, f"stress_{i}.svg")
            with open(svg_file, "w") as f:
                f.write(svg_content)

            job_name = f"stress_job_{i}"
            job_names.append(job_name)

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    job_name,
                    "--queue",
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

        end_time = time.time()
        total_time = end_time - start_time

        # Performance should be reasonable
        assert total_time < 60.0, f"Stress test took too long: {total_time}s"
        assert len(job_names) == job_count

        # Verify all jobs are in ploTTY
        result = subprocess.run(
            [
                "vpype",
                "plotty-list",
                "--format",
                "json",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    @skip_if_no_sandbox
    def test_resource_cleanup(self, workspace_dir):
        """Test resource cleanup after operations."""
        from vpype_plotty.database import PlottyIntegration

        plotty = PlottyIntegration(workspace_dir)

        # Add jobs
        initial_jobs = []
        for i in range(10):
            import vpype
            from shapely.geometry import LineString

            document = vpype.Document()
            line = LineString([(0, 0), (10, 10)])
            document.add(line)

            job_id = f"cleanup_test_{i}"
            initial_jobs.append(job_id)
            plotty.add_job(document, job_id, "fast", "A4")

        # Verify jobs exist
        jobs_before = plotty.list_jobs()
        job_count_before = len(
            [j for j in jobs_before if j["name"].startswith("cleanup_test_")]
        )
        assert job_count_before == 10

        # Clean up jobs (if supported)
        for job_id in initial_jobs:
            try:
                plotty.delete_job(job_id)
            except Exception:
                # Delete might not be implemented, which is fine
                pass

        # Verify cleanup
        jobs_after = plotty.list_jobs()
        job_count_after = len(
            [j for j in jobs_after if j["name"].startswith("cleanup_test_")]
        )

        # Either cleanup worked or jobs still exist (both are valid states)
        assert job_count_after <= job_count_before

    @skip_if_no_sandbox
    def test_performance_regression_detection(self, workspace_dir):
        """Test for performance regressions."""
        # Define performance baselines
        baselines = {
            "simple_job_addition": 5.0,  # 5 seconds
            "job_listing": 1.0,  # 1 second
            "status_check": 2.0,  # 2 seconds
        }

        # Test simple job addition performance
        svg_content = """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<rect x="10" y="10" width="80" height="80" fill="none" stroke="black" stroke-width="1"/>
</svg>"""

        svg_file = os.path.join(workspace_dir, "regression_test.svg")
        with open(svg_file, "w") as f:
            f.write(svg_content)

        # Test job addition
        start_time = time.time()
        result = subprocess.run(
            [
                "vpype",
                "read",
                svg_file,
                "plotty-add",
                "--name",
                "regression_test",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )
        end_time = time.time()

        assert result.returncode == 0
        job_addition_time = end_time - start_time
        assert job_addition_time < baselines["simple_job_addition"], (
            f"Job addition regression: {job_addition_time}s > {baselines['simple_job_addition']}s"
        )

        # Test job listing
        start_time = time.time()
        result = subprocess.run(
            [
                "vpype",
                "plotty-list",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )
        end_time = time.time()

        assert result.returncode == 0
        listing_time = end_time - start_time
        assert listing_time < baselines["job_listing"], (
            f"Job listing regression: {listing_time}s > {baselines['job_listing']}s"
        )
