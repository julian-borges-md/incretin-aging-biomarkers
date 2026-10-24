###############################################################################
# prisma_figure.R
#
# Draws the PRISMA 2020 flow diagram, Figure 1 of the submission, from docs/prisma_counts.json in
# figure style 2 (analysis/figure_style.R): 183 mm wide, in the vendored Inter typeface, as a
# vector PDF and a 600 dpi PNG, with its data twin, the count in every box.
#
# It replaced src/prisma_diagram.py on 24 October 2026. That script drew the diagram as an SVG
# whose text the viewer set in its own Helvetica or Arial, at no journal size and with a title
# inside it; the decision of that day for figure style 2 made every figure of the submission one
# standard, which an SVG set in the viewer's fonts cannot meet. Its design constraints carry over
# unchanged, each from a source rather than from taste:
#
#   1. docs/PRISMA_FLOW.md requires that Stream B, the mono agonist trials adopted from two
#      published reviews, is shown as a SEPARATE inflow and never merged into our own screening
#      stages: "A single merged diagram implying one unified search would misrepresent the
#      process." It is drawn as a dashed box joining at the synthesis, by a dashed route down the
#      right margin that crosses none of the exclusion boxes, with its status in the box text.
#   2. Every number is computed here from the declared counts and asserted before anything is
#      drawn. A PRISMA diagram is a chain of subtractions, so a box holding a number that does not
#      follow from the box above it is a published error. src/prisma_check.py asserts the
#      identities among the recorded counts; this script asserts the ones the diagram itself
#      creates, which are the exclusion counts shown on the right.
#   3. No data is encoded in colour. A flow diagram has no series; the adopted inflow is
#      distinguished by a dashed outline AND its label, and each phase by its label, never by
#      colour alone. The figure is legible in greyscale print.
#
# The layout is computed in millimetres before anything is drawn: every line of text is wrapped to
# its box with the typeface's own advance widths (systemfonts, at the size it is set in), every box
# takes the height of its lines, and the page takes the height of its boxes. The diagram is then
# drawn by ggplot2 on a canvas of exactly that size, one data unit to the millimetre, so it passes
# through save_figure like every other figure and is written by the same two devices.
#
# The figure gate (src/figure_check.py) recomputes every count of the twin with src/prisma_counts.py,
# an independent implementation in Python of the same arithmetic from the same file, and fails on
# any difference, so a declared count changed without this script being rerun, or a twin edited by
# hand, stops the gate chain.
#
# Usage, from the repository root:   Rscript src/prisma_figure.R [output directory]   (make prisma)
# The output directory defaults to analysis/output. Exit status 1 if any count on the diagram fails
# to follow from the counts above it.
###############################################################################

args <- commandArgs(trailingOnly = TRUE)
OUT_DIR <- if (length(args) >= 1) args[1] else file.path("analysis", "output")
source(file.path("analysis", "figure_style.R"))

counts <- jsonlite::read_json(file.path("docs", "prisma_counts.json"))
a   <- counts$stream_a_identification
sb  <- counts$stream_b_adopted
b   <- counts$title_abstract_screening
f   <- counts$full_text_stage
g   <- counts$grouping_and_extraction
inc <- counts$included_in_synthesis

# Counts the diagram itself creates, asserted before use.
ex_screen <- b$pool1_v2_remain_excluded + b$pool2_exclude + b$pool3_exclude
if (ex_screen + b$records_to_full_text != b$records_screened_all_pools) {
  stop(sprintf("screening does not balance: %d + %d != %d", ex_screen, b$records_to_full_text,
               b$records_screened_all_pools), call. = FALSE)
}
ex_fulltext <- f$needing_a_screen - f$included_records
if (ex_fulltext < 0) stop("negative full text exclusions", call. = FALSE)
not_assessed <- f$without_any_text + f$already_in_master
closed <- g$no_usable_contrast_scan + g$no_usable_contrast + g$excluded_at_extraction +
  g$molecule_not_admitted + g$ongoing_no_results + g$held_pending_decision
contributing <- g$extracted + g$already_extracted
if (closed + contributing != g$ledger_groups_final) {
  stop(sprintf("ledger does not balance: %d + %d != %d", closed, contributing,
               g$ledger_groups_final), call. = FALSE)
}

