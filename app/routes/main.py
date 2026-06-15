from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    request,
    url_for,
    current_app
)
from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from app.models.book import Book, PhysicalBook, DigitalBook, Category
from app.models.user import User
from app.models.borrow import BorrowRequest, BorrowHistory


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    newest = Book.query.options(
        joinedload(Book.author),
        joinedload(Book.category)
    ).order_by(
        desc(Book.created_at)
    ).limit(8).all()

    popular = PhysicalBook.query.options(
        joinedload(PhysicalBook.author),
        joinedload(PhysicalBook.category)
    ).order_by(
        desc(PhysicalBook.borrow_count)
    ).limit(8).all()

    categories = Category.query.order_by(
        Category.name.asc()
    ).limit(12).all()

    stats = {
        "books": Book.query.count(),
        "users": User.query.filter_by(role=User.ROLE_USER).count(),
        "borrows": BorrowHistory.query.count(),
        "categories": Category.query.count(),
        "physical_books": PhysicalBook.query.count(),
        "digital_books": DigitalBook.query.count(),
        "active_borrows": BorrowHistory.query.filter_by(status="Borrowed").count(),
        "pending_requests": BorrowRequest.query.filter_by(status="Pending").count()
    }

    from app.models.system import Settings, Announcement
    from app.utils.datetime import now_local
    from sqlalchemy import case, or_

    hero_quote_text_setting = Settings.query.filter_by(key="hero_quote_text").first()
    hero_quote_author_setting = Settings.query.filter_by(key="hero_quote_author").first()
    
    quote_text = hero_quote_text_setting.value if hero_quote_text_setting else "Education is the most powerful weapon which you can use to change the world."
    quote_author = hero_quote_author_setting.value if hero_quote_author_setting else "- Nelson Mandela"

    announcements_enabled_setting = Settings.query.filter_by(key="homepage_announcements_enabled").first()
    announcements_enabled = (announcements_enabled_setting.value == "True") if announcements_enabled_setting else True

    announcements = []
    if announcements_enabled:
        today = now_local().date()
        query = Announcement.query.filter(Announcement.status == "active")
        query = query.filter(
            or_(Announcement.start_date == None, Announcement.start_date <= today),
            or_(Announcement.end_date == None, Announcement.end_date >= today)
        )
        
        priority_order = case(
            (Announcement.priority == "high", 1),
            (Announcement.priority == "medium", 2),
            (Announcement.priority == "low", 3),
            else_=4
        )
        announcements = query.order_by(priority_order, Announcement.created_at.desc()).all()

    return render_template(
        "home.html",
        newest=newest,
        popular=popular,
        categories=categories,
        stats=stats,
        quote_text=quote_text,
        quote_author=quote_author,
        announcements=announcements,
        announcements_enabled=announcements_enabled
    )


@main_bp.route("/robots.txt")
def robots_txt():
    from flask import send_from_directory
    import os
    return send_from_directory(os.path.join(current_app.root_path, "static"), "robots.txt")


@main_bp.route("/sitemap.xml")
def sitemap_xml():
    from flask import send_from_directory
    import os
    return send_from_directory(os.path.join(current_app.root_path, "static"), "sitemap.xml")


@main_bp.route("/maintenance")
def maintenance():
    return render_template("errors/maintenance.html"), 503


@main_bp.route("/emergency-lockdown")
def emergency_lockdown():
    return render_template("errors/lockdown.html"), 503
