# Environmental disclosure gaps for compressed machine learning models

Replication package for:

> Gaur L, Raman R. Efficiency without accounting: environmental disclosure gaps
> for compressed machine learning models on a public model hub.
> *Manuscript submitted to Environmental Systems Research.*

An audit of the 3000 most-downloaded models on the Hugging Face Hub, sampled on
14 September 2026, measuring how often environmental information is attached to
models and to the compressed artifacts derived from them.

## Headline results

| Measure | Value |
|---|---|
| Models declaring the structured emissions field | 7 of 3000 (0.23%) |
| Cards reporting any environmental quantity | 11 of 590 (1.86%), from 6 accounts |
| Models carrying a compression or efficiency tag | 920 of 3000 (30.7%) |
| Quantizations among models declaring a parent | 740 of 1145 (64.6%) |
| Compression artifacts disclosing in either channel | 0 |
| Download volume attached to models with no emissions figure | 99.88% |

The four reporting conventions behind those 11 cards are described in the paper.
Seven of the 11 carry a single carbon-footprint block, six under two accounts
operated by the company that authored it and one a third-party republication.

## Repository layout

```
notebooks/
  01_hub_metadata_harness.ipynb        crawl: model metadata, parents, README text
  02_environmental_disclosure_analysis.ipynb   analysis against the cached crawl
src/
  analysis_v3.py                       final analysis, hand-verified patterns
data/
  hub_crawl_snapshot.zip               the cached crawl (2 MB, 9 files)
  cards_annotated.csv                  per-card flags used in Tables 2 and 3
docs/
  coding_protocol.md                   manual verification protocol
  student_coding_guidelines.md         blinded instructions for a second coder
figures/
  Fig1.png Fig2.png Fig3.png           figures as published
```

## Reproducing the results

The analysis reads the cached snapshot and makes no network calls, so every
number in the paper is recomputable without contacting the platform. The crawl
notebook is included for transparency but is not needed to reproduce the results
and will not return the same snapshot if re-run, because the hub changes.

```bash
pip install -r requirements.txt
unzip data/hub_crawl_snapshot.zip -d cache/
HF_GOV_CACHE=cache python src/analysis_v3.py
```

Expect: 3000 models, 590 cards with retrievable text, 7 models with the
`co2_eq_emissions` tag, 11 cards reporting a quantity.

In Colab, open `notebooks/02_environmental_disclosure_analysis.ipynb`, upload
the zip or mount Drive, and run all cells. The loader locates the cache
automatically.

## Data description

`data/hub_crawl_snapshot.zip` contains the full crawl. Only the first three
files are used by the analysis in this repository; the rest are included because
they were produced by the same crawl and support a companion study of licence
and provenance inheritance on the same snapshot.

| File | Used here | Contents |
|---|---|---|
| `models.jsonl` | yes | metadata for 3000 models: id, downloads, tags, licence, declared parents, derivation type |
| `readmes.jsonl` | yes | README text for 590 of 600 sampled models |
| `manifest.json` | yes | configuration, package versions, row counts, file checksums |
| `parents.jsonl` | no | metadata for 374 declared parent repositories outside the main sample |
| `license_edges.csv` | no | 1333 parent-child edges with licence inheritance outcomes |
| `prose_parents_fixed.csv` | no | per-card provenance extraction from the companion study |
| `prose_contradictions.csv` | no | superseded first-pass extraction, retained for transparency |
| `validation_parents_TO_CODE.csv` | no | manual coding sheet for the companion study |
| `validation_sample_TO_CODE.csv` | no | superseded coding sheet |

The archive deliberately contains no `figures/` directory. An earlier build of
this snapshot carried three figures belonging to the companion study, which
would have collided with this repository's own `figures/` on extraction.

The crawl records public repository metadata only. No personal data were
collected. Repository and account identifiers are public platform identifiers.

## Method notes worth reading before reuse

**Quantity detection requires a number.** A card counts as reporting a quantity
only when a numeral is attached to a unit. An earlier keyword-only rule matched a
dataset named Visual7W, a model named vlT5kw, an image URL fragment, a coordinate
tuple in example code, and a phrase describing a graphics card used for timing.
All 23 candidate matches under the corrected patterns were inspected by hand and
confirmed.

**Card counts overstate independent practice.** Card text is copied between
repositories, so organization counts are reported alongside card counts
throughout. Any reuse of this code should do the same.

**Precision is measured, recall is not.** The sample is drawn from cards where
detection fired, so the reported rate is a lower bound.

## Citation

See `CITATION.cff`. Please cite the paper rather than this repository where
the finding is what you are citing.

## Licence

Code is released under the MIT Licence (`LICENSE`). The cached data in `data/`
is released under CC BY 4.0. The underlying model cards remain under the
licences set by their respective publishers.
