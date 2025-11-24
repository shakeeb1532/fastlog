from setuptools import setup, Extension

warphybrid_ext = Extension(
    "warphybrid",
    sources=["fastlog/warphybrid.c"],
    include_dirs=["/opt/homebrew/include", "/usr/local/include"],
    library_dirs=["/opt/homebrew/lib", "/usr/local/lib"],
    libraries=["lz4"],
    extra_compile_args=["-O3"],
)

setup(
    name="fastlog",
    version="1.0.0",
    packages=["fastlog"],
    ext_modules=[warphybrid_ext],
    include_package_data=True,
)

