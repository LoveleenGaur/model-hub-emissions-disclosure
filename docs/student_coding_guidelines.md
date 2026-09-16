# Coding guidelines for the second rater

You are the second independent coder on a study of how model provenance is
documented on the Hugging Face Hub. Your codes will be compared against a first
rater's using Cohen's kappa, which is a published measure of whether two people
applying the same rules reach the same conclusions. That comparison only means
something if you work independently, so please read Section 6 before you start.

Time required: roughly 30 minutes for 45 rows.

---

## 1. Background in three sentences

Most models on the Hub are derived from other models: fine-tuned, quantized,
merged, or adapted. A model card can record that ancestry in two places, a
structured `base_model` field read by tooling, and the human-readable prose of
the card. We built an automated extractor that reads the prose and pulls out
the identifier of the model it thinks this model was derived from. You are
checking whether the extractor got it right.

## 2. What you are judging

For each row: **is the identifier in the `prose_parent` column genuinely a
derivation ancestor of the model in the `id` column, as the card itself
presents it?**

You are NOT judging:

- whether the `tag_parent` value is correct
- whether the card is well written or complete
- whether the model is any good

Only whether the extracted identifier is really an ancestor.

**Unit of analysis:** one row, one card.

## 3. Procedure

1. Read `evidence_1`, and `evidence_2` if it is filled. This is the exact
   sentence from the card that caused the extractor to pull out `prose_parent`.
2. Assign one `relation_code` from Section 4.
3. Open `card_url` only if the sentence leaves you unsure. If you open it,
   put `y` in `opened_card`. We report that proportion in the methods section,
   so please be accurate about it.
4. If both `tag_parent` and `prose_parent` are filled, also complete
   `which_channel_correct` (Section 5). Leave it blank otherwise.
5. Add a short `note` explaining your reasoning. One line is enough. These are
   genuinely useful when we reconcile disagreements later.

Work down the sheet in order. Do not go back and revise earlier rows once you
have developed a feel for the task partway through. If you think a rule is
wrong, finish the pass, then tell us.

## 4. Relation codes

Assign exactly one code per row. Take the first that applies.

| Code | Meaning |
|---|---|
| `immediate_parent` | The extracted model is the direct input to whatever produced this model: the thing that was fine-tuned, quantized, converted, merged, or adapted. |
| `ancestor` | A genuine ancestor but not the direct input, for example the parent of the parent. This happens often when a derivative copies its parent's card text word for word. |
| `teacher` | The source of knowledge distillation or weight alignment, where this model was not initialized from it. |
| `sibling_variant` | A different edition of the same model, usually by the same author: another quantization level, an uncensored version, a 4-bit build. Not an ancestor. |
| `evaluation_component` | A model used in benchmarking, comparison, or to retrieve candidates in an evaluation. Not an ancestor. |
| `component` | A tokenizer, encoder, or module built into this model, but not the model it was derived from. |
| `unrelated` | Mentioned for some other reason entirely: a dataset, a documentation page, related work, the author's other projects. |
| `unclear` | You cannot tell, even after opening the card. Use this rather than guessing. |

`unclear` is a legitimate answer. We would rather have an honest `unclear` than
a coin flip, and we report the rate separately.

## 5. `which_channel_correct`

Only for rows where both `tag_parent` and `prose_parent` are filled. Which
channel names the **immediate** parent?

- `tag` - the structured field has it right, the prose points elsewhere
- `prose` - the prose has it right, the structured field is wrong or vaguer
- `both` - both are true, at different hops (tag names the parent, prose names the grandparent)
- `neither`
- `unclear`

## 6. Independence

This is the part that makes the exercise worth doing.

- Do not discuss any specific row with the first coder or the supervisor until
  you have submitted the whole sheet.
- Do not ask anyone whether a particular answer is right.
- If a rule genuinely does not cover a case, code your best judgment, write a
  note, and carry on. Ask afterwards.
- Disagreement between the two of us is expected and is data, not failure. A
  study reporting 100% agreement usually means someone was influenced.

## 7. Worked examples

These are **constructed** illustrations, not rows from your sheet. We wrote
them rather than reusing real cases so that nothing here gives away an answer.

**A.** Card for `acme/bert-sentiment`. Sentence: "This model is a fine-tuned
version of [acme-labs/bert-base-xx](https://huggingface.co/acme-labs/bert-base-xx)
on a product review dataset." Extracted: `acme-labs/bert-base-xx`.
The extracted model is exactly what was fine-tuned.
-> `immediate_parent`

**B.** Card for `someone/foo-instruct-AWQ`, a quantized build. Tag says
`orgx/foo-instruct`. Sentence: "This model is an instruction-fine-tuned version
of the base model orgx/foo-base." Extracted: `orgx/foo-base`.
The quantizer copied the parent's card, and that sentence describes how the
*parent* was made. Foo-base is the grandparent, which is a real ancestor.
-> `ancestor`, and `which_channel_correct` = `both`

**C.** Card for `orgz/leaf-retriever`. Tag says `microsoft/tiny-encoder`.
Sentence: "aligned to orgy/embed-v2, the model it has been distilled from."
Extracted: `orgy/embed-v2`.
Distillation source, and the model was initialized from something else.
-> `teacher`, and `which_channel_correct` = `both`

**D.** Card for `bob/model-8bit`. Sentence: "If you need the 4-bit edition,
download bob/model-4bit instead." Extracted: `bob/model-4bit`.
A parallel edition by the same author, not an ancestor.
-> `sibling_variant`

**E.** Card for `org/reranker-large`. Sentence: "All scores are based on the
top-100 candidates retrieved by orgw/embed-small." Extracted: `orgw/embed-small`.
This describes an evaluation setup, not how the model was built.
-> `evaluation_component`

**F.** Card for `org/vision-model`. Sentence: "It uses orgv/clip-vit-l as its
text encoder." Extracted: `orgv/clip-vit-l`.
A module inside the model, not the model it was derived from.
-> `component`

**G.** Card for `org/ner-model`. Sentence: "This model is a fine-tuned version
of roberta-large on the org/some-corpus dataset." Extracted: `org/some-corpus`.
The extractor grabbed the dataset, not the model.
-> `unrelated`

## 8. Common traps

- **A link is not a claim.** Cards link to many things: alternatives, demos,
  documentation, papers. Only code an ancestor relation when the sentence says
  this model came from that one.
- **Watch the direction.** "You can find the quantized version here" points
  *downstream*, to something built from this model. That is not an ancestor.
- **Datasets and docs look like models.** Identifiers like `org/some-corpus`
  or a `.../model_doc/...` path are not model repositories. Code `unrelated`.
- **Copied card text is common.** Small repositories often paste the upstream
  card wholesale. The sentence may describe a model further up the chain.
  That is `ancestor`, not an error.
- **The repository name can mislead.** Judge from the card's claim, not from
  what the repo happens to be called.

## 9. What to send back

The completed CSV, with `relation_code` filled for all 45 rows,
`which_channel_correct` filled where applicable, `opened_card` marked, and a
short note per row. Please do not rename or reorder the columns.

Thank you. This step is what lets the finding be reported as a measured result
rather than an unverified one, and you will be credited in the paper's methods
for the reliability coding.
