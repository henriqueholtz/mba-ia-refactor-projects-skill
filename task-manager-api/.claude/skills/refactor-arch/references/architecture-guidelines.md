# Target Architecture Guidelines (Phase 3)

The MVC structure to refactor toward. Layer **responsibilities** are the contract; the **folder
layout** adapts to the stack. A change is only "MVC" if each layer does its job and nothing else.

## Layer responsibilities

| Layer | Owns | Must NOT do |
| --- | --- | --- |
| **Config** | Read settings/secrets from env vars; expose typed config object | Contain hardcoded secrets; contain business logic |
| **Models** | Data representation + persistence (queries/ORM) for one domain | Handle HTTP, validate requests, format responses, hold cross-domain logic |
| **Views / Routes** | HTTP routing only: map method+path → controller; parse/return JSON | Build SQL, compute business rules, talk to the DB directly |
| **Controllers** | Orchestrate the flow: validate input, call models/services, shape response | Contain raw SQL; know about HTTP framework internals beyond req/res |
| **Middlewares** | Cross-cutting concerns: centralized error handling, auth, logging | Hold domain logic |
| **Entry point** | Composition root: build config, wire layers, register routes, start server | Define routes or business logic inline |

Optional **Services** layer: when business logic is heavy or shared across controllers, put it in
`services/` and have controllers call it. (Models stay persistence-only.)

## Target layout

The reference tree (from the challenge). Keep the **roles**; rename folders to stack convention.

```
src/
├── config/settings.py          # env-based config, no hardcoded secrets
├── models/
│   ├── produto_model.py        # one model per domain
│   └── usuario_model.py
├── views/
│   └── routes.py               # routing only (Flask blueprints / Express routers)
├── controllers/
│   ├── produto_controller.py   # one controller per domain
│   └── pedido_controller.py
├── middlewares/error_handler.py # centralized error handling
└── app.py                       # composition root / entry point
```

**Stack adaptations:**
- **Python/Flask:** package with `__init__.py`; routes as Blueprints registered in the app factory;
  config via `os.environ` (optionally `python-dotenv`); models use parameterized `sqlite3` or SQLAlchemy.
- **Node/Express:** `src/` with `routes/` (express `Router`), `controllers/`, `models/` (repository per
  domain), `config/index.js` reading `process.env`, error-handling middleware via `app.use((err,req,res,next)=>...)`;
  prefer `async/await` over callbacks.
- **Already partial-MVC** (has `models/`, `routes/`, `services/` but no `controllers/`): **add the
  controllers layer**, move business logic out of routes into controllers/services, extract config, add
  centralized error handling — don't gratuitously move what's already correct.

## Invariants to preserve

- **Every original endpoint keeps its path, method, and response contract.** Refactor structure, not API.
- **No secret remains in source** — all moved to config/env.
- **No raw SQL outside models** — controllers/routes call models.
- **Validation centralized** — at the controller/middleware boundary, not duplicated per route.
- **One clear entry point** that boots the wired app.

## Validation checklist (used at end of Phase 3)

- [ ] Directory structure follows MVC (config / models / views / controllers / middlewares / entry point)
- [ ] Config extracted to a config module (no hardcoded secrets)
- [ ] Models abstract data access (no SQL in routes/controllers)
- [ ] Views/Routes only route
- [ ] Controllers concentrate the flow
- [ ] Error handling centralized
- [ ] Clear entry point / composition root
- [ ] Application boots without errors
- [ ] Original endpoints respond correctly
- [ ] Zero anti-patterns remaining (or remainder explicitly justified)
