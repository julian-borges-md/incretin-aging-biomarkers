# Figures

The figure set of the M5-AGE manuscript, what produces each one, which submission number it
carries, and what its plotted values are recomputed from. `src/figure_check.py` reads this document
and fails the gate chain when a figure named here has not been produced, a figure that has been
produced is not named here, or a figure plots values that differ from the tables it is drawn from.

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

| Submission | File stem | Produced by | Plotted values, recomputed from | Content |
| --- | --- | --- | --- | --- |
| Figure 1 | `figure0_prisma_flow` | `src/prisma_figure.R` (`make prisma`) | `figure0_prisma_flow.csv`; every box count recomputed by `src/prisma_counts.py` from `docs/prisma_counts.json` | PRISMA 2020 flow, three screening pools, 1009 records screened to 76 included trials |
| Figure 2 | `figure2_forest_overall` | pipeline section 10 | `figure2_forest_overall.csv`; `table2_pipeline.csv`, with names and favourable directions from `biomarker_inventory.csv` | Forest plot of the overall pooled percent change per biomarker across all receptor classes, ordered by effect, set as a table: name, favourable direction and k, the estimate with its interval, and I² per row |
| Figure 3 | `figure1_signature_heatmap` | pipeline section 10 | `figure1_signature_heatmap.csv`; `table3_primary_results.csv` times the aging direction in `biomarker_inventory.csv` | Direction adjusted signature heatmap, biomarkers by hallmark domain against the four receptor classes |
| Figure 4 | `figure4_weight_adjusted_liverfat` | pipeline section 10 | `figure4_weight_adjusted_liverfat.csv`; points matched to `extraction_master_harmonised.csv`, line and band refitted at the variance of `table4a_hepatic_metaregression.csv`, arm count against `table2_pipeline.csv` | Liver fat against mean body weight change, point area inverse variance, point shape receptor class, line and band the random effects meta-regression of Table 4a |
| Figure 5 | `figure5_nbais` | pipeline section 10 | `figure5_nbais.csv`; the computed rows of `table5_nbais.csv` | Net Biological Age Impact Score by receptor class under three weighting schemes, with the percentile interval of the two level bootstrap |
| Figure 6 | `figure6_rob_summary` | pipeline section 10 | `figure6_rob_summary.csv`; recounted from `risk_of_bias.csv` | RoB-2 judgements across the five domains and overall, as the share of assessed trials |
| Figure S1 | `figureS1_rob_traffic_light` | pipeline section 10 | `figureS1_rob_traffic_light.csv`; `risk_of_bias.csv` | Per trial RoB-2 traffic light for every assessed trial |

Each stem exists as a vector `.pdf` for submission, its glyphs drawn as outlines, and a 600 dpi
`.png` for documents and inspection, both drawn at the figure's journal width in figure style 2
(described below); the PRISMA diagram is drawn the same way by `src/prisma_figure.R` rather than by
the pipeline. Each stem also exists as a `.csv`, the figure's plotted values, described in the next
section. `analysis/output/figure_index.csv` is written by the run and records the files, the
plotted values, captions and sizes in millimetres as they were saved; the captions there are the
figure legends, since no figure carries a title or caption inside it.

## Plotted values

Every figure writes the values it draws beside it, as a data twin with the figure's stem and the
extension `.csv`, added 23 October 2026. The checks above establish that a figure exists, is the
file the run produced and is the one the manuscript numbers; none of them reads what the figure
shows, and a PDF does not record which number a mark stands for. A figure is a second rendering of
numbers a table already reports, and the two can disagree with every file present: until 19
October Figure 4 drew one least squares line per receptor class beside a table reporting a random
effects meta-regression, and nothing in the repository could have noticed.

| Element | Rule | Where |
| --- | --- | --- |
| Twin | The data frame each layer is drawn from, with the columns the figure encodes; a figure with several layers stacks them under a `layer` column; empty cells are values the figure leaves empty, such as a heatmap cell with no pooled estimate | `write_twin` and `save_figure` in `analysis/figure_style.R`, used by the pipeline and by `src/prisma_figure.R` |
| Rounding | Doubles to ten significant digits, far finer than anything readable from a figure and far coarser than a platform's last bits, so the twin of an unchanged figure is the same file on every run | `write_twin` |
| Content check | One rule per figure recomputes its twin from the files named in the table above, without the pipeline, and requires agreement to the ten digits written; a produced figure with no rule fails, so a figure enters the manuscript with the rule that checks it | `src/figure_check.py`, in the gate chain with its self test |
| Record | Each figure's row above names its twin and every file its rule reads, and the gate fails when it does not | `src/figure_check.py` |
| Determinism | The PDF device writes no creation or modification time and the PNG device none at all, so an unchanged figure is byte identical across runs on one machine and the manifest records a change only when a figure changed | `PDF_ARGS` in `analysis/figure_style.R` |

