#!/bin/zsh
# Twenty five gate chain in order; log work/gates_<sha>.log (same format as gates_424477c.log).
#
# This file is the tracked copy and the one to edit. The chain lived at work/run_gates.sh until
# 16 October, where the gitignore keeps it out of version control: the script that validates the
# pipeline was not reproducible from a clone, which is the same class of defect as an unrecorded
# amendment. work/run_gates.sh is now a one line wrapper that calls this file.
# Gates one to eight are the pipeline. Gate nine checks that the figures written in the Results
# narrative are the figures the pipeline just produced: the narrative is edited by hand after every
# extraction pass, so a paragraph can be left at the previous commit's numbers while the table moves
# under it. It runs last because it reads analysis/output, which gate six and gate seven write.
cd "$HOME/dev/fxmedus-ai/incretin-aging-biomarkers" || exit 1
sha=$(git rev-parse --short HEAD)
log="work/gates_${sha}.log"
: > "$log"
for g in verify selftest validate_pipeline build_master harmonise_units pool_biomarkers compute_composite receptor_class_contrast; do
  echo "== $g $(date +%H:%M:%S)" >> "$log"
  Rscript "src/$g.R" > "work/gate_$g.log" 2>&1; rc=$?
  echo "exit $rc" >> "$log"
  [ $rc -ne 0 ] && { echo "GATE FAILED: $g (see work/gate_$g.log)" >> "$log"; exit $rc; }
