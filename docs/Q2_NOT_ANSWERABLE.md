# Q2 cannot currently be answered

Computed 2026-10-15 from the 47 row corpus. Recorded because it determines what work matters next.

## The result

**Zero of fifteen biomarkers support a replicated receptor class contrast.**

| Biomarker | mono | GIP | GCGR | triple | classes |
|---|---|---|---|---|---|
| hsCRP | 1 | 1 | 0 | 0 | **2** |
| GDF-15, IL-6, YKL-40, ICAM-1, leptin, NT-proBNP | 0 | 1 | 0 | 0 | 1 |
| HOMA-IR, HOMA-beta, adiponectin, glucagon, C-peptide, fasting glucose, fasting insulin | 0 | 0 | 2 | 0 | 1 |
| liver fat PDFF | 0 | 0 | 0 | 1 | 1 |

Fourteen of fifteen biomarkers appear in exactly one receptor class. The fifteenth, hsCRP, appears in two classes with one trial each, which makes any difference between them confounded with every other way those two trials differ: population, duration, assay, era, sponsor.

## Why the corpus looks like this

Each trial contributed a disjoint biomarker panel, and each trial belongs to one class.

| Trial | Class | What it measured |
|---|---|---|
| Wilson 2021 tirzepatide | GLP1_GIP | the inflammatory and endothelial panel |
| Ekinci 2026 survodutide | GLP1_GCGR | the glycaemic and adipokine panel |
| SELECT (Plutzky, Meyhofer) | GLP1_mono | hsCRP and liver enzymes |
| Sanyal 2024 retatrutide | triple | liver fat only |

The classes are almost perfectly confounded with the biomarker panels. This is not bad luck. It is what opportunistic extraction from convenience sampled trials produces: each paper was found because it reported something interesting, and different papers report different things.

## What this means

The descriptive per class means in `table3b` are **not comparable to one another** and must never be presented as a class contrast. GLP1_GIP_GCGR shows the largest value (82.7 per cent) only because its single marker is liver fat, which has the largest effect of any marker in the corpus. GLP1_mono shows 37.8 per cent because its only included marker is hsCRP. These numbers describe different things.

Q2 is the review's central claim to novelty, and it is currently unanswerable. Not weakly answered. Unanswerable.

## What would fix it

Not more opportunistic extraction. The problem is structural: adding another trial that reports a unique panel adds a row and no comparability.

What is needed is biomarkers measured in **at least two trials in each of at least two classes**. The practical route is the one already identified: the reference lists of Ren 2025 (52 RCTs) and Alrasheed 2026 (40 RCTs), which are overwhelmingly mono agonist trials reporting CRP, IL-6, TNF-alpha, leptin and adiponectin.

That would give the mono class depth on exactly the markers where GLP1_GIP (Wilson) and GLP1_GCGR (Ekinci) already have data. hsCRP, IL-6, leptin and adiponectin are the four biomarkers where a replicated contrast is reachable soonest.

| Target | Needs |
|---|---|
| hsCRP | mono trials beyond SELECT; GIP trials beyond Wilson |
| IL-6 | mono trials; a second GIP trial |
| leptin | mono trials; a second GIP trial |
| adiponectin | mono trials; GIP data, currently none |

## Honest statement for the manuscript

Until that work is done, the review can report Q1 (which biomarkers move, and how much) and Q4 with its caveats, and must report Q2 as a structured demonstration that the comparison is not yet possible, naming exactly which trials would make it possible.

That is a weaker paper than intended. It is also the only defensible one from this corpus, and the specification of what is missing is itself usable by anyone designing the next trial.
