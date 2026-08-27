#!/usr/bin/env python3
"""Run one full image build; retain local evidence even when the build fails."""

import argparse
import csv
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
TARGET = "agentos_cf_x86_64-aosp_current-userdebug"
GIB = 1024 ** 3
OVERRIDES = ("AGENTOS_TOTAL_MEMORY_KIB", "AGENTOS_FREE_DISK_KIB")
COMMAND = """set -eo pipefail
# AOSP envsetup is not required to be nounset-safe.
source build/envsetup.sh
lunch agentos_cf_x86_64-aosp_current-userdebug
get_abs_build_var PRODUCT_OUT > "$1/product-out.txt"
get_abs_build_var HOST_OUT > "$1/host-out.txt"
get_build_var BUILD_FINGERPRINT > "$1/build-fingerprint.txt"
get_build_var PLATFORM_VERSION > "$1/platform-version.txt"
m -j"$2"
"""


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def positive_integer(value):
    if not re.fullmatch(r"[1-9][0-9]{0,14}", str(value)):
        raise ValueError("expected a positive decimal integer, got {!r}".format(value))
    return int(value)


def filesystem(path):
    while not path.exists():
        path = path.parent
    return shutil.disk_usage(path)


def memory():
    return {key: int(value.split()[0]) * 1024
            for key, value in (line.split(":", 1)
                               for line in Path("/proc/meminfo").read_text().splitlines())
            if value.split()[-1] == "kB"}


def preflight(workspace, output, check_only):
    simulated = any(name in os.environ for name in OVERRIDES)
    if simulated and not check_only:
        raise ValueError("resource overrides are only allowed with --check-only")
    if simulated:
        if not all(name in os.environ for name in OVERRIDES):
            raise ValueError("simulated checks require both resource overrides")
        total, free = (positive_integer(os.environ[name]) * 1024 for name in OVERRIDES)
    else:
        if platform.system() != "Linux" or platform.machine() != "x86_64":
            raise ValueError("full AOSP builds require an x86-64 Linux host")
        total = memory()["MemTotal"]
        free = filesystem(output).free
    # ponytail: tolerate reserved RAM on nominal 64 GiB machines, not smaller hosts.
    if total < 60 * GIB:
        raise ValueError("use a 64 GiB-class host (at least 60 GiB visible RAM)")
    if free < 400 * GIB:
        raise ValueError("reserve at least 400 GiB free on the output filesystem AFTER sync")
    if check_only:
        print("{}resource checks passed; no image was built".format(
            "SIMULATED " if simulated else "AgentOS "))
        return
    if not (workspace / "build/envsetup.sh").is_file() or not (workspace / ".repo").is_dir():
        raise ValueError("AOSP checkout missing; run scripts/bootstrap.sh first")
    for command in ("bash", "git", "repo", "du", "lscpu"):
        if not shutil.which(command):
            raise ValueError("required command missing: " + command)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def logged(command, workspace, evidence):
    with (evidence / "build.log").open("ab") as log:
        subprocess.run(command, cwd=workspace, stdout=log, stderr=subprocess.STDOUT, check=True)


def pin_sources(workspace, evidence, name):
    logged(["repo", "manifest", "-r", "-o", str(evidence / name)], workspace, evidence)
    manifest = ET.parse(evidence / name).getroot()
    if manifest.findall("submanifest"):
        raise ValueError("submanifests require separate snapshots; this collector supports one manifest")
    projects = list(manifest.iter("project"))
    if not projects or not all(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", p.get("revision", ""))
                               for p in projects):
        raise ValueError("exported source manifest does not pin every project to a commit")
    if not any(p.get("path") == "vendor/agentos" for p in projects):
        raise ValueError("source manifest is missing vendor/agentos")
    logged(["repo", "forall", "-c", 'state=$(git status --porcelain --untracked-files=normal) || exit 1; '
            'if test -n "$state"; '
            'then printf "Dirty source: %s\\n" "$REPO_PATH"; exit 1; fi'], workspace, evidence)


