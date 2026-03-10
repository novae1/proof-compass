# Continuation Environment

The theorem-continuation experiments should run in the main repo environment at
`/workspace/proof-compass/.venv`.

## Why

`transformers==5.3.0` corrupts tokenization for `DeepSeek-Prover-V2-7B` in this repo's
current setup. The observed failure mode is collapsed whitespace and malformed decoded
continuations. The repo-wide dependency stack is now pinned so `./init.sh` installs the
validated continuation setup directly.

## Bootstrap

```bash
./init.sh
```

That creates or updates `.venv` using the pinned `requirements.txt`, then validates the
installed `transformers`, `tokenizers`, `accelerate`, `huggingface_hub`, and
`sentencepiece` versions and prints whether CUDA is visible.

## Activate

```bash
source .venv/bin/activate
```

## Run

```bash
.venv/bin/python rag_experiments/debug_continuation_fidelity.py inspect \
  --preset mathd_algebra_10 \
  --builder deepseek_noncot
```

```bash
.venv/bin/python rag_experiments/run_msc180_v3_theorem_continuations.py deepseek \
  --max-slots 3 \
  --attempts-per-slot 1 \
  --max-new-tokens 24 \
  --output-name smoke_continuations_tf457.json
```

## Guardrail

The continuation harness and the v3 continuation runner both enforce
`transformers==4.57.6` by default. To bypass that check for debugging only, set:

```bash
export PROOF_COMPASS_ALLOW_UNSUPPORTED_TRANSFORMERS=1
```

The older `.venvs/continuation-tf457` and `init-continuation.sh` flow is no longer the
canonical setup.
