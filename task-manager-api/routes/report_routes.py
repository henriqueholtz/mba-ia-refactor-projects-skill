from flask import Blueprint, request
from controllers import report_controller, category_controller

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return report_controller.summary()


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    return report_controller.user_report(user_id)


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    return category_controller.get_all()


@report_bp.route('/categories', methods=['POST'])
def create_category():
    return category_controller.create(request.get_json())


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    return category_controller.update(cat_id, request.get_json())


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    return category_controller.delete(cat_id)
