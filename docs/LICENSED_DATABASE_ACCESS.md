# Licensed database access

The routes that work, recorded because a session on 2026-10-15 wasted time rediscovering them wrongly.

## Web of Science

**Use this link. Nothing else.**

```
https://ezproxy.bu.edu/login?url=https://www.webofscience.com/wos/woscc/advanced-search
```

Confirm success by the address bar: it must read `www-webofscience-com.ezproxy.bu.edu`. That is how you know you are on BU's subscription rather than a personal profile.

### What fails, and why it is not obvious

Going to `webofscience.com` directly redirects to the Clarivate sign-in page, which attaches Dr Borges' **free personal Web of Science profile**. That profile can search Researchers and author profiles but **cannot search the Core Collection**. The failure presents as either a profile completeness page, or "Oops, something went wrong", or document-search URLs returning "This page doesn't exist".

The misleading part is that the session looks authenticated. The header shows his name. Everything suggests a working login. The entitlement is simply absent.

### If you land on the personal profile

1. Sign out of Clarivate, top right
2. Reopen the proxy link above

The personal session takes precedence over the institutional one, so it must be cleared first.

### What is NOT the right path

The Clarivate sign-in page offers an "Institutional Sign In" dropdown. That list contains **federations**, not universities, so typing "Boston University" into it finds nothing. The entry that looks correct is "Incommon Federation", which leads to a SeamlessAccess institution picker where Boston University does appear.

That path may eventually work, but it is slower, it prompts a fresh Shibboleth login, and it ticks "Remember this choice" against the account. The proxy link avoids all of it. **Do not go down the federation path.**

### Session reuse

The proxy may complete without a password prompt if a BU session is already active from another database, such as Embase. A fresh browser or a different Chrome profile will prompt for Kerberos and Duo. Each Chrome profile keeps its own cookies, so confirm you are in the window where BU sign-in is active.

**The agent does not complete the BU login.** Submitting Kerberos credentials and Duo is an authentication step for Dr Borges, even when the fields are pre-filled.

## Embase

Works at `embase.com` directly once signed in. No proxy needed.

Before running any line, clear all four automatic mapping options:

| Option | State |
|---|---|
| Map to preferred term in Emtree | cleared |
| Search also as free text in all fields | cleared |
| Explode using narrower Emtree terms | cleared |
| Search as broadly as possible | cleared |

Explosion is then specified explicitly by `/exp` inside the strings, so the search reproduces from the strings alone rather than depending on interface defaults.

Export caveat: the export dialog lists "Medline PMID" as an included field, but **no PMID tag appears in the delivered RIS records**. Linkage to PubMed must go through DOI. On the 2026-10-15 export, DOI was present for 611 of 659 records.

## Standing protocol for any licensed search

| Step | Requirement |
|---|---|
| 1 | Dr Borges signs in himself |
| 2 | Agent runs the protocol strings as written, no improvised edits |
| 3 | Every line's hit count logged |
| 4 | RIS full record export only after his explicit yes |
| 5 | Exported record count gated against the reported search count before ingest |
| 6 | SHA-256 of the export file recorded |
| 7 | The `.ris` itself is gitignored in public repos; it is licensed content. The log carries strings, counts and hash so the export stays verifiable |

## Known prior searches

A Web of Science search of **514 records** was run in an earlier session and reported as exported and logged. Before re-running, check whether it used these strings. Two searches of the same database must not both feed the PRISMA counts.
