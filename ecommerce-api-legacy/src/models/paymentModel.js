const { run } = require('./db');

const create = async (enrollmentId, amount, status) => {
  const result = await run(
    'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
    [enrollmentId, amount, status]
  );
  return { id: result.lastID, enrollmentId, amount, status };
};

module.exports = { create };
