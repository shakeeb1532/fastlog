#ifndef WARPHYBRID_H
#define WARPHYBRID_H

#include <stddef.h>

#define WH_OK               0
#define WH_ERR_COMPRESS     1
#define WH_ERR_FALLBACK     2
#define WH_ERR_DECOMPRESS   3

// ============================================================
// OLD API (full-buffer compression)
// ============================================================

unsigned char* warphybrid_compress(
    const unsigned char* input,
    size_t input_len,
    int level,
    int threads,
    int block_size,
    size_t* out_len,
    int* status
);

unsigned char* warphybrid_decompress(
    const unsigned char* input,
    size_t input_len,
    size_t* out_len,
    int* status
);


// ============================================================
// NEW FASTLOGv2 BLOCK API  (CLEAN & SAFE)
// ============================================================
//
// IMPORTANT:
// • `expected_size` must be the ORIGINAL block size.
// • This avoids the old “input_len * 4” heuristic which fails
//   with highly-compressible blocks.
// • Now decompression is 100% safe.
//
// ============================================================

unsigned char* wh_compress_block(
    const unsigned char* input,
    size_t input_len,
    int level,
    size_t* out_len,
    int* status
);

unsigned char* wh_decompress_block(
    const unsigned char* input,
    size_t input_len,
    size_t expected_size,   // ORIGINAL block size
    size_t* out_len,
    int* status
);

#endif // WARPHYBRID_H

