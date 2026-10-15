# PROSPERO field map

Every field the intervention review template asks for, in form order, with its constraint and the pre-flight section that should already answer it. Built by filling the form on 2026-10-15, not from documentation.

Where the "pre-flight source" column says **gap**, our twelve section pre-flight does not currently produce that answer and the author has to improvise at the form. Those are the entries worth fixing.

## Before you start

Registration is gated. See `registration_gate.md`. The form will block you if data extraction has started.

Two things are decided before the form opens and cannot be changed later:

| Choice | Consequence |
|---|---|
| Live record vs training record | Training records are never published and the status cannot be changed afterwards. A new record would be needed |
| Human vs animal participants | Selects the template |

## Section 1. Review title and basic details

| # | Field | Constraint | Pre-flight source |
|---|---|---|---|
| 1 | Review title | 5 to 30 words | Title |
| 2 | Review type | Set by the opening choices | Design |
| 3 | Condition or domain | PICO tags (autocomplete, ≥3 chars) plus free text, 0 to 200 words | Section 3 eligibility, population |
| 4 | Rationale | **250 words** | Section 2 background |
| 5 | Review objectives | 250 words | Section 1 questions |
| 6 | Keywords | ≥3, autocomplete | **gap** |
| 7 | Country | Autocomplete | **gap** |

## Section 2. Eligibility criteria

| # | Field | Constraint | Pre-flight source |
|---|---|---|---|
| 1 | Population | Inclusion 5 to 200 words, exclusion separate, 0 to 200 | Section 3 |
| 2 | Interventions | PICO tags or text, inclusion and exclusion separate | Section 3 |
| 3 | Comparators | Three way radio, then PICO tags plus text | Section 3 |
| 4 | Study design | Randomised and non-randomised checkboxes, include and exclude text | Section 3 |
| 5 | Context | 0 to 200 words | **gap** |

## Section 3. Similar reviews

| # | Field | Constraint | Pre-flight source |
|---|---|---|---|
| 1 | Check for similar records | **Mandatory.** PROSPERO surfaces three matches and all three must be assessed before submission | **gap** |

Each match: different or similar. Marking one *similar* triggers a proceed decision, a reason checklist (population, intervention, outcomes, more up to date, improved methods, COI concerns) and a free text box. PROSPERO does not block a similar registration; it records your reasons publicly.

Worth treating as a real duplication check rather than a formality. On this review it surfaced a registration covering most of our hepatic outcome set in one receptor class, which belongs in the manuscript Discussion regardless of registration.

## Section 4. Timeline

| # | Field | Constraint | Pre-flight source |
|---|---|---|---|
| 1 | Start date | Date picker, pre-filled with today. Must be after protocol completion and before extraction begins | **gap** |
| 1 | End date | Date picker | **gap** |

## Section 5. Availability of full protocol

| # | Field | Options | Pre-flight source |
|---|---|---|---|
| 1 | Protocol availability | Not written / published with DOI / upload PDF / written but unavailable | **gap** |

There is **no option for a public URL without a DOI**. A protocol on GitHub with no Zenodo DOI fits none of the four truthfully. Either mint the DOI first or upload the PDF. Decide before reaching this field.

## Section 6. Searching and screening

| # | Field | Constraint | Pre-flight source |
|---|---|---|---|
| 1 | Published and unpublished | Two checkboxes | Section 4 |
| 2 | Main sources | Checklist. **No "Web of Science" entry**: use SCIE. "Other sources" opens a 50 word box | Section 4 |
| 3 | Language restrictions | Radio | Section 3 |
| 4 | Date restrictions | Radio | Section 4 |
| 5 | Other identification methods | Six checkboxes plus 50 word box | Section 4 |
| 6 | Link to search strategy | Not available / upload PDF / contained in full protocol | Section 5 |
| 7 | Selection process | Four radio options on screener number and adjudication | Section 6 |
| 8 | Other screening information | 0 to 250 words | **gap** |

## Section 7. Data collection process

