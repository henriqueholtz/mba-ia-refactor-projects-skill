function errorHandler(err, req, res, next) { // eslint-disable-line no-unused-vars
  console.error(err.stack);
  const status = err.status || 500;
  res.status(status).json({ error: err.message || 'Internal Server Error' });
}

module.exports = { errorHandler };
