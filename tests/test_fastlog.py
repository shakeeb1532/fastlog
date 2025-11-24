import subprocess
import os
from fastlog.core import FastLogCore

def test_round_trip():
    core = FastLogCore()

    raw = b"Hello FastLog — WarpHybrid + DCF mix mode!"
    blob = core.encode(raw)
    out = core.decode(blob)

    assert raw == out, "Round trip failed"

def test_file_round_trip(tmp_path):
    input_file = tmp_path / "in.log"
    output_file = tmp_path / "out.fastlog"
    final_file = tmp_path / "decode.log"

    input_file.write_bytes(b"Sample log line 123\nAnother line\n")

    subprocess.run([
        "python3", "-m", "fastlog.cli", "encode",
        str(input_file), str(output_file)
    ])

    subprocess.run([
        "python3", "-m", "fastlog.cli", "decode",
        str(output_file), str(final_file)
    ])

    assert input_file.read_bytes() == final_file.read_bytes()

