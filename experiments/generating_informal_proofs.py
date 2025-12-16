import json
from openai import OpenAI
from pathlib import Path

keys_path = Path(__file__).resolve().parent.parent / "keys.json"

with keys_path.open('r') as f:
    api_keys = json.load(f)

client = OpenAI(api_key=api_keys['deepseek'], base_url="https://api.deepseek.com")


def prompt_nl_proof(informal_statement, previous_proofs=None):
    if previous_proofs is None:
        previous_proofs = []
    user_prompt = f"""Theorem Statement:
{informal_statement}

"""
    if previous_proofs:
        user_prompt += """<previous_proofs>:
"""
        for i, proof in enumerate(previous_proofs, 1):
            user_prompt += f"Previous proof {i}:\n{proof}\n"
        user_prompt += """</previous_proofs>

Generate a new rigorous and detailed proof in natural language for the theorem that is distinct from all the previous proofs."""
    else:
        user_prompt += "Provide a rigorous and detailed proof in natural language for the theorem."

    return user_prompt


def generate_nl_proof(informal_statement, previous_proofs=None) -> str:
    if previous_proofs is None:
        previous_proofs = []

    system_prompt = "You are a mathematical theorem prover. Your task is to generate a rigorous, detailed proof in natural language for the given theorem statement."
    if previous_proofs:
        system_prompt += " Additionally, you must ensure your proof is distinct from all of the previous proofs provided by the user."

    user_prompt = prompt_nl_proof(informal_statement, previous_proofs)

    try: 
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"ERROR:\n{e}")
        return ""


def prompt_proof_summary(informal_statement, nl_proof):
    prompt = f"""Theorem Statement:
{informal_statement}

Complete Proof:
{nl_proof}

Write your summarized proof below"""
        
    return prompt


def generate_proof_summary(informal_statement, nl_proof):
    system_prompt = """You are a mathematical proof summarizer. You will be given a theorem statement and its natural language proof. Your response should contain only a summarized version of the natural language proof that's both concise and complete. You should write only the proof in your response, nothing more."""

    user_prompt = prompt_proof_summary(informal_statement, nl_proof)

    try: 
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"ERROR:\n{e}")
        return ""