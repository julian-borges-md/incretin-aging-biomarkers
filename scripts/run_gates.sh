#!/bin/zsh
# Twenty four gate chain in order; log work/gates_<sha>.log (same format as gates_424477c.log).
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
# The last three check artefacts that `make analysis` produces rather than this chain: the analysis
# pipeline is a separate command because it costs ten minutes of permutation and bootstrap work.
# They are in the chain because the committed output is part of the repository, and an output that
# disagrees with the data beside it is a defect whether or not the run that made it is in scope.
#
# Four run with their self tests, for the same reason gate fourteen does: a gate that reports
# nothing has not thereby shown that it works. The three self tests inject the defects these gates
# were written for, including the one that prompted each.
for g in prisma_check table1_inventory table2_reproduction_check; do
  echo "== $g $(date +%H:%M:%S)" >> "$log"
  python3 -I "src/$g.py" > "work/gate_$g.log" 2>&1; rc=$?
  echo "exit $rc" >> "$log"
  [ $rc -ne 0 ] && { echo "GATE FAILED: $g (see work/gate_$g.log)" >> "$log"; exit $rc; }
done
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
# own measurement: it classifies 3 of the 122 and reports 119 unclassifiable, and a gate that
# prints 119 unknowns on every run is a green light that means almost nothing. The header order
# gate is the extension docs/ARM_ATTRIBUTION_TRIAGE.md specified for the 80 rows whose arm names
# sit in a table header rather than in front of the values. It classifies 15 of those 80 soundly,
# which is far short of the 72 the document projected, because the projection counted headers that
# name both arms and not the four conditions under which an order rule actually attributes: a
# matched value must be a column value and not a dispersion, the two values must be adjacent
# columns, the header must be a row of column labels and not prose, and every candidate line must
# agree. The first version of that gate, without those conditions, reported five swapped arms and
# all five were artefacts of the rule. The document records the measurement and the correction.
#
# Together the pair classifies 18 of the 122, which is why both now hold a slot: the adjacent gate
# alone did not justify one, and the extension changed the arithmetic. Both run with their self
# tests, which inject a swap into every row each gate attributes, because neither reports a finding
# on this corpus and a gate that reports nothing has not thereby shown that it works. The header
# gate's self test also carries the four artefacts above as fixtures.
for g in arm_attribution_check arm_header_attribution_check; do
  echo "== $g $(date +%H:%M:%S)" >> "$log"
  python3 -I "src/$g.py" --self-test > "work/gate_$g.log" 2>&1; rc=$?
  echo "exit $rc" >> "$log"
  [ $rc -ne 0 ] && { echo "GATE FAILED: $g (see work/gate_$g.log)" >> "$log"; exit $rc; }
done
echo "ALL DONE $(date +%H:%M:%S)" >> "$log"
