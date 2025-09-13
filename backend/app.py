import os
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from models import db, User, Task, Submission
import config
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = config.UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()

# Public API: get tasks
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([{"id": t.id, "name": t.name, "link": t.link, "description": t.description} for t in tasks])

# Public API: submit proof
# expects form-data: telegram_id, task_id, note (optional), file (optional)
@app.route("/api/submit", methods=["POST"])
def submit_task():
    telegram_id = request.form.get("telegram_id")
    task_id = request.form.get("task_id")
    note = request.form.get("note", "")
    if not telegram_id or not task_id:
        return jsonify({"error": "telegram_id and task_id required"}), 400
    # ensure user exists
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, username=request.form.get("username"))
        db.session.add(user)
        db.session.commit()

    proof_filename = None
    if 'file' in request.files:
        f = request.files['file']
        if f.filename:
            filename = f"{telegram_id}_{secure_filename(f.filename)}"
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)
            proof_filename = filename

    sub = Submission(user_telegram_id=telegram_id, task_id=int(task_id), proof_filename=proof_filename, note=note)
    db.session.add(sub)
    db.session.commit()

    # Return submission id so bot can forward or admin can view
    return jsonify({"ok": True, "submission_id": sub.id})

# Admin: add task (protected by ADMIN_TOKEN header)
@app.route("/api/admin/tasks/add", methods=["POST"])
def add_task():
    token = request.headers.get("X-ADMIN-TOKEN")
    if token != config.ADMIN_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.json or {}
    name = data.get("name")
    if not name:
        return jsonify({"error":"name required"}), 400
    t = Task(name=name, link=data.get("link"), description=data.get("description"))
    db.session.add(t)
    db.session.commit()
    return jsonify({"ok": True, "task": {"id": t.id, "name": t.name}})

# Admin: list submissions
@app.route("/api/admin/submissions", methods=["GET"])
def list_submissions():
    token = request.headers.get("X-ADMIN-TOKEN")
    if token != config.ADMIN_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    subs = Submission.query.order_by(Submission.submitted_at.desc()).all()
    result = []
    for s in subs:
        result.append({
            "id": s.id,
            "user_telegram_id": s.user_telegram_id,
            "task": {"id": s.task.id, "name": s.task.name},
            "proof_url": f"/api/uploads/{s.proof_filename}" if s.proof_filename else None,
            "note": s.note,
            "status": s.status,
            "submitted_at": s.submitted_at.isoformat()
        })
    return jsonify(result)

# serve uploaded files (admin-only access simple check)
@app.route("/api/uploads/<path:filename>", methods=["GET"])
def uploaded_file(filename):
    token = request.headers.get("X-ADMIN-TOKEN")
    if token != config.ADMIN_TOKEN:
        abort(401)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Admin: change submission status
@app.route("/api/admin/submissions/<int:sub_id>/status", methods=["POST"])
def change_status(sub_id):
    token = request.headers.get("X-ADMIN-TOKEN")
    if token != config.ADMIN_TOKEN:
        return jsonify({"error":"unauthorized"}), 401
    data = request.json or {}
    new_status = data.get("status")
    if new_status not in ("pending","approved","rejected"):
        return jsonify({"error":"invalid status"}), 400
    sub = Submission.query.get_or_404(sub_id)
    sub.status = new_status
    db.session.commit()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
