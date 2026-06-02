from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from coffee_dependency_tracker.cli import main


class CliTests(unittest.TestCase):
    def test_cli_add_list_and_report_flow(self) -> None:
        with TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "coffee.json"

            add_buffer = StringIO()
            with redirect_stdout(add_buffer):
                main([
                    "--data",
                    str(data_path),
                    "add",
                    "--cups",
                    "2",
                    "--note",
                    "launch prep",
                    "--source",
                    "home",
                    "--at",
                    "2026-06-02T08:15:00",
                ])

            list_buffer = StringIO()
            with redirect_stdout(list_buffer):
                main(["--data", str(data_path), "list", "--limit", "5"])

            report_buffer = StringIO()
            with redirect_stdout(report_buffer):
                main(["--data", str(data_path), "report", "--days", "1", "--no-chart"])

            self.assertIn("Logged 2.0 cup(s)", add_buffer.getvalue())
            self.assertIn("2026-06-02 08:15: 2.0 cup(s) (home) — launch prep", list_buffer.getvalue())
            self.assertIn("Coffee report", report_buffer.getvalue())
            self.assertIn("Forecast (next day):", report_buffer.getvalue())