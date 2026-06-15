const config = require('../config');
const courseModel = require('../models/courseModel');
const userModel = require('../models/userModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditModel = require('../models/auditModel');

const REQUIRED_FIELDS = ['name', 'email', 'courseId', 'cardNumber'];

async function checkout(req, res, next) {
  try {
    const { name, email, password, courseId, cardNumber } = req.body;

    for (const field of REQUIRED_FIELDS) {
      if (!req.body[field]) return res.status(400).json({ error: `Campo obrigatório: ${field}` });
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return res.status(400).json({ error: 'Formato de email inválido' });
    }

    const parsedCourseId = parseInt(courseId, 10);
    if (isNaN(parsedCourseId)) {
      return res.status(400).json({ error: 'courseId deve ser um número inteiro' });
    }

    const course = await courseModel.findActiveById(parsedCourseId);
    if (!course) return res.status(404).json({ error: 'Curso não encontrado' });

    let user = await userModel.findByEmail(email);
    if (!user) {
      user = await userModel.create(name, email, password || '123456');
    }

    const paymentStatus = cardNumber.startsWith(config.VISA_PREFIX) ? 'PAID' : 'DENIED';
    if (paymentStatus === 'DENIED') return res.status(400).json({ error: 'Pagamento recusado' });

    const enrollment = await enrollmentModel.create(user.id, parsedCourseId);
    await paymentModel.create(enrollment.id, course.price, paymentStatus);
    await auditModel.log(`Checkout curso ${parsedCourseId} por ${user.id}`);

    res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollment.id });
  } catch (err) {
    next(err);
  }
}

module.exports = { checkout };