# The text of every box. Titles carry the box count; the counts are the variables the twin records.
n_ <- function(x) format(x, scientific = FALSE, trim = TRUE)
boxes <- list(
  list(row = 1, col = "main",
       title = sprintf("Records identified from our own searching (n = %s)",
                       n_(b$records_screened_all_pools)),
       body = c(sprintf("Embase, 15 Oct 2026: %s hits, %s article records and %s registry records exported",
                        n_(a$embase_hits), n_(a$embase_article_records_exported),
                        n_(a$embase_registry_records_exported)),
                sprintf("CENTRAL, 15 Oct 2026: %s exported, %s not already in Embase",
                        n_(a$central_records_exported), n_(a$central_unique)),
                sprintf("Web of Science, 16 Oct 2026: %s exported, %s in neither other database",
                        n_(a$wos_records_exported), n_(a$wos_in_neither)),
                sprintf("PubMed anchor searches for the dual and triple agonists: %s, %s and %s PMIDs",
                        n_(a$pubmed_anchor_body_composition), n_(a$pubmed_anchor_hepatic),
                        n_(a$pubmed_anchor_gdf15)))),
  list(row = 1, col = "side", dashed = TRUE,
       title = "Separate inflow, not from our searching",
       body = c(sprintf(paste("Mono agonist comparator trials adopted from two published systematic",
                              "reviews: Alrasheed 2026, %s RCTs; Ren 2025, %s RCTs."),
                        n_(sb$alrasheed_2026_rcts), n_(sb$ren_2025_rcts)),
                paste("Their screening was performed by other groups and is inherited, so these",
                      "records do not pass through the stages below. Re-screened against this",
                      "review's criteria at extraction."))),
  list(row = 2, col = "main",
       title = sprintf("Records screened, title and abstract (n = %s)",
                       n_(b$records_screened_all_pools)),
       body = c(sprintf(paste("Three pools screened on different days by two independent reviewers",
                              "with a third adjudicating: pool 1, the %s Embase articles; pool 2, %s",
                              "registry and CENTRAL only records; pool 3, %s Web of Science records."),
                        n_(a$embase_article_records_exported), n_(b$pool2_records),
                        n_(b$pool3_records)),
                sprintf("Cohen kappa %s (pool 1) and %s (pool 2).",
                        as.character(b$kappa_pool1_v1), as.character(b$kappa_pool2_v2)))),
  list(row = 2, col = "side",
       title = sprintf("Records excluded (n = %s)", n_(ex_screen)),
       body = c(sprintf("Pool 1 after the criteria v2 rescreen of its v1 exclusions: %s (%s of %s rescued).",
                        n_(b$pool1_v2_remain_excluded), n_(b$pool1_v2_rescued_from_exclusions),
                        n_(b$pool1_v1_exclude)),
                sprintf("Pool 2: %s.  Pool 3: %s.", n_(b$pool2_exclude), n_(b$pool3_exclude)))),
  list(row = 3, col = "main",
       title = sprintf("Records sought for full text (n = %s)", n_(b$records_to_full_text)),
       body = sprintf("Pool 1: %s.  Pool 2: %s.  Pool 3: %s.", n_(b$pool1_to_full_text),
                      n_(b$pool2_include), n_(b$pool3_include))),
  list(row = 3, col = "side",
       title = sprintf("Not assessed (n = %s)", n_(not_assessed)),
       body = c(sprintf("No text obtainable: %s, listed with reasons.", n_(f$without_any_text)),
                sprintf("Already held in the master under another record: %s.",
                        n_(f$already_in_master)))),
  list(row = 4, col = "main",
       title = sprintf("Records assessed at full text (n = %s)", n_(f$needing_a_screen)),
       body = sprintf(paste("Raw agreement %s of %s, Cohen kappa %s, low because the marginals are",
                            "extremely unbalanced and reported as such. All %s disagreements",
                            "adjudicated, %s to include and %s to exclude."),
                      n_(f$raw_agreement_numerator), n_(f$raw_agreement_denominator),
                      as.character(f$kappa), n_(f$disagreements_adjudicated),
                      n_(f$adjudicated_to_include), n_(f$adjudicated_to_exclude))),
  list(row = 4, col = "side",
       title = sprintf("Records excluded (n = %s)", n_(ex_fulltext)),
       body = "Design, population, intervention, outcome or timing criterion not met."),
  list(row = 5, col = "main",
       title = sprintf("Records included, grouped into studies (n = %s)",
                       n_(g$ledger_groups_final)),
       body = sprintf(paste("%s included records grouped by DOI, title and registry identifier, so",
                            "one study with a conference abstract, a register entry and a full text",
                            "is one group."), n_(f$included_records))),
  list(row = 6, col = "main",
       title = sprintf("Studies contributing to the synthesis (n = %s groups)", n_(contributing)),
       body = sprintf(paste("%s contrasts over %s trials or trial analyses; groups can share a trial.",
                            "%s convertible to the percent change scale, %s not, for want of a",
                            "printed baseline denominator. Risk of bias assessed for %s records."),
                      n_(inc$rows), n_(inc$trials_or_trial_analyses),
                      n_(inc$rows_convertible_to_percent_scale), n_(inc$rows_not_convertible),
                      n_(inc$risk_of_bias_records))),
  list(row = 6, col = "side",
       title = sprintf("Studies closed without contributing (n = %s)", n_(closed)),
       body = c(sprintf("No recoverable variance, closed by the deterministic scan: %s.",
                        n_(g$no_usable_contrast_scan)),
                sprintf("No recoverable variance on reading: %s.", n_(g$no_usable_contrast)),
                sprintf(paste("Eligibility failure visible only at extraction, including three data",
                              "integrity refusals: %s."), n_(g$excluded_at_extraction)),
                sprintf("Molecule outside the admitted classes: %s.  Registered without posted results: %s.",
                        n_(g$molecule_not_admitted), n_(g$ongoing_no_results)),
                sprintf("Held for a Director decision on population or co formulation: %s.",
                        n_(g$held_pending_decision))))
)
phases <- list(list(label = "Identification", rows = 1), list(label = "Screening", rows = 2:3),
               list(label = "Eligibility", rows = 4:5), list(label = "Included", rows = 6))

