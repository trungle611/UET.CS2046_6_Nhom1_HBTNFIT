"""Chạy các kiểm tra ứng viên nộp bài, dừng ngay khi có bước thất bại."""

import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    npm = shutil.which("npm")
    if not npm:
        print("Không tìm thấy npm. Cài Node.js phù hợp rồi mở lại terminal.")
        return 1
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = ROOT / ".local" / "release-checks" / stamp
    output.mkdir(parents=True, exist_ok=False)
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    report = {
        "commit": commit,
        "working_tree_dirty": bool(status),
        "python": platform.python_version(),
        "steps": [],
        "passed": False,
    }
    commands = [
        ("backend-tests", [sys.executable, "-m", "pytest", "backend/tests", "-q"], ROOT),
        ("backend-lint", [sys.executable, "-m", "ruff", "check", "backend"], ROOT),
        ("backend-format", [sys.executable, "-m", "ruff", "format", "--check", "backend"], ROOT),
        ("frontend-install", [npm, "ci"], ROOT / "frontend"),
        ("frontend-format", [npm, "run", "format:check"], ROOT / "frontend"),
        ("frontend-build", [npm, "run", "build"], ROOT / "frontend"),
        ("evaluation-cli", [sys.executable, "-m", "backend.evaluation", "--help"], ROOT),
    ]
    environment = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    for name, command, directory in commands:
        print(f"Đang kiểm tra: {name}", flush=True)
        started = time.monotonic()
        log = output / (name + ".log")
        with log.open("wb") as stream:
            # Windows cần shell để thực thi npm.cmd; đối số npm ở đây là hằng số.
            result = subprocess.run(
                command,
                cwd=directory,
                stdout=stream,
                stderr=subprocess.STDOUT,
                env=environment,
                shell=os.name == "nt" and command[0] == npm,
            )
        report["steps"].append(
            {
                "name": name,
                "exit_code": result.returncode,
                "seconds": round(time.monotonic() - started, 2),
                "log": log.name,
            }
        )
        print(log.read_text(encoding="utf-8", errors="replace"), flush=True)
        if result.returncode:
            break
    report["passed"] = len(report["steps"]) == len(commands) and all(
        step["exit_code"] == 0 for step in report["steps"]
    )
    (output / "checks.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Minh chứng kiểm tra: {output}")
    print(
        "Tất cả kiểm tra đạt."
        if report["passed"]
        else "Có bước thất bại; xem log trước khi tạo tag."
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
