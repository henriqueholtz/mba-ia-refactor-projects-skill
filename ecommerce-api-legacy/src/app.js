const express = require('express');
const config = require('./config');
const { db } = require('./models/db');
const routes = require('./routes');
const { errorHandler } = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());
app.use(routes);
app.use(errorHandler);

db.serialize(() => {
  db.run("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)");
  db.run("CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
  db.run("CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
  db.run("CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
  db.run("CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)");

  db.run("INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '$2b$12$7R6vHPiRjQlRkh7cqgTxMuugiLnEvDVIbsrI9.5GHbqp22mEAjfaK')");
  db.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
  db.run("INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)");
  db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
});

app.listen(config.port, () => {
  console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
});

module.exports = app;
