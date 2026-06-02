from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from coffee_dependency_tracker.cli import main
from coffee_dependency_tracker.models import CoffeeEntry
from coffee_dependency_tracker.storage import load_entries, save_entries


SOURCE_ENTRIES = [
    CoffeeEntry.from_dict({"timestamp": "2026-06-01T09:00:00", "cups": 1, "note": "", "source": "desk"}),
    CoffeeEntry.from_dict({"timestamp": "2026-06-02T10:30:00", "cups": 2, "note": "pairing", "source": "cafe"}),
]


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

    def test_cli_import_from_json_replaces_existing_log(self) -> None:
        with TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "coffee.json"
            import_path = Path(tmpdir) / "import.json"

            save_entries([
                CoffeeEntry.from_dict({"timestamp": "2026-06-01T07:00:00", "cups": 3, "note": "old", "source": "home"}),
            ], data_path)
            save_entries(SOURCE_ENTRIES, import_path)

            stdout = StringIO()
            with redirect_stdout(stdout):
                main(["--data", str(data_path), "import", str(import_path)])

            self.assertIn(f"Imported {len(SOURCE_ENTRIES)} entries", stdout.getvalue())
            self.assertEqual(load_entries(data_path), SOURCE_ENTRIES)

    def test_cli_import_from_csv_replaces_existing_log(self) -> None:
        with TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "coffee.json"
            import_path = Path(tmpdir) / "import.csv"

            save_entries([
                CoffeeEntry.from_dict({"timestamp": "2026-06-01T07:00:00", "cups": 3, "note": "old", "source": "home"}),
            ], data_path)
            save_entries(SOURCE_ENTRIES, import_path)

            stdout = StringIO()
            with redirect_stdout(stdout):
                main(["--data", str(data_path), "import", str(import_path)])

            self.assertIn(f"Imported {len(SOURCE_ENTRIES)} entries", stdout.getvalue())
            self.assertEqual(load_entries(data_path), SOURCE_ENTRIES)

    def test_cli_import_empty_source_clears_existing_log(self) -> None:
        with TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "coffee.json"
            import_path = Path(tmpdir) / "empty.json"

            save_entries([
                CoffeeEntry.from_dict({"timestamp": "2026-06-01T07:00:00", "cups": 3, "note": "old", "source": "home"}),
            ], data_path)
            import_path.write_text("[]", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                main(["--data", str(data_path), "import", str(import_path)])

            self.assertIn("Imported 0 entries", stdout.getvalue())
            self.assertEqual(data_path.read_text(encoding="utf-8"), "[]")

    def test_cli_import_nonexistent_path_reports_zero(self) -> None:
        with TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "coffee.json"
            import_path = Path(tmpdir) / "does_not_exist.json"

            stdout = StringIO()
            with redirect_stdout(stdout):
                main(["--data", str(data_path), "import", str(import_path)])

            self.assertIn("Imported 0 entries", stdout.getvalue())

    def test_cli_import_malformed_json_reports_zero(self) -> None:
        with TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "coffee.json"
            import_path = Path(tmpdir) / "bad.json"
            import_path.write_text("{ not: valid json }", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                main(["--data", str(data_path), "import", str(import_path)])

            self.assertIn("Imported 0 entries", stdout.getvalue())

    def test_cli_export_csv_format_writes_csv(self) -> None:
        with TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "coffee.json"
            data_entries = [
                CoffeeEntry.from_dict({"timestamp": "2026-06-01T09:00:00", "cups": 1, "note": "", "source": "desk"}),
            ]
            save_entries(data_entries, data_path)

            out_path = Path(tmpdir) / "out.csv"
            stdout = StringIO()
            with redirect_stdout(stdout):
                main(["--data", str(data_path), "export", "--out", str(out_path), "--force"]) 

            self.assertTrue(out_path.exists())
            text = out_path.read_text(encoding="utf-8")
            self.assertIn("timestamp,cups,note,source", text)