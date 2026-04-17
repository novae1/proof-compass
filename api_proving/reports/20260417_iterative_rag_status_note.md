# Iterative RAG Status Note

## Current view

Iterative RAG still appears to be a relevant idea, but its overall importance is currently unclear.

What looks real:

- theorem-name hallucination is a real failure mode in Lean theorem proving
- retrieval conditioned on the model's own failed attempt can change the model's behavior
- on earlier small-model experiments, iterative retrieval reduced hallucination rates and sometimes improved solve coverage
- on the DeepSeek V3.2 MSC-180 slice, iterative attempt-RAG eventually became competitive with or slightly better than strong basic RAG when given enough attempts

What is still unclear:

- whether iterative RAG is actually better than a strong basic RAG baseline in a general setting
- whether its main value is solve-rate improvement or failure-mode control
- whether the observed gains are large enough to matter for a paper framed as a methods contribution
- how much of the current mixed evidence comes from the method itself versus infrastructure fragility, benchmark choice, or limited same-subset baselines

## Best current interpretation

The strongest claim supported by the evidence so far is not:

- "iterative RAG is a major theorem-proving improvement"

It is closer to:

- "iterative, failure-conditioned retrieval is a targeted way to address grounding and hallucination failures, but its downstream importance is not yet established"

That is a narrower claim, but it is defensible.

## Why this still matters

Even if iterative RAG is not ultimately the best-performing method, it may still be useful as:

- a mechanistic probe of theorem-hallucination failures
- a way to separate grounding failures from later proof-completion failures
- a baseline for future verifier-guided or repair-based systems

## What is missing before stronger conclusions

The main missing pieces are:

- stronger same-model, same-subset baselines
- more reliable execution infrastructure for long API runs
- clearer interpretation of whether improvements are on accuracy, hallucination control, or both

## Bottom line

Iterative RAG does not look dead.

But it also does not yet justify a strong claim that it is broadly important or clearly superior.

At the moment, it looks promising enough to study further, but not established enough to anchor a large methods claim without tighter comparisons and cleaner evidence.
