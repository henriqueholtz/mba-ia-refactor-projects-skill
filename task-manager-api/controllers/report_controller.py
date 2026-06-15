from flask import jsonify
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import joinedload
from utils.helpers import calculate_percentage


def _now():
    return datetime.now(timezone.utc)


def _is_overdue(task):
    return task.is_overdue()


def summary():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    priority_counts = {
        'critical': Task.query.filter_by(priority=1).count(),
        'high': Task.query.filter_by(priority=2).count(),
        'medium': Task.query.filter_by(priority=3).count(),
        'low': Task.query.filter_by(priority=4).count(),
        'minimal': Task.query.filter_by(priority=5).count(),
    }

    now = _now()
    all_tasks = Task.query.all()
    overdue_list = [
        {
            'id': task.id,
            'title': task.title,
            'due_date': str(task.due_date),
            'days_overdue': (now - task.due_date.replace(tzinfo=timezone.utc)).days
            if task.due_date.tzinfo is None
            else (now - task.due_date).days,
        }
        for task in all_tasks
        if task.is_overdue()
    ]

    seven_days_ago = now - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done',
        Task.updated_at >= seven_days_ago,
    ).count()

    # Single query for all users + their tasks to avoid N+1
    users = User.query.options(joinedload(User.tasks)).all()
    user_stats = []
    for user in users:
        total = len(user.tasks)
        completed = sum(1 for task in user.tasks if task.status == 'done')
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total),
        })

    return jsonify({
        'generated_at': str(now),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': priority_counts,
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }), 200


def user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()

    total = len(tasks)
    done = pending = in_progress = cancelled = overdue = high_priority = 0

    for task in tasks:
        if task.status == 'done':
            done += 1
        elif task.status == 'pending':
            pending += 1
        elif task.status == 'in_progress':
            in_progress += 1
        elif task.status == 'cancelled':
            cancelled += 1

        if task.priority <= 2:
            high_priority += 1

        if task.is_overdue():
            overdue += 1

    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': calculate_percentage(done, total),
        },
    }), 200
