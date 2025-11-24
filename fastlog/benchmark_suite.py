import os
import time
from fastlog.core import FastLogCore

def human(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} TB"

def measure(name, data):
    core = FastLogCore(bandit="one")

    t0 = time.time()
    encoded = core.encode(data)
    t1 = time.time()

    t2 = time.time()
    decoded = core.decode(encoded)
    t3 = time.time()

    return {
        "name": name,
        "raw_size": len(data),
        "encoded_size": len(encoded),
        "ratio": len(encoded) / len(data) * 100,
        "encode_time": t1 - t0,
        "encode_speed": len(data) / (t1 - t0) / 1e6,
        "decode_time": t3 - t2,
        "decode_speed": len(data) / (t3 - t2) / 1e6,
        "correct": data == decoded
    }

def run_benchmarks():
    results = []

    comp = (b"INFO User logged in\n" * 4_000_000)
    results.append(measure("Highly-compressible text", comp))

    inc = os.urandom(100 * 1024 * 1024)
    results.append(measure("Incompressible random data", inc))

    mixed = (
        b"{\"event\":\"login\",\"user\":123}\n" * 500000 +
        os.urandom(20 * 1024 * 1024) +
        b"GET /index.html HTTP/1.1\n" * 500000
    )
    results.append(measure("Mixed real logfile", mixed))

    return results


if __name__ == "__main__":
    res = run_benchmarks()
    for r in res:
        print("\n============", r["name"], "============")
        print("Raw size:      ", human(r["raw_size"]))
        print("Encoded size:  ", human(r["encoded_size"]))
        print("Ratio:         ", f"{r['ratio']:.2f}%")
        print("Encode speed:  ", f"{r['encode_speed']:.2f} MB/s")
        print("Decode speed:  ", f"{r['decode_speed']:.2f} MB/s")
        print("Round-trip OK: ", r["correct"])

