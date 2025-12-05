import time
import uuid
import statistics
import requests

BACKEND_BASE = "http://127.0.0.1:5001"
MONITOR_BASE = "http://127.0.0.1:5002"  # proxy monitor


def new_session():
    return str(uuid.uuid4())


def timed_post(base, path, sid, json=None):
    t0 = time.time()
    resp = requests.post(
        base + path,
        json=json or {},
        headers={"X-Session-ID": sid},
        timeout=5,
    )
    return resp, (time.time() - t0)


def timed_get(base, path, sid, params=None):
    t0 = time.time()
    resp = requests.get(
        base + path,
        params=params or {},
        headers={"X-Session-ID": sid},
        timeout=5,
    )
    return resp, (time.time() - t0)


def run_phase(base, label, num_sessions=50):
    latencies = []
    i = 0

    while i < num_sessions:
        sid = new_session()

        _, dt = timed_post(base, "/login", sid,
                           {"username": "anushka", "password": "12345"})
        latencies.append(dt)

        _, dt = timed_get(base, "/profile", sid, {"user": "anushka"})
        latencies.append(dt)

        _, dt = timed_get(base, "/download-data", sid, {"user": "anushka"})
        latencies.append(dt)

        i += 1 

    mean = statistics.mean(latencies)
    p95 = sorted(latencies)[int(0.95 * len(latencies)) - 1]

    print(f"{label}:")
    print(f"  Total requests: {len(latencies)}")
    print(f"  Mean latency: {mean*1000:.2f} ms")
    print(f"  95th percentile latency: {p95*1000:.2f} ms\n")

    return mean


if __name__ == "__main__":
    baseline_mean = run_phase(BACKEND_BASE, "Direct backend (no monitor)")
    monitored_mean = run_phase(MONITOR_BASE, "Through monitor proxy")

    extra_ms = (monitored_mean - baseline_mean) * 1000
    overhead_pct = ((monitored_mean / baseline_mean) - 1) * 100 if baseline_mean else 0

    print("Runtime Overhead Results:")
    print(f"  Additional delay per request: {extra_ms:.2f} ms")
    print(f"  Relative overhead: {overhead_pct:.1f}%")
