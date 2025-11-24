import struct
import warphybrid
from .bandit import OneShotBandit, FullBandit, OffBandit
from .format import MAGIC, HEADER_STRUCT, BLOCK_HEADER

class WarpAdapter:
    def __init__(self, bandit="one", level=9):
        if bandit == "one":
            self.policy = OneShotBandit()
        elif bandit == "full":
            self.policy = FullBandit()
        else:
            self.policy = OffBandit()

        self.level = level
        self.candidates = [256 * 1024, 1024 * 1024, 4 * 1024 * 1024]

    def _compress_block(self, block_data):
        import time
        t0 = time.time()

        out = warphybrid.compress_block(block_data, self.level)

        t1 = time.time()
        ratio = len(out) / len(block_data)
        speed = 1.0 / (t1 - t0)

        return out, ratio, (t1 - t0), speed

    # ======================================================
    # STREAM ENCODER
    # ======================================================
    def compress_stream(self, data: bytes):
        offset = 0
        length = len(data)
        history = []
        blocks = []

        while offset < length:
            bs = self.policy.choose_block_size(self.candidates, history)
            block = data[offset:offset+bs]
            offset += bs

            out, ratio, t, speed = self._compress_block(block)

            if hasattr(self.policy, "update_reward"):
                self.policy.update_reward(bs, t, ratio)

            if len(history) < len(self.candidates):
                history.append({
                    "block_size": bs,
                    "ratio": ratio,
                    "speed": speed
                })

            blocks.append((bs, len(out), out))

        blob = bytearray()
        blob.extend(MAGIC)
        blob.extend(HEADER_STRUCT.pack(len(blocks)))

        for (orig_bs, clen, cblk) in blocks:
            blob.extend(BLOCK_HEADER.pack(orig_bs, clen, self.level))
            blob.extend(cblk)

        return bytes(blob)

    # ======================================================
    # STREAM DECODER (FIXED)
    # ======================================================
    def decompress_stream(self, blob: bytes):
        p = 0

        if blob[p:p+len(MAGIC)] != MAGIC:
            raise ValueError("Invalid FASTLOGv2 container")
        p += len(MAGIC)

        (block_count,) = HEADER_STRUCT.unpack(blob[p:p+HEADER_STRUCT.size])
        p += HEADER_STRUCT.size

        out = bytearray()

        for _ in range(block_count):
            bs, clen, level = BLOCK_HEADER.unpack(blob[p:p+BLOCK_HEADER.size])
            p += BLOCK_HEADER.size

            cblk = blob[p:p+clen]
            p += clen

            # 🔥 FIX: pass original block size `bs`
            dec = warphybrid.decompress_block(cblk, bs)
            if dec is None:
                raise RuntimeError("Block decompress failed")

            out.extend(dec)

        return bytes(out)

