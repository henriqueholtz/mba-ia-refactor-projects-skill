const ADMIN_TOKEN = process.env.ADMIN_TOKEN;
if (!ADMIN_TOKEN) throw new Error('ADMIN_TOKEN env var is required');

module.exports = {
  port: parseInt(process.env.PORT || '3000', 10),
  dbPath: process.env.DB_PATH || ':memory:',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  smtpUser: process.env.SMTP_USER || '',
  adminToken: ADMIN_TOKEN,

  VISA_PREFIX: '4',
  BCRYPT_ROUNDS: 12,
};
