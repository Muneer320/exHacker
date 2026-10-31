"""Real SIGKILL / RAM-loss verification on the isolated Docker stack only.

No inference requests are sent. A worker is enabled only after its RAM registry
is empty; resubmission is tested with the worker disabled, then cancelled.
"""

import json
import secrets
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTAINER = "exhacker-verify-byok-restart"
BASE = "http://127.0.0.1:8200/api/v1"
TOKEN = secrets.token_hex(32)
SYNTHETIC = "synthetic-restart-test-credential"


def docker(*args, check=True):
    result = subprocess.run(
        ["docker", *args], capture_output=True, text=True, timeout=90
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout


def compose(*args):
    return docker(
        "compose",
        "-p",
        "exhacker-verify",
        "-f",
        str(ROOT / "compose.verify.yml"),
        *args,
    )


def request(path, method="GET", payload=None, lease="", expected=200):
    req = urllib.request.Request(
        BASE + path,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "X-AI-Lease": lease,
        },
        data=json.dumps(payload).encode() if payload is not None else None,
    )
    try:
        response = urllib.request.urlopen(req, timeout=15)
    except urllib.error.HTTPError as exc:
        response = exc
    body = response.read().decode()
    assert SYNTHETIC not in body, "A credential appeared in an API response."
    assert response.status == expected, (
        f"Unexpected status {response.status} for {method} {path}"
    )
    return json.loads(body).get("data")


def wait_api():
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        try:
            request("/health")
            return
        except (OSError, AssertionError):
            time.sleep(0.25)
    raise AssertionError("The verification API did not start.")


def temporary_api(worker):
    compose(
        "run",
        "--no-deps",
        "--detach",
        "--service-ports",
        "--name",
        CONTAINER,
        "-e",
        "STUDIO_DEMO_MODE=false",
        "-e",
        "AI_ACCESS_MODE=byok",
        "-e",
        f"STUDIO_WORKER_ENABLED={'true' if worker else 'false'}",
        "backend",
    )
    wait_api()


def remove_temporary():
    docker("rm", "-f", CONTAINER, check=False)


def connect():
    return request(
        "/ai/leases",
        "POST",
        {"provider": "openai", "model": "gpt-6-luna", "key": SYNTHETIC},
        expected=201,
    )["id"]


def main():
    assert request("/config")["demo"], (
        "Only the disposable demonstration stack may be interrupted."
    )
    intake = {
        "idea": "Help rural students coordinate offline mentoring sessions",
        "available_hours": 24,
        "teammates": [
            {
                "name": "Asha",
                "skills": [{"technology": "React", "proficiency": "advanced"}],
            }
        ],
    }
    baseline = request("/projects", "POST", intake, expected=201)
    for _ in range(100):
        baseline = request(f"/projects/{baseline['id']}")
        if not baseline["active_job"]:
            break
        time.sleep(0.1)
    assert baseline["context"].get("ideas")
    compose("stop", "backend")
    try:
        temporary_api(worker=False)
        handle = connect()
        project = request("/projects", "POST", intake, lease=handle, expected=201)
        path = f"/projects/{project['id']}"
        job = request(path + "/jobs")["jobs"][0]
        assert job["status"] == "queued"
        docker("kill", "--signal", "SIGKILL", CONTAINER)
        remove_temporary()
        temporary_api(worker=True)
        for _ in range(100):
            job = request(path + "/jobs")["jobs"][0]
            if job["status"] == "credentials_required":
                break
            time.sleep(0.1)
        assert job["status"] == "credentials_required", job["status"]
        assert job["attempts"] == 1
        assert request(path)["context"] == {}
        assert request("/ai/leases/" + handle, expected=428) is None
        assert SYNTHETIC not in docker("logs", CONTAINER)
        # Keep recovery verification free of paid/invalid provider requests.
        remove_temporary()
        temporary_api(worker=False)
        handle = connect()
        resumed = request(
            path + f"/jobs/{job['id']}/resume",
            "POST",
            {"revision": 1},
            lease=handle,
            expected=202,
        )
        assert resumed["status"] == "queued"
        assert resumed["inference"]["model"] == "gpt-6-luna"
        request(path + f"/jobs/{job['id']}/cancel", "POST", {"revision": 1})
        assert request(path)["active_job"] is None
        assert SYNTHETIC not in docker("logs", CONTAINER)
    finally:
        remove_temporary()
        compose("start", "backend")
        wait_api()
    saved = request(f"/projects/{baseline['id']}")
    assert saved["context"] == baseline["context"]
    assert saved["revision"] == baseline["revision"]
    print(
        "PASS: SIGKILL drops RAM credentials; durable job pauses before external calls; matching reentry resumes; cancellation and prior artifacts survive."
    )
    print("No paid AI or search request was made.")


if __name__ == "__main__":
    main()
