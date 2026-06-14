# Analysis Heuristics (Phase 1)

How to detect the stack, database, domain, and architecture of an unknown backend project.
All heuristics are signal-based — never rely on a project name or a specific filename.

## 1. Language & framework

Start from the **dependency manifest**, then confirm with imports and the entry point.

| Manifest file present | Language | Framework signals (in manifest or imports) |
| --- | --- | --- |
| `requirements.txt`, `pyproject.toml`, `Pipfile` | Python | `flask` → Flask · `django` → Django · `fastapi` → FastAPI · `flask-sqlalchemy` → Flask + SQLAlchemy ORM |
| `package.json` | Node.js | `express` → Express · `@nestjs/*` → NestJS · `koa` → Koa · `fastify` → Fastify |
| `pom.xml`, `build.gradle` | Java/Kotlin | `spring-boot-*` → Spring Boot |
| `composer.json` | PHP | `laravel/framework` → Laravel · `symfony/*` → Symfony |
| `Gemfile` | Ruby | `rails` → Rails · `sinatra` → Sinatra |
| `go.mod` | Go | `gin-gonic/gin`, `labstack/echo`, etc. |

- **Version**: read the pinned version in the manifest (`flask==3.1.1`, `"express": "^4.18.2"`).
- **Confirm with imports**: e.g. `from flask import Flask`, `const express = require('express')`.
- **Entry point**: the manifest often names it (`"main": "src/app.js"`, `"scripts": {"start": ...}`) or it's the file that instantiates the app and binds a port (`app = Flask(__name__)`, `app.listen(...)`).

## 2. Dependencies

List the runtime deps from the manifest. Flag deps that are **declared but never imported**
anywhere (dead dependencies) — note them for the audit (LOW: dead code).

## 3. Database & tables

Detect the persistence approach, then enumerate tables.

| Signal | Persistence approach |
| --- | --- |
| `import sqlite3`, `psycopg2`, `mysql.connector`, raw `cursor.execute(...)` | Raw driver / hand-written SQL |
| `flask_sqlalchemy`, `SQLAlchemy`, `db.Model` subclasses | SQLAlchemy ORM |
| `sequelize`, `prisma`, `typeorm`, `mongoose` | Node ORM/ODM |
| `sqlite3.Database(':memory:')` or `.Database('file.db')` | SQLite (in-memory vs file) |

**Enumerate tables** from whichever exists:
- `CREATE TABLE <name> (...)` statements in init/seed code.
- ORM model classes (`class Task(db.Model)` → table `tasks`; check `__tablename__`).
- Migration files.

Also note schema gaps for the audit: missing `FOREIGN KEY`, missing `UNIQUE`/indexes, no `CHECK` constraints.

## 4. Domain inference

Infer what the app *is* from concrete names — don't guess from the folder name:
- **Route paths**: `/produtos`, `/pedidos`, `/checkout` → e-commerce; `/courses`, `/enrollments` → LMS; `/tasks`, `/categories` → task manager.
- **Table/model names**: `produtos, usuarios, pedidos, itens_pedido` → e-commerce; `users, courses, enrollments, payments` → LMS; `tasks, users, categories` → task manager.
- **Seed data** often reveals the business (sample products, courses, etc.).

State the domain in one line, e.g. *"E-commerce API (produtos, pedidos, usuários)"*.

## 5. Architecture mapping

Classify the current structure, and identify the **missing layer**:

| Observation | Classification |
| --- | --- |
| Everything in a handful of flat files; routes + SQL + business logic interleaved | **Monolithic** — no layer separation |
| One class/file owns DB init + all routes + all logic | **God-class monolith** |
| `models/`, `routes/`, `services/`, `utils/` exist but **no `controllers/`**, and logic lives in routes | **Partial MVC** — controller layer missing |
| Clear `models/ + views(routes)/ + controllers/ + config/` with thin routes | **Full MVC** (little to do) |

**How to spot a missing/leaky layer:**
- Routes that build SQL, hash passwords, or compute reports inline → controller/service layer missing.
- A config value (secret key, DB path, port) hardcoded in app setup → config layer missing.
- No centralized error handler / middleware → cross-cutting layer missing.
- An entry point that also defines routes and business logic → no clean composition root.

Record the count of files you actually read as "Source files analyzed".

## Output

Feed these findings into the **Phase 1 banner** in `SKILL.md`. Keep values concrete and real —
they will be checked against the actual project.
