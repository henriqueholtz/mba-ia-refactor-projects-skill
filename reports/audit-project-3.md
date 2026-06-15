================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Files:   11 analyzed | ~560 lines of code

Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] Hardcoded Credentials / Secrets (AP-02)
File: app.py:13, services/notification_service.py:9-10
Description: app.py:13 hardcodes SECRET_KEY = 'super-secret-key-123' directly in
             source code. notification_service.py:9-10 hardcodes SMTP credentials
             (email_user = 'taskmanager@gmail.com', email_password = 'senha123').
             Neither value is loaded from environment variables or a config file.
Impact: Credentials committed to source control are permanently compromised.
        Any repository clone or leak exposes the SMTP password and the Flask session
        signing key, enabling session forgery and unauthorized email access.
Recommendation: Move all secrets to environment variables and load them via python-dotenv
                (already in requirements.txt). Create a config module that reads
                os.environ and raises on missing required values.

[CRITICAL] Weak Password Hashing (AP-04)
File: models/user.py:29,32 | models/user.py:17-25 (to_dict exposes hash)
Description: set_password() and check_password() use hashlib.md5 — a cryptographically
             broken, unsalted hash. models/user.py:29: self.password = hashlib.md5(pwd.encode()).hexdigest()
             Additionally, to_dict() at models/user.py:17-25 returns the 'password' field,
             exposing the hash on every API call that serializes a User (e.g. login response
             at user_routes.py:208 returns user.to_dict()).
Impact: MD5 hashes are reversible via rainbow tables in seconds. The hash is also leaked
        in API responses, giving attackers both the algorithm and the value to crack offline.
Recommendation: Replace MD5 with bcrypt or werkzeug.security (generate_password_hash /
                check_password_hash). Remove 'password' from to_dict(). See AP-04.

[CRITICAL] Fake / Unauthenticated Auth Token + Debug in Production (AP-08)
File: routes/user_routes.py:210, app.py:34
Description: The login endpoint at user_routes.py:210 returns
             'token': 'fake-jwt-token-' + str(user.id) — a predictable, unverified
             token that any caller can forge. app.py:34 runs with debug=True in production
             (app.run(debug=True)).
Impact: The token provides no actual authorization guarantee; any authenticated route
        relying on it can be trivially bypassed. debug=True exposes an interactive
        debugger (Werkzeug PIN bypass) over the network — equivalent to remote code execution.
Recommendation: Implement real JWT (PyJWT or flask-jwt-extended). Move debug=True behind
                an env-var guard (DEBUG=os.environ.get('FLASK_DEBUG', 'false') == 'true').

[HIGH] Business Logic in Routes — No Controller Layer (AP-05)
File: routes/task_routes.py:12-299, routes/user_routes.py:10-211,
      routes/report_routes.py:12-223
Description: Every route handler performs input validation, database queries, business
             computations (overdue logic, completion rates, per-user productivity stats),
             and response shaping directly inline. For example, task_routes.py:13-63
             fetches all tasks, decides overdue status, resolves user and category names,
             and builds the response dict — all within the route function. No controller
             or service layer orchestrates this; routes/report_routes.py also owns
             categories CRUD (unrelated to reporting).
Impact: Logic is not reusable or unit-testable without spinning up HTTP. Adding new
        behaviour (e.g. caching, permissions) requires touching every route.
Recommendation: Extract business logic into controllers/ (one per domain: TaskController,
                UserController, CategoryController, ReportController). Routes become thin
                dispatchers that call controller methods. See AP-05 and playbook.

[HIGH] N+1 Queries (AP-06)
File: routes/task_routes.py:42-48, routes/user_routes.py:22,
      routes/report_routes.py:56-68
Description: GET /tasks (task_routes.py:42-48) fires one User.query.get(t.user_id) and
             one Category.query.get(t.category_id) per task row — 1 + 2N queries for N
             tasks. GET /users (user_routes.py:22) calls len(u.tasks) per user, triggering
             a lazy-load SELECT per user. report_routes.py:56-68 runs Task.query.filter_by(user_id=u.id)
             inside a loop over all users — 1 + N queries.
Impact: On 100 tasks/users, GET /tasks fires 201 queries. Performance degrades
        linearly; pages time out under real load.
Recommendation: Use SQLAlchemy eager loading (joinedload / selectinload) or a single
                JOIN query. Replace per-row User.query.get() with a pre-fetched dict.
                See AP-06.

