# Coding protocol: prose provenance extraction

Version 1.0. Applies to `validation_coding_sheet.csv` (45 cards).

## 1. What you are validating

The pipeline extracts, from a model card's prose, the identifier of a model it
claims this model was derived from. You are judging **whether that extracted
identifier really is a derivation ancestor of this model**, as the card itself
presents it.

You are *not* judging whether the model's tag metadata is correct, whether the
card is well written, or whether the license is appropriate. Only the extraction.

**Unit of analysis:** one card (one row).

## 2. Procedure

1. Hide the `flag_agree` column before you start. Your judgment must not be
   anchored on what the pipeline concluded.
2. Read `evidence_1` (and `evidence_2` if present). This is the exact sentence
   from the card that triggered extraction.
3. Assign a `relation_code` from Section 3. The sentence is usually enough.
4. Open `card_url` only if the sentence is ambiguous. If still ambiguous after
   reading the card, code `unclear` and say why in `human_note`.
5. For rows where `cell` is `disagree`, also fill `which_channel_correct`
   (Section 5).
6. Do not revise earlier rows after you develop a view partway through. If a
   rule needs changing, finish the pass, amend this document, and recode from
   the start. Record that you did so.

Budget roughly 20 to 30 minutes for 45 rows.

## 3. Relation codes

Assign exactly one, choosing the first that applies.

| Code | Meaning |
|---|---|
| `immediate_parent` | The extracted model is the direct input to the derivation that produced this model: the model that was finetuned, quantized, converted, merged, or adapted. |
| `ancestor` | A real ancestor but not the direct input, e.g. the parent of the parent. Common when a derivative copies its parent's card text verbatim. |
| `teacher` | Source of knowledge distillation or weight alignment, where this model was not initialized from it. |
| `sibling_variant` | A different variant of the same model by the same author (another quantization level, an uncensored edition). Not an ancestor. |
| `evaluation_component` | A model used in benchmarking, retrieval of candidates, or comparison. Not an ancestor. |
| `component` | A tokenizer, encoder, or module incorporated into this model but not the model it was derived from. |
| `unrelated` | Mentioned for any other reason: recommendations, related work, author's other projects. |
| `unclear` | Cannot be determined from the sentence or the card. |

## 4. Deriving the verdict

`human_verdict` follows mechanically from `relation_code`, so fill the code
first and let the verdict follow. This keeps the judgment on observable
relations rather than on a right/wrong intuition.

- `immediate_parent`, `ancestor`, `teacher` -> `true_positive`
- `sibling_variant`, `evaluation_component`, `component`, `unrelated` -> `false_positive`
- `unclear` -> `unclear`

Rationale for including `ancestor` and `teacher` as true positives: the claim
the pipeline makes is that the prose names a derivation source, not that it
names the immediate parent. Report `immediate_parent` separately so a reader
can apply the stricter definition if they prefer.

## 5. Extra field for the `disagree` cell

`which_channel_correct`, one of:

- `tag` - the metadata names the immediate parent, the prose names something else
- `prose` - the prose names the immediate parent, the metadata is wrong or coarser
- `both` - both are true at different hops (tag names the parent, prose names the grandparent)
- `neither`
- `unclear`

## 6. Worked examples from this sample

**`stelterlab/Mistral-Small-24B-Instruct-2501-AWQ`**
Tag: `mistralai/Mistral-Small-24B-Instruct-2501`. Prose: "an instruction-fine-tuned
version of the base model: Mistral-Small-24B-Base-2501".
The AWQ quantization inherited Mistral's own card text, which describes how the
*Instruct* model was made. Base-2501 is the grandparent.
-> `relation_code: ancestor`, `human_verdict: true_positive`, `which_channel_correct: both`

**`Qwen/Qwen3-Reranker-8B`**
Prose: "the top-100 candidates retrieved by dense embedding model Qwen3-Embedding-0.6B".
This is a benchmarking setup description. The embedding model retrieved candidates
for evaluation; it is not an ancestor.
-> `relation_code: evaluation_component`, `human_verdict: false_positive`, `which_channel_correct: tag`

**`Bucoid/Qwen3.8-27B-Uncensored-IQ4-XS-MTP-16GB-VRAM-GGUF`**
Prose links `Bucoid/Qwen3.8-27B-Heretic-Ara-IQ4-XS-16GB-VRAM-GGUF`, described as
an alternative to download. Same author, parallel edition.
-> `relation_code: sibling_variant`, `human_verdict: false_positive`, `which_channel_correct: tag`

**`MongoDB/mdbr-leaf-ir`**
Tag: `microsoft/MiniLM-L6-v2`. Prose: "aligned to snowflake-arctic-embed-m-v1.5,
the model it has been distilled from".
Both are real: MiniLM is the initialization, Arctic is the distillation teacher.
-> `relation_code: teacher`, `human_verdict: true_positive`, `which_channel_correct: both`

**`xinsir/controlnet-openpose-sdxl-1.0`**
Prose: "Finetuned from model [optional]: stabilityai/stable-diffusion-xl-base-1.0",
with no `base_model` tag present.
-> `relation_code: immediate_parent`, `human_verdict: true_positive`

## 7. Reliability

Single-coder validation is weaker than a reviewer would like. In order of
preference:

1. **Two coders.** Have a doctoral student code all 45 independently against this
   document. Report Cohen's kappa on `relation_code`. Resolve disagreements by
   discussion and report how many needed it.
2. **Intra-rater.** Code the sheet, wait at least 48 hours, code a shuffled copy
   again blind to the first pass, and report the agreement between your two passes.

Kappa above 0.80 is strong, 0.60 to 0.80 is acceptable and worth stating plainly.
If it falls below 0.60, the categories are underspecified and this document needs
revising before the numbers mean anything.

## 8. What to report in the paper

- Precision of the extraction overall and per cell, with the `unclear` rate stated
  separately rather than folded into either side.
- The distribution of `relation_code`, which is a finding in its own right:
  it shows *how* prose provenance claims fail, not merely how often.
- The number of cards whose prose appears inherited from a parent card, since
  that is the mechanism behind most of the ancestor cases.
- Coder count, kappa, and this document as an appendix or repository file.

## 9. Known limits of this instrument

- Card prose is sometimes copied verbatim from the parent, so "what the card
  claims" and "what the author wrote" are not always the same thing. The
  `ancestor` code captures this but does not resolve it.
- The sample is drawn from cards where extraction fired, so precision is
  measurable but recall is not. State this. Estimating recall would require
  coding a random sample of cards where extraction did not fire.
- Judgments are made from the sentence by default, not the whole card. Note the
  proportion of rows where you opened the card.
