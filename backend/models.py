from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(128))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(1024))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_telegram_id = db.Column(db.String(64), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    proof_filename = db.Column(db.String(1024))
    note = db.Column(db.Text)
    status = db.Column(db.String(32), default="pending")  # pending / approved / rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    task = db.relationship("Task", backref="submissions")
