from __future__ import annotations

import io
import subprocess
import tarfile
from dataclasses import dataclass
from pathlib import Path

DISALLOWED_SUFFIXES = {
    ".doc",
    ".docx",
    ".pdf",
    ".xls",
    ".xlsx",
    ".nc",
    ".mat",
    ".m",
    ".kml",
    ".kmz",
}

BANNED_TERMS = {
    "disser" + "tation",
    "done" + ".docx",
    "ex" + "eter",
    "m" + "sc",
    "the" + "sis",
    "\u683c\u5f0f\u8981\u6c42",
    "\u8bba\u6587",
    "\u8f85\u5bfc",
}


@dataclass(frozen=True)
class ReleaseAuditResult:
    mode: str
    checked_files: int
    findings: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


def audit_release(root: str | Path = ".", *, mode: str = "tracked") -> ReleaseAuditResult:
    root_path = Path(root)
    if mode == "tracked":
        files = _tracked_files(root_path)
        return _audit_named_payloads(mode, files)
    if mode == "archive":
        files = _archive_files(root_path)
        return _audit_named_payloads(mode, files)
    raise ValueError("mode must be 'tracked' or 'archive'")


def format_audit_result(result: ReleaseAuditResult) -> str:
    status = "PASS" if result.passed else "FAIL"
    lines = [f"{status}: release audit ({result.mode}) checked {result.checked_files} files"]
    lines.extend(f"- {finding}" for finding in result.findings)
    return "\n".join(lines)


def _tracked_files(root: Path) -> list[tuple[str, bytes]]:
    completed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    payloads: list[tuple[str, bytes]] = []
    for name in completed.stdout.splitlines():
        path = root / name
        if path.is_file():
            payloads.append((name, path.read_bytes()))
    return payloads


def _archive_files(root: Path) -> list[tuple[str, bytes]]:
    completed = subprocess.run(
        ["git", "archive", "--format=tar", "HEAD"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
    )
    payloads: list[tuple[str, bytes]] = []
    with tarfile.open(fileobj=io.BytesIO(completed.stdout), mode="r:") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            handle = archive.extractfile(member)
            if handle is None:
                continue
            payloads.append((member.name, handle.read()))
    return payloads


def _audit_named_payloads(mode: str, files: list[tuple[str, bytes]]) -> ReleaseAuditResult:
    findings: list[str] = []
    for name, payload in files:
        suffix = Path(name).suffix.lower()
        if suffix in DISALLOWED_SUFFIXES:
            findings.append(f"disallowed release file type: {name}")
        lowered_name = name.lower()
        for term in sorted(BANNED_TERMS):
            if term.lower() in lowered_name:
                findings.append(f"banned public term '{term}' found in path {name}")
        decoded = _decode_text(payload)
        if decoded is None:
            continue
        lowered = decoded.lower()
        for term in sorted(BANNED_TERMS):
            if term.lower() in lowered:
                findings.append(f"banned public term '{term}' found in {name}")
    return ReleaseAuditResult(mode=mode, checked_files=len(files), findings=tuple(findings))


def _decode_text(payload: bytes) -> str | None:
    if b"\x00" in payload[:2048]:
        return None
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return None
