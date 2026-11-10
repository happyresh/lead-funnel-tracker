# RFC Template

> An RFC (request for comments) is the detailed technical contract for one risky area (for example authentication, data import, alert rules, privacy). Write one when the SDD summary is not enough to build it safely. Copy to `docs/rfc-<topic>.md`. Changes to an approved RFC need a change record.

**Status:** Draft, Working or Locked
**Scope:** which PRD features it covers (for example F1, F5)

## Objective
What this area must achieve, in two or three sentences.

## Current State
What exists today, with file paths.

## Design
The rules, data flow and components, step by step. Use a pipeline block for flows:

```text
upload -> size and type check -> private storage -> parse -> validate -> stage -> map -> save -> audit
```

## Safety Rules
- What must never happen (for example "never trust the file extension", "never retrieve data before scoping it").
- How each rule is enforced.

## Edge Cases
Empty input, duplicates, very large input, partial failure, retries, concurrency.

## Provenance and Audit
What is recorded about who did what and when.

## Tests
Required QAD rows (happy, sad, abuse) and test files.

## Open Questions
Anything not decided, with an owner.
