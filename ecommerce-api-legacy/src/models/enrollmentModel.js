const { run } = require('./db');

const create = async (userId, courseId) => {
  const result = await run(
    'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
    [userId, courseId]
  );
  return { id: result.lastID, userId, courseId };
};

module.exports = { create };
