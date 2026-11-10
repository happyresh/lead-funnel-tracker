# System Design Document (SDD)

**Status:** Draft

> How the system is built: architecture, data, APIs, security and deployment. The PRD says what; this says how. Keep it true to the code; when they disagree, the code wins and this file is fixed (or a change record is opened). Lines starting with "Guide:" explain what to write.

## 1. Architectural Principles
Guide: three to six rules the design follows (for example "server decides permissions", "one database, scoped by organization", "no direct browser access to core data").

## 2. High-level Architecture

### 2.1 Component View

```text
browser (web app) -> API -> database
                        -> file storage
                        -> third-party services
```

Guide: replace with your real components and one line on each.

### 2.2 Deployment View
Guide: where each component runs (for example Vercel, Supabase, Render) and which branch deploys where.

### 2.3 Trust Boundaries
Guide: where data crosses from untrusted to trusted, and what checks happen there.

### 2.4 Tech Stack

| Layer | Technology | Why chosen |
|---|---|---|
| Guide: versions come from the dependency file, never typed here | | |

## 3. Data Architecture

### 3.1 Entity Relationship Diagram
Guide: a Mermaid `erDiagram` block or an image in `docs/reference/`.

### 3.2 Key Tables

| Table | Purpose | Owner scope | Sensitive fields |
|---|---|---|---|
| Guide: one row per main table | | Guide: organization, project or user | |

### 3.3 Data Integrity
Guide: constraints, transactions, audit history, soft delete rules.

## 4. API Design

| Endpoint | Purpose | Who may call | Input validation |
|---|---|---|---|
| Guide: one row per endpoint group | | | |

Guide: add sequence diagrams (Mermaid `sequenceDiagram`) for the two or three most important flows.

## 5. Security and Authorization
Guide: sign-in method, session handling, role and permission model, organization isolation, secret storage. Detailed decisions go in an RFC (`docs/rfc-<topic>.md`).

## 6. Infrastructure, CI/CD and Deployment
Guide: CI checks, environments (local, development, production), migrations process, backups.

## 7. Non-functional Requirements

| Quality | Requirement | How verified |
|---|---|---|
| Performance | Guide: for example main pages under 2 s at 10,000 rows | Guide: load test or measurement |
| Availability | | |
| Security | | |
| Accessibility | | |

## 8. AI Features
Guide: "None" or a summary, with details in `docs/aia.md`.
