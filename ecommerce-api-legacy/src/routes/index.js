const { Router } = require('express');
const { checkout } = require('../controllers/checkoutController');
const { financialReport } = require('../controllers/reportController');
const { deleteUser } = require('../controllers/userController');
const { requireAdmin } = require('../middlewares/auth');

const router = Router();

router.post('/api/checkout', checkout);
router.get('/api/admin/financial-report', requireAdmin, financialReport);
router.delete('/api/users/:id', requireAdmin, deleteUser);

module.exports = router;
