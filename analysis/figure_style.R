###############################################################################
# figure_style.R
#
# Figure style 2 of the laboratory, in R: the laboratory's standard for the figures it publishes,
# adopted for this review on 24 October 2026 at the Director's decision for more resolution and a
# more modern style. Sourced by the analysis pipeline (section 10) and by src/prisma_figure.R, so
# every figure of the submission is drawn one way.
#
# WHAT A FIGURE IS. Every figure is drawn at its final journal width, 89 mm for a single column,
# 120 mm for one and a half columns or 183 mm for a double column, and at most 170 mm high, with
# text between 5.8 and 7 pt and panel letters at 8 pt, so nothing is rescaled in production. It is
# written three ways, all three version controlled and hashed in the result manifest:
#
#   <name>.pdf   vector, the submission format; glyphs drawn as outlines, so the typeface needs no
#                font file wherever the PDF is opened
#   <name>.png   600 dpi, for documents and inspection
#   <name>.csv   the data twin: the values the figure plots, which src/figure_check.py recomputes
#                from the tables and data each figure is drawn from
#
# THE TYPEFACE. Inter 4.1 (SIL Open Font License 1.1, analysis/fonts/OFL-Inter.txt), vendored in
# analysis/fonts and verified by SHA-256 before anything is drawn: a font file that differs from its
# registered digest stops the run, because a figure drawn in a substitute face is a different
# figure. It is registered twice, for the two devices: with sysfonts, so that showtext draws its
# glyphs as outlines in the PDF, and with systemfonts, so that ragg renders it in the PNG. Neither
# device consults the fonts installed on the machine for this family.
#
# WHY THESE DEVICES. grDevices::pdf has no external dependency, which is why it replaced cairo_pdf
# on 19 October (section 10 of the pipeline records why), but it cannot embed a TrueType face; with
# showtext the glyphs are drawn as paths, so the PDF carries the typeface without embedding it. Its
# timestamp is switched off where the device supports it (R 4.4 and later), so the PDF of an
# unchanged figure is byte identical across runs, as the PNG from ragg already is.
#
# COLOUR. The categorical slots blue, orange and aqua and the sequential blue ramp of the validated
# reference palette, the same tokens as the laboratory's Python figures, re-validated on white with
# all pairs compared; aqua sits below 3:1 contrast, so it never carries text. The diverging pair runs
# from a dark orange through a neutral grey to a dark blue, two hues and no hue at the midpoint.
# Status colours (low, some concerns and high risk of bias) are reserved for status and always carry
# a glyph and a label. Text uses the ink tokens, never a series colour.
#
# LAYOUT. White surface, left and bottom axes only, light solid gridlines on the value axis only,
# legends outside the plotting area, no title inside a figure: the caption is written to
# figure_index.csv by the run and carried by the manuscript legend.
###############################################################################

suppressPackageStartupMessages({
  library(ggplot2)
})

FIGURE_FONT_DIR <- file.path("analysis", "fonts")
FIGURE_FONTS <- c(   # Inter 4.1, extras/ttf of the release archive Inter-4.1.zip
  "Inter-Regular.ttf"  = "40d692fce188e4471e2b3cba937be967878f631ad3ebbbdcd587687c7ebe0c82",
  "Inter-Italic.ttf"   = "bbc051dd204b5019a1aa0bc0ae2aa8a05ab13e7a3f979fa357631dc7feb6833a",
  "Inter-Medium.ttf"   = "97ad806f526e41546d46365bb3a393145f75b7b1568913db74549ad8b8dba872",
  "Inter-SemiBold.ttf" = "78a843fade9d4612a5567302fb595b56976eb5fcebf4fea5a5912d638bafcde3"
)

FIG_WIDTHS_MM     <- c(single = 89, one_and_a_half = 120, double = 183)
FIG_MAX_HEIGHT_MM <- 170   # a figure with its legend on a page
FIG_PAGE_DEPTH_MM <- 247   # the full page depth, for a supplementary figure that is a page of its own
FIG_DPI           <- 600

