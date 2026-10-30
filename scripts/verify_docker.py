"""Verify real container APIs, exports, persistence, and queued-job recovery.

Uses only the Python standard library. Run against compose.verify.yml, never a
live installation: this deliberately stops and restarts the verification API.
"""

import argparse
import io
import json
import secrets
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:3200")
    parser.add_argument("--backend-url", default="http://127.0.0.1:8200")
    parser.add_argument("--project", default="exhacker-verify")
    parser.add_argument("--restart", action="store_true")
    args = parser.parse_args()
    if args.project != "exhacker-verify":
        parser.error(
            "Recovery checks are restricted to the isolated exhacker-verify Compose project."
        )
    key = secrets.token_hex(32)

    def request(
        path, method="GET", data=None, expected=200, *, base=None, token=key, raw=False
    ):
        req = urllib.request.Request(
            (base or args.base_url) + "/api/v1" + path,
            data=json.dumps(data).encode() if data is not None else None,
            method=method,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        try:
            response = urllib.request.urlopen(req, timeout=25)
        except urllib.error.HTTPError as error:
            response = error
        content = response.read()
        if response.status != expected:
            raise AssertionError(
                f"{method} {path}: expected {expected}, got {response.status}: {content[:600]!r}"
            )
        return content if raw else json.loads(content).get("data")

    def idle(project_id):
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            project = request(f"/projects/{project_id}")
            if not project["active_job"]:
                job = request(f"/projects/{project_id}/jobs")["jobs"][0]
                assert job["status"] == "completed", job
                return project
            time.sleep(0.25)
        raise AssertionError("The operation did not complete within 60 seconds.")

    def compose(*command, check=True):
        result = subprocess.run(
            [
                "docker",
                "compose",
                "-p",
                args.project,
                "-f",
                str(ROOT / "compose.verify.yml"),
                *command,
            ],
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        if check and result.returncode:
            raise RuntimeError(result.stderr)
        return result

    def wait_api():
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            try:
                request("/health", base=args.backend_url)
                return
            except (OSError, AssertionError):
                time.sleep(0.5)
        raise AssertionError("Verification API did not restart.")

    assert request("/config")["demo"], (
        "This test only runs against explicit demonstration mode."
    )
    request("/health")
    intake = {
        "name": "Docker verification",
        "idea": "Help rural students find STEM mentors despite unreliable internet",
        "available_hours": 48,
        "teammates": [
            {
                "name": "Asha",
                "skills": [{"technology": "React", "proficiency": "advanced"}],
            },
            {
                "name": "Dev",
                "skills": [{"technology": "Python", "proficiency": "intermediate"}],
            },
        ],
    }
    request("/projects", "POST", {**intake, "available_hours": 0}, expected=422)
    project = request("/projects", "POST", intake, expected=201)
    project = idle(project["id"])
    path = f"/projects/{project['id']}"
    assert len(project["context"]["ideas"]) == 5
    request(path, token=secrets.token_hex(32), expected=404)
    request(path + "/jobs", "POST", {"kind": "ideas", "revision": 1}, expected=409)
    selected = project["context"]["ideas"][2]
    request(
        path + f"/ideas/{selected['id']}/confirm",
        "POST",
        {"revision": project["revision"]},
    )
    project = idle(project["id"])
    request(path + "/stack/confirm", "POST", {"revision": project["revision"]})
    project = idle(project["id"])
    assert project["state"] == "ready"
    exported = request(path + "/export", raw=True)
    assert exported == request(path + "/export", raw=True)
    with zipfile.ZipFile(io.BytesIO(exported)) as archive:
        assert len(archive.namelist()) == 10
        assert selected["title"] in archive.read("PRD.md").decode()
        for name in archive.namelist():
            assert request(path + "/documents/" + name, raw=True) == archive.read(name)
    for question in [
        "How should Asha and Dev split the work?",
        "What should we build first?",
    ]:
        request(
            path + "/chat",
            "POST",
            {"revision": project["revision"], "message": question},
            expected=202,
        )
        project = idle(project["id"])
    messages = request(path + "/chat")["messages"]
    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]
    print(
        "PASS: real HTTP workflow, selection, ownership, stale edits, ten matching Markdown exports, and ordered persistent chat."
    )
    if args.restart:
        queue_name = args.project + "-queued-api"
        compose("stop", "backend")
        try:
            request(path, expected=503)
            compose(
                "run",
                "-d",
                "--no-deps",
                "--rm",
                "--name",
                queue_name,
                "-e",
                "STUDIO_WORKER_ENABLED=false",
                "--service-ports",
                "backend",
            )
            wait_api()
            queued = request(
                "/projects", "POST", intake, expected=201, base=args.backend_url
            )
            assert queued["active_job"] is not None
            pending = request(f"/projects/{queued['id']}/jobs", base=args.backend_url)[
                "jobs"
            ][0]
            assert pending["status"] == "queued"
            subprocess.run(
                ["docker", "kill", "--signal", "SIGKILL", queue_name],
                check=True,
                capture_output=True,
                timeout=30,
            )
        finally:
            # Only this script's disposable container is removed.
            subprocess.run(
                ["docker", "rm", "-f", queue_name], capture_output=True, timeout=30
            )
            compose("start", "backend")
        wait_api()
        recovered = idle(queued["id"])
        assert len(recovered["context"]["ideas"]) == 5
        assert request(path)["revision"] == project["revision"]
        assert request(path + "/export", raw=True) == exported
        assert request(path + "/chat")["messages"] == messages
        print(
            "PASS: backend outage returns 503, SIGKILL after queue acceptance, queued-job recovery, and unchanged documents/chat after restart."
        )
    print("Docker verification passed. No paid AI or research request was made.")


if __name__ == "__main__":
    main()
