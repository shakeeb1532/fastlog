#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "warphybrid.h"
#include "lz4.h"
#include "lz4hc.h"

// ===============================================
// Low-Level Hybrid Functions (Primary + Fallback)
// ===============================================

static int primary_compress(
    const unsigned char* input,
    size_t input_len,
    unsigned char** out,
    size_t* out_len,
    int level
) {
    int max_dst = LZ4_compressBound((int)input_len);
    *out = (unsigned char*)malloc(max_dst);
    if (!*out) {
        return WH_ERR_COMPRESS;
    }

    int written = LZ4_compress_HC(
        (const char*)input,
        (char*)*out,
        (int)input_len,
        max_dst,
        level
    );

    if (written <= 0) {
#if WH_DEBUG
        printf("[PRIMARY] FAILED\n");
#endif
        free(*out);
        *out = NULL;
        return WH_ERR_COMPRESS;
    }

    *out_len = (size_t)written;
    return WH_OK;
}

static int fallback_compress(
    const unsigned char* input,
    size_t input_len,
    unsigned char** out,
    size_t* out_len
) {
    int max_dst = LZ4_compressBound((int)input_len);
    *out = (unsigned char*)malloc(max_dst);
    if (!*out) {
        return WH_ERR_FALLBACK;
    }

    int written = LZ4_compress_default(
        (const char*)input,
        (char*)*out,
        (int)input_len,
        max_dst
    );

    if (written <= 0) {
#if WH_DEBUG
        printf("[FALLBACK] FAILED\n");
#endif
        free(*out);
        *out = NULL;
        return WH_ERR_FALLBACK;
    }

    *out_len = (size_t)written;
    return WH_OK;
}


// ===============================================
// OLD API (Full-buffer hybrid compression)
// ===============================================

unsigned char* warphybrid_compress(
    const unsigned char* input,
    size_t input_len,
    int level,
    int threads,
    int block_size,
    size_t* out_len,
    int* status
) {
    (void)threads;
    (void)block_size;

    unsigned char* out = NULL;

    *status = primary_compress(
        input, input_len,
        &out, out_len,
        level
    );

    if (*status == WH_OK)
        return out;

    *status = fallback_compress(
        input, input_len,
        &out, out_len
    );

    return out;
}

unsigned char* warphybrid_decompress(
    const unsigned char* input,
    size_t input_len,
    size_t* out_len,
    int* status
) {
    // Legacy heuristic: 4x compressed size
    size_t alloc = input_len * 4;
    unsigned char* out = (unsigned char*)malloc(alloc);
    if (!out) {
        *status = WH_ERR_DECOMPRESS;
        return NULL;
    }

    int written = LZ4_decompress_safe(
        (const char*)input,
        (char*)out,
        (int)input_len,
        (int)alloc
    );

    if (written < 0) {
        free(out);
        *status = WH_ERR_DECOMPRESS;
        return NULL;
    }

    *out_len = (size_t)written;
    *status = WH_OK;
    return out;
}


// ===============================================
// NEW FASTLOGv2 API: Block Compression
// ===============================================

unsigned char* wh_compress_block(
    const unsigned char* input,
    size_t input_len,
    int level,
    size_t* out_len,
    int* status
) {
    unsigned char* out = NULL;

    *status = primary_compress(
        input, input_len,
        &out, out_len,
        level
    );

    if (*status == WH_OK)
        return out;

    *status = fallback_compress(
        input, input_len,
        &out, out_len
    );

    return out;
}

unsigned char* wh_decompress_block(
    const unsigned char* input,
    size_t input_len,
    size_t expected_size,
    size_t* out_len,
    int* status
) {
    // For FASTLOGv2 we KNOW the original block size from the header → use it.
    unsigned char* out = (unsigned char*)malloc(expected_size);
    if (!out) {
        *status = WH_ERR_DECOMPRESS;
        return NULL;
    }

    int written = LZ4_decompress_safe(
        (const char*)input,
        (char*)out,
        (int)input_len,
        (int)expected_size
    );

    if (written < 0) {
        free(out);
        *status = WH_ERR_DECOMPRESS;
        return NULL;
    }

    *out_len = (size_t)written;
    *status = WH_OK;
    return out;
}