# Geometry, in millimetres from the left and from the top of the page.
PAGE_W   <- FIG_WIDTHS_MM[["double"]]
PHASE_X  <- c(0.6, 5.4)                 # phase bars
MAIN_X   <- c(7.6, 108)                 # boxes of our own stream
SIDE_X   <- c(116, 176.6)               # exclusions and the separate inflow
ROUTE_X  <- 180                         # the adopted inflow's route down the right margin
PAD_X    <- 2.0
PAD_Y    <- 1.7
ROW_GAP  <- 5.0
TOP      <- 0.8
TITLE_PT <- FIG_PT$tick
BODY_PT  <- FIG_PT$small
LEADING  <- 1.28                        # line height as a multiple of the type size
mm_per_pt <- 25.4 / 72

# Greedy wrapping on the typeface's advance widths, at the size the text is set in. Paragraphs
# break where they are given; words never break.
# systemfonts returns whole pixels, so widths are taken at a hundred pixels to the point.
text_mm <- function(x, family, pt) {
  systemfonts::string_width(x, family = family, size = pt, res = 7200) / 100 * mm_per_pt
}
wrap_mm <- function(paragraphs, width, family, pt) {
  unlist(lapply(paragraphs, function(p) {
    words <- strsplit(p, " ", fixed = TRUE)[[1]]
    words <- words[nzchar(words)]
    lines <- character(0)
    cur <- ""
    for (w in words) {
      trial <- if (nzchar(cur)) paste(cur, w) else w
      if (nzchar(cur) && text_mm(trial, family, pt) > width) {
        lines <- c(lines, cur)
        cur <- w
      } else cur <- trial
    }
    c(lines, cur)
  }))
}
line_mm <- function(pt) pt * LEADING * mm_per_pt

for (i in seq_along(boxes)) {
  bx <- boxes[[i]]
  x <- if (bx$col == "main") MAIN_X else SIDE_X
  inner <- diff(x) - 2 * PAD_X
  bx$x <- x
  bx$title_lines <- wrap_mm(bx$title, inner, "Inter Medium", TITLE_PT)
  bx$body_lines  <- wrap_mm(bx$body, inner, "Inter", BODY_PT)
  bx$h <- 2 * PAD_Y + length(bx$title_lines) * line_mm(TITLE_PT) + 0.5 +
    length(bx$body_lines) * line_mm(BODY_PT)
  if (is.null(bx$dashed)) bx$dashed <- FALSE
  boxes[[i]] <- bx
}