| # | Field | Constraint | Pre-flight source |
|---|---|---|---|
| 1 | Data extraction | Five radio options, then author contact radio, then IPD radio | Section 7 |
| 2 | Risk of bias | Yes/no, then tool checklist (RoB-2, ROBINS-I, AMSTAR-2, QUADAS and others), assessor number, additional information | Section 9 |
| 3 | Reporting bias | Yes/no plus 50 word methods box | **gap** |
| 4 | Certainty assessment | Yes/no plus 5 to 250 word methods box | Section 9 |

## Section 8. Outcomes

| # | Field | Constraint | Pre-flight source |
|---|---|---|---|
| 1 | Main outcomes | 5 to 250 words. Asks explicitly for definition, measurement instrument, timepoint **and effect measure** | Section 8 |
| 2 | Additional outcomes | 0 to 250 words, same structure | Section 8 |

## Section 9. Planned data synthesis

| # | Field | Constraint | Pre-flight source |
|---|---|---|---|
| 1 | Strategy for data synthesis | Formal synthesis yes/no, then **30 to 500 words** | Section 10 |

The largest free text field in the form. Everything in our Section 10 and the sensitivity list fits.

## Section 10. Current review stage

| # | Field | Constraint | Pre-flight source |
|---|---|---|---|
| 1 | Stage at submission | Six stages, each not started / started / completed, plus overall status | **gap, and a gate** |
| 2 | Publication of review results | | **gap** |

**The binding constraint.** Data extraction beyond "Not started" blocks the section. See `registration_gate.md`.

## Section 11. Review affiliation, funding and peer review

| # | Field | Constraint | Pre-flight source |
|---|---|---|---|
| 1 | Review team members | **Minimum two.** Members must have consented and are emailed to confirm before publication. One must be guarantor | **gap, and a blocker for sole-author reviews** |
| 2 | Review affiliation | 1 to 20 words | Profile |
| 3 | Funding source | Three radio options plus 50 word box | Section 12 |
| 4 | Peer review | Radio | **gap** |

## Section 12. Additional information

| # | Field | Constraint | Pre-flight source |
|---|---|---|---|
| 1 | Additional information | **250 words** | **gap** |
| 2 | Conflict of interest | Radio | Section 12 |
| 3 | MeSH headings | Auto-populate (up to 3 minutes, sometimes unavailable) or manual autocomplete | **gap** |

Enter MeSH manually. Auto-populate is slow and leaving the page loses it. Note that several obvious terms have no MeSH entry: "Glucagon-Like Peptide-1 Receptor Agonists" does not resolve, and MASLD indexes as "Non-alcoholic Fatty Liver Disease".

## Gaps to close in the pre-flight template

Fourteen fields have no pre-flight source. Four matter:

**Registration timing.** A pre-flight that is complete but unregistered does not authorise extraction. Now covered by `registration_gate.md`.

**Team composition.** Two consenting members minimum. A sole-author review has to resolve this before reaching the form, and nobody should be named without having agreed. Our sole-author default collides with this directly.

**Protocol deposition route.** DOI or PDF, decided before the form.

**Additional information.** This is where anything the structured fields cannot carry goes, within 250 words. On this review it carried the disclosure of pre-registration pilot work. Worth drafting deliberately rather than at the form.

The remaining ten (keywords, country, context, dates, reporting bias methods, peer review status, MeSH, publication plans) are mechanical and could be added to the pre-flight template as a short registration block.

## Mechanical notes

| Behaviour | Handling |
|---|---|
| Checkboxes may ignore programmatic setting | Click, or focus and press space. Verify by zoom; a click that lands on the edge sets focus without toggling |
| Backspacing in a PICO combobox deletes already added tags once the text field empties | Clear by selecting the typed text, not by repeated backspace |
| Element references invalidate after each click on re-rendering sections | Use coordinates for multi checkbox groups, and re-read refs after each click elsewhere |
| "Go back" prompts to abandon unsaved changes | Answer No, then "Mark as complete" |
| Word counters turn red over limit and block completion | Check before marking complete. Rationale at 250 and additional information at 250 are the tightest |
