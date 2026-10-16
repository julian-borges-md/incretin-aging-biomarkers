#!/bin/zsh
# Thirteen gate chain in order; log work/gates_<sha>.log (same format as gates_424477c.log).
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
for m in manuscript/RESULTS_*.md; do
  [ -e "$m" ] || continue
  echo "== results_numbers_check $m $(date +%H:%M:%S)" >> "$log"
  python3 -I src/results_numbers_check.py "$m" > "work/gate_results_numbers_check.log" 2>&1; rc=$?
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
for g in packet_grouping_check extraction_attachment_check pvalue_reconcile duplicate_numbers_check; do
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
echo "ALL DONE $(date +%H:%M:%S)" >> "$log"
