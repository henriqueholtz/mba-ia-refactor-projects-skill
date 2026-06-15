const bcrypt = require('bcryptjs');
const config = require('../config');
const { get, run } = require('./db');

const findByEmail = (email) =>
  get('SELECT id, name, email FROM users WHERE email = ?', [email]);

const findById = (id) =>
  get('SELECT id, name, email FROM users WHERE id = ?', [id]);

const create = async (name, email, password) => {
  const hash = await bcrypt.hash(password, config.BCRYPT_ROUNDS);
  const result = await run(
    'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
    [name, email, hash]
  );
  return { id: result.lastID, name, email };
};

const remove = (id) =>
  run('DELETE FROM users WHERE id = ?', [id]);

module.exports = { findByEmail, findById, create, remove };
