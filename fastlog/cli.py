import argparse
import time
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich import box

from fastlog.core import FastLogCore
from fastlog.benchmark import benchmark as run_benchmark

console = Console()

# ============================================================
# Helper: Pretty table for stats
# ============================================================

def show_stats(title, rows):
    table = Table(
        title=title,
        box=box.ROUNDED,
        style="cyan",
        title_style="bold yellow"
    )

    table.add_column("Metric", style="magenta", no_wrap=True)
    table.add_column("Value", style="white")

    for k, v in rows.items():
        table.add_row(k, v)

    console.print(table)


# ============================================================
# Encode operation
# ============================================================

def run_encode(input_path, output_path, bandit_mode):
    core = FastLogCore(bandit=bandit_mode)

    with open(input_path, "rb") as f:
        data = f.read()

    console.print(f"[cyan]Encoding [white]{input_path}[/white] → [green]{output_path}[/green][/cyan]")

    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:

        task = progress.add_task("[bold green]Compressing & Encrypting...", total=None)

        t0 = time.time()
        blob = core.encode(data)
        t1 = time.time()

    with open(output_path, "wb") as f:
        f.write(blob)

    show_stats("FASTLOGv2 Encode Stats", {
        "Input Size": f"{len(data)/1024/1024:.2f} MB",
        "Output Size": f"{len(blob)/1024/1024:.2f} MB",
        "Elapsed Time": f"{t1-t0:.4f}s",
        "Throughput": f"{len(data)/(t1-t0)/1e6:.2f} MB/s",
        "Bandit Mode": bandit_mode,
    })


# ============================================================
# Decode operation
# ============================================================

def run_decode(input_path, output_path):
    core = FastLogCore()

    with open(input_path, "rb") as f:
        blob = f.read()

    console.print(f"[cyan]Decoding [white]{input_path}[/white] → [green]{output_path}[/green][/cyan]")

    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:

        task = progress.add_task("[bold blue]Decrypting & Decompressing...", total=None)

        t0 = time.time()
        raw = core.decode(blob)
        t1 = time.time()

    with open(output_path, "wb") as f:
        f.write(raw)

    show_stats("FASTLOGv2 Decode Stats", {
        "Output Size": f"{len(raw)/1024/1024:.2f} MB",
        "Elapsed Time": f"{t1-t0:.4f}s",
        "Throughput": f"{len(raw)/(t1-t0)/1e6:.2f} MB/s",
    })


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="FASTLOGv2 Toolkit (WarpHybrid-AI Compression)")

    sub = parser.add_subparsers(dest="cmd")

    # Encode
    enc = sub.add_parser("encode")
    enc.add_argument("input")
    enc.add_argument("output")
    enc.add_argument("--bandit", choices=["one", "full", "off"], default="one")

    # Decode
    dec = sub.add_parser("decode")
    dec.add_argument("input")
    dec.add_argument("output")

    # Benchmark
    bench = sub.add_parser("bench")
    bench.add_argument("file")

    args = parser.parse_args()

    if args.cmd == "encode":
        run_encode(args.input, args.output, args.bandit)

    elif args.cmd == "decode":
        run_decode(args.input, args.output)

    elif args.cmd == "bench":
        run_benchmark(args.file)

    else:
        console.print("[red]No command provided. Use encode, decode, or bench.")

