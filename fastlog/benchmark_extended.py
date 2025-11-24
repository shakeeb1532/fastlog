import os
import time
from fastlog.core import FastLogCore

core = FastLogCore()

def make_compressible(size):
    return (b"A" * 1024 + b"ABCDEF1234567890") * (size // 1032)

def make_random(size):
    return os.urandom(size)

TEST_SIZES = [
    ("1 B", 1),
    ("16 B", 16),
    ("64 B", 64),
    ("256 B", 256),
    ("1 KB", 1024),
    ("4 KB", 4096),
    ("16 KB", 16_384),
    ("64 KB", 65_536),
    ("256 KB", 262_144),
    ("512 KB", 524_288),
    ("1 MB", 1_000_000),
    ("2 MB", 2_000_000),
    ("5 MB", 5_000_000),
    ("10 MB", 10_000_000),
    ("20 MB", 20_000_000),
    ("50 MB", 50_000_000),
    ("100 MB", 100_000_000),
    ("250 MB", 250_000_000),
    ("500 MB", 500_000_000),
    ("1 GB", 1_000_000_000),
]

def bench_one(label, size, data):
    print(f"\n--- {label} ({size:,} bytes) ---")

    # Encode
    t0 = time.time()
    encoded = core.encode(data)
    t1 = time.time()

    # Decode
    decoded = core.decode(encoded)
    t2 = time.time()

    assert decoded == data, "Round-trip failed!"

    enc_mb = (size / (1024*1024)) / (t1 - t0)
    dec_mb = (size / (1024*1024)) / (t2 - t1)

    print(f"Raw Size:     {size:,}")
    print(f"Encoded Size: {len(encoded):,}")
    print(f"Ratio:        {len(encoded)/size*100:.2f}%")
    print(f"Encode MB/s:  {enc_mb:.2f}")
    print(f"Decode MB/s:  {dec_mb:.2f}")

def main():
    for name, size in TEST_SIZES:
        bench_one(name + " (Compressible)", size, make_compressible(size))
        bench_one(name + " (Random)", size, make_random(size))


if __name__ == "__main__":
    main()

