from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.system import Notification
from app import db

api_bp = Blueprint("api", __name__)


@api_bp.route("/notifications/latest")
@login_required
def latest_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(
        Notification.created_at.desc()
    ).limit(5).all()

    unread_count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()

    return jsonify({
        "success": True,
        "unread_count": unread_count,
        "notifications": [
            {
                "id": notification.id,
                "message": notification.message,
                "type": notification.type,
                "created_at": notification.created_at.strftime("%d %b %Y %H:%M")
                if notification.created_at
                else ""
            }
            for notification in notifications
        ]
    })

@api_bp.route("/notifications/read/<int:notif_id>", methods=["POST"])
@login_required
def mark_notification_read(notif_id):
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Notification not found"}), 404

@api_bp.route("/notifications/read-all", methods=["POST"])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"success": True})