rows <- sort(unique(vapply(boxes, `[[`, numeric(1), "row")))
row_top <- numeric(length(rows))
row_h <- numeric(length(rows))
y <- TOP
for (r in rows) {
  row_top[r] <- y
  row_h[r] <- max(vapply(Filter(function(bx) bx$row == r, boxes), `[[`, numeric(1), "h"))
  y <- y + row_h[r] + ROW_GAP
}
route_y <- row_top[max(rows)] + row_h[max(rows)] + 3.2     # below the last row
PAGE_H <- ceiling(route_y + 4.0)
for (i in seq_along(boxes)) boxes[[i]]$top <- row_top[boxes[[i]]$row]

# From millimetres below the top of the page to the canvas's y, which runs upward.
yy <- function(from_top) PAGE_H - from_top

rects <- do.call(rbind, lapply(boxes, function(bx) data.frame(
  xmin = bx$x[1], xmax = bx$x[2], ymin = yy(bx$top + bx$h), ymax = yy(bx$top), dashed = bx$dashed)))
title_text <- do.call(rbind, lapply(boxes, function(bx) data.frame(
  x = bx$x[1] + PAD_X,
  y = yy(bx$top + PAD_Y + (seq_along(bx$title_lines) - 0.5) * line_mm(TITLE_PT)),
  label = bx$title_lines)))
body_text <- do.call(rbind, lapply(boxes, function(bx) data.frame(
  x = bx$x[1] + PAD_X,
  y = yy(bx$top + PAD_Y + length(bx$title_lines) * line_mm(TITLE_PT) + 0.5 +
           (seq_along(bx$body_lines) - 0.5) * line_mm(BODY_PT)),
  label = bx$body_lines)))

main <- Filter(function(bx) bx$col == "main", boxes)
side <- Filter(function(bx) bx$col == "side" && !bx$dashed, boxes)
main_cx <- mean(MAIN_X)
main_at <- function(r) Filter(function(bx) bx$row == r, main)[[1]]
# Down the main column, box to box; across to each exclusion box at the height where the two
# boxes overlap, so the arrow is horizontal and meets both.
down <- do.call(rbind, lapply(rows[-length(rows)], function(r) data.frame(
  x = main_cx, xend = main_cx,
  y = yy(main_at(r)$top + main_at(r)$h), yend = yy(main_at(r + 1)$top))))
across <- do.call(rbind, lapply(side, function(sx) {
  m <- main_at(sx$row)
  mid <- (max(m$top, sx$top) + min(m$top + m$h, sx$top + sx$h)) / 2
  data.frame(x = MAIN_X[2], xend = SIDE_X[1], y = yy(mid), yend = yy(mid))
}))
# The adopted inflow: out of the dashed box's right edge, down the margin, under the last row and
# up into the box of the studies contributing to the synthesis.
inflow <- Filter(function(bx) bx$dashed, boxes)[[1]]
target <- main_at(max(rows))
route <- data.frame(
  x = c(SIDE_X[2], ROUTE_X, ROUTE_X, main_cx, main_cx),
  y = yy(c(inflow$top + inflow$h / 2, inflow$top + inflow$h / 2, route_y, route_y,
           target$top + target$h)))
phase_rects <- do.call(rbind, lapply(phases, function(p) data.frame(
  xmin = PHASE_X[1], xmax = PHASE_X[2],
  ymin = yy(row_top[max(p$rows)] + row_h[max(p$rows)]), ymax = yy(row_top[min(p$rows)]),
  label = p$label)))