[HIGH] Global Mutable State in NotificationService (AP-07)
File: services/notification_service.py:6-7
Description: NotificationService.__init__ initialises self.notifications = [] as
             instance state, and the service is presumably instantiated once at module
             level or per-import. Under a multi-worker/multi-threaded WSGI server this
             list accumulates notifications across all requests and users, leading to data
             leaks between user sessions and unbounded memory growth.
Impact: Notifications from one user's session are visible to another's
        (get_notifications returns any matching user_id from a shared list);
        memory grows indefinitely without eviction.
Recommendation: Remove the in-process list; persist notifications to the DB or use a
                proper message queue. Instantiate the service per-request or inject it.

[MEDIUM] Pervasive Deprecated API Usage (AP-10)
File: models/user.py:14, models/task.py:15-16, routes/task_routes.py:31,
      routes/user_routes.py:5, routes/report_routes.py:35, seed.py:66-76
Description: datetime.utcnow() is used in 10+ locations across models, routes, and seed.
             It was deprecated in Python 3.12 (PEP 615) in favour of
             datetime.now(timezone.utc). All datetime columns use default=datetime.utcnow
             (a callable reference to the deprecated function).
Impact: Code will raise DeprecationWarning on Python 3.12+ and break on future
        Python versions. The values produced are also timezone-naive, making
        comparisons with timezone-aware datetimes ambiguous.
Recommendation: Replace all datetime.utcnow() calls with datetime.now(timezone.utc).
                Update column defaults to default=lambda: datetime.now(timezone.utc).

[MEDIUM] Duplicated Overdue Logic (AP-12)
File: routes/task_routes.py:30-39, routes/task_routes.py:71-80,
      routes/task_routes.py:283-287, routes/user_routes.py:171-180,
      routes/report_routes.py:33-44, models/task.py:50-60
Description: The "is this task overdue?" logic (compare due_date to utcnow(), check
             status not in ['done','cancelled']) is copy-pasted at least 6 times across
             routes and models. models/task.py:50-60 already defines is_overdue() but
             the routes never call it — they re-implement the same 6-line block inline.
Impact: Any change to the overdue definition (e.g. adding 'archived' to the exempt
        statuses) must be applied in 6 places; drift will silently produce inconsistencies.
Recommendation: Use the existing Task.is_overdue() method everywhere. Remove inline
                duplicates. See AP-12.

[MEDIUM] Dead Code / Unused Imports and Dependencies (AP-15)
File: requirements.txt:4-6, app.py:7, routes/task_routes.py:7,
      routes/user_routes.py:6, utils/helpers.py:2-6
Description: Three dependencies declared in requirements.txt are never imported anywhere:
             marshmallow==3.20.1 (declared, never used), requests==2.31.0 (unused),
             python-dotenv==1.0.0 (unused — no load_dotenv() call exists anywhere).
             In source: app.py:7 imports os, sys, json (unused); task_routes.py:7 imports
             json, os, sys, time (none used); user_routes.py:6 imports json (unused);
             utils/helpers.py:2-6 imports os, json, sys, math (all unused).
Impact: Misleads maintainers, inflates the attack surface, and wastes install time.
        python-dotenv being unused means no .env file is ever loaded — secrets cannot
        be configured via environment even if someone adds them.
Recommendation: Remove unused deps from requirements.txt. Clean up unused imports.
                Add load_dotenv() call before config is read (or remove the dependency).

[LOW] Magic Numbers and Strings (AP-13)
File: routes/task_routes.py:96-100,110,113, routes/user_routes.py:64,71,
      routes/report_routes.py:129, utils/helpers.py:64,84
Description: Validation literals are scattered inline: title length bounds (3, 200),
             priority range (1-5), password minimum length (4), and valid status/role
             sets are redeclared per route handler. utils/helpers.py:110-116 defines
             named constants (MAX_TITLE_LENGTH, MIN_TITLE_LENGTH, VALID_STATUSES, etc.)
             but they are never imported or used in the routes.
Impact: If the minimum password length changes, every route and helper that encodes 4
        must be found and updated; inconsistencies are easy to miss.
Recommendation: Import and use the constants already defined in utils/helpers.py. Remove
                inline literals.

[LOW] Poor Naming / Single-Letter Variables (AP-14)
File: routes/task_routes.py:17 (t), routes/user_routes.py:14 (u),
      routes/report_routes.py:159 (c), models/category.py:14 (d)
Description: Loop variables t (task), u (user), c (category), and local dict d are used
             throughout route handlers and model methods. While somewhat idiomatic in
             Python one-liners, they obscure meaning across 20-60 line functions.
Impact: Reduces readability during maintenance and code review.
Recommendation: Use descriptive names (task, user, category, result) consistently.

================================
Total: 11 findings
================================
