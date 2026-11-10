# Postmortem Template

> Use a postmortem after something broke (outage, data problem, failed deploy, failed demo). Copy this file to `docs/postmortem-<short-name>.md`. Blameless: focus on systems, assumptions and checks, not people.

**Incident date:** write the date.
**Severity:** P0 (everything down or data lost), P1 (major feature broken), P2 (partial), P3 (minor).
**Status:** Draft or Final.

## Impact
Who was affected, how, and for how long.

## Timeline
Times and events, from first sign to full recovery.

## Detection
How it was noticed, and how it could have been noticed sooner.

## Root Cause
The underlying reason, not just the trigger.

## Contributing Conditions
What made it possible or worse.

## Recovery
What was done to fix it.

## What Went Well

## What Made Recovery Harder

## Action Items

| Action | Owner | Due | Status | Evidence |
|---|---|---|---|---|

## Documentation and Test Changes
Tests, reviewer rules or documents updated so this cannot happen again.
