# Registration gate

Added 2026-10-15, after a registration attempt was blocked by a rule we did not know applied to us.

## The rule

PROSPERO will not accept an initial registration once a review has progressed beyond data extraction. The form enforces this: setting the data extraction stage to anything other than "Not started" prevents the stage section from being marked complete, with the message *"PROSPERO registrations are not allowed when the review has progressed beyond the data extraction stage."*

The terms of use say the same thing earlier, in term 5: *"Reviews must be registered before data extraction has started, or before individual participant data have been received."*

## What it cost us

On this review, one trial was extracted before registration. It was a deliberate pilot: a single trial run through the 51 column extraction form to test whether the schema worked. It did not produce a pooled estimate or a finding. It did two useful things, which is why it was run. It exposed a schema defect, since the schema assumed arm level means and standard deviations whereas this literature reports treatment contrasts. And it refuted an argument that had survived several drafts.

Both were worth finding. Neither was worth a registration.

Whether a one trial form pilot counts as "data extraction" under term 5 is genuinely arguable, and the answer belongs to CRD rather than to us. But the arguing happens after the block, under time pressure, with a half completed record sitting in the account. That is the wrong order.

## The gate

**No trial data is extracted, transcribed or entered into an extraction file until the registration is submitted.**

| Activity | Permitted before registration |
|---|---|
| Scoping and anchor searches | Yes |
| Reading full texts | Yes |
| Building the extraction schema | Yes |
| Writing the analysis pipeline | Yes |
| Testing the pipeline on simulated data | Yes |
| Testing the pipeline on a real trial's numbers | **No** |
| Transcribing any trial's results into any file | **No** |

The line is between building the instrument and pointing it at the data.

## How to test a schema without breaking the gate

The pilot was run because an untested 51 column schema is a real risk: a defect found at trial forty is expensive. That risk is real and the gate does not dismiss it. It redirects it.

**Simulate instead.** Generate a synthetic extraction file matching the schema, with the value shapes this literature actually produces: contrasts with confidence intervals, arm level means with standard errors, p values reported as bounds, missing standard deviations. Run the pipeline on it. This finds schema defects, conversion errors and integrity gate failures without touching a trial. `src/validate_pipeline.R` does exactly this, and found a sign error that a single trial pilot would not have caught.

**Dry read, do not record.** Reading a paper and noticing that it reports contrasts rather than arm means is not extraction. Writing that observation into a schema specification is not extraction. Writing its numbers into a CSV is.

## Sequence

1. Scope, anchor search, read full texts
2. Build the extraction schema from what the literature actually reports
3. Write the analysis pipeline
4. Validate the pipeline against simulated data matching the schema
5. Publish the protocol and pipeline with a timestamp
6. **Register**
7. Extract

Step 6 before step 7. The public timestamped protocol at step 5 is worth having regardless, but it is not a substitute for registration and does not exempt step 7 from the gate.

## Where this sits

A G2 gate condition, enforced alongside the twelve section pre-flight. A pre-flight that is complete but unregistered does not authorise extraction.
