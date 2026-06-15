from flask import jsonify
from database import db
from models.category import Category
from models.task import Task
from utils.helpers import DEFAULT_COLOR


def get_all():
    categories = Category.query.all()
    result = []
    for category in categories:
        cat_data = category.to_dict()
        cat_data['task_count'] = Task.query.filter_by(category_id=category.id).count()
        result.append(cat_data)
    return jsonify(result), 200


def create(data):
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    name = data.get('name')
    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400

    category = Category(
        name=name,
        description=data.get('description', ''),
        color=data.get('color', DEFAULT_COLOR),
    )

    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        raise e


def update(cat_id, data):
    category = Category.query.get(cat_id)
    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = data['color']

    try:
        db.session.commit()
        return jsonify(category.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        raise e


def delete(cat_id):
    category = Category.query.get(cat_id)
    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Categoria deletada'}), 200
    except Exception as e:
        db.session.rollback()
        raise e