done
# Extended 2026-10-22 from manuscript/RESULTS_*.md to every manuscript file, and from prose to
# table rows. A pooled quantity written into a table cell was invisible to this gate, because it
# read prose only: the Discussion's summary table of the unfavourable axis cited five markers with
# their estimates and intervals and no gate read any of them. A table is where a number is most
# likely to be copied by hand and least likely to be reread. The self test runs first, because the
# table pass misfired twice while being written, once on the receptor class tables and once on the
# correlation sensitivity table, and both counterexamples are now in it.
echo "== results_numbers_check --self-test $(date +%H:%M:%S)" >> "$log"
python3 -I src/results_numbers_check.py --self-test > "work/gate_results_numbers_check.log" 2>&1; rc=$?
echo "exit $rc" >> "$log"
[ $rc -ne 0 ] && { echo "GATE FAILED: results_numbers_check self test (see work/gate_results_numbers_check.log)" >> "$log"; exit $rc; }
for m in manuscript/*.md; do
  [ -e "$m" ] || continue
  echo "== results_numbers_check $m $(date +%H:%M:%S)" >> "$log"
  python3 -I src/results_numbers_check.py "$m" >> "work/gate_results_numbers_check.log" 2>&1; rc=$?
  echo "exit $rc" >> "$log"
  [ $rc -ne 0 ] && { echo "GATE FAILED: results_numbers_check $m (see work/gate_results_numbers_check.log)" >> "$log"; exit $rc; }
done
# Gates ten to fourteen are provenance gates over the corpus rather than the pipeline. Ten asks
# whether any packet bundles two unrelated studies, which silently drops the study that was not
# read; eleven asks whether every extracted number is attached to the row's own biomarker in its
# source; twelve asks whether a row's printed p value reconciles with the p implied by its own
# effect and standard error, which is the part of the amendment A5 verifier pass that scales;
# thirteen asks whether two trials share a run of printed values, which is how a duplicate
# publication enters a corpus twice; fourteen asks whether a row's arm values and its reported
# effect agree in sign and magnitude, which is the one mechanical error the others cannot see,
# because a swapped arm leaves every number present, attached and self consistent. Each one fails
# only on a case not yet written up in its triage document, so a new defect blocks the chain while
# the known and judged ones do not.
# Three of these four now run with their self tests, added 2026-10-19. Gates ten, eleven and
# thirteen had reported no untriaged case since the known ones were written up, which is the state a
# gate is supposed to reach and also the state in which nobody can tell a working gate from a broken
# one. Each self test injects the defect its gate exists for, group 219's bundled studies and the
# repeated ALT means among them, and the legitimate shapes it must not flag. The twelfth, the p
# value reconciler, reports a finding on every run and needs no such proof.
for g in packet_grouping_check extraction_attachment_check duplicate_numbers_check; do
  echo "== $g $(date +%H:%M:%S)" >> "$log"
  python3 -I "src/$g.py" --self-test > "work/gate_$g.log" 2>&1; rc=$?
  echo "exit $rc" >> "$log"
  [ $rc -ne 0 ] && { echo "GATE FAILED: $g (see work/gate_$g.log)" >> "$log"; exit $rc; }
done
for g in pvalue_reconcile; do
  echo "== $g $(date +%H:%M:%S)" >> "$log"
  python3 -I "src/$g.py" > "work/gate_$g.log" 2>&1; rc=$?
  echo "exit $rc" >> "$log"
  [ $rc -ne 0 ] && { echo "GATE FAILED: $g (see work/gate_$g.log)" >> "$log"; exit $rc; }
done
# Gate fourteen runs with its self test, because a gate that reports no finding has not thereby
# shown that it works. The self test injects a swapped arm into every passing row and a tenfold
# digit shift into a sample of them, and fails the chain if the gate does not catch them.
echo "== arm_orientation_check $(date +%H:%M:%S)" >> "$log"
python3 -I src/arm_orientation_check.py --self-test > "work/gate_arm_orientation_check.log" 2>&1; rc=$?
echo "exit $rc" >> "$log"
[ $rc -ne 0 ] && { echo "GATE FAILED: arm_orientation_check (see work/gate_arm_orientation_check.log)" >> "$log"; exit $rc; }
# Gate fifteen asks what the gates above are entitled to claim. It classifies every retained source
# by whether it is the publisher's text or a capture this review wrote while reading a page, and
# splits the rows accordingly, because a match against the second establishes only that the
# extraction reproduces the capture. It fails on a source it cannot classify and on a new capture
# written without a provenance preamble, which is how the capture convention is enforced rather
# than merely recommended.
echo "== source_provenance $(date +%H:%M:%S)" >> "$log"
python3 -I src/source_provenance.py > "work/gate_source_provenance.log" 2>&1; rc=$?
echo "exit $rc" >> "$log"
[ $rc -ne 0 ] && { echo "GATE FAILED: source_provenance (see work/gate_source_provenance.log)" >> "$log"; exit $rc; }
# Added 2026-10-19. Six gates that existed and were reachable only by being remembered. A check
# written, committed and never put in the chain runs on the day it is written and on no other day,
# which is how the pipeline came to report success for five days while producing no figures. These
# six ask, in order: whether the PRISMA stages reconcile; whether every pooled biomarker has an
# inventory entry and every inventory entry is accounted for; whether the pipeline's Table 2
# reproduces the gate scripts' own pooling to the last decimal; whether every composite interval
# contains its own estimate; whether the committed reference record still describes the committed
# corpus; and whether every figure the manuscript will submit exists, is hashed in the manifest and
# is mapped to a submission number; and whether every digest in the result manifest still matches
# the file beside it, which turns the manifest from a list into a check.
#
# The figure gate was extended 2026-10-23 from whether a figure exists to what it shows. Every
# figure now writes its plotted values beside it, and the gate recomputes them from the result
# tables and the data each figure is drawn from, by one rule per figure, and fails on a
# disagreement or on a figure with no rule. Its self test injects into the tracked figures the
# defects the rules exist for, the per class least squares lines Figure 4 drew until 19 October
# among them. From 2026-10-24 it also reads each figure's files, which figure style 2 fixes: a
# vector PDF with no date and no font, and a 600 dpi PNG at a journal width, the size the figure
# index states.
#
# The last three check artefacts that `make analysis` produces rather than this chain: the analysis
# pipeline is a separate command because it costs ten minutes of permutation and bootstrap work.
# They are in the chain because the committed output is part of the repository, and an output that
# disagrees with the data beside it is a defect whether or not the run that made it is in scope.
#
# Four run with their self tests, for the same reason gate fourteen does: a gate that reports
# nothing has not thereby shown that it works. The three self tests inject the defects these gates
# were written for, including the one that prompted each.
for g in prisma_check table2_reproduction_check; do
  echo "== $g $(date +%H:%M:%S)" >> "$log"
  python3 -I "src/$g.py" > "work/gate_$g.log" 2>&1; rc=$?
  echo "exit $rc" >> "$log"
  [ $rc -ne 0 ] && { echo "GATE FAILED: $g (see work/gate_$g.log)" >> "$log"; exit $rc; }
done
# Gate seventeen runs in --check mode, added 2026-10-22. It generates Table 1 from the biomarker
# inventory joined to the harmonised master, and this chain ran it in its writing mode, so the gate
# REGENERATED the artefact it was supposed to verify. A chain that writes to what it verifies cannot
# fail on it. Nothing had gone wrong, because the table is a deterministic function of two tracked
# inputs, but the gate established nothing, and it had one visible consequence: a display name
# change in the inventory left the result manifest describing a Table 1 that no longer existed, and
# the manifest gate failed on a file this one had correctly rewritten. Regeneration is now a
# deliberate step, `make table1` followed by `make manifest`, and the chain compares.
echo "== table1_inventory --check $(date +%H:%M:%S)" >> "$log"
python3 -I src/table1_inventory.py --check > "work/gate_table1_inventory.log" 2>&1; rc=$?
echo "exit $rc" >> "$log"
[ $rc -ne 0 ] && { echo "GATE FAILED: table1_inventory (see work/gate_table1_inventory.log)" >> "$log"; exit $rc; }
for g in composite_interval_check citation_record_check figure_check manifest_check; do
  echo "== $g $(date +%H:%M:%S)" >> "$log"
  python3 -I "src/$g.py" --self-test > "work/gate_$g.log" 2>&1; rc=$?
  echo "exit $rc" >> "$log"
  [ $rc -ne 0 ] && { echo "GATE FAILED: $g (see work/gate_$g.log)" >> "$log"; exit $rc; }
done
# Gates twenty three and twenty four, added 2026-10-22, are the arm attribution pair. They reach
# the 122 derived rows, where the effect was computed FROM the two arm values and so cannot be
# checked against a reported effect: a swapped arm flips the derived effect too, and the two agree
# by construction.
#
# The adjacent label gate was written on 19 October and deliberately left out of this chain, on its
# own measurement: it classified 3 of the 122 and reported 119 unclassifiable, and a gate that
# prints 119 unknowns on every run is a green light that means almost nothing. The header order
# gate is the extension docs/ARM_ATTRIBUTION_TRIAGE.md specified for the rows whose arm names sit
# in a table header rather than in front of the values. It classifies 15 of them soundly, which is
# far short of the 72 the document projected, because the projection counted headers that name both
# arms and not the four conditions under which an order rule actually attributes: a matched value
# must be a column value and not a dispersion, the two values must be adjacent columns, the header
# must be a row of column labels and not prose, and every candidate line must agree. The first
# version of that gate, without those conditions, reported five swapped arms and all five were
# artefacts of the rule. The document records the measurement and the correction.
#
# Building it also found that the adjacent gate located a value as a string, falling back to the
# unsigned string, which matches the row value -4 against the printed dispersion 4.5. Both gates now
# share one numeric locator, which took the adjacent gate from 3 attributed rows to 8 and moved 25
# rows out of the header gate's scope whose values never shared a line to begin with.
#
# Together the pair classifies 23 of the 122, which is why both hold a slot: the adjacent gate alone
# did not justify one, and the extension changed the arithmetic. Both run with their self tests,
# which inject a swap into every row each gate attributes, because neither reports a finding on this
# corpus and a gate that reports nothing has not thereby shown that it works. The header gate's self
# test also carries the four artefacts above as fixtures.
for g in arm_attribution_check arm_header_attribution_check; do
  echo "== $g $(date +%H:%M:%S)" >> "$log"
  python3 -I "src/$g.py" --self-test > "work/gate_$g.log" 2>&1; rc=$?
  echo "exit $rc" >> "$log"
  [ $rc -ne 0 ] && { echo "GATE FAILED: $g (see work/gate_$g.log)" >> "$log"; exit $rc; }
done
# Gate twenty five, added 2026-10-22, is the last candidate from version 1.1 of the chain document
# and the only one of the three it listed that was not struck. It asks, for a row the review marks
# as the trial's prespecified endpoint, whether the timepoint it was read at is the timepoint the
# trial REGISTERED as its primary endpoint. An unflagged row carries no expectation and gets no
# verdict, because a week 24 reading in a week 48 trial is a fact about the paper.
#
# Its reach was measured twice. Against the registry records already on disk it reached 5 rows of
# 524, and that number was a retrieval gap rather than a property of the data: those 38 records came
# from the screening pool and exactly one was for an included trial. src/corpus_registry_harvest.py
# retrieves the records of the corpus, and the reach is 291 rows, of which 234 reach a verdict.
#
# It reads work/fulltext/registry_corpus/, which is gitignored like every other retrieved source, so
# a clone must run that harvester once before this gate can say anything. Its self test fails rather
# than passes when the records are absent, because with nothing to compare it would otherwise report
# a green light for a check it did not perform; the failure names the command.
echo "== timepoint_check $(date +%H:%M:%S)" >> "$log"
python3 -I src/timepoint_check.py --self-test > "work/gate_timepoint_check.log" 2>&1; rc=$?
echo "exit $rc" >> "$log"
[ $rc -ne 0 ] && { echo "GATE FAILED: timepoint_check (see work/gate_timepoint_check.log)" >> "$log"; exit $rc; }
echo "ALL DONE $(date +%H:%M:%S)" >> "$log"
