================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   5 analyzed | ~415 lines of code

Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] SQL Injection (AP-01)
File: models.py:28, 48-50, 57-62, 66, 92-93, 110-111, 126-130, 140, 148-151, 155-166, 174, 188, 193, 220-221, 225, 280-281, 290-297
Description: Every SQL statement in models.py is built by string concatenation of user-controlled values. Examples:
  - get_produto_por_id(): `"SELECT * FROM produtos WHERE id = " + str(id)` (line 28)
  - criar_produto(): INSERT built by concatenating nome, descricao, preco, categoria (lines 48-50)
  - login_usuario(): `"... WHERE email = '" + email + "' AND senha = '" + senha + "'"` (lines 110-111)
  - buscar_produtos(): dynamic WHERE built by appending termo, categoria, preco values (lines 290-297)
  - atualizar_status_pedido(): `"UPDATE pedidos SET status = '" + novo_status + "'"` (line 280)
Impact: Attackers can bypass authentication, dump or delete the entire database, and execute arbitrary SQL by injecting into any of these parameters.
Recommendation: Replace all string-concatenated queries with parameterized queries using `?` placeholders and a params tuple. See playbook T1.

[CRITICAL] Hardcoded Credentials / Secrets (AP-02)
File: app.py:7, controllers.py:287-290
Description: SECRET_KEY is hardcoded in source as `"minha-chave-super-secreta-123"` (app.py:7). The `/health` endpoint in controllers.py echoes both `secret_key` and `debug` values back to any unauthenticated caller (controllers.py:287-290). Seed data in database.py also stores plaintext admin password in code (database.py:76).
Impact: The secret key leaks via git history and via the public `/health` API response, enabling session forgery. Any caller can extract the app's secret.
Recommendation: Move SECRET_KEY to an environment variable loaded via `os.environ` or `python-dotenv`. Never expose config values in API responses.

[CRITICAL] Weak / Plaintext Password Storage (AP-04)
File: models.py:122-131, database.py:76-79, models.py:82-87, models.py:96-102
Description: Passwords are stored and compared as plaintext strings. `criar_usuario()` inserts `senha` as-is (models.py:126-130). `login_usuario()` compares raw passwords in the SQL WHERE clause (models.py:110-111). Seed data inserts `"admin123"`, `"123456"`, `"senha123"` into the DB (database.py:76-79). `get_todos_usuarios()` and `get_usuario_por_id()` return `senha` in every response dict (models.py:82-87, 96-102).
Impact: A single DB leak exposes every user's real password. Passwords are also returned over the API to any caller of `GET /usuarios`.
Recommendation: Hash passwords with bcrypt/argon2 on write; compare with the hash verifier on login; never include `senha` in API response dicts.

[CRITICAL] Insecure / Unauthenticated Dangerous Endpoints (AP-08)
File: app.py:47-57, app.py:59-78
Description: Two admin endpoints exist with zero authentication:
  - `POST /admin/reset-db` (app.py:47-57): deletes all rows from all tables — completely destructive with no auth check.
  - `POST /admin/query` (app.py:59-78): executes arbitrary raw SQL from the request body, a Remote Code Execution-equivalent against the database. `DEBUG=True` is also hardcoded (app.py:8).
Impact: Anyone who discovers these URLs can wipe the database or run `DROP TABLE` / `SELECT * FROM usuarios` with no credentials.
Recommendation: Remove or protect these endpoints behind admin-only auth middleware. Move `DEBUG` to an env var and default it to `False`.

[HIGH] Business Logic in Controllers / Routes (AP-05)
File: controllers.py:208-210, controllers.py:247-252, models.py:235-273
Description: Notification side-effects (email, SMS, push) are printed inline in route handlers `criar_pedido()` (controllers.py:208-210) and `atualizar_status_pedido()` (controllers.py:247-252). Discount calculation business logic (thresholds 10000/5000/1000 and percentage formulas) lives inside `models.py:relatorio_vendas()` (models.py:256-263) — the model layer is performing business rule computation, not just data access.
Impact: Business rules are not reusable or testable without the HTTP layer; notification logic is impossible to mock or replace.
Recommendation: Extract notification side effects into a NotificationService. Extract discount logic into a dedicated service or controller layer. See playbook T4.

