# Prompt from Prover Agent

def build_goedel_prompt(lean_header: str, theorem: str, nl_proof: str) -> str:
    return f"""Your goal is to implement the following theorem, using Lean 4 and the mathlib library:

```lean4
{lean_header}


{theorem}
```

The English proof is as follows:
```text
{nl_proof}
```

Complete the following Lean 4 code:

```lean4
{lean_header}

{theorem}
```

Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof."""

INITIAL_PROOF = {
    "model": "Goedel-LM/Goedel-Prover-V2-8B",
    "filename": "Main.lean",
    "prompt": (
        "Your goal is to implement the following theorem, using Lean 4 and the mathlib library:\n"
        "\n"
        "```lean4\n"
        "{lean_header}\n"
        "\n"
        "\n"
        "{theorem}\n"
        "```\n"
        "\n"
        "The English proof is as follows:\n"
        "```text\n"
        "{nl_proof}\n"
        "```\n"
        "\n"
        "Complete the following Lean 4 code:\n"
        "\n"
        "```lean4\n"
        "{lean_header}\n"
        "\n"
        "{theorem}\n"
        "```\n"
        "\n"
        "Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.\n"
        "The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof."
    ),
    "runner_type": "openai_api",
    "messages": lambda prompt: [
        {"role": "system", "content": "You are an expert in mathematics and Lean 4."},
        {"role": "user", "content": prompt},
    ],
    "extract_output_format": "code",
    "output_prefix": (
        "{lean_header}\n"
        "\n"
        "\n"
    ),
    "required_contents": [
        (
            "{lean_header}\n"
            "\n"
            "\n"
            "{theorem}"
        ),
    ],
    "code_comment_type": "code",
    "num_selections": [100, 20],
}

if __name__ == "__main__":
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    torch.manual_seed(30)

    model_id = "Goedel-LM/Goedel-Prover-V2-32B"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, device_map="auto", torch_dtype=torch.bfloat16, trust_remote_code=True
    )

    formal_statement = """
import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat


theorem square_equation_solution {x y : ℝ} (h : x^2 + y^2 = 2*x - 4*y - 5) : x + y = -1 := by
  sorry
""".strip()

    prompt = """
Complete the following Lean 4 code:

```lean4
{}```

Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.
""".strip()

    chat = [
        {"role": "user", "content": prompt.format(formal_statement)},
    ]

    inputs = tokenizer.apply_chat_template(
        chat, tokenize=True, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    import time

    start = time.time()
    outputs = model.generate(inputs, max_new_tokens=32768)
    print(tokenizer.batch_decode(outputs))
    print(time.time() - start)
