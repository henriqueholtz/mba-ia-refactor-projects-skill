# Audit Report Template (Phase 2)

Render the Phase-2 audit in **exactly** this structure. Print it to the console **and** save a
copy to `reports/audit-project-N.md` (at the project root). Findings must be sorted **CRITICAL → HIGH → MEDIUM → LOW**.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project folder name>
Stack:   <Language + Framework>, e.g. Python + Flask
Files:   <N> analyzed | ~<LOC> lines of code

Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

Findings

[CRITICAL] <Anti-pattern name>
File: <path:line> (or path:line-range)
Description: <what the code does wrong, concretely>
Impact: <consequence — security/perf/maintainability>
Recommendation: <how to fix; reference the playbook transformation>

[CRITICAL] <next finding>
File: ...
Description: ...
Impact: ...
Recommendation: ...

[HIGH] <...>
File: ...
Description: ...
Impact: ...
Recommendation: ...

[MEDIUM] <...>
...

[LOW] <...>
...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Rules

- **One block per finding**, in the order above (all CRITICALs first, then HIGH, etc.).
- **Every finding cites `file:line`** (a single line or a range). No vague locations.
- The **Summary** counts must match the number of finding blocks per severity.
- Map each finding back to a catalog entry (AP-NN) in the Recommendation when helpful.
- The report **ends with the `[y/n]` prompt** — nothing is modified until the human approves.
- Saved file: `reports/audit-project-N.md` with the same content (drop the trailing `[y/n]` line is
  optional in the saved file; keep it in the console output).

## Worked example (abbreviated)

```
[CRITICAL] SQL Injection
File: models.py:48-50
Description: criar_produto() builds an INSERT via string concatenation of user input
             ("INSERT INTO produtos (...) VALUES ('" + nome + "', ...)").
Impact: Attackers can inject SQL to read/alter/delete arbitrary data.
Recommendation: Use parameterized queries (placeholders + params tuple). See playbook T1.

[CRITICAL] Hardcoded Credentials
File: app.py:7
Description: SECRET_KEY hardcoded as 'minha-chave-super-secreta-123'; also echoed at /health.
Impact: Secret leaks via source control and API responses; session forgery possible.
Recommendation: Move to a config module reading env vars. See playbook T2.
```