Two of the rules do more than look values up. Figure 4's points must each be one of their trial's
liver fat arms in the harmonised master, with that trial's receptor class, and weighted least
squares at the between trial variance Table 4a reports must reproduce from them that table's slope
and standard error, which holds only if they are the points the model was fitted to; the drawn line
and band must then be that fit's prediction and confidence band at every one of the hundred points
drawn. Figure 5's rule compares the drawn interval with the percentile interval of
`table5_nbais.csv` and requires the table to label it so, because the table carries the BCa interval
beside it, and a figure drawing that one would match a column of the table and contradict its own
caption.

The self test injects into the tracked twins and tables the defects the rules exist for, among them
another dose arm of a trial plotted in Figure 4, its line fitted by unweighted least squares, the
method of the per class lines drawn until 19 October, the BCa interval drawn in Figure 5, a
favourable direction flipped in Figure 2, a judgement recoded in the risk of bias data, a PRISMA
count changed without the diagram being redrawn and a PRISMA box summed without one of its terms,
and requires each to be caught and the tracked figures to pass.

## Figure style 2

Adopted 24 October 2026 at the Director's decision for more resolution and a more modern style, the
standard the laboratory's governed research template and its other programs draw in. Until then the
figures were drawn at a size chosen for each in inches, in the device's default face, at 300 dpi,
with a caption inside the image; a journal reduces such a figure to its column width, so its text
reached the page at whatever size the reduction left, and the caption appeared twice.

| Element | Standard | Where |
| --- | --- | --- |
| Size | Drawn at the final journal width, 89 mm (single column), 120 mm (one and a half) or 183 mm (double), at most 170 mm high, or 247 mm, the full page depth, for a supplementary figure that is a page of its own; nothing is rescaled in production | `save_figure` refuses any other size |
| Typeface | Inter 4.1 (SIL Open Font License 1.1, `analysis/fonts/OFL-Inter.txt`), Regular, Italic, Medium and SemiBold, vendored in `analysis/fonts` and verified by SHA-256 before anything is drawn; a file that differs from its digest stops the run | `register_figure_fonts` |
| Text | 7 pt axis titles, 6.5 pt ticks, legends and table columns, 6.3 pt values printed on marks, 5.8 pt in the PRISMA boxes and the 77 rows of Figure S1; numbers carry a true minus sign | `FIG_PT`, `fig_num`, `fig_axis_number` |
| Devices | PDF through `grDevices::pdf` with showtext, which draws every glyph as an outline, so the file needs no font wherever it is opened; PNG at 600 dpi through `ragg`; neither depends on cairo or X11 | `save_figure` |
| Colour | The validated categorical blue for every single series; the sequential blue ramp for magnitude; a diverging ramp from the dark orange step through a hueless grey to the sequential blue for the signed heatmap; status colours only for risk of bias, always with a glyph; text in the ink tokens, white on the darkest fills by computed contrast | `analysis/figure_style.R` |
| Layout | White surface, left and bottom axes only, light gridlines on value axes, legends outside the plotting area, no title or caption inside a figure | `theme_figure` |

The sizes, stem first, because the gate reads the rows that begin with the submission number as the
figure set table above:

| File stem | Submission | Width, mm | Height, mm |
| --- | --- | --- | --- |
| `figure0_prisma_flow` | Figure 1 | 183 | 145, set by its content |
| `figure2_forest_overall` | Figure 2 | 183 | 20 plus 4.4 per biomarker row, 143.2 for 28 |
| `figure1_signature_heatmap` | Figure 3 | 120 | 150 |
| `figure4_weight_adjusted_liverfat` | Figure 4 | 120 | 82 |
| `figure5_nbais` | Figure 5 | 183 | 60 |
| `figure6_rob_summary` | Figure 6 | 183 | 52 |
| `figureS1_rob_traffic_light` | Figure S1 | 120 | 240 |

The figure gate reads the files themselves as well as the records of them: every figure has both
files; the PNG records 600 dpi and is a journal width wide and within its height; the size in
`figure_index.csv` is the PNG's; the PDF is the PNG's size, carries no date and declares no font,
because a font resource in a figure drawn in outlines is text set in a face other than Inter. Its
self test builds files with each of those defects and requires each to be caught.

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
| A diverging ramp only for a signed quantity, with a neutral midpoint | Figure 3 runs from the dark orange step through a hueless grey to the steps of the validated sequential blue, both arms scaled by the largest magnitude on either side; it replaced the ColorBrewer RdBu poles on 24 October, whose red arm is the colour the risk of bias figures reserve for high risk |
| Identity never carried by colour alone | Figure 4 carries receptor class by point shape, Figure 2 by row label, Figure 6 and S1 by a glyph in every cell |
| Colour separation measured, not judged | No four hue set from the reference palette clears the all pairs colour vision deficiency and normal vision floors, measured with the palette validator, so Figure 4 spends no colour on class at all |
| Status scales are reserved and ship with a glyph and a label | Figures 6 and S1 use the status palette for low, some concerns and high, each cell carrying `+`, `?` or `×` so a monochrome print stays readable, and the legend carries the same glyphs |
| A number printed on a filled mark stays legible | The ink of each printed value is chosen by its contrast with the fill it sits on, computed with the scale's own palette: white on the darkest blues of Figure 3 and on the high risk red of Figure 6 |
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
