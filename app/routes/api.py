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


# ---------------------------------------------------------------------------
# Student Rankings External API (Authenticated via ApiKey)
# ---------------------------------------------------------------------------

def _cors_response(data, status_code=200):
    resp = jsonify(data)
    resp.status_code = status_code
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key, Authorization"
    return resp


def _validate_api_key():
    from app.models.system import ApiKey
    from app.utils.datetime import now_local

    key_val = request.args.get("api_key") or request.headers.get("X-API-Key")
    if not key_val and request.headers.get("Authorization"):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            key_val = auth_header[7:].strip()

    if not key_val:
        return None, _cors_response({
            "success": False,
            "error": "API Key required. Provide '?api_key=YOUR_KEY' query param or 'X-API-Key' header."
        }, 401)

    api_key = ApiKey.query.filter_by(key=key_val.strip()).first()
    if not api_key:
        return None, _cors_response({
            "success": False,
            "error": "Invalid API Key."
        }, 403)

    if not api_key.is_active:
        return None, _cors_response({
            "success": False,
            "error": "This API Key has been deactivated."
        }, 403)

    # Track usage
    try:
        api_key.last_used_at = now_local()
        api_key.request_count = (api_key.request_count or 0) + 1
        db.session.commit()
    except Exception:
        db.session.rollback()

    return api_key, None


@api_bp.route("/rankings/students", methods=["GET", "OPTIONS"])
def get_students_rankings():
    if request.method == "OPTIONS":
        return _cors_response({"status": "ok"})

    api_key, error_response = _validate_api_key()
    if error_response:
        return error_response

    from app.services.student_ranking_service import get_student_rankings
    limit_arg = request.args.get("limit", type=int)

    data = get_student_rankings(limit=limit_arg)
    data["api_client"] = api_key.name
    return _cors_response(data)


@api_bp.route("/rankings/student/<path:passport_number>", methods=["GET", "OPTIONS"])
def get_single_student_ranking(passport_number):
    if request.method == "OPTIONS":
        return _cors_response({"status": "ok"})

    api_key, error_response = _validate_api_key()
    if error_response:
        return error_response

    from app.services.student_ranking_service import get_student_rankings

    data = get_student_rankings(passport_filter=passport_number)
    data["api_client"] = api_key.name
    status_code = 200 if data.get("found", True) else 404
    return _cors_response(data, status_code=status_code)

