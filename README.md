# IREE playground

The GELU activation is commonly used in the Transformer based models in between
the MLP part. By defination, it consists of a bunch of pointwise operations,
such as multiplication, tanh, pow, etc. This examples demostrates how the IREE
is going to compile and optimize it on the GPUs.

There are some highlights:

0. Each pointwise op (mul, tanh, etc) is defined in its own `linalg.generic` at
   the very begining.
1. The `iree-flow-fusion-of-tensor-ops` pass will fuse all the ops into one
   `linalg.generic`.
2. The `iree-llvmgpu-tile-tensor` wraps the `linalg.generic` into `scf.forall`.
3. The `iree-codegen-gpu-vectorization` changes the `linalg.generic` with
   `vector.transfer_read`.
4. The `iree-llvmgpu-distribute` removes the `scf.forall` and uses
   `gpu.thread_id` to divide the workload.
5. The `iree-codegen-polynomial-approximation` replaces `tanh` to a bunch of
   light-weight ops.
6. The `iree-convert-to-nvvm` transforms the ops from `math.*` or `arith.*` to
   `llvm.*`.


## Install the IREE in the NGC container
```bash
bash install.sh
```

## Generate MLIR from TF script
```bash
python -m pip install iree-compiler iree-runtime iree-tools-tf -f \
    https://openxla.github.io/iree/pip-release-links.html
python model.py > model.mlir
```

## Compile the MLIR file and generate intermediate passes
```bash
/opt/iree/tools/iree-compile model.mlir --iree-input-type=mhlo \
    --iree-hal-target-backends=cuda  --mlir-disable-threading \
    --mlir-print-ir-after-all --mlir-print-ir-after-change -o out \
    &> mlir_passes.mlir
```

## Split each pass and highlight changes for each pass
```bash
python diff-passes.py mlir_passes.mlir logs/
```

