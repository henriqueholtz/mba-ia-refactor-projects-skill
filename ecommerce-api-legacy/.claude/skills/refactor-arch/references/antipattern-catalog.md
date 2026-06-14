# Anti-Pattern Catalog (Phase 2)

The catalog the auditor cross-references code against. Each entry has a **severity**, concrete
**detection signals** (what to grep/look for), and **why it matters**. Signals are stack-agnostic;
examples span Python and Node. Match on *behavior*, not on a specific filename.

Severity scale (from the challenge spec):
- **CRITICAL** — architecture/security failure: breaks the app, exposes data, or fully collapses separation of concerns.
- **HIGH** — strong MVC/SOLID violation that badly hurts maintainability/testability.
- **MEDIUM** — standardization, duplication, or moderate performance/correctness issues.
- **LOW** — readability, naming, magic numbers, dead code.

---

## CRITICAL

### AP-01 · SQL Injection
- **Signals:** SQL built with string concatenation or interpolation around user input —
  `"... WHERE id = " + str(id)`, `f"... '{email}'"`, template literals `` `SELECT ... ${x}` ``.
  Any `cursor.execute(...)`/`db.run(...)` whose query string is assembled from variables instead of `?`/`%s` placeholders.
- **Why:** Attackers bypass auth, read/dump/delete data. Most severe and most common in legacy code.

### AP-02 · Hardcoded Credentials / Secrets
- **Signals:** literal secrets in source — `SECRET_KEY = "..."`, `dbPass: "..."`, API/payment keys
  (`pk_live_...`), SMTP passwords, secrets echoed in a `/health` response. Anything that should be an env var.
- **Why:** Credentials leak via source control, logs, and API responses; instant compromise.

### AP-03 · God Class / God Method
- **Signals:** a single class or file that owns **DB access + routing + business logic + response shaping**
  for multiple domains; hundreds of lines; methods doing many unrelated things. Detect by responsibility
  count, not by name (could be `AppManager.js`, `models.py`, anything).
- **Why:** Impossible to test in isolation; any change risks breaking everything.

### AP-04 · Weak or Plaintext Password Storage
- **Signals:** passwords stored as-is; hashing with `md5`/`sha1`; "encryption" via Base64
  (`Buffer.from(pwd).toString('base64')`); no salt; password returned in `to_dict()`/API responses.
- **Why:** Trivially reversible/crackable; one DB leak compromises every account.

---

## HIGH

### AP-05 · Business Logic in Controllers / Routes
- **Signals:** route handlers that validate, compute reports/discounts, talk to the DB directly, or
  orchestrate multi-step workflows inline (payment + enrollment + audit in one handler). Fat routes, thin/absent service+controller layer.
- **Why:** Logic isn't reusable or testable without the HTTP layer; routes become unmaintainable.

### AP-06 · N+1 Queries
- **Signals:** a query **inside a loop** (`for item in items: cursor.execute(...)`,
  `enrollments.forEach(() => db.get(...))`); ORM lazy-loads triggered per row (`len(u.tasks)` in a loop,
  `User.query.get(t.user_id)` per task). One list endpoint firing dozens–hundreds of queries.
- **Why:** Performance collapses with data growth; should be a single JOIN / eager load.

### AP-07 · Global Mutable State
- **Signals:** module-level mutable globals (`globalCache = {}`, `totalRevenue = 0`, a shared
  `db_connection` with `check_same_thread=False`) read/written across requests.
- **Why:** Race conditions, memory leaks, state pollution under concurrency; untestable.

### AP-08 · Insecure / Unauthenticated Dangerous Endpoints & Debug-in-Prod
- **Signals:** endpoints executing arbitrary SQL (`POST /admin/query` running `request.json["sql"]`),
  destructive admin routes with no auth (`POST /admin/reset-db`), `DEBUG=True`/`app.config["DEBUG"]=True`
  in shipped code, fake/unverified auth tokens (`"fake-jwt-token-"+id`), secrets/PII logged to console
  (full credit-card numbers).
- **Why:** Full data loss, RCE-equivalent SQL access, info disclosure via stack traces, broken authz.

---

## MEDIUM

### AP-09 · Missing Input Validation
- **Signals:** request fields used without type/format/range checks (`data.get('user_id')` passed straight
  to a query; `int(priority)` with no guard; no email/length validation); a validation lib declared but unused (marshmallow).
- **Why:** Invalid/garbage data reaches the DB; crashes get swallowed by broad excepts.

### AP-10 · Deprecated APIs  *(always check this — required by spec)*
- **Signals:**
  - Python: `datetime.utcnow()` (deprecated 3.12+) → use `datetime.now(timezone.utc)`; `cgi`, `imp`, `distutils` imports.
  - Node/Express: callback-style `sqlite3` instead of promises/async-await; `new Buffer()`; `url.parse()`;
    EOL Express 4.x patterns; bare callbacks where async/await is the modern norm.
  - Any framework pinned to an **EOL version** in the manifest.
- **Detection:** grep for the signatures above and inspect manifest version pins.
- **Why:** Deprecated APIs break on upgrade, miss security fixes, and signal unmaintained code.

### AP-11 · Callback Hell / No Async, and Poor Error Handling
- **Signals:** deeply nested callbacks ("pyramid of doom"), manual counter coordination across async
  callbacks (race-prone); broad/bare `except:` / `catch(e){}` that swallow errors; inconsistent error
  shapes (sometimes raise, sometimes return `{"erro": ...}`); `print()` instead of a logger.
- **Why:** Unreadable, race-prone, and hides real failures — undiagnosable in production.

### AP-12 · Duplicated Logic / Missing Abstraction
- **Signals:** the same block (e.g. "is overdue?" check, dict-building) copy-pasted across 3+ handlers;
  validation constants re-declared inline in many places instead of one source.
- **Why:** Changes must be made in many places; drift introduces inconsistencies and bugs.

---

## LOW

### AP-13 · Magic Numbers & Strings
- **Signals:** unexplained literals in logic — discount thresholds (`if total > 10000: ...`),
  `priority < 1 or priority > 5`, `len(title) < 3`, card-prefix `"4"`, date formats `'%Y-%m-%d'` repeated.
- **Why:** Intent is opaque; values drift; should be named constants.

### AP-14 · Poor Naming
- **Signals:** cryptic single-letter or abbreviated identifiers (`u`, `e`, `cid`, `cc`, `req.body.usr`).
- **Why:** Hurts readability and onboarding.

### AP-15 · Dead Code / Unused Imports & Dependencies
- **Signals:** declared-but-unused deps (marshmallow/requests/python-dotenv pinned but never imported);
  unused imports (`os, sys, json, time`); functions defined but never called; exported-but-unused vars.
- **Why:** Noise, larger attack surface, misleads maintainers.

---

## Coverage guidance

Across any of the 3 target stacks this catalog reliably surfaces **≥ 5 findings including ≥ 1
CRITICAL/HIGH**. When a project is *partially* organized (has `models/`, `routes/`, `services/` but no
controllers), the dominant findings shift toward **AP-05, AP-06, AP-10, AP-11** rather than AP-01/AP-03 —
audit by signal, and report what you actually find.
