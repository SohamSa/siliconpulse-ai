"""Smoke-test the local demo API path."""

from __future__ import annotations

import json
import time
import urllib.request

BASE = "http://127.0.0.1:8787"


def call(path: str, method: str = "GET", body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode())


def main() -> None:
    print("health", call("/health"))
    print("devices", call("/api/v1/overview")["summary"]["device_count"])
    call("/api/v1/scenarios/reset", "POST", {})
    call(
        "/api/v1/scenarios/inject",
        "POST",
        {"scenario": "cooling_degradation", "device_id": "GPU-042", "severity": 0.9},
    )
    incident = None
    for i in range(45):
        time.sleep(1)
        overview = call("/api/v1/overview")
        detail = call("/api/v1/devices/GPU-042")["intelligence"]
        hits = [x for x in overview["open_incidents"] if "GPU-042" in x["affected_devices"]]
        print(
            f"t={i + 1} twin={detail['twin_deviation_score']:.2f} "
            f"anom={detail['anomaly_score']:.2f} failP={detail['failure_probability']:.2f} "
            f"type={detail['predicted_failure_type']} inc={len(hits)}"
        )
        if hits:
            incident = hits[0]["incident_id"]
            break
    if not incident:
        raise SystemExit("NO_INCIDENT")
    rca = call(f"/api/v1/incidents/{incident}/investigate", "POST", {})
    print("rca", rca["result"]["most_likely_cause"], rca["result"]["confidence"])
    maint = call(f"/api/v1/incidents/{incident}/maintenance", "POST", {})
    approval_id = maint["approval"]["approval_id"]
    call(f"/api/v1/approvals/{approval_id}/approve", "POST", {"comments": "ok"})
    time.sleep(8)
    report = call(f"/api/v1/incidents/{incident}/report", "POST", {})
    print("report", report["report_id"], report["technical_summary"]["likely_root_cause"])
    print("DEMO_PATH_OK")



if __name__ == "__main__":
    main()
