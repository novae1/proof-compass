# CoT Markdown Structure Analysis

## Scope

- files scanned: `35`
- CoT files matched: `25`
- CoT completions analyzed: `928`

## Main Counts

- with any markdown heading: `924` (99.6%)
- with any recognized core heading: `919` (99.0%)
- with Lean code block: `914` (98.5%)
- parseable as `detailed_analysis + abstract_plan + complete_proof`: `599` (64.5%)
- parseable as `detailed_analysis + abstract_plan + lean_sketch + complete_proof`: `453` (48.8%)
- with some summary/analysis before final proof: `853` (91.9%)
- with complete proof as the last core section: `856` (92.2%)

## Size Statistics

- completion length: mean `7073.3`, median `5374.5`
- prose before first Lean code block: mean `4219.8`, median `2953.5`
- prose before first Lean code block as share of total output: mean `62.2%`, median `66.1%`

## Core Section Presence

- `detailed_analysis`: `877` (94.5%)
- `abstract_plan`: `614` (66.2%)
- `lean_sketch`: `575` (62.0%)
- `explanation`: `334` (36.0%)
- `complete_proof`: `883` (95.2%)

## Core Section Sizes

- `detailed_analysis`: mean `2637.9` chars, median `1388`, mean share when present `34.7%`
- `abstract_plan`: mean `676.5` chars, median `555.5`, mean share when present `10.6%`
- `lean_sketch`: mean `459.4` chars, median `432`, mean share when present `8.2%`
- `explanation`: mean `496.6` chars, median `366.5`, mean share when present `8.0%`
- `complete_proof`: mean `1868.2` chars, median `882`, mean share when present `24.0%`

## Most Common Exact Headings

- `Complete Lean 4 Proof`: `931`
- `Detailed Proof and Analysis`: `448`
- `Detailed Proof`: `309`
- `Step-by-Step Abstract Plan`: `201`
- `Step 1: Abstract Plan`: `166`
- `Lean 4 `have` Statements`: `148`
- `Abstract Plan`: `139`
- `Explanation:`: `114`
- `Explanation`: `100`
- `Key Observations:`: `87`
- `Lean 4 Proof Sketch with `have` Statements`: `82`
- `Proof Plan`: `74`
- `Lean 4 code`: `66`
- `Step 2: Lean 4 `have` Statements`: `64`
- `Problem Analysis`: `60`
- `Complete Lean 4 Code`: `58`
- `Abstract Step-by-Step Plan`: `54`
- `1. Understanding the Problem`: `42`
- `Lean 4 Proof Sketch with `have``: `40`
- `Proof Sketch:`: `39`

## Most Common Normalized Core Orders

- `detailed_analysis -> abstract_plan -> lean_sketch -> complete_proof`: `288`
- `detailed_analysis -> abstract_plan -> lean_sketch -> explanation -> complete_proof`: `160`
- `detailed_analysis -> complete_proof`: `87`
- `detailed_analysis -> abstract_plan -> complete_proof`: `80`
- `detailed_analysis -> abstract_plan -> explanation -> complete_proof`: `65`
- `detailed_analysis -> lean_sketch -> complete_proof`: `57`
- `detailed_analysis -> lean_sketch -> explanation -> complete_proof`: `50`
- `detailed_analysis`: `30`
- `complete_proof`: `30`
- `detailed_analysis -> complete_proof -> explanation`: `24`
- `detailed_analysis -> explanation -> complete_proof`: `23`
- `abstract_plan -> lean_sketch -> complete_proof`: `5`
- `detailed_analysis -> abstract_plan`: `4`
- `abstract_plan -> lean_sketch -> explanation -> complete_proof`: `3`
- `lean_sketch -> complete_proof`: `2`
- `detailed_analysis -> abstract_plan -> lean_sketch -> complete_proof -> explanation`: `2`
- `detailed_analysis -> explanation -> abstract_plan -> lean_sketch -> complete_proof`: `2`
- `detailed_analysis -> explanation -> lean_sketch -> complete_proof`: `1`
- `detailed_analysis -> lean_sketch -> abstract_plan`: `1`
- `detailed_analysis -> lean_sketch -> abstract_plan -> explanation -> complete_proof`: `1`

## Most Common Last Pre-Code Headings

- `lean 4 have statements`: `167`
- `step 2 lean 4 have statements`: `89`
- `lean 4 proof sketch with have statements`: `82`
- `lean 4 code`: `52`
- `lean 4 proof sketch with have`: `39`
- `step 2 lean have statements`: `37`
- `complete lean 4 code`: `34`
- `lean 4 proof with have statements`: `26`
- `detailed proof and analysis`: `25`
- `lean have statements`: `22`
- `lean 4 proof sketch`: `18`
- `lean 4 proof sketch (using have statements)`: `17`
- `detailed proof`: `12`
- `step 3 lean 4 have statements`: `11`
- `proof plan`: `11`
- `step 2 lean 4 proof sketch with have statements`: `10`
- `lean 4 plan with have statements`: `10`
- `step 3 lean have statements`: `6`
- `step 2 have statements`: `5`
- `lean 4 sketch with have statements`: `4`

## Model Family Summary

### `deepseekv2`
- attempts: `656`
- exact `Complete Lean 4 Proof`: `642` (97.9%)
- any abstract-plan variant: `527` (80.3%)
- any detailed-proof variant: `651` (99.2%)
- any explanation variant: `269` (41.0%)
- parseable `detail + plan + proof`: `521` (79.4%)
- parseable `detail + plan + lean + proof`: `393` (59.9%)

### `deepseekv32`
- attempts: `76`
- exact `Complete Lean 4 Proof`: `0` (0.0%)
- any abstract-plan variant: `0` (0.0%)
- any detailed-proof variant: `76` (100.0%)
- any explanation variant: `24` (31.6%)
- parseable `detail + plan + proof`: `0` (0.0%)
- parseable `detail + plan + lean + proof`: `0` (0.0%)

### `goedelv2`
- attempts: `76`
- exact `Complete Lean 4 Proof`: `73` (96.1%)
- any abstract-plan variant: `55` (72.4%)
- any detailed-proof variant: `63` (82.9%)
- any explanation variant: `21` (27.6%)
- parseable `detail + plan + proof`: `46` (60.5%)
- parseable `detail + plan + lean + proof`: `34` (44.7%)

### `gpt52`
- attempts: `76`
- exact `Complete Lean 4 Proof`: `0` (0.0%)
- any abstract-plan variant: `0` (0.0%)
- any detailed-proof variant: `38` (50.0%)
- any explanation variant: `0` (0.0%)
- parseable `detail + plan + proof`: `0` (0.0%)
- parseable `detail + plan + lean + proof`: `0` (0.0%)

### `other`
- attempts: `44`
- exact `Complete Lean 4 Proof`: `44` (100.0%)
- any abstract-plan variant: `32` (72.7%)
- any detailed-proof variant: `41` (93.2%)
- any explanation variant: `20` (45.5%)
- parseable `detail + plan + proof`: `32` (72.7%)
- parseable `detail + plan + lean + proof`: `26` (59.1%)
