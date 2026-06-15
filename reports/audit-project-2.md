================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18.2
Files:   3 analyzed | ~170 lines of code

Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 2 | LOW: 2

Findings

[CRITICAL] AP-02 · Hardcoded Credentials / Secrets
File: src/utils.js:1-7
Description: The config object embeds production secrets directly in source code:
             dbPass "senha_super_secreta_prod_123", paymentGatewayKey "pk_live_1234567890abcdef",
             and smtpUser credentials. The live payment key is also echoed to stdout at
             src/AppManager.js:45 ("Processando cartão ... na chave pk_live_...").
Impact: Credentials leak via source control and server logs; instant payment-gateway and
        database compromise.
Recommendation: Move all secrets to environment variables (process.env.*). Introduce a
                config module that reads from .env (via dotenv) and throws on missing required vars.
                Never log raw keys. See playbook T2.

[CRITICAL] AP-03 · God Class
File: src/AppManager.js:1-141
Description: AppManager owns DB initialization (initDb, lines 10-23), HTTP route definitions
             (setupRoutes, lines 25-138), payment processing logic (lines 43-64), user creation
             with password hashing (lines 66-75), N+1 query orchestration for the financial
             report (lines 80-129), and audit logging (lines 57-58) — all in a single 141-line
             class spanning four distinct domains.
Impact: Impossible to unit-test any single concern; a change to payment logic risks breaking
        user creation or the financial report. Zero separation of concerns.
Recommendation: Split into domain-specific controllers (CheckoutController, ReportController,
                UserController), service classes (PaymentService, EnrollmentService), and a
                dedicated DB/model layer. See playbook T3.

[CRITICAL] AP-04 · Weak Password Storage
File: src/utils.js:17-23, src/AppManager.js:68
Description: badCrypto() hashes passwords by Base64-encoding the raw password 10,000 times
             and then truncating to 10 characters. This produces a deterministic, low-entropy
             string with no salt. The seed user (src/AppManager.js:18) stores "123" as plaintext.
Impact: Trivially reversible. One DB dump exposes every user's password. Base64 is encoding,
        not hashing.
Recommendation: Replace with bcrypt (bcryptjs) or argon2 with a work factor ≥ 12. Never
                store plaintext or base64-encoded passwords. See playbook T4.

[CRITICAL] AP-08 · Insecure / Unauthenticated Dangerous Endpoints
File: src/AppManager.js:131-137
Description: DELETE /api/users/:id deletes a user with no authentication, no authorization
             check, and no cascading cleanup — enrollments and payments are left as orphan rows
             (the response literally says "mas as matrículas e pagamentos ficaram sujos no banco").
             The financial admin report (GET /api/admin/financial-report) is also completely open
             with no auth guard.
Impact: Any anonymous caller can delete arbitrary users or read full financial data. Data
        integrity is permanently broken by the orphan rows.
Recommendation: Add authentication middleware (JWT or session). Protect admin routes with a
                role check. Add ON DELETE CASCADE foreign keys or explicit cleanup logic.

[HIGH] AP-05 · Business Logic in Routes
File: src/AppManager.js:28-78 (checkout handler), 80-129 (financial-report handler)
Description: Route handlers perform multi-step business workflows inline: the /api/checkout
             handler directly runs payment-status computation (line 46), user lookup/creation
             (lines 66-75), enrollment INSERT, payment INSERT, and audit log INSERT — all inside
             nested callbacks inside a route definition. The financial-report handler builds an
             aggregated revenue report inline. No service or controller layer exists.
Impact: Business logic cannot be tested without starting an HTTP server; it cannot be reused
        by other callers (e.g. a CLI or a cron job).
Recommendation: Extract checkout flow into CheckoutService/CheckoutController and report
                aggregation into ReportService. Routes should only parse the request and
                delegate to a controller. See playbook T5.

[HIGH] AP-06 · N+1 Queries
File: src/AppManager.js:89-128
Description: The financial-report handler first fetches all courses (line 83), then for each
             course fires a query for its enrollments (line 92), then for each enrollment fires
             two more queries — one for the user (line 104) and one for the payment (line 106).
             With C courses and E enrollments each, this fires 1 + C + 2×C×E queries.
Impact: Response time grows quadratically with data; will time-out or cause DB overload in
        production.
Recommendation: Replace with a single JOIN query:
                SELECT c.title, u.name, u.email, p.amount, p.status
                FROM courses c
                LEFT JOIN enrollments e ON e.course_id = c.id
                LEFT JOIN users u ON u.id = e.user_id
                LEFT JOIN payments p ON p.enrollment_id = e.id
                Aggregate in JavaScript. See playbook T6.

[HIGH] AP-07 · Global Mutable State
File: src/utils.js:9-10
Description: globalCache and totalRevenue are module-level mutable variables shared across
             all requests. logAndCache() writes to globalCache on every checkout. totalRevenue
             is exported but never updated — it is dead state today but a race-condition trap
             if ever used.
Impact: Under concurrent requests, writes to globalCache race. Cache grows unboundedly,
        causing memory leaks. State is invisible to tests.
Recommendation: Remove the in-process cache. If caching is needed, use Redis or a proper
                caching layer. Eliminate totalRevenue or compute it from the DB on demand.
                See playbook T7.

[MEDIUM] AP-09 · Missing Input Validation
File: src/AppManager.js:29-35
Description: The checkout handler reads usr, eml, pwd, c_id, cc from req.body and checks
             only for presence (line 35). No email format validation, no numeric validation of
             c_id, no card number format/length check. The user ID in DELETE /api/users/:id
             (line 131) is passed directly to the DB with no integer validation.
Impact: Malformed data (e.g. c_id="'; DROP TABLE--") can reach the DB; crashes are swallowed.
Recommendation: Use a validation library (express-validator or zod) to check types, formats,
                and ranges on every route. See playbook T9.

[MEDIUM] AP-11 · Callback Hell / Poor Async & Error Handling
File: src/AppManager.js:37-128
Description: The checkout route nests 5 levels of sqlite3 callbacks (course → user → insert
             enrollment → insert payment → insert audit_log). The financial-report handler uses
             manual decrement counters (coursesPending, enrPending) to detect completion — a
             fragile, race-prone pattern. Errors in several DB callbacks (e.g. line 106) are
             silently ignored.
Impact: Unreadable; the slightest timing difference between async DB calls can cause double
        responses or missed sends. Silent error swallowing hides real failures.
Recommendation: Wrap sqlite3 in a promise utility (or use better-sqlite3 for synchronous ops).
                Convert all handlers to async/await. Add centralized error-handling middleware.
                See playbook T11.

[LOW] AP-13 · Magic Numbers & Strings
File: src/AppManager.js:46, src/utils.js:20-22
Description: The payment approval rule cc.startsWith("4") (line 46) is an unexplained literal.
             The badCrypto loop count 10000 and truncation length 10 (utils.js:20-22) are
             unnamed constants.
Impact: Intent is opaque; values can drift without obvious impact.
Recommendation: Name constants (VISA_PREFIX = "4", HASH_ITERATIONS, etc.) even if the
                crypto is being replaced. See playbook T13.

[LOW] AP-14 · Poor Naming
File: src/AppManager.js:29-34
Description: Request body fields use cryptic abbreviated names: usr, eml, pwd, c_id, cc.
             Local variables u, e, p, cid, cc shadow the meaning throughout the handler.
Impact: Onboarding cost; obscures intent and makes code review harder.
Recommendation: Use descriptive names in both the API contract (name, email, courseId,
                cardNumber) and internal variables. See playbook T14.

================================
Total: 11 findings
================================
