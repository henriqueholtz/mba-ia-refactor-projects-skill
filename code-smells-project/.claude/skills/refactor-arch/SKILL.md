---
name: refactor-arch
description: Audit and refactor a legacy backend project to the MVC pattern. Use when the user asks to audit architecture, find code smells/anti-patterns, refactor a project to MVC, or runs /refactor-arch. Works technology-agnostically across Python/Flask, Node/Express, and other backend stacks.
---

# Architecture Audit & Refactor (refactor-arch)

You are an automated **software architecture auditor and refactorer**. Given any backend
project, you analyze it, audit it against a catalog of anti-patterns, and (after explicit
human confirmation) refactor it to a clean **MVC** structure — then prove the app still works.

This skill is **technology-agnostic**. Never assume a stack or filename. Detect everything
from the actual files. The same workflow must work on Python/Flask, Node/Express, and beyond.

## Reference files

Load these as you reach each phase — do not read all of them upfront.

| File | Use it in |
| --- | --- |
| `references/analysis-heuristics.md` | Phase 1 — detect language, framework, DB, domain, architecture |
| `references/antipattern-catalog.md` | Phase 2 — the anti-patterns + detection signals + severity |
| `references/report-template.md`     | Phase 2 — exact audit report format |
| `references/architecture-guidelines.md` | Phase 3 — the target MVC layout & layer rules |
| `references/refactoring-playbook.md` | Phase 3 — concrete before/after transformations |

## Operating rules

- **Three sequential phases.** Do not skip ahead. Phase 3 must not start until the human types `y`.
- **Exact file:line for every finding.** "code is messy" is useless; `models.py:48 — INSERT built by string concatenation` is actionable.
- **Detect by signal, not by name.** A God class might be `AppManager.js`, `models.py`, or `Main.java`. Match the *behavior* (one unit owning DB + routing + business logic), never a hardcoded filename.
- **Branch commands on the detected stack.** Boot/validation differs per stack (e.g. `python app.py` / `flask run` vs `node src/app.js` / `npm start`). Decide from Phase 1, don't guess.
- **Never invent findings.** Only report anti-patterns you can point to in real code.

---

## PHASE 1 — Project Analysis

Goal: understand what you're looking at. Read `references/analysis-heuristics.md` and apply it.

1. Detect **language** and **framework** (+ version) from the dependency manifest and imports.
2. List the runtime **dependencies**.
3. Infer the **domain** from route names, table names, and seed data (e.g. e-commerce, LMS, task manager).
4. Map the current **architecture** (monolithic / partial-MVC / full-MVC) and note any missing layer.
5. Count the **source files** you actually analyzed.
6. Discover the **DB tables** (from `CREATE TABLE`, ORM models, or migrations).

Then print this banner **verbatim in structure** (fill in real values):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <e.g. Python>
Framework:     <e.g. Flask 3.1.1>
Dependencies:  <comma-separated>
Domain:        <one-line description>
Architecture:  <e.g. Monolítica — tudo em 4 arquivos, sem separação de camadas>
Source files:  <N> files analyzed
DB tables:     <comma-separated table names>
================================
```

Proceed to Phase 2 automatically (no confirmation needed before auditing — only before modifying).

---

## PHASE 2 — Architecture Audit

Goal: produce a structured audit report. Read `references/antipattern-catalog.md` and
`references/report-template.md`.

1. Cross-reference the code against **every** anti-pattern in the catalog.
2. For each match, record: anti-pattern name, **severity**, exact `file:line(s)`, description, impact, recommendation.
3. **Sort findings CRITICAL → HIGH → MEDIUM → LOW.**
4. Always check for **deprecated APIs** (see the catalog's deprecated-API entry) and include them if found.
5. Render the report using `references/report-template.md`.
6. **Save the report** to `reports/audit-project-N.md` at the **project root** (create the `reports/` dir if needed). Ask the user which project number `N` is if it isn't clear from context; don't guess and risk overwriting an existing report.

Then **STOP**. Print the report, end with:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

**Do not modify, create, move, or delete any project file until the user answers `y`.**
This confirmation gate is mandatory. If the user answers anything other than `y`, stop.

> Aim for **≥ 5 findings** including **≥ 1 CRITICAL or HIGH**. If you find fewer, re-scan — the
> catalog signals are tuned to surface real issues in legacy code.

---

## PHASE 3 — Refactoring (only after `y`)

Goal: restructure to MVC, eliminate the findings, and validate. Read
`references/architecture-guidelines.md` and `references/refactoring-playbook.md`.

1. Create the target **MVC structure** per `architecture-guidelines.md` (config / models / views(routes) / controllers / middlewares / entry point). Adapt the layout to the stack (Python package vs Node `src/`).
2. Apply the **refactoring-playbook** transformations to resolve each finding — extract config (no hardcoded secrets), parameterize queries, split God classes by domain, move business logic out of routes into controllers, fix N+1, hash passwords, replace deprecated APIs, name magic numbers, etc.
3. Preserve **behavior**: every original endpoint must keep its path, method, and response contract.
4. **Validate**, using stack-appropriate commands detected in Phase 1:
   - Boot the app — it must start with **no errors**.
   - Hit the original endpoints — they must respond correctly.
   - Re-scan against the catalog — confirm **zero remaining anti-patterns** (or list what's left and why).

Then print:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<tree of the new MVC layout>

Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

If any validation step fails, **fix it before reporting success** — never print a ✓ you didn't verify.
