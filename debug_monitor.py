#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, "/home/bk/source/vpype-vfab")

# Set environment variables
os.environ["DISPLAY"] = ""
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import importlib.util
from unittest.mock import MagicMock, patch

# Import monitor module directly
spec = importlib.util.spec_from_file_location(
    "monitor", "/home/bk/source/vpype-vfab/vpype_plotty/monitor.py"
)
monitor = importlib.util.module_from_spec(spec)
sys.modules["monitor"] = monitor
spec.loader.exec_module(monitor)

# Test what actually gets called
mock_integration = MagicMock()
mock_integration.list_jobs.return_value = [
    {
        "id": "job1",
        "name": "test_job_1",
        "state": "running",
        "created_at": "2024-01-01T12:00:00Z",
    },
    {"id": "job2", "name": "test_job_2", "state": "completed"},
]
mock_integration.workspace = "/test/workspace"

m = monitor.SimplePlottyMonitor()
m.plotty_integration = mock_integration

with patch("click.echo") as mock_echo:
    m.update_display()

    print("All calls:")
    for i, call in enumerate(mock_echo.call_args_list):
        if call.args:
            print(f"  {i}: {call.args[0]}")
        else:
            print(f"  {i}: <no args>")