def sizes(workspace, output):
    paths = {"workspace_including_nested_output": workspace, "repo": workspace / ".repo",
             "output": output}
    if os.environ.get("CCACHE_DIR"):
        paths["ccache"] = (workspace / os.environ["CCACHE_DIR"]).resolve()
    result = {}
    for name, path in paths.items():
        if path.exists():
            measured = subprocess.run(["du", "-sk", str(path)], capture_output=True, text=True)
            result[name] = (int(measured.stdout.split()[0]) * 1024
                            if measured.returncode == 0 else None)
    return result


def sample(workspace, output):
    mem = memory()
    source_disk, output_disk = filesystem(workspace), filesystem(output)
    return {"utc": utc_now(), "host_memory_used_bytes": mem["MemTotal"] - mem["MemAvailable"],
            "host_swap_used_bytes": mem["SwapTotal"] - mem["SwapFree"],
            "host_load_1m": os.getloadavg()[0],
            "source_fs_used_bytes": source_disk.used, "source_fs_free_bytes": source_disk.free,
            "output_fs_used_bytes": output_disk.used, "output_fs_free_bytes": output_disk.free}


def machine_details(output):
    return {"os": platform.system(), "kernel": platform.release(), "arch": platform.machine(),
            "logical_cpus": os.cpu_count(), "available_cpus": len(os.sched_getaffinity(0)),
            "memory_bytes": memory(), "output_fs_bytes": filesystem(output)._asdict(),
            "kvm_accessible": os.access("/dev/kvm", os.R_OK | os.W_OK),
            "os_release": Path("/etc/os-release").read_text()}


