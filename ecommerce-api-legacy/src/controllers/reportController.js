const reportModel = require('../models/reportModel');

async function financialReport(req, res, next) {
  try {
    const rows = await reportModel.getFinancialData();

    const byCourse = {};
    for (const row of rows) {
      if (!byCourse[row.courseId]) {
        byCourse[row.courseId] = { course: row.title, revenue: 0, students: [] };
      }
      if (row.studentName) {
        if (row.status === 'PAID') byCourse[row.courseId].revenue += row.amount;
        byCourse[row.courseId].students.push({ student: row.studentName, paid: row.amount || 0 });
      }
    }

    res.json(Object.values(byCourse));
  } catch (err) {
    next(err);
  }
}

module.exports = { financialReport };
