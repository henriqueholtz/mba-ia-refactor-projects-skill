const { run } = require('./db');

const log = (action) =>
  run("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [action]);

module.exports = { log };
