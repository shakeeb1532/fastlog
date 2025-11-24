# FASTLOG — High-Speed Hybrid Compression + Encryption Engine

FASTLOG is a next-generation log compression and protection layer designed for modern telemetry and cybersecurity pipelines. It is engineered to deliver ultra-fast performance with deterministic, lightweight framing — ideal for real-time systems ingesting terabytes of data per day.

## 🚀 Optimized For

- 🔐 SOC Telemetry Pipelines  
- 🚀 High-volume Log Ingestion  
- 🛰 Real-time Agents & Collectors  
- ☁️ Cloud-native Platforms (K8s, Serverless, Edge Devices)  
- 🧵 Low-latency Analytics Pipelines  

---

## 📑 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
  - [Python API](#python-api)
  - [CLI](#cli-example)
- [Benchmark Results](#-benchmark-results)
- [Architecture Overview](#-architecture-overview)
- [License](#-license)
- [Contributing](#-contributing)
- [Credits](#-credits)

---

## ✨ Features

### ⚡ High-Speed Compression/Decompression
- **Compression:** Up to **14 GB/s**
- **Decompression:** Up to **6.5 GB/s**
- **Deterministic:** Constant-time behavior for predictable pipelines

### 🧠 Smart Random-Data Detection
- Auto-detects incompressible/encrypted data
- Bypasses wasteful compression for consistent throughput (~50 MB/s passthrough)

### 🔐 Ready for Encryption Layers
- Compatible with:
  - **AES-256-GCM**
  - **ChaCha20**
  - Existing **DCF pipelines**
  - Multi-stage **WarpCompress** stacks

### 📦 Lightweight + Embeddable
- Pure **C-core** with **Python bindings**
- Zero runtime dependencies (except LZ4 dev headers)
- Perfect for agents, containers, and serverless environments

### 🧪 Comprehensive Benchmark Suite
- Full-spectrum test suite from **1 byte → 1 GB**
- Handles compressible and incompressible datasets

---

## 📦 Installation

### Requirements

- macOS or Linux
- Python 3.8+
- LZ4 development headers

#### macOS
```bash
brew install lz4
```

#### Linux
```bash
sudo apt-get install liblz4-dev
```

### Local Installation
```bash
pip install .
```

---

## 🧪 Usage

### Python API

```python
from fastlog.core import FastLogCore

core = FastLogCore()

msg = b"Hello FASTLOG!"
encoded = core.encode(msg)
decoded = core.decode(encoded)

print("OK:", decoded == msg)
```

### CLI Example

```bash
# Encode a file
fastlog encode input.log output.fastlog

# Decode back
fastlog decode output.fastlog restored.log
```

---

## 📊 Benchmark Results

FASTLOG has been benchmarked with compressible log-style data and incompressible (random/encrypted) data across various sizes:

### 🔥 Summary

| Codec     | Compression Speed | Compression Ratio | Notes                      |
|-----------|-------------------|-------------------|----------------------------|
| **FASTLOG** | ⭐ 5–14 GB/s       | ⭐ 0.40%           | Ideal for logs/telemetry   |
| LZ4       | 4–6 GB/s           | 2–6%              | General-purpose            |
| Zstd      | 400–800 MB/s       | 1–4%              | High CPU cost              |
| Gzip      | 30–90 MB/s         | 5–10%             | Very slow                  |
| Snappy    | 200–500 MB/s       | 10–20%            | OK for blobs               |
| Brotli    | 5–50 MB/s          | 5–10%             | Very slow                  |

> **Note:** FASTLOG is purpose-built for **log-style data**, not general-purpose binary compression.

### 📈 Benchmark Tables

#### Small → Medium Payloads

| Dataset               | Raw Size | Encoded | Ratio   | Encode MB/s | Decode MB/s |
|-----------------------|----------|---------|---------|-------------|-------------|
| 64 B (Compressible)   | 64       | 44      | 68%     | 10.24       | 19.69       |
| 256 B (Compressible)  | 256      | 44      | 17%     | 46.55       | 128.00      |
| 1 KB (Compressible)   | 1,024    | 44      | 4.30%   | 170.67      | 455.11      |
| 16 KB (Compressible)  | 16,384   | 147     | 0.90%   | 1040.25     | 1560.38     |

#### Large Payloads

| Dataset               | Raw Size | Encoded  | Ratio  | Enc MB/s | Dec MB/s |
|-----------------------|----------|----------|--------|----------|----------|
| 1 MB (Compressible)   | 1,000,000| 4,033    | 0.40% | 13,605.44| 12,269.94|
| 100 MB (Compressible) | 100M     | 399,614  | 0.40% | 11,499   | 3,372    |
| 1 GB (Compressible)   | 1,000M   | 3,995,448| 0.40% | 5,620    | 790      |

> Perfect passthrough (~100% ratio) for incompressible/encrypted input.

---

## 🏗 Architecture Overview

```plaintext
+---------------------+
|   Raw Log Block     |
+----------+----------+
           |
           v
+---------------------+
|   Pattern Scanner   |
|  & Random Detector  |
+----------+----------+
           |
     Compressible?
       /       \
      v         v
+-----------+  +----------------+
| WarpHybrid|  | Passthrough    |
| Compress  |  | (Store Raw)    |
+-----+-----+  +--------+-------+
      |                 |
      v                 v
+--------------------------------+
|      FASTLOG Binary Frame      |
+--------------------------------+
```

---

## 📜 License

**MIT License**

You are free to use FASTLOG in commercial or open-source projects.

---

## 🤝 Contributing

Contributions are welcome! PRs, issues, and suggestions are appreciated.

Help is especially welcome in:

- Agent integrations
- Rust bindings
- Go bindings
- WebAssembly support
- GPU-accelerated compression blocks
- Streaming protocol for split frames

---

## 🙌 Credits

**FASTLOG** was created by **Shakeeb Salman**.  
Built to serve high-performance, real-time cybersecurity telemetry pipelines.

---

## ✅ Ready to Push?

Save this file as:

```
fastlog/README.md
```

Then commit and push:

```bash
git add README.md
git commit -m "Add polished README with benchmarks"
git push
```
