const { get, all } = require('./db');

const findActiveById = (id) =>
  get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);

const findAll = () =>
  all('SELECT * FROM courses', []);

module.exports = { findActiveById, findAll };
