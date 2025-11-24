from .warp_adapter import WarpAdapter
from .dcf_adapter import DCFAdapter

class FastLogCore:
    def __init__(self, bandit="one"):
        self.warp = WarpAdapter(bandit=bandit)
        self.dcf = DCFAdapter()

    def encode(self, data: bytes) -> bytes:
        cstream = self.warp.compress_stream(data)
        enc, nonce = self.dcf.encrypt(cstream)
        return nonce + enc

    def decode(self, blob: bytes) -> bytes:
        nonce = blob[:12]
        enc = blob[12:]
        dec = self.dcf.decrypt(enc, nonce)
        return self.warp.decompress_stream(dec)