arrow_head <- grid::arrow(length = grid::unit(1.25, "mm"), angle = 24, type = "closed")
flow <- ggplot2::ggplot() +
  ggplot2::geom_rect(data = phase_rects,
                     ggplot2::aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax),
                     fill = FIG_TINT_BLUE, colour = NA) +
  ggplot2::geom_text(data = phase_rects,
                     ggplot2::aes(x = (xmin + xmax) / 2, y = (ymin + ymax) / 2, label = label),
                     angle = 90, family = "Inter Medium", size = fig_size(FIG_PT$tick),
                     colour = FIG_INK) +
  ggplot2::geom_segment(data = down, ggplot2::aes(x = x, y = y, xend = xend, yend = yend),
                        colour = FIG_AXIS, linewidth = fig_lw(0.6), arrow = arrow_head,
                        arrow.fill = FIG_AXIS) +
  ggplot2::geom_segment(data = across, ggplot2::aes(x = x, y = y, xend = xend, yend = yend),
                        colour = FIG_AXIS, linewidth = fig_lw(0.6), arrow = arrow_head,
                        arrow.fill = FIG_AXIS) +
  ggplot2::geom_path(data = route, ggplot2::aes(x = x, y = y), colour = FIG_AXIS,
                     linewidth = fig_lw(0.6), linetype = "22", arrow = arrow_head,
                     arrow.fill = FIG_AXIS, linejoin = "mitre") +
  ggplot2::annotate("text", x = main_cx + 2, y = yy(route_y) + 1.3,
                    label = "adopted comparator trials, re-screened at extraction",
                    hjust = 0, family = "Inter", fontface = "italic",
                    size = fig_size(BODY_PT), colour = FIG_INK_SOFT) +
  ggplot2::geom_rect(data = rects,
                     ggplot2::aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax,
                                  linetype = dashed),
                     fill = "white", colour = FIG_RULE, linewidth = fig_lw(0.6)) +
  ggplot2::scale_linetype_manual(values = c(`FALSE` = "solid", `TRUE` = "22"), guide = "none") +
  ggplot2::geom_text(data = title_text, ggplot2::aes(x = x, y = y, label = label), hjust = 0,
                     family = "Inter Medium", size = fig_size(TITLE_PT), colour = FIG_INK) +
  ggplot2::geom_text(data = body_text, ggplot2::aes(x = x, y = y, label = label), hjust = 0,
                     family = "Inter", size = fig_size(BODY_PT), colour = FIG_INK_SOFT) +
  ggplot2::scale_x_continuous(limits = c(0, PAGE_W), expand = c(0, 0)) +
  ggplot2::scale_y_continuous(limits = c(0, PAGE_H), expand = c(0, 0)) +
  ggplot2::coord_cartesian(clip = "off") +
  ggplot2::theme_void() +
  ggplot2::theme(plot.margin = ggplot2::margin(0, 0, 0, 0),
                 plot.background = ggplot2::element_rect(fill = "white", colour = NA))

# The count in every box, in drawing order. The titles above are formatted from these same
# variables, so the twin is what the boxes print; src/prisma_counts.py computes the same rows.
twin <- tibble::tribble(
  ~stage,           ~box,                                        ~n,
  "identification", "Records identified from our own searching", b$records_screened_all_pools,
  "identification", "Separate inflow, Alrasheed 2026 RCTs",      sb$alrasheed_2026_rcts,
  "identification", "Separate inflow, Ren 2025 RCTs",            sb$ren_2025_rcts,
  "screening",      "Records screened, title and abstract",      b$records_screened_all_pools,
  "screening",      "Records excluded at title and abstract",    ex_screen,
  "screening",      "Records sought for full text",              b$records_to_full_text,
  "screening",      "Not assessed",                              not_assessed,
  "eligibility",    "Records assessed at full text",             f$needing_a_screen,
  "eligibility",    "Records excluded at full text",             ex_fulltext,
  "eligibility",    "Records included, grouped into studies",    g$ledger_groups_final,
  "included",       "Studies contributing to the synthesis",     contributing,
  "included",       "Studies closed without contributing",       closed
) |>
  dplyr::mutate(n = as.integer(n))

save_figure("figure0_prisma_flow", flow, width_mm = PAGE_W, height_mm = PAGE_H,
            caption = "PRISMA 2020 flow of records through the review.", data = twin)

message(sprintf("screening balances: %d excluded + %d sought = %d screened", ex_screen,
                b$records_to_full_text, b$records_screened_all_pools))
message(sprintf("full text: %d assessed - %d excluded = %d included records", f$needing_a_screen,
                ex_fulltext, f$included_records))
message(sprintf("ledger balances: %d closed + %d contributing = %d groups", closed, contributing,
                g$ledger_groups_final))
message(sprintf("diagram %d mm by %d mm, %d box counts", PAGE_W, PAGE_H, nrow(twin)))
