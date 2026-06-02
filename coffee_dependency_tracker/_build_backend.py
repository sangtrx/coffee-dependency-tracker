from __future__ import annotations

import base64
import csv
import hashlib
import re
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "coffee_dependency_tracker"
DISTRIBUTION_NAME = "coffee-dependency-tracker"
WHEEL_TAG = "py3-none-any"


def _read_version() -> str:
    init_path = PROJECT_ROOT / PACKAGE_NAME / "__init__.py"
    match = re.search(r'^__version__ = "([^"]+)"$', init_path.read_text(encoding="utf-8"), re.MULTILINE)
    if not match:
        raise RuntimeError("Unable to determine package version from __init__.py")
    return match.group(1)


VERSION = _read_version()


def _normalize_distribution_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower().replace("-", "_")


def _dist_info_dir() -> str:
    return f"{_normalize_distribution_name(DISTRIBUTION_NAME)}-{VERSION}.dist-info"


def _wheel_name() -> str:
    return f"{_normalize_distribution_name(DISTRIBUTION_NAME)}-{VERSION}-{WHEEL_TAG}.whl"


def _metadata_text() -> str:
    return "\n".join(
        [
            "Metadata-Version: 2.1",
            f"Name: {DISTRIBUTION_NAME}",
            f"Version: {VERSION}",
            "Summary: Log coffee consumption and get a tiny productivity forecast.",
            "Requires-Python: >=3.10",
            "",
        ]
    )


def _wheel_text() -> str:
    return "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: coffee-dependency-tracker._build_backend",
            "Root-Is-Purelib: true",
            f"Tag: {WHEEL_TAG}",
            "",
        ]
    )


def _entry_points_text() -> str:
    return "\n".join(
        [
            "[console_scripts]",
            "coffee-dependency-tracker = coffee_dependency_tracker.cli:main",
            "",
        ]
    )


def _top_level_text() -> str:
    return f"{PACKAGE_NAME}\n"


def _record_row(path: str, data: bytes | None) -> list[str]:
    if data is None:
        return [path, "", ""]
    digest = hashlib.sha256(data).digest()
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return [path, f"sha256={encoded}", str(len(data))]


def _iter_package_files() -> list[Path]:
    files: list[Path] = []
    for path in PROJECT_ROOT.joinpath(PACKAGE_NAME).rglob("*"):
        if path.is_dir():
            continue
        if path.name.endswith(".pyc") or path.name.startswith("."):
            continue
        files.append(path)
    return sorted(files)


def _write_wheel(wheel_directory: str, files: list[tuple[str, bytes]]) -> str:
    wheel_path = Path(wheel_directory) / _wheel_name()
    dist_info = _dist_info_dir()
    records: list[list[str]] = []

    with ZipFile(wheel_path, "w", compression=ZIP_DEFLATED) as zf:
        for rel_path, data in files:
            zf.writestr(rel_path, data)
            records.append(_record_row(rel_path, data))

        metadata_files = {
            f"{dist_info}/METADATA": _metadata_text().encode("utf-8"),
            f"{dist_info}/WHEEL": _wheel_text().encode("utf-8"),
            f"{dist_info}/entry_points.txt": _entry_points_text().encode("utf-8"),
            f"{dist_info}/top_level.txt": _top_level_text().encode("utf-8"),
        }
        for rel_path, data in metadata_files.items():
            zf.writestr(rel_path, data)
            records.append(_record_row(rel_path, data))

        record_path = f"{dist_info}/RECORD"
        record_buffer = tempfile.SpooledTemporaryFile(mode="w+", newline="", encoding="utf-8")
        writer = csv.writer(record_buffer)
        for row in records:
            writer.writerow(row)
        writer.writerow([record_path, "", ""])
        record_buffer.seek(0)
        record_data = record_buffer.read().encode("utf-8")
        zf.writestr(record_path, record_data)

    return wheel_path.name


def _editable_files() -> list[tuple[str, bytes]]:
    return [(f"{PACKAGE_NAME}.pth", f"{PROJECT_ROOT}\n".encode("utf-8"))]


def get_requires_for_build_wheel(config_settings: dict | None = None) -> list[str]:
    return []


def get_requires_for_build_editable(config_settings: dict | None = None) -> list[str]:
    return []


def prepare_metadata_for_build_wheel(metadata_directory: str, config_settings: dict | None = None) -> str:
    dist_info = Path(metadata_directory) / _dist_info_dir()
    dist_info.mkdir(parents=True, exist_ok=True)
    (dist_info / "METADATA").write_text(_metadata_text(), encoding="utf-8")
    (dist_info / "WHEEL").write_text(_wheel_text(), encoding="utf-8")
    (dist_info / "entry_points.txt").write_text(_entry_points_text(), encoding="utf-8")
    (dist_info / "top_level.txt").write_text(_top_level_text(), encoding="utf-8")
    return dist_info.name


def prepare_metadata_for_build_editable(metadata_directory: str, config_settings: dict | None = None) -> str:
    return prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def build_wheel(
    wheel_directory: str,
    config_settings: dict | None = None,
    metadata_directory: str | None = None,
) -> str:
    files = [(f"{PACKAGE_NAME}/{path.relative_to(PROJECT_ROOT / PACKAGE_NAME)}", path.read_bytes()) for path in _iter_package_files()]
    return _write_wheel(wheel_directory, files)


def build_editable(
    wheel_directory: str,
    config_settings: dict | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _write_wheel(wheel_directory, _editable_files())


def build_sdist(
    sdist_directory: str,
    config_settings: dict | None = None,
) -> str:
    raise NotImplementedError("sdist builds are not supported by this lightweight backend")