# Colour tokens.
FIG_BLUE        <- "#2a78d6"   # categorical slot 1, the single series hue
FIG_ORANGE      <- "#eb6834"   # categorical slot 2
FIG_AQUA        <- "#1baf7a"   # categorical slot 3, never carries text
FIG_SEQ         <- c("#86b6ef", "#5598e7", "#2a78d6", "#184f95")
FIG_INK         <- "#0b0b0b"   # primary text
FIG_INK_SOFT    <- "#52514e"   # secondary text
FIG_AXIS        <- "#8a8984"   # axis rules and ticks
FIG_GRID        <- "#e6e5e1"   # gridlines
FIG_BAND        <- "#e1edfb"   # shaded ranges, a solid tint of the series hue
FIG_TINT_BLUE   <- "#eef4fc"
FIG_TINT_ORANGE <- "#fdeee8"
FIG_RULE        <- "#c9c8c3"   # box outlines in diagrams
FIG_ROW         <- "#f4f3f0"   # alternate row band in tables and forest plots
FIG_DIV_LOW     <- "#c4501f"   # diverging pole for negative values, a dark step of the orange slot
FIG_DIV_MID     <- "#f4f3f0"   # neutral midpoint, a grey with no hue
FIG_DIV_HIGH    <- "#184f95"   # diverging pole for positive values, the dark step of the blue ramp
FIG_NA_FILL     <- "#d3d2cd"   # no estimate: clearly darker than the midpoint, and marked with a glyph
FIG_STATUS      <- c(low = "#0ca30c", some_concerns = "#fab219", high = "#d03b3b")
FIG_STATUS_TEXT <- c(low = FIG_INK, some_concerns = FIG_INK, high = "#ffffff")

# Text sizes in points and line widths in points, with their conversions to ggplot's units: a text
# size is given in millimetres of the font's em, and a line width in units of 0.75 points scaled by
# .pt, so a width written in points has to be converted rather than passed through.
FIG_PT <- list(text = 7, tick = 6.5, note = 6.3, small = 5.8, letter = 8)
FIG_LW <- list(data = 1.25, ref = 0.75, axis = 0.5, grid = 0.4)
fig_size   <- function(pt) pt / ggplot2::.pt
fig_lw     <- function(pt) pt * 96 / 72 / ggplot2::.pt
# A point's outline is drawn at stroke * .stroke / 2 in the same units as a line width.
fig_stroke <- function(pt) pt * 96 / 72 * 2 / ggplot2::.stroke

# Text printed on a filled mark takes whichever ink contrasts more with the fill, by the WCAG
# contrast ratio of their relative luminances, so the number in a dark cell is white and the number
# in a pale one is ink. An absent fill returns an absent ink.
fig_luminance <- function(hex) {
  rgb <- grDevices::col2rgb(hex) / 255
  lin <- ifelse(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055)^2.4)
  as.vector(c(0.2126, 0.7152, 0.0722) %*% lin)
}
fig_text_on <- function(fill) {
  out <- rep(NA_character_, length(fill))
  ok <- !is.na(fill)
  y <- fig_luminance(fill[ok])
  on_ink   <- (y + 0.05) / (fig_luminance(FIG_INK) + 0.05)
  on_white <- 1.05 / (y + 0.05)
  out[ok] <- ifelse(on_white > on_ink, "#ffffff", FIG_INK)
  out
}

# Numbers printed in a figure carry a true minus sign, as typeset text does, rather than a hyphen.
fig_num <- function(x, digits = 1) {
  ifelse(is.na(x), NA_character_, sub("^-", "\u2212", formatC(x, format = "f", digits = digits)))
}
fig_axis_number <- scales::label_number(style_negative = "minus")

register_figure_fonts <- function(dir = FIGURE_FONT_DIR) {
  for (f in names(FIGURE_FONTS)) {
    path <- file.path(dir, f)
    if (!file.exists(path)) {
      stop("figure font ", path, " is missing; the figures would be drawn in a substitute face",
           call. = FALSE)
    }
    # as.vector drops the hash class that as.character keeps, which identical() would compare.
    digest <- as.vector(as.character(openssl::sha256(file(path))))
    if (!identical(digest, unname(FIGURE_FONTS[f]))) {
      stop("figure font ", path, " differs from its registered SHA-256; the figures would not ",
           "reproduce", call. = FALSE)
    }
  }
  face <- function(f) file.path(dir, f)
  sysfonts::font_add("Inter", regular = face("Inter-Regular.ttf"), italic = face("Inter-Italic.ttf"),
                     bold = face("Inter-SemiBold.ttf"), bolditalic = face("Inter-SemiBold.ttf"))
  sysfonts::font_add("Inter Medium", regular = face("Inter-Medium.ttf"))
  systemfonts::register_font("Inter", plain = face("Inter-Regular.ttf"),
                             italic = face("Inter-Italic.ttf"), bold = face("Inter-SemiBold.ttf"),
                             bolditalic = face("Inter-SemiBold.ttf"))
  systemfonts::register_font("Inter Medium", plain = face("Inter-Medium.ttf"))
  invisible(TRUE)
}

