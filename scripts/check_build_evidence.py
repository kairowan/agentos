#!/usr/bin/env python3
"""Offline assertions with fake AOSP commands; NEVER evidence of a real OS build."""

import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import threading
from unittest.mock import patch

import build_evidence as build


def rejects(action):
    try:
        action()
    except (ValueError, RuntimeError):
        return
    raise AssertionError("invalid input was accepted")


with tempfile.TemporaryDirectory(prefix="agentos-evidence-selfcheck-") as directory, \
        contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    root = Path(directory).resolve()
    entry, workspace, binaries = root / "entry", root / "source tree", root / "bin"
    for path in (entry / "scripts", entry / "local_manifests", workspace / "build", binaries):
        path.mkdir(parents=True)
    output = root / "separate output"
    (workspace / ".repo").mkdir()
    manifest = '<manifest><project path="vendor/agentos" name="agentos-platform" revision="' + 'a' * 40 + '" /></manifest>\n'
    (workspace / "manifest.xml").write_text(manifest)
    (entry / "local_manifests/agentos.xml").write_text(manifest)
    shutil.copy2(build.ROOT / "scripts/bootstrap.sh", entry / "scripts/bootstrap.sh")

    def executable(name, contents):
        path = binaries / name
        path.write_text("#!/usr/bin/env bash\nset -eu\n" + contents)
        path.chmod(0o755)

    executable("repo", '''
case "$1" in
  init|sync) test "${TEST_REPO_FAILURE:-}" != "$1" || exit 24 ;;
  manifest)
    test "${TEST_REPO_FAILURE:-}" != "manifest" || exit 25
    cp "$TEST_WORKSPACE/manifest.xml" "$4"
    ;;
  forall) test "${TEST_REPO_FAILURE:-}" != "dirty" || exit 26 ;;
  version) printf 'SIMULATED repo\\n' ;;
  *) exit 91 ;;
esac
''')
    executable("git", '''
case "$*" in
  *rev-parse*) printf '%040d\\n' 1 ;;
  *status*) : ;;
  *) exit 92 ;;
esac
''')
    executable("lscpu", "printf 'SIMULATED CPU\\n'\n")
    executable("adb", '''
test "$1" = -s && test "$2" = localhost:6520
shift 2
case "$*" in
  get-state) printf 'device\\n' ;;
  'shell getprop sys.boot_completed') printf '%s\\n' "${TEST_BOOTED:-1}" ;;
  'shell getprop ro.product.name') printf '%s\\n' "${TEST_PRODUCT:-agentos_cf_x86_64}" ;;
  'shell getprop ro.build.fingerprint') printf '%s\\n' "${TEST_FINGERPRINT:-SIMULATED/AgentOS:17/test}" ;;
  'shell getprop ro.build.version.release') printf '17\\n' ;;
  'shell pm path '* ) printf 'package:/%s/app/example.apk\\n' "${TEST_PACKAGE_PARTITION:-system}" ;;
  'shell getenforce') printf 'Enforcing\\n' ;;
  'exec-out screencap -p') printf '\\211PNG\\r\\n\\032\\nSIMULATED screenshot' ;;
  'logcat -d -v threadtime') printf 'SIMULATED boot log\\n' ;;
  *) exit 93 ;;
esac
''')
    (workspace / "build/envsetup.sh").write_text('''
# Deliberately uses an unset variable, as real envsetup may do.
printf 'SIMULATED setup %s\\n' "$UNSET_AOSP_VARIABLE"
lunch() { test "${TEST_LUNCH_FAIL:-0}" = 0; }
get_abs_build_var() {
  if [ "$1" = PRODUCT_OUT ]; then printf '%s/product\\n' "$OUT_DIR";
  else printf '%s/host\\n' "$OUT_DIR"; fi
}
get_build_var() {
  if [ "$1" = BUILD_FINGERPRINT ]; then printf 'SIMULATED/AgentOS:17/test\\n';
  else printf '%s\\n' "${TEST_ANDROID_VERSION:-17}"; fi
}
m() {
  printf 'SIMULATED full build %s\\n' "$*"
  if [ "${TEST_SLEEP:-0}" = 1 ]; then sleep 30; fi
  if [ "${TEST_BUILD_FAIL:-0}" = 1 ]; then return 23; fi
  mkdir -p "$OUT_DIR/product"
  for name in boot super userdata; do
    if [ "${TEST_EMPTY_IMAGE:-0}" = 1 ]; then : > "$OUT_DIR/product/$name.img";
    else printf 'SIMULATED image\\n' > "$OUT_DIR/product/$name.img"; fi
  done
  if [ "${TEST_CHANGE_SOURCE:-0}" = 1 ]; then
    sed 's/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/' \\
      "$TEST_WORKSPACE/manifest.xml" > "$TEST_WORKSPACE/changed.xml"
    mv "$TEST_WORKSPACE/changed.xml" "$TEST_WORKSPACE/manifest.xml"
  fi
}
''')

    clean_environment = {key: value for key, value in os.environ.items()
                         if key not in build.OVERRIDES and key not in ("OUT_DIR", "OUT_DIR_COMMON_BASE")}
    clean_environment.update(PATH=str(binaries) + os.pathsep + os.environ["PATH"],
                             TEST_WORKSPACE=str(workspace))
    with patch.dict(os.environ, clean_environment, clear=True):
        with patch.object(Path, "read_text", return_value="MemTotal: 64 kB\nMemAvailable: 30 kB\nHugePages_Total: 2\n"):
            assert build.memory() == {"MemTotal": 64 * 1024, "MemAvailable": 30 * 1024}
        for bad in ("0", "-1", "1.5", "2+3", "a[$(touch /tmp/should-not-exist)]", ""):
            rejects(lambda: build.positive_integer(bad))
        assert build.positive_integer("16") == 16
        overrides = dict(AGENTOS_TOTAL_MEMORY_KIB=str(64 * 1024 ** 2),
                         AGENTOS_FREE_DISK_KIB=str(400 * 1024 ** 2))
        with patch.dict(os.environ, overrides):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                build.preflight(workspace, output, True)
            assert "SIMULATED" in stream.getvalue()
            rejects(lambda: build.preflight(workspace, output, False))
            with patch.dict(os.environ, AGENTOS_FREE_DISK_KIB="1024"):
                rejects(lambda: build.preflight(workspace, output, True))
            with patch.dict(os.environ, AGENTOS_TOTAL_MEMORY_KIB="1024"):
                rejects(lambda: build.preflight(workspace, output, True))
            with patch.dict(os.environ, AGENTOS_TOTAL_MEMORY_KIB=str(60 * 1024 ** 2)):
                build.preflight(workspace, output, True)
        with patch.dict(os.environ, AGENTOS_TOTAL_MEMORY_KIB="1024"):
            rejects(lambda: build.preflight(workspace, output, True))

        def latest_build():
            return max((entry / "evidence").glob("build-*"), key=lambda p: p.stat().st_mtime_ns)

        fake_memory = {"MemTotal": 64 * build.GIB, "MemAvailable": 30 * build.GIB,
                       "SwapTotal": build.GIB, "SwapFree": build.GIB}
        with patch.object(build, "ROOT", entry), patch.object(build, "preflight"), \
                patch.object(build, "memory", return_value=fake_memory), \
                patch.object(build, "machine_details", return_value={"SIMULATED": True}):
            assert build.collect(workspace, output, 2) == 0
            success = latest_build()
            summary = json.loads((success / "summary.json").read_text())
            assert summary["status"] == "build_succeeded_boot_unverified"
            assert summary["boot_verified"] is False and summary["build_exit_code"] == 0
            assert summary["image_count"] == 3 and not summary["output_preexisting"]
            assert summary["build_elapsed_seconds"] >= 0
            assert "m -j" in (success / "commands.sh").read_text()
            assert "SIMULATED full build -j2" in (success / "build.log").read_text()
            assert len((success / "resources.csv").read_text().splitlines()) >= 3
            for line in (success / "images.sha256").read_text().splitlines():
                digest, name = line.split("  ")
                assert digest == build.sha256(output / "product" / name)

            for changes, error_text in (({"TEST_BUILD_FAIL": "1"}, "23"),
                                        ({"TEST_LUNCH_FAIL": "1"}, "full AOSP build"),
                                        ({"TEST_EMPTY_IMAGE": "1"}, "empty"),
                                        ({"TEST_ANDROID_VERSION": "16"}, "expected AOSP 17"),
                                        ({"TEST_REPO_FAILURE": "manifest"}, "25"),
                                        ({"TEST_REPO_FAILURE": "dirty"}, "26"),
                                        ({"TEST_CHANGE_SOURCE": "1"}, "changed")):
                with patch.dict(os.environ, changes):
                    assert build.collect(workspace, output, 2) == 1
                failed = latest_build()
                report = json.loads((failed / "summary.json").read_text())
                assert report["status"] == "failed" and error_text in report["error"], report
                assert not (failed / "images.sha256").exists()
                assert (failed / "build.log").exists()
                (workspace / "manifest.xml").write_text(manifest)

            (workspace / "manifest.xml").write_text(manifest.replace("a" * 40, "main"))
            assert build.collect(workspace, output, 2) == 1
            (workspace / "manifest.xml").write_text(manifest)
            (output / "product/userdata.img").unlink()
            rejects(lambda: build.image_checksums(success, output))
            (output / "product/userdata.img").write_text("SIMULATED image\n")
            (output / "product/escape.img").symlink_to(workspace / "manifest.xml")
            rejects(lambda: build.image_checksums(success, output))
            (output / "product/escape.img").unlink()
            assert (success / "images.sha256").exists(), "later runs overwrote old evidence"

            with patch.dict(os.environ, TEST_SLEEP="1"):
                original_run = build.run_build

                def interrupt_build(*args):
                    timer = threading.Timer(0.5, lambda: os.kill(os.getpid(), signal.SIGTERM))
                    timer.start()
                    try:
                        return original_run(*args)
                    finally:
                        timer.cancel()

                with patch.object(build, "run_build", side_effect=interrupt_build):
                    assert build.collect(workspace, output, 2) == 1
                interrupted = latest_build()
                assert "interrupted" in json.loads((interrupted / "summary.json").read_text())["error"]

        assert build.capture_boot(success, "localhost:6520") == 0
        for changes in ({"TEST_BOOTED": "0"}, {"TEST_PRODUCT": "generic_x86_64"},
                        {"TEST_FINGERPRINT": "different-build"}, {"TEST_PACKAGE_PARTITION": "data"}):
            with patch.dict(os.environ, changes):
                assert build.capture_boot(success, "localhost:6520") == 1
        rejects(lambda: build.capture_boot(success, None))
        rejects(lambda: build.capture_boot(interrupted, "localhost:6520"))

        for stage in ("", "init", "sync", "manifest"):
            with patch.dict(os.environ, TEST_REPO_FAILURE=stage):
                result = subprocess.run(["bash", str(entry / "scripts/bootstrap.sh"), str(workspace)],
                                        capture_output=True, text=True)
            assert (result.returncode == 0) == (stage == ""), result.stdout + result.stderr
            evidence = max((entry / "evidence").glob("sync-*"), key=lambda p: p.stat().st_mtime_ns)
            assert "exit_code=" + str(result.returncode) in (evidence / "sync.txt").read_text()
            assert (evidence / "sync.log").exists()
            assert (evidence / "source-manifest.xml").exists() == (stage == "")

print("AgentOS build evidence self-checks passed (SIMULATED, no AOSP image built)")
