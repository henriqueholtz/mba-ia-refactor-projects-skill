from flask import Blueprint, request
from controllers import task_controller

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return task_controller.get_all()


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return task_controller.get_one(task_id)


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    return task_controller.create(request.get_json())


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    return task_controller.update(task_id, request.get_json())


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    return task_controller.delete(task_id)


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    return task_controller.search(
        query_str=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', ''),
    )


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return task_controller.stats()
