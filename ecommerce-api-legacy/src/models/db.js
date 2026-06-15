const sqlite3 = require('sqlite3').verbose();
const config = require('../config');

const db = new sqlite3.Database(config.dbPath);

const get = (sql, params = []) =>
  new Promise((resolve, reject) =>
    db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)))
  );

const all = (sql, params = []) =>
  new Promise((resolve, reject) =>
    db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)))
  );

const run = (sql, params = []) =>
  new Promise((resolve, reject) =>
    db.run(sql, params, function (err) {
      if (err) return reject(err);
      resolve({ lastID: this.lastID, changes: this.changes });
    })
  );

const serialize = (fn) =>
  new Promise((resolve, reject) => {
    db.serialize(() => {
      try { fn(); resolve(); } catch (e) { reject(e); }
    });
  });

module.exports = { db, get, all, run, serialize };
