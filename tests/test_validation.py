from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from coffee_dependency_tracker.cli import main


class ValidationTests(unittest.TestCase):
    def test_add_rejects_non_positive_cups(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            main(["add", "--cups", "0"])

        self.assertEqual(ctx.exception.code, 2)

    def test_add_rejects_future_timestamp(self) -> None:
        future = (datetime.now() + timedelta(days=1)).isoformat(timespec="seconds")

        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as ctx:
            main(["add", "--at", future])

        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("Timestamp cannot be in the future", stderr.getvalue())

    def test_export_requires_force_when_output_exists(self) -> None:
        with TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "coffee.json"
            export_path = Path(tmpdir) / "coffee.csv"
            data_path.write_text(
                "[{\"timestamp\": \"2026-06-02T08:15:00\", \"cups\": 1, \"note\": \"\", \"source\": \"\"}]",
                encoding="utf-8",
            )
            export_path.write_text("already here", encoding="utf-8")

            stderr = StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as ctx:
                main(["--data", str(data_path), "export", "--out", str(export_path)])

            self.assertEqual(ctx.exception.code, 2)
            self.assertIn("use --force to overwrite", stderr.getvalue())

    def test_export_can_overwrite_with_force(self) -> None:
        with TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "coffee.json"
            export_path = Path(tmpdir) / "coffee.csv"
            data_path.write_text(
                "[{\"timestamp\": \"2026-06-02T08:15:00\", \"cups\": 1, \"note\": \"\", \"source\": \"\"}]",
                encoding="utf-8",
            )
            export_path.write_text("already here", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                main(["--data", str(data_path), "export", "--out", str(export_path), "--force"])

            self.assertIn("Exported 1 entries", stdout.getvalue())
            self.assertNotEqual(export_path.read_text(encoding="utf-8"), "already here")

    def test_since_until_invalid(self) -> None:
        with TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "coffee.json"
            data_path.write_text("[]", encoding="utf-8")

            stderr = StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as ctx:
                main(["--data", str(data_path), "stats", "--since", "2026-06-03", "--until", "2026-06-01"])

            self.assertEqual(ctx.exception.code, 2)
            self.assertIn("--since must be on or before --until", stderr.getvalue())

    def test_days_must_be_positive(self) -> None:
        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as ctx:
            main(["stats", "--days", "0"])

        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("must be greater than 0", stderr.getvalue())

    def test_limit_must_be_positive(self) -> None:
        with TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "coffee.json"
            data_path.write_text("[]", encoding="utf-8")

            stderr = StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as ctx:
                main(["--data", str(data_path), "list", "--limit", "0"])

            self.assertEqual(ctx.exception.code, 2)
            self.assertIn("must be greater than 0", stderr.getvalue())