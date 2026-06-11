# mac-ecc

A parallelized modular arithmetic unit for ECC over NIST P-256, using Montgomery
multiplication for modular multiply and Fermat's Little Theorem for the modular
inverse. The CPU version is a plain Python reference; the GPU version reimplements
the same operations as CUDA kernels that run a whole batch in parallel.

## Directory structure

```
src/
  cpu/        CPU reference: modulus.py, ecc.py, constants.py
  gpu/        GPU version: kernels.py (CUDA source) + notebooks 01-03
tests/        pytest correctness tests (CPU)
benchmarks/   pytest-benchmark timing tests (CPU)
report/       report sections and generated figures
cpu/          earlier standalone scripts + notebooks (kept for reference)
```

The GPU notebooks build on each other in order:
1. `01_core_arithmetic_gpu.ipynb` - mod add/sub/mul/exp
2. `02_fermat_inverse_gpu.ipynb` - modular inverse
3. `03_ecc_application_gpu.ipynb` - point ops and scalar multiplication

## Setup

Install [uv](https://docs.astral.sh/uv/) (handles dependencies and the Python version):

```bash
# mac/linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

From the project directory, sync the environment:

```bash
uv sync
```

## Running the CPU code

Tests:

```bash
uv run pytest
```

Benchmarks:

```bash
uv run pytest benchmarks/
```

## Running the GPU notebooks

The GPU notebooks require an NVIDIA GPU with CUDA. They will not run on a Mac or any
machine without one. Run them either on a local machine with an NVIDIA card or on UCSD
DataHub with a GPU environment. The CUDA toolkit must be installed so PyCUDA can
compile the kernels at runtime.

Open the notebooks in `src/gpu/` and run the cells top to bottom. Each notebook checks
its results against the CPU reference and prints a short benchmark at the end.
