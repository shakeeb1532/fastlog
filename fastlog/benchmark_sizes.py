import os
import time
from rich.console import Console
from rich.table import Table
from rich.progress import track
from .core import FastLogCore

console = Console()

# Sizes to test (in bytes)
TEST_SIZES = [
    1024,            # 1 KB
    10 * 1024,       # 10 KB
    100 * 1024,      # 100 KB
    1 * 1024**2,     # 1 MB
    5 * 1024**2,     # 5 MB
    50 * 1024**2,    # 50 MB
    100 * 1024**2,   # 100 MB
    250 * 1024**2,   # 250 MB
    500 * 1024**2,   # 500 MB
    1 * 1024**3,     # 1 GB
]


def generate_data(size_bytes, compressible=True):
    """
    Generate synthetic data:
    compressible → repeated patterns
    incompressible → random bytes
    """
    if compressible:
        return (b"FASTLOG-COMPRESSIBLE-PATTERN|" * (size_bytes // 32))[:size_bytes]
    else:
        return os.urandom(size_bytes)


def benchmark_blob(name, blob):
    core = FastLogCore()

    # ---- Encode ----
    t0 = time.time()
    encoded = core.encode(blob)
    t1 = time.time()

    # ---- Decode ----
    t2 = time.time()
    decoded = core.decode(encoded)
    t3 = time.time()

    assert decoded == blob, "❌ Round-trip mismatch!"

    return {
        "dataset": name,
        "raw": len(blob),
        "encoded": len(encoded),
        "ratio": round((len(encoded) / len(blob)) * 100, 2),
        "encode_speed": round((len(blob) / (t1 - t0)) / (1024**2), 2),
        "decode_speed": round((len(blob) / (t3 - t2)) / (1024**2), 2),
    }


def run_all():
    results = []

    console.rule("[bold cyan]FASTLOG Multi-Size Benchmark Suite[/bold cyan]")

    for size in TEST_SIZES:
        label = f"{size // 1024} KB" if size < 1024**2 else f"{size // 1024**2} MB"
        console.print(f"\n[bold yellow]▶ Testing size: {label}[/bold yellow]")

        for dtype, cname in [(True, "Compressible"), (False, "Random")]:
            console.print(f"[cyan]• Generating {cname} data…[/cyan]")
            blob = generate_data(size, compressible=dtype)

            console.print(f"[magenta]• Running encode/decode…[/magenta]")
            res = benchmark_blob(f"{label} ({cname})", blob)
            results.append(res)

    # ----- Print results -----
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Dataset")
    table.add_column("Raw Size")
    table.add_column("Encoded Size")
    table.add_column("Ratio %")
    table.add_column("Encode MB/s")
    table.add_column("Decode MB/s")

    for r in results:
        table.add_row(
            r["dataset"],
            f"{r['raw']:,}",
            f"{r['encoded']:,}",
            f"{r['ratio']}%",
            str(r["encode_speed"]),
            str(r["decode_speed"]),
        )

    console.rule("[bold green]BENCHMARK RESULTS[/bold green]")
    console.print(table)

    return results


if __name__ == "__main__":
    run_all()

