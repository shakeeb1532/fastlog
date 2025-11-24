import time
import os
from fastlog.core import FastLogCore

def human(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} TB"

def benchmark(path):
    core = FastLogCore()
    data = open(path, "rb").read()
    size_raw = len(data)

    print("===== FASTLOG BENCHMARK =====")
    print("File:", path)
    print("Raw size:", human(size_raw))
    print("==============================")

    # Compress only
    t0 = time.time()
    compressed = core.warp.compress(data)
    t1 = time.time()

    cr = len(compressed) / size_raw * 100
    print(f"Hybrid compression: {human(len(compressed))} ({cr:.2f}% of original)")
    print(f"Compression time: {(t1 - t0):.4f}s ({size_raw / (t1 - t0) / 1e6:.2f} MB/s)")

    # Encrypt only
    t2 = time.time()
    encrypted, nonce = core.dcf.encrypt(compressed)
    t3 = time.time()

    print(f"Encryption time: {(t3 - t2):.4f}s ({len(compressed) / (t3 - t2) / 1e6:.2f} MB/s)")

    # Full encode
    t4 = time.time()
    blob = core.encode(data)
    t5 = time.time()

    print(f"Full FASTLOG encode: {(t5 - t4):.4f}s ({size_raw / (t5 - t4) / 1e6:.2f} MB/s)")

    # Full decode
    t6 = time.time()
    restored = core.decode(blob)
    t7 = time.time()

    print(f"Full FASTLOG decode: {(t7 - t6):.4f}s ({size_raw / (t7 - t6) / 1e6:.2f} MB/s)")
    print("Match:", restored == data)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 benchmark.py <file>")
        exit(1)
    benchmark(sys.argv[1])

