import json
from pathlib import Path
from .generating_informal_proofs import generate_nl_proof, generate_proof_summary

minif2f_valid_path = Path(__file__).resolve().parent.parent / "benchmarks/processed/miniF2F_valid.json"

with open(minif2f_valid_path, 'r', encoding='utf-8') as f:
    minif2f_valid = json.load(f)

aime_informal_problems = dict()

NUM_PROOFS = 2

for name, info in minif2f_valid.items():
    if 'aime' in name:
        print(name)

        informal_statement = info['informal_statement']
        proofs = []
        previous_proofs = []

        while len(proofs) < NUM_PROOFS:
            nl_proof = generate_nl_proof(
                informal_statement=informal_statement, 
                previous_proofs=previous_proofs
            )
            if nl_proof:
                previous_proofs.append(nl_proof)
            else:
                continue
            print("GENERATED nl_proof")

            proof_summary = generate_proof_summary(
                informal_statement=informal_statement,
                nl_proof=nl_proof
            )
            proofs.append({
                'nl_proof': nl_proof,
                'proof_summary': proof_summary
            })
            print("GENERATED proof_summary")

        aime_informal_problems[name] = {
            'informal_statement': informal_statement,
            'proofs': proofs,
        }

        with open('aime_informal_problems.json', 'w', encoding='utf-8') as f:
            json.dump(aime_informal_problems, f, indent=4)