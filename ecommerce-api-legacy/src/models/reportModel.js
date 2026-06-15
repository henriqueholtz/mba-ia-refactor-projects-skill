const { all } = require('./db');

const getFinancialData = () =>
  all(
    `SELECT c.id AS courseId, c.title,
            u.name AS studentName,
            p.amount, p.status
     FROM courses c
     LEFT JOIN enrollments e ON e.course_id = c.id
     LEFT JOIN users u       ON u.id = e.user_id
     LEFT JOIN payments p    ON p.enrollment_id = e.id`,
    []
  );

module.exports = { getFinancialData };