theme_figure <- function(base = FIG_PT$text) {
  ggplot2::theme_minimal(base_size = base, base_family = "Inter") +
    ggplot2::theme(
      text               = ggplot2::element_text(colour = FIG_INK),
      axis.title         = ggplot2::element_text(size = FIG_PT$text, colour = FIG_INK),
      axis.text          = ggplot2::element_text(size = FIG_PT$tick, colour = FIG_INK_SOFT),
      axis.line          = ggplot2::element_line(colour = FIG_AXIS, linewidth = fig_lw(FIG_LW$axis)),
      axis.ticks         = ggplot2::element_line(colour = FIG_AXIS, linewidth = fig_lw(FIG_LW$axis)),
      axis.ticks.length  = grid::unit(0.9, "mm"),
      panel.grid.major   = ggplot2::element_line(colour = FIG_GRID, linewidth = fig_lw(FIG_LW$grid)),
      panel.grid.minor   = ggplot2::element_blank(),
      panel.background   = ggplot2::element_rect(fill = "white", colour = NA),
      plot.background    = ggplot2::element_rect(fill = "white", colour = NA),
      strip.text         = ggplot2::element_text(family = "Inter Medium", size = FIG_PT$text,
                                                 colour = FIG_INK, hjust = 0,
                                                 margin = ggplot2::margin(0, 0, 1.5, 0, "mm")),
      legend.position    = "bottom",
      legend.title       = ggplot2::element_text(size = FIG_PT$tick, colour = FIG_INK),
      legend.text        = ggplot2::element_text(size = FIG_PT$tick, colour = FIG_INK),
      legend.key.size    = grid::unit(3, "mm"),
      legend.margin      = ggplot2::margin(0, 0, 0, 0),
      legend.box.spacing = grid::unit(2, "mm"),
      plot.tag           = ggplot2::element_text(size = FIG_PT$letter, face = "bold", colour = FIG_INK),
      plot.title         = ggplot2::element_text(family = "Inter Medium", size = FIG_PT$text,
                                                 colour = FIG_INK, hjust = 0),
      plot.margin        = ggplot2::margin(1.5, 2, 1.5, 1.5, "mm")
    )
}

# Each figure is recorded as it is written, and the index is an output of the run rather than a
# document kept in step by hand. docs/FIGURES.md maps these files to the submission numbering.
FIGURE_INDEX <- list()

# The plotted values of every figure are written beside it as <name>.csv, its data twin, added
# 23 October. A PDF or a PNG records what the device drew and not what the figure claims: nothing
# in a forest plot file says which estimate a square stands for, so a figure drawn from a stale
# object, a differently filtered frame or a different model passes every check of existence while
# disagreeing with the table it illustrates. Figure 4 did exactly that until 19 October, drawing one
# least squares line per receptor class beside a table that reports a random effects
# meta-regression, and nothing in the repository could have noticed. The twin makes the drawn
# values a record, and src/figure_check.py recomputes every twin from the result tables and the data
# the figure is drawn from and stops the gate chain on a disagreement.
#
# Doubles are rounded to ten significant digits, a resolution far finer than anything a reader can
# measure from a figure and far coarser than the last bits of a platform's floating point, so the
# twin of an unchanged figure is the same file on every run. A figure with more than one layer
# passes a named list and the layers are stacked under a layer column. The twin is written before
# the images, so a figure whose plotted values cannot be recorded stops the run before any file of
# it exists.
write_twin <- function(name, data, out_dir = OUT_DIR) {
  layered <- !is.data.frame(data)
  if (layered && (is.null(names(data)) || any(names(data) == ""))) {
    stop("figure ", name, ": a figure with several layers names each of them", call. = FALSE)
  }
  if (!layered) data <- list(data)
  parts <- lapply(seq_along(data), function(i) {
    d <- dplyr::mutate(dplyr::ungroup(data[[i]]),
                       dplyr::across(dplyr::where(is.factor), as.character),
                       dplyr::across(dplyr::where(is.double), ~ signif(.x, 10)))
    if (layered) d <- dplyr::mutate(d, layer = names(data)[i], .before = 1)
    d
  })
  twin <- dplyr::bind_rows(parts)
  if (nrow(twin) == 0) {
    stop("figure ", name, " has no plotted values, and a figure of nothing is not written",
         call. = FALSE)
  }
  path <- file.path(out_dir, paste0(name, ".csv"))
  readr::write_csv(twin, path, na = "")
  path
}

