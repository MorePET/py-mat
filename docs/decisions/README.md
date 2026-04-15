# Architectural Decision Records

This directory contains Architectural Decision Records (ADRs) for `mat`.

An ADR captures a decision that shapes the architecture — what was decided,
why, what was rejected, and what the consequences are. It exists so that a
reader months later can reconstruct the reasoning and spot the trigger that
would overturn it.

We use a light MADR-ish format. Each ADR is one markdown file named
`NNNN-short-dash-separated-title.md`, where `NNNN` is a zero-padded sequential
number.

## Statuses

- **Proposed**: under discussion, not yet in effect
- **Accepted**: in effect
- **Deprecated**: no longer applies but kept for historical context
- **Superseded by NNNN**: replaced by another ADR

## Writing a new ADR

1. Copy the template below into `NNNN-title.md`.
2. Fill it in. Keep each section short — ADRs are not design docs.
3. Open a PR. Discussion happens there, not in the file.
4. Once merged, the ADR is Accepted.

## Template

```markdown
# NNNN. Title

- Status: Proposed | Accepted | Deprecated | Superseded by NNNN
- Date: YYYY-MM-DD
- Deciders: @handles

## Context

What is the forcing function? Who cares? What constraints apply?

## Decision

The decision itself, stated as a single sentence if possible.

## Consequences

What this enables, what it costs, what it rules out.

## Alternatives considered

Named alternatives with one-line rationale for rejection.

## Upgrade trigger

Under what future condition should this ADR be revisited or superseded?
```
