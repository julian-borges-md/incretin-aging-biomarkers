# Draft email to CRD

Send to the PROSPERO contact address from jyborges@bu.edu. Two questions, both blocking a record currently sitting incomplete in the account.

Review the wording before sending. In particular, decide whether you want to describe the pilot as candidly as the draft does. I think you should, because the extraction is public and timestamped and they can see it, but it is your call.

---

**Subject:** Eligibility questions before submitting a registration: pre-registration form pilot, and sole author team requirement

Dear PROSPERO team,

I am preparing to register a systematic review and network meta-analysis and have reached two points I would rather ask about than guess at. The record is complete apart from these and is held in my account under the title "Aging biomarker signatures of incretin and glucagon receptor agonism across receptor classes".

**1. Does a single trial form pilot count as data extraction?**

Before registering, I extracted one trial (Sanyal et al., Nature Medicine 2024, PMID 38858523) in order to test a 51 column extraction form. The purpose was to find defects in the form, and it did: the schema had assumed arm level means and standard deviations, whereas this literature reports treatment contrasts, so the schema was rebuilt. No pooled estimate was produced and no result was derived.

When I set the data extraction stage to "Started", which is accurate, the form prevents the section from being completed and returns the message that registrations are not allowed beyond the data extraction stage.

My question is whether a pilot of this kind falls within "data extraction has started" in term 5, or whether it falls under "Pilot work (pilot searching, testing forms etc.)", which is the first stage listed on that same page and which I have also marked as Started. I am not asking to be allowed to record something inaccurate. If the pilot does bar an initial registration, I would rather know that than proceed.

The protocol, the analysis code, the extraction schema and the extraction itself are public with commit timestamps at https://github.com/julian-borges-md/incretin-aging-biomarkers, so the sequence of events is independently verifiable.

**2. Is there a route for a sole author review?**

The review is sole authored. The team members field requires a minimum of two, and the guidance is clear that named members must have agreed to be included and will be asked to confirm the record before publication. I am not willing to add anyone who has not consented.

Is there a route to register with a single team member, or is the expected solution to add a methodologist in a protocol review capacity? If the latter, I would want to understand what that person is taken to be attesting to when they confirm the record, so that their role is described accurately rather than nominally.

I would be grateful for guidance on both.

With thanks,

Julian Borges, MD, MS
Department of Computer Science, Boston University
jyborges@bu.edu
ORCID 0009-0001-9929-3135

---

## If they say the pilot bars registration

Three options, in the order I would consider them:

| Option | Note |
|---|---|
| Register the review as it stands and accept it cannot be a prospective registration | PROSPERO records retrospective registrations in some circumstances; ask what applies |
| Rely on the public timestamped protocol alone | The commit history already fixes the analysis plan before extraction, which is the substantive protection. Some journals will still want a registry number |
| Scope a second review that has not been touched, and register that one first | Only sensible if a second review is genuinely planned, not as a workaround |

Deleting the extraction is not on this list. It is already public and timestamped, the manuscript's corrected hepatic section depends on it, and removing it would make the record and the repository disagree.
