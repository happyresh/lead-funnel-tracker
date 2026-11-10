# Scrutiny Gate

**Status:** Draft

> A hard, honest check of the idea and plan before committing to the build. Ask Claude to play a skeptical reviewer (adviser, panel, investor) using this structure. Lines starting with "Guide:" explain what to write.

## 1. Verdict

Guide: Proceed, Proceed with conditions (list them), or Stop. One paragraph why.

## 2. Claim and Reference Audit

| Claim | Source | Verified? | Action |
|---|---|---|---|
| Guide: every number or strong claim in IDEA, BRD or the manuscript | | Guide: yes, partly, no | Guide: keep, soften, remove or find a source |

## 3. Gap Analysis

Guide: what is missing between the problem, the requirements and the planned features.

## 4. Assumption Stress-test

| Assumption | If wrong, what happens | How to test it cheaply |
|---|---|---|
| Guide: one row each | | |

## 5. Feasibility and Scope

Guide: is the scope realistic for the time and team? What should be cut first?

## 6. Risk and Compliance Pre-flight

Guide: privacy, legal, safety, ethics or platform rules that could block the project. Details go in `docs/compliance.md`.

## 7. Blocking Questions

Guide: questions that must be answered before building starts, each with an owner.