[HIGH] N+1 Queries (AP-06)
File: models.py:171-201, models.py:203-233
Description: Both `get_pedidos_usuario()` and `get_todos_pedidos()` execute a SELECT on `pedidos`, then loop over each result running a nested SELECT on `itens_pedido`, then for each item run a further nested SELECT on `produtos` to get the product name. With 100 orders of 5 items each, this is 1 + 100 + 500 = 601 queries per list call.
Impact: Response time grows linearly with data volume; becomes unusable at scale.
Recommendation: Replace with a single JOIN query or two bulk queries with an in-memory grouping step. See playbook T5.

[HIGH] Global Mutable State (AP-07)
File: database.py:4, database.py:7-10
Description: `db_connection` is a module-level global variable (database.py:4) that is shared across all requests with `check_same_thread=False`. SQLite connections are not thread-safe; concurrent requests share and mutate the same connection object.
Impact: Race conditions and data corruption under concurrent load; impossible to test in isolation; connection state leaks between requests.
Recommendation: Use Flask's `g` object (`flask.g`) to scope a connection per request, or use a thread-safe connection pool.

[MEDIUM] Missing Input Validation (AP-09)
File: controllers.py:146-165, controllers.py:237-242, controllers.py:118-120
Description:
  - `criar_usuario()`: email format is never validated (controllers.py:146-165); any string passes as a valid email.
  - `atualizar_status_pedido()`: if the JSON body is None, `dados.get("status", "")` silently sets status to `""` with no helpful message (controllers.py:237-242).
  - `buscar_produtos()`: `preco_min`/`preco_max` are cast with `float()` but no guard for non-numeric values (controllers.py:118-120).
Impact: Invalid data silently reaches the DB; error messages are inconsistent and unpredictable.
Recommendation: Introduce a validation layer (e.g. marshmallow or manual checks) for email format, required fields, and type coercions.

[MEDIUM] Poor Error Handling / print() Instead of Logger (AP-11)
File: controllers.py:8, 11, 57, 106, 161, 179-180, 208-210, 219; app.py:56
Description: All error and event reporting uses `print()` statements scattered across controllers and app.py. There is no structured logger, no log levels, and no way to suppress output in production or redirect to a log aggregator.
Impact: Impossible to filter, format, or ship logs in production; sensitive operations leave no auditable trail.
Recommendation: Replace all `print()` calls with Python's `logging` module configured at startup.

[MEDIUM] Duplicated Logic / Missing Abstraction (AP-12)
File: models.py:12-21, models.py:31-40, models.py:79-86, models.py:96-102, models.py:303-313
Description: The row-to-dict conversion for `produtos` is copy-pasted identically in `get_todos_produtos()`, `get_produto_por_id()`, and `buscar_produtos()` — 10-line blocks of identical field mapping duplicated 3 times. The same pattern exists for `usuarios`.
Impact: A schema change requires updating 3+ places; drift leads to inconsistencies and bugs.
Recommendation: Extract `_row_to_produto_dict()` and `_row_to_usuario_dict()` helpers and call them from all sites.

[LOW] Magic Numbers & Strings (AP-13)
File: models.py:257-262, controllers.py:52-54
Description:
  - Discount thresholds `10000`, `5000`, `1000` and rates `0.1`, `0.05`, `0.02` are inline magic numbers with no named constants (models.py:257-262).
  - The valid category list `["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]` is an inline magic list (controllers.py:52-54).
Impact: Business rules are opaque and hard to change consistently.
Recommendation: Define `DISCOUNT_TIERS`, `VALID_CATEGORIAS` as module-level constants.

[LOW] Dead Code / Unused Imports (AP-15)
File: models.py:2, database.py:2
Description: `import sqlite3` appears at the top of `models.py` (models.py:2) but is never used there. `import os` appears in `database.py` (database.py:2) but is never referenced.
Impact: Misleads maintainers; slight noise in the dependency graph.
Recommendation: Remove unused imports.

================================
Total: 12 findings
================================
