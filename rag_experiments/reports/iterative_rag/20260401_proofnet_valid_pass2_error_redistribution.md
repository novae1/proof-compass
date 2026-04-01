# ProofNet-valid Pass2 Error Redistribution

This note compares the first-pass baseline against pass2 on the triggered subsets only.

Triggered subset = problems that were unsolved in the corresponding first-pass run and had at least one filtered theorem-like hallucination.


Bucket definitions:
- `hallucination`: filtered theorem-like `unknown identifier` / `unknown constant`
- `unknown_other`: other unresolved-name errors that do not pass the theorem-like filter
- `typeclass_synthesis`: `failed to synthesize`, stuck typeclass search, or related instance errors
- `unsolved_goals`: explicit unsolved-goal failures
- `local_proof_shape`: type mismatch, application failure, rewrite failure, invalid field notation, exact/apply shape errors
- `simplifier`: `simp` / `simp_all` no-progress failures
- `arithmetic_solver`: `linarith` / `omega` failures
- `automation`: `aesop` / `tauto` failures
- `timeout`: deterministic heartbeat timeouts
- `verification_artifact`: runner/verifier placeholder strings; should be zero in valid comparisons
- `other`: everything else

## no-hint

### Error Count Per Failed Attempt

| run | failed attempts | mean error lines | median | p90 | 1 error | 2 errors | 3+ errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base subset | 232 | 2.659 | 2.0 | 5.0 | 75 | 72 | 85 |
| pass2 | 226 | 2.894 | 2.0 | 6.3 | 84 | 63 | 79 |

### First Error Bucket Distribution

| bucket | base subset | pass2 | delta |
| --- | ---: | ---: | ---: |
| `arithmetic_solver` | 4 | 6 | +2 |
| `automation` | 2 | 7 | +5 |
| `hallucination` | 79 | 51 | -28 |
| `local_proof_shape` | 80 | 70 | -10 |
| `other` | 6 | 10 | +4 |
| `simplifier` | 9 | 14 | +5 |
| `timeout` | 4 | 4 | +0 |
| `typeclass_synthesis` | 29 | 39 | +10 |
| `unknown_other` | 1 | 6 | +5 |
| `unsolved_goals` | 18 | 19 | +1 |

### Failed Attempts With At Least One Error From Each Bucket

| bucket | base subset | pass2 | delta |
| --- | ---: | ---: | ---: |
| `arithmetic_solver` | 15 | 17 | +2 |
| `automation` | 12 | 20 | +8 |
| `hallucination` | 110 | 80 | -30 |
| `local_proof_shape` | 110 | 111 | +1 |
| `other` | 52 | 51 | -1 |
| `simplifier` | 19 | 29 | +10 |
| `timeout` | 7 | 9 | +2 |
| `typeclass_synthesis` | 36 | 49 | +13 |
| `unknown_other` | 4 | 6 | +2 |
| `unsolved_goals` | 54 | 56 | +2 |

### Top First Errors

Base subset:
- `25`: `failed to synthesize`
- `18`: `unsolved goals`
- `17`: `application type mismatch`
- `12`: ``exact?` could not close the goal. Try `apply?` to see partial suggestions.`
- `11`: `tactic 'rewrite' failed, did not find instance of the pattern in the target expression`
- `9`: `function expected at`
- `8`: `tactic 'apply' failed, failed to unify`
- `7`: `type mismatch`
- `5`: `simp_all made no progress`
- `4`: `linarith failed to find a contradiction`
- `4`: `invalid field notation, type is not of the form (C ...) where C is a constant`
- `4`: `unknown identifier 'ClosedEmbedding'`

Pass2:
- `35`: `failed to synthesize`
- `19`: `unsolved goals`
- `19`: `tactic 'apply' failed, failed to unify`
- `11`: `application type mismatch`
- `8`: `tactic 'rewrite' failed, did not find instance of the pattern in the target expression`
- `8`: `invalid field notation, type is not of the form (C ...) where C is a constant`
- `7`: ``exact?` could not close the goal. Try `apply?` to see partial suggestions.`
- `6`: `tactic 'aesop' failed, made no progress`
- `6`: `simp_all made no progress`
- `5`: `function expected at`
- `5`: `simp made no progress`
- `4`: `linarith failed to find a contradiction`

## statement-rag-top2

### Error Count Per Failed Attempt

| run | failed attempts | mean error lines | median | p90 | 1 error | 2 errors | 3+ errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base subset | 200 | 2.635 | 2.0 | 5.0 | 52 | 67 | 81 |
| pass2 | 196 | 2.796 | 2.0 | 5.0 | 70 | 41 | 85 |

### First Error Bucket Distribution

| bucket | base subset | pass2 | delta |
| --- | ---: | ---: | ---: |
| `arithmetic_solver` | 6 | 6 | +0 |
| `automation` | 3 | 5 | +2 |
| `hallucination` | 69 | 49 | -20 |
| `local_proof_shape` | 65 | 59 | -6 |
| `other` | 6 | 10 | +4 |
| `simplifier` | 11 | 11 | +0 |
| `timeout` | 0 | 4 | +4 |
| `typeclass_synthesis` | 20 | 40 | +20 |
| `unknown_other` | 2 | 2 | +0 |
| `unsolved_goals` | 18 | 10 | -8 |

### Failed Attempts With At Least One Error From Each Bucket

| bucket | base subset | pass2 | delta |
| --- | ---: | ---: | ---: |
| `arithmetic_solver` | 11 | 13 | +2 |
| `automation` | 13 | 14 | +1 |
| `hallucination` | 101 | 67 | -34 |
| `local_proof_shape` | 97 | 104 | +7 |
| `other` | 48 | 46 | -2 |
| `simplifier` | 27 | 27 | +0 |
| `timeout` | 2 | 5 | +3 |
| `typeclass_synthesis` | 36 | 47 | +11 |
| `unknown_other` | 4 | 3 | -1 |
| `unsolved_goals` | 44 | 43 | -1 |

### Top First Errors

Base subset:
- `19`: `failed to synthesize`
- `18`: `unsolved goals`
- `10`: ``exact?` could not close the goal. Try `apply?` to see partial suggestions.`
- `8`: `application type mismatch`
- `7`: `type mismatch`
- `7`: `tactic 'rewrite' failed, did not find instance of the pattern in the target expression`
- `6`: `invalid field notation, type is not of the form (C ...) where C is a constant`
- `6`: `simp_all made no progress`
- `6`: `tactic 'apply' failed, failed to unify`
- `5`: `linarith failed to find a contradiction`
- `5`: `function expected at`
- `4`: `ambiguous, possible interpretations `

Pass2:
- `32`: `failed to synthesize`
- `16`: `tactic 'apply' failed, failed to unify`
- `11`: ``exact?` could not close the goal. Try `apply?` to see partial suggestions.`
- `10`: `unsolved goals`
- `8`: `application type mismatch`
- `8`: `type mismatch`
- `7`: `simp_all made no progress`
- `6`: `typeclass instance problem is stuck, it is often due to metavariables`
- `5`: `tactic 'aesop' failed, made no progress`
- `5`: `function expected at`
- `4`: `(deterministic) timeout at `whnf`, maximum number of heartbeats (200000) has been reached`
- `4`: `linarith failed to find a contradiction`

