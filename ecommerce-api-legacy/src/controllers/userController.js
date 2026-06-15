const userModel = require('../models/userModel');

async function deleteUser(req, res, next) {
  try {
    const id = parseInt(req.params.id, 10);
    if (isNaN(id)) return res.status(400).json({ error: 'ID deve ser um número inteiro' });

    const user = await userModel.findById(id);
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });

    await userModel.remove(id);
    res.json({ msg: 'Usuário deletado' });
  } catch (err) {
    next(err);
  }
}

module.exports = { deleteUser };
