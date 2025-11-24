import struct

# ================================
# FASTLOGv2 FILE FORMAT
# ================================

MAGIC = b"FASTLOG2"
HEADER_STRUCT = struct.Struct("<Q")     # number of blocks
BLOCK_HEADER = struct.Struct("<III")    # block_size, compressed_size, level

# Level = which compression level was used (bandit may change this)
# Block_size = original uncompressed size
# Compressed_size = compressed size of block

