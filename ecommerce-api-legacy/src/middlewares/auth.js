const config = require('../config');

function requireAdmin(req, res, next) {
  const authHeader = req.headers['authorization'] || '';
  const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;
  if (!token || token !== config.adminToken) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
}

module.exports = { requireAdmin };
