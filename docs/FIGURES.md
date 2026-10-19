# Figures

The figure set of the M5-AGE manuscript, what produces each one, and which submission number it
carries. `src/figure_check.py` reads this document and fails the gate chain when a
figure named here has not been produced, or a figure that has been produced is not named here.

## State before 19 October 2026

No figure had ever existed in `analysis/output`. Every figure in
`analysis/M5_AGE_analysis_pipeline.R` was written with `device = cairo_pdf`; the cairo shared object
cannot load on the analysis machine because the X11 libraries it links against are absent;
`cairo_pdf` warns rather than failing; `ggsave` returns normally; no file is created at the path it
was given. The run then counted the files in the output directory and printed `Pipeline complete. 35
output files written`, a statement that was true of the directory and false of the figures.
`capabilities()["cairo"]` reports TRUE on this machine, which is why the device was chosen and why
nothing in the script doubted it.

The figures were not merely absent. With the requested device unavailable, each `ggsave` fell
through to R's default device, which opens `Rplots.pdf` in the working directory, so all three
figures were drawn one after another into a single untracked file in the repository root, each
overwriting the last. The file recovered on 19 October held the third of them, the composite score
chart, carrying both of the defects since corrected: bars coloured by receptor class with the legend
suppressed, and an axis labelled in Hedges' g on a percent change scale. It also shows, visibly, an
error bar that does not reach the top of its own bar, which is the composite interval defect that
`src/composite_interval_check.py` now exists to catch. Three signals were available and none was
read: a warning in a run that emitted 35 of them, an output directory with no figures, and a plot
file in the repository root that `git status` listed among the untracked.

Three changes follow from that, and all three are in place:

| Change | Where |
| --- | --- |
| Figures are written with `grDevices::pdf` and `ragg::agg_png`, neither of which depends on cairo or X11 | `save_figure` in the pipeline |
| Each saved file is checked for existence and for a size above 1 KiB before the run reports it, and a figure that produced no file stops the run | `save_figure` |
| The figure set, the manifest hashes and this document are required to agree on every run | `src/figure_check.py` |

A capability a library reports is a claim. A file on disk is evidence. The pipeline now reports only
the second.

## The figure set

Point estimates are percent change relative to the comparator, which is the pooling scale this
review uses; it is a declared deviation from the registered Hedges' g plan, recorded at the head of
the pipeline. Three figures previously carried `Hedges' g` in their axis labels, which on this scale
would have understated every printed quantity by roughly a factor of twenty.

| Submission | File stem | Produced by | Content |
| --- | --- | --- | --- |
| Figure 1 | `figure0_prisma_flow` | `src/prisma_diagram.py` | PRISMA 2020 flow, three screening pools, 1009 records screened to 76 included trials |
| Figure 2 | `figure2_forest_overall` | pipeline section 10 | Forest plot of the overall pooled percent change per biomarker across all receptor classes, ordered by effect, with k and I2 per row |
| Figure 3 | `figure1_signature_heatmap` | pipeline section 10 | Direction adjusted signature heatmap, biomarkers by hallmark domain against the four receptor classes |
| Figure 4 | `figure4_weight_adjusted_liverfat` | pipeline section 10 | Liver fat against mean body weight change, point area inverse variance, point shape receptor class, line and band the random effects meta-regression of Table 4a |
| Figure 5 | `figure5_nbais` | pipeline section 10 | Net Biological Age Impact Score by receptor class under three weighting schemes, with the percentile interval of the two level bootstrap |
| Figure 6 | `figure6_rob_summary` | pipeline section 10 | RoB-2 judgements across the five domains and overall, as the share of assessed trials |
| Figure S1 | `figureS1_rob_traffic_light` | pipeline section 10 | Per trial RoB-2 traffic light for every assessed trial |

Each stem exists as a `.pdf` for submission and a 300 dpi `.png` for drafts and for inspection; the
PRISMA diagram is an `.svg` written directly rather than through ggplot. `analysis/output/figure_
index.csv` is written by the run and records the files, captions and sizes as they were saved.

## File names are not submission numbers

The numeric prefix in a file stem is historical and does not track the submission number: Figure 3
is `figure1_signature_heatmap`, because that figure was written first and named for its position in
an earlier plan. The stems are deliberately content named and deliberately stable. Submission
numbering changes between venues and at revision; a file whose name encodes a number has to be
renamed every time it does, and every record that cites the old name goes stale. This table is the
authoritative mapping, and `src/figure_check.py` keeps it honest.

The consequence for submission is that the upload step renames copies rather than the originals.
Journals require `Figure1.pdf` and the like; producing those is a scripted export from this table,
which is the next action below, not a rename in the repository.

## Design rules applied

| Rule | How it is met |
| --- | --- |
| One series takes one hue; hues are never cycled | Figures 2 and 5 are single series in one blue; Figure 5 previously coloured its bars by receptor class with the legend suppressed, which spent the identity channel on what the axis already named |
| A diverging ramp only for a signed quantity, with a neutral midpoint | Figure 3 uses the ColorBrewer RdBu poles with a near neutral midpoint, a published scheme with balanced arms |
| Identity never carried by colour alone | Figure 4 carries receptor class by point shape, Figure 2 by row label, Figure 6 and S1 by a glyph in every cell |
| Colour separation measured, not judged | No four hue set from the reference palette clears the all pairs colour vision deficiency and normal vision floors, measured with the palette validator, so Figure 4 spends no colour on class at all |
| Status scales are reserved and ship with a glyph and a label | Figures 6 and S1 use the status palette for low, some concerns and high, each cell carrying `+`, `?` or `x` so a monochrome print stays readable |
| Absence distinguishable from zero | Figure 3 marks a cell with no pooled estimate `n/e` and fills it with a grey clearly separated from the diverging midpoint; the previous `grey90` was within three per cent of it, so "no estimate" and "no effect" were the same colour |
| A figure's fitted line is the model the table reports | Figure 4's line is the random effects meta-regression, not the per class ordinary least squares lines `geom_smooth` had been drawing, one of them through a single point |

## What is not yet a figure

| Candidate | Why it is not here |
| --- | --- |
| Funnel plots per biomarker | `table_diagnostics.csv` carries the Egger test and trim and fill for every biomarker; a funnel plot is informative at k of 10 or more, which four biomarkers reach. A panel of four is a supplementary figure and is worth adding once the Director has settled which biomarkers the Results feature |
| Network geometry | The network block is gated off: 36 comparators cannot be collapsed into one placebo node when 240 rows are active controlled. There is no network to draw, and drawing one would assert a geometry the analysis declined to assume |
| Dose response curves | Dose arms are collapsed to one arm per trial per biomarker before pooling, so the pooled frame carries no dose axis. A dose response figure needs the pre collapse frame and a decision about shared controls that has not been taken |
| Epigenetic age | The inventory entry exists and no trial reports it, which Table 1 records as a gap. An empty panel is not a figure |

## Next actions

| Action | Owner |
| --- | --- |
| Scripted submission export that writes `Figure1.pdf` through `Figure6.pdf` and `FigureS1.pdf` from this table | agent, once the venue is chosen and its figure format is known |
| Figure callouts in the Results text, which currently names no figure at all | agent, with the remaining Results prose |
| Decide whether the funnel panel is included | Director |
