# Refactoring Playbook (Phase 3)

Concrete before/after transformations, each tied to a catalog anti-pattern (AP-NN). Apply the one
that matches each finding. Examples are shown in the language where the pattern most commonly appears;
the principle transfers across stacks.

---

## T1 · SQL concatenation → parameterized query  (AP-01)

**Before** (Python, raw sqlite3):
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("INSERT INTO produtos (nome, preco) VALUES ('" + nome + "', " + str(preco) + ")")
```
**After:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (nome, preco))
```
Node equivalent: `db.get("SELECT * FROM users WHERE id = ?", [id], cb)` (already parameterized — keep it).
With an ORM, prefer `Model.query.get(id)` / `session.query(...)` over hand-built SQL.

---

## T2 · Hardcoded secret → config module from env  (AP-02)

**Before:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```
**After** — `config/settings.py`:
```python
import os
SECRET_KEY = os.environ["SECRET_KEY"]          # fail fast if missing
DB_PATH    = os.environ.get("DB_PATH", "loja.db")
DEBUG      = os.environ.get("DEBUG", "false").lower() == "true"
```
```python
from config import settings
app.config["SECRET_KEY"] = settings.SECRET_KEY
```
Node: `config/index.js` reading `process.env.SECRET_KEY` etc. Add `.env` to `.gitignore`; never echo secrets in responses.

---

## T3 · God class → split by domain into model + controller  (AP-03)

**Before:** one `AppManager`/`models.py` owning DB init, every route, and all business logic.

**After:** extract per-domain modules.
```
models/produto_model.py        # produto persistence only
controllers/produto_controller.py  # produto flow
views/routes.py                # routing only, delegates to controllers
app.py                         # wires them together
```
Move each responsibility to its layer; the entry point only composes them.

---

## T4 · Business logic in route → controller/service  (AP-05)

**Before** (Flask route doing everything):
```python
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if len(data["title"]) < 3 or len(data["title"]) > 200:
        return jsonify({"erro": "titulo invalido"}), 400
    if not User.query.get(data["user_id"]):
        return jsonify({"erro": "usuario nao existe"}), 400
    task = Task(title=data["title"], user_id=data["user_id"])
    db.session.add(task); db.session.commit()
    return jsonify(task.to_dict()), 201
```
**After** — route delegates; controller orchestrates:
```python
# views/routes.py
@bp.route("/tasks", methods=["POST"])
def create_task():
    return task_controller.create(request.get_json())

# controllers/task_controller.py
def create(data):
    validate_task(data)                 # raises ValidationError -> error middleware
    user = user_model.get(data["user_id"]) or _not_found("usuario")
    task = task_model.create(title=data["title"], user_id=user.id)
    return jsonify(task.to_dict()), 201
```

---

## T5 · N+1 queries → single JOIN / eager load  (AP-06)

**Before:**
```python
pedidos = get_all_pedidos()
for p in pedidos:
    for item in get_items(p["id"]):          # query per order
        item["nome"] = get_produto(item["produto_id"])["nome"]  # query per item
```
**After** — one query with a JOIN:
```python
cursor.execute("""
    SELECT p.id, i.quantidade, pr.nome
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    JOIN produtos pr     ON pr.id = i.produto_id
""")
```
ORM: use `joinedload`/`selectinload` (SQLAlchemy) or `include` (Sequelize) instead of per-row lazy loads.

---

## T6 · Plaintext/MD5/Base64 password → strong hash  (AP-04)

**Before:**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()    # broken, unsalted
```
```javascript
function badCrypto(pwd){ /* base64 loop */ }               // reversible, not a hash
```
**After:**
```python
from werkzeug.security import generate_password_hash, check_password_hash
self.password = generate_password_hash(pwd)               # salted PBKDF2/scrypt
# verify:
check_password_hash(self.password, attempt)
```
Node: `bcrypt.hash(pwd, 12)` / `bcrypt.compare(attempt, hash)`. Never return the hash in API responses.

---

## T7 · Callback hell → async/await + DB helper  (AP-11)

**Before** (Node pyramid of doom):
```javascript
db.get(q1, [a], (e, course) => {
  db.get(q2, [b], (e, user) => {
    db.run(q3, [c], (e) => { res.send("ok"); });
  });
});
```
**After** — promisify and `async/await`:
```javascript
const get = (sql, p) => new Promise((ok, no) => db.get(sql, p, (e, r) => e ? no(e) : ok(r)));
const run = (sql, p) => new Promise((ok, no) => db.run(sql, p, e => e ? no(e) : ok()));

async function checkout(req, res, next) {
  try {
    const course = await get(q1, [a]);
    const user   = await get(q2, [b]);
    await run(q3, [c]);
    res.send("ok");
  } catch (err) { next(err); }   // -> centralized error middleware
}
```
Python: replace bare `except:` with specific exceptions; raise to a centralized handler instead of returning ad-hoc `{"erro": ...}`.

---

## T8 · Deprecated API → modern replacement  (AP-10)

**Before:**
```python
created_at = datetime.utcnow()          # deprecated in Python 3.12+
```
**After:**
```python
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
```
Other swaps: Node `new Buffer(x)` → `Buffer.from(x)`; `url.parse()` → `new URL()`; bump EOL framework pins in the manifest; replace callback DB APIs with promise-based ones (see T7).

---

## T9 · Magic numbers → named constants  (AP-13)

**Before:**
```python
if faturamento > 10000: desconto = faturamento * 0.1
elif faturamento > 5000: desconto = faturamento * 0.05
```
**After:**
```python
DISCOUNT_TIERS = [(10_000, 0.10), (5_000, 0.05), (1_000, 0.02)]
desconto = next((fat * rate for limit, rate in DISCOUNT_TIERS if fat > limit), 0)
```
Same idea for `PRIORITY_MIN/MAX`, `TITLE_MAX_LEN`, date-format constants.

---

## T10 · Global mutable state → encapsulation / injection  (AP-07)

**Before:**
```javascript
let globalCache = {};            // module-level, shared across requests
let totalRevenue = 0;
```
**After:** encapsulate in a class/closure and inject it where needed (constructor arg / app context),
or use the framework's request-scoped state. No cross-request mutable module globals. For DB
connections, use a connection factory/pool per request rather than one shared mutable handle.

---

## T11 · Centralized error handling  (AP-08, AP-11)

Add one error boundary instead of ad-hoc try/except per route.
- **Flask:** `@app.errorhandler(Exception)` / `@app.errorhandler(ValidationError)` returning a
  consistent JSON shape; raise typed exceptions from controllers.
- **Express:** `app.use((err, req, res, next) => res.status(err.status||500).json({error: err.message}))`
  registered last; controllers call `next(err)`.
Also: remove dangerous endpoints (arbitrary-SQL `/admin/query`), gate admin routes behind auth, and never log secrets/PII.

---

## T12 · Remove dead code & unused deps  (AP-15)

Delete unused imports, never-called functions, and exported-but-unused vars. Remove
declared-but-unimported dependencies from the manifest (`requirements.txt` / `package.json`), or wire
them in if they were meant to be used (e.g. adopt marshmallow for the validation in T4).

---

> Apply transformations until the post-refactor re-scan against `antipattern-catalog.md` returns zero
> findings (or a short, justified remainder). Preserve every endpoint's contract throughout (T3–T5 are
> structure moves, not behavior changes).