# The PDF device writes its creation and modification times into every file, so a rerun that drew
# the same figure produced a different file, and the manifest recorded a change that was only the
# clock. Without the timestamp the PDF of an unchanged figure is byte identical across runs. The
# argument exists from R 4.4; on an older R the device is called as before rather than failing.
PDF_ARGS <- c(list(useDingbats = FALSE),
              if ("timestamp" %in% names(formals(grDevices::pdf))) list(timestamp = FALSE))

save_figure <- function(name, plot, width_mm, height_mm, caption, data, out_dir = OUT_DIR,
                        max_height_mm = FIG_MAX_HEIGHT_MM) {
  if (!any(abs(width_mm - FIG_WIDTHS_MM) < 1e-9)) {
    stop("figure ", name, " is ", width_mm, " mm wide; a figure is drawn at a journal width, ",
         paste(FIG_WIDTHS_MM, collapse = ", "), " mm", call. = FALSE)
  }
  if (height_mm > max_height_mm || max_height_mm > FIG_PAGE_DEPTH_MM) {
    stop("figure ", name, " is ", height_mm, " mm high, above the ", max_height_mm, " mm it may ",
         "take", call. = FALSE)
  }
  twin <- write_twin(name, data, out_dir)
  written <- character(0)
  attempts <- list(
    list(ext = "pdf", dev = grDevices::pdf, args = PDF_ARGS,           outlines = TRUE),
    list(ext = "png", dev = ragg::agg_png,  args = list(dpi = FIG_DPI), outlines = FALSE)
  )
  for (a in attempts) {
    path <- file.path(out_dir, paste0(name, ".", a$ext))
    if (file.exists(path)) unlink(path)
    # showtext draws the glyphs as outlines on the PDF device only; ragg renders the registered face
    # itself, so showtext is switched off for the PNG.
    showtext::showtext_auto(a$outlines)
    ok <- tryCatch({
      do.call(ggplot2::ggsave,
              c(list(filename = path, plot = plot, device = a$dev,
                     width = width_mm, height = height_mm, units = "mm", bg = "white"),
                a$args))
      TRUE
    }, error = function(e) {
      message("  figure ", name, " device ", a$ext, " failed: ", conditionMessage(e))
      FALSE
    }, finally = showtext::showtext_auto(FALSE))
    if (ok && file.exists(path) && file.size(path) > 1024) {
      written <- c(written, path)
    } else {
      message("  FIGURE NOT WRITTEN: ", path)
      if (file.exists(path)) unlink(path)
    }
  }
  if (length(written) == 0) {
    stop("figure ", name, " produced no file on any device; the run is stopped rather than ",
         "reporting a figure that does not exist", call. = FALSE)
  }
  FIGURE_INDEX[[name]] <<- tibble::tibble(
    name = name, caption = caption,
    files = paste(basename(written), collapse = "; "),
    twin = basename(twin),
    width_mm = width_mm, height_mm = height_mm,
    bytes = paste(file.size(written), collapse = "; ")
  )
  message("  figure ", name, ": ", paste(basename(written), collapse = ", "))
  invisible(written)
}

register_figure_fonts()

# Text drawn by a geom, rather than by the theme, takes the same face and ink by default, so that no
# label falls back to the device's default family.
ggplot2::update_geom_defaults("text", list(family = "Inter", colour = FIG_INK,
                                           size = fig_size(FIG_PT$tick)))
ggplot2::update_geom_defaults("label", list(family = "Inter", colour = FIG_INK,
                                            size = fig_size(FIG_PT$tick)))