// ===============================================
// Helper: Convert C buffer → Python bytes
// ===============================================

static PyObject* py_bytes_from_buf(unsigned char* buf, size_t len) {
    PyObject* obj = PyBytes_FromStringAndSize((const char*)buf, len);
    free(buf);
    return obj;
}


// ===============================================
// Python bindings for OLD API
// ===============================================

static PyObject* py_wh_compress(PyObject* self, PyObject* args) {
    const unsigned char* input;
    Py_ssize_t input_len;
    int level, threads, block_size;

    if (!PyArg_ParseTuple(args, "y#iii",
        &input, &input_len,
        &level, &threads, &block_size))
        return NULL;

    size_t out_len = 0;
    int status = 0;

    unsigned char* out = warphybrid_compress(
        input, (size_t)input_len,
        level, threads, block_size,
        &out_len, &status
    );

    if (!out || status != WH_OK) {
        PyErr_SetString(PyExc_RuntimeError, "Hybrid compress failed");
        return NULL;
    }

    return py_bytes_from_buf(out, out_len);
}

static PyObject* py_wh_decompress(PyObject* self, PyObject* args) {
    const unsigned char* input;
    Py_ssize_t input_len;

    if (!PyArg_ParseTuple(args, "y#", &input, &input_len))
        return NULL;

    size_t out_len = 0;
    int status = 0;

    unsigned char* out = warphybrid_decompress(
        input, (size_t)input_len,
        &out_len, &status
    );

    if (!out || status != WH_OK) {
        PyErr_SetString(PyExc_RuntimeError, "Hybrid decompress failed");
        return NULL;
    }

    return py_bytes_from_buf(out, out_len);
}


// ===============================================
// Python bindings for FASTLOGv2 block API
// ===============================================

static PyObject* py_wh_compress_block(PyObject* self, PyObject* args) {
    const unsigned char* input;
    Py_ssize_t input_len;
    int level;

    if (!PyArg_ParseTuple(args, "y#i",
        &input, &input_len, &level))
        return NULL;

    size_t out_len = 0;
    int status = 0;

    unsigned char* out = wh_compress_block(
        input, (size_t)input_len,
        level,
        &out_len, &status
    );

    if (!out || status != WH_OK) {
        PyErr_SetString(PyExc_RuntimeError, "Block compress failed");
        return NULL;
    }

    return py_bytes_from_buf(out, out_len);
}

static PyObject* py_wh_decompress_block(PyObject* self, PyObject* args) {
    const unsigned char* input;
    Py_ssize_t input_len;
    unsigned long long expected;

    if (!PyArg_ParseTuple(args, "y#K",
        &input, &input_len, &expected))
        return NULL;

    size_t out_len = 0;
    int status = 0;

    unsigned char* out = wh_decompress_block(
        input, (size_t)input_len,
        (size_t)expected,
        &out_len, &status
    );

    if (!out || status != WH_OK) {
        PyErr_SetString(PyExc_RuntimeError, "Block decompress failed");
        return NULL;
    }

    return py_bytes_from_buf(out, out_len);
}


// ===============================================
// Python Method Table
// ===============================================

static PyMethodDef WHMethods[] = {
    {"compress", py_wh_compress, METH_VARARGS, "Hybrid compress"},
    {"decompress", py_wh_decompress, METH_VARARGS, "Hybrid decompress"},
    {"compress_block", py_wh_compress_block, METH_VARARGS, "Block compress"},
    {"decompress_block", py_wh_decompress_block, METH_VARARGS, "Block decompress"},
    {NULL, NULL, 0, NULL}
};


// ===============================================
// Python Module Definition
// ===============================================

static struct PyModuleDef whmodule = {
    PyModuleDef_HEAD_INIT,
    "warphybrid",
    "WarpHybrid Compression Extension",
    -1,
    WHMethods
};


// ===============================================
// Module Initializer
// ===============================================

PyMODINIT_FUNC PyInit_warphybrid(void) {
    return PyModule_Create(&whmodule);
}