def run_build(workspace, output, evidence, jobs, report):
    (evidence / "commands.sh").write_text(COMMAND)
    environment = dict(os.environ, OUT_DIR=str(output), LC_ALL="C")
    cancelled = []
    process = None

    def interrupt(signum, _frame):
        cancelled.append(time.monotonic())
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

    previous = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        with (evidence / "build.log").open("ab") as log, \
                (evidence / "resources.csv").open("w", newline="") as metrics:
            first = sample(workspace, output)
            writer = csv.DictWriter(metrics, fieldnames=list(first))
            writer.writeheader()
            writer.writerow(first)
            metrics.flush()
            report["sampled_peaks"] = {key: value for key, value in first.items()
                                       if key.endswith("used_bytes") or key == "host_load_1m"}
            started = time.monotonic()
            process = subprocess.Popen(["bash", str(evidence / "commands.sh"), str(evidence), str(jobs)],
                                       cwd=workspace, env=environment, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            print("Build log: {}".format(evidence / "build.log"), flush=True)
            # ponytail: 5-second whole-host samples are sizing estimates, not per-build isolation.
            # Use a dedicated VM; use cgroup accounting if shared-worker attribution is needed.
            while True:
                try:
                    code = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    code = None
                row = sample(workspace, output)
                writer.writerow(row)
                metrics.flush()
                for key in report["sampled_peaks"]:
                    report["sampled_peaks"][key] = max(report["sampled_peaks"][key], row[key])
                if cancelled and code is None and time.monotonic() - cancelled[0] >= 10:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                if code is not None:
                    report["build_elapsed_seconds"] = round(time.monotonic() - started, 3)
                    report["build_exit_code"] = code
                    if cancelled:
                        raise RuntimeError("build interrupted; partial evidence retained")
                    if code:
                        raise subprocess.CalledProcessError(code, "full AOSP build")
                    return
    finally:
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def image_checksums(evidence, output):
    product = Path((evidence / "product-out.txt").read_text().strip()).resolve()
    product.relative_to(output)
    for name in ("boot.img", "super.img", "userdata.img"):
        if not (product / name).is_file() or (product / name).stat().st_size == 0:
            raise ValueError("full Cuttlefish output missing or empty: " + name)
    images = sorted(product.glob("*.img"))
    lines = []
    for path in images:
        path.resolve().relative_to(output)
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError("invalid image: " + str(path))
        lines.append("{}  {}\n".format(sha256(path), path.name))
    (evidence / "images.sha256").write_text("".join(lines))
    return len(images)


def collect(workspace, output, jobs):
    evidence_root = ROOT / "evidence"
    if evidence_root == workspace or workspace in evidence_root.parents:
        raise ValueError("keep the entry repository and evidence outside the AOSP source tree")
    if (output == workspace or output in workspace.parents or output == evidence_root
            or evidence_root in output.parents or output in evidence_root.parents):
        raise ValueError("OUT_DIR must be a dedicated build directory, not the source or evidence root")
    evidence_root.mkdir(exist_ok=True)
    evidence = Path(tempfile.mkdtemp(prefix="build-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime()) + "-",
                                     dir=evidence_root))
    report = {"status": "in_progress", "started_utc": utc_now(), "target": TARGET, "jobs": jobs,
              "workspace": str(workspace), "output": str(output), "boot_verified": False,
              "measurement_scope": "5-second whole-host samples, including other processes and caches"}
    started = time.monotonic()
    print("Evidence: {}".format(evidence), flush=True)
    try:
        (evidence / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
        report["stage"] = "preflight"
        preflight(workspace, output, False)
        (evidence / "machine.json").write_text(json.dumps(machine_details(output), indent=2) + "\n")
        logged(["lscpu"], workspace, evidence)
        logged(["repo", "version"], workspace, evidence)
        report["entry_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        report["entry_dirty"] = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT))
        shutil.copyfile(__file__, evidence / "build_evidence.py")
        report["driver_sha256"] = sha256(evidence / "build_evidence.py")
        report["stage"] = "source_snapshot"
        pin_sources(workspace, evidence, "source-manifest.xml")
        report["platform_commit"] = subprocess.check_output(
            ["git", "-C", "vendor/agentos", "rev-parse", "HEAD"], cwd=workspace, text=True).strip()
        report["directory_bytes_before"] = sizes(workspace, output)
        output.mkdir(parents=True, exist_ok=True)
        report["output_preexisting"] = any(output.iterdir())
        report["stage"] = "build"
        run_build(workspace, output, evidence, jobs, report)
        report["stage"] = "artifact_validation"
        pin_sources(workspace, evidence, "source-manifest-after.xml")
        if (evidence / "source-manifest.xml").read_bytes() != (evidence / "source-manifest-after.xml").read_bytes():
            raise ValueError("source revisions changed during the build")
        report["platform_version"] = (evidence / "platform-version.txt").read_text().strip()
        report["build_fingerprint"] = (evidence / "build-fingerprint.txt").read_text().strip()
        if report["platform_version"] != "17":
            raise ValueError("expected AOSP 17, got PLATFORM_VERSION=" + report["platform_version"])
        if not report["build_fingerprint"]:
            raise ValueError("empty build fingerprint; cannot associate later boot evidence")
        report["image_count"] = image_checksums(evidence, output)
        report["status"] = "build_succeeded_boot_unverified"
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, ET.ParseError, KeyboardInterrupt) as error:
        report["status"] = "failed"
        report["error"] = str(error) or type(error).__name__
        print("Build evidence failed: " + report["error"], file=sys.stderr)
    finally:
        try:
            if shutil.which("du"):
                report["directory_bytes_after"] = sizes(workspace, output)
        except (OSError, ValueError) as error:
            report["final_disk_measurement_error"] = str(error)
        report["finished_utc"] = utc_now()
        report["total_elapsed_seconds"] = round(time.monotonic() - started, 3)
        (evidence / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
        print("Status: {}; evidence: {}".format(report["status"], evidence))
    return 0 if report["status"] == "build_succeeded_boot_unverified" else 1


def capture_boot(evidence, serial):
    if not serial or not re.fullmatch(r"[A-Za-z0-9_.:\[\]-]+", serial) or serial.startswith("-"):
        raise ValueError("--serial must explicitly identify the Cuttlefish instance")
    build = json.loads((evidence / "summary.json").read_text())
    if (build.get("status") != "build_succeeded_boot_unverified"
            or not build.get("build_fingerprint") or not build.get("platform_version")):
        raise ValueError("boot evidence requires a successful, artifact-validated build")
    capture = Path(tempfile.mkdtemp(prefix="boot-", dir=evidence))
    report = {"status": "failed", "started_utc": utc_now(), "serial": serial,
              "build_summary_sha256": sha256(evidence / "summary.json"),
              "scope": "matching-image boot and system-package smoke check, not CTS/VTS or DSP validation"}

    def adb(*arguments):
        return subprocess.check_output(["adb", "-s", serial, *arguments], stderr=subprocess.STDOUT,
                                       timeout=30).decode().strip()

    try:
        if adb("get-state") != "device" or adb("shell", "getprop", "sys.boot_completed") != "1":
            raise ValueError("selected device is not booted and authorized")
        report["product"] = adb("shell", "getprop", "ro.product.name")
        report["fingerprint"] = adb("shell", "getprop", "ro.build.fingerprint")
        report["platform_version"] = adb("shell", "getprop", "ro.build.version.release")
        if report["product"] != "agentos_cf_x86_64" or report["fingerprint"] != build["build_fingerprint"]:
            raise ValueError("device does not match this AgentOS build; stock-emulator APK demos do not qualify")
        if report["platform_version"] != build["platform_version"]:
            raise ValueError("device Android version does not match the recorded build")
        report["system_packages"] = {}
        for package in ("shell", "capability", "media", "voice"):
            name = "com.agentos." + package
            paths = adb("shell", "pm", "path", name).splitlines()
            if not paths or not all(re.match(r"package:/(system|system_ext|product|vendor)/", p) for p in paths):
                raise ValueError(name + " is missing or installed as a data APK, not a system package")
            report["system_packages"][name] = paths
        report["selinux"] = adb("shell", "getenforce")
        with (capture / "screen.png").open("wb") as screen:
            subprocess.run(["adb", "-s", serial, "exec-out", "screencap", "-p"],
                           stdout=screen, stderr=subprocess.PIPE, check=True, timeout=30)
        with (capture / "screen.png").open("rb") as screen:
            if screen.read(8) != b"\x89PNG\r\n\x1a\n":
                raise ValueError("invalid screenshot")
        with (capture / "logcat.txt").open("wb") as log:
            subprocess.run(["adb", "-s", serial, "logcat", "-d", "-v", "threadtime"],
                           stdout=log, stderr=subprocess.PIPE, check=True, timeout=30)
        report["status"] = "boot_smoke_passed"
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report["error"] = str(error)
        print(report["error"], file=sys.stderr)
    finally:
        report["finished_utc"] = utc_now()
        (capture / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
        print("Boot evidence: {} ({})".format(capture, report["status"]))
    return 0 if report["status"] == "boot_smoke_passed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", default=str(ROOT / "workspace"))
    parser.add_argument("--check-only", action="store_true", help="check resources without syncing or building")
    parser.add_argument("--capture-boot", type=Path, metavar="EVIDENCE", help="read-only smoke check of an already booted image")
    parser.add_argument("--serial", help="explicit adb serial for --capture-boot")
    args = parser.parse_args()
    try:
        if args.capture_boot:
            if args.check_only:
                raise ValueError("--check-only and --capture-boot are separate operations")
            return capture_boot(args.capture_boot.resolve(), args.serial)
        if args.serial:
            raise ValueError("--serial is only used with --capture-boot")
        workspace = Path(args.workspace).resolve()
        if os.environ.get("OUT_DIR_COMMON_BASE"):
            raise ValueError("use an explicit OUT_DIR instead of OUT_DIR_COMMON_BASE for measured builds")
        output = (workspace / os.environ.get("OUT_DIR", "out")).resolve()
        jobs = positive_integer(os.environ.get("AGENTOS_BUILD_JOBS", os.cpu_count() or 1))
        if args.check_only:
            preflight(workspace, output, True)
            return 0
        return collect(workspace, output, jobs)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
