"""Library analytics based on real database models."""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from sqlalchemy import case, desc, func

from app import db
from app.models.user import User
from app.models.faculty import Faculty
from app.models.book import Book, PhysicalBook, DigitalBook, ReadingProgress, BookRead
from app.models.borrow import BorrowRequest, BorrowHistory, FavoriteBook
from app.models.activity import ActivityLog
from app.models.system import Review
from app.models.competition import CompetitionCertificate, QuizAttempt, ReadingCompetition
from app.utils.datetime import now_local


def _competition_score_for_user(user_id: int) -> float:
    try:
        from app.services.ranking_service import get_competition_best_score

        return get_competition_best_score(user_id)
    except Exception:
        return 0.0


def _month_key(dt):
    if not dt:
        return None
    return dt.strftime("%Y-%m")


def _reader_score_row(
    borrows,
    pages_read,
    completed,
    reviews,
    favorites,
    competition_pct=0.0,
):
    """Best reader: 40% reading, 30% borrow, 20% competition, 10% reviews/favorites."""
    reading_part = min(100, (pages_read or 0) * 0.5 + (completed or 0) * 15)
    borrow_part = min(100, (borrows or 0) * 12)
    review_part = min(100, (reviews or 0) * 8 + (favorites or 0) * 4)
    competition_part = min(100, competition_pct or 0)

    return round(
        reading_part * 0.40
        + borrow_part * 0.30
        + competition_part * 0.20
        + review_part * 0.10,
        1,
    )


def _book_popularity_score(borrows, favorites, reviews, rating, reads_or_borrows):
    return round(
        (borrows or 0) * 4
        + (favorites or 0) * 2
        + (reviews or 0) * 2
        + (reads_or_borrows or 0) * 1.5
        + (rating or 0) * 2,
        1,
    )


def build_library_analytics():
    now = now_local()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    six_months_ago = now - timedelta(days=180)

    overdue_borrows = BorrowHistory.query.filter(
        BorrowHistory.status == "Borrowed",
        BorrowHistory.return_date < now,
    ).all()
    for borrow in overdue_borrows:
        borrow.status = "Overdue"
    if overdue_borrows:
        db.session.commit()

    physical_count = Book.query.filter_by(book_type="physical").count()
    digital_count = Book.query.filter_by(book_type="digital").count()

    overview = {
        "total_users": User.query.count(),
        "total_books": Book.query.count(),
        "physical_books": physical_count,
        "digital_books": digital_count,
        "active_borrowings": BorrowHistory.query.filter(
            BorrowHistory.status.in_(["Borrowed", "Overdue"])
        ).count(),
        "pending_requests": BorrowRequest.query.filter_by(status="Pending").count(),
        "overdue": BorrowHistory.query.filter_by(status="Overdue").count(),
        "users_week": User.query.filter(User.created_at >= week_ago).count(),
        "borrows_week": BorrowHistory.query.filter(BorrowHistory.borrowed_at >= week_ago).count(),
    }

    borrow_counts = dict(
        db.session.query(BorrowHistory.user_id, func.count(BorrowHistory.id))
        .group_by(BorrowHistory.user_id)
        .all()
    )
    review_counts = dict(
        db.session.query(Review.user_id, func.count(Review.id)).group_by(Review.user_id).all()
    )
    favorite_counts = dict(
        db.session.query(FavoriteBook.user_id, func.count(FavoriteBook.id))
        .group_by(FavoriteBook.user_id)
        .all()
    )

    competition_attempt_counts = dict(
        db.session.query(
            QuizAttempt.user_id,
            func.count(QuizAttempt.id),
        )
        .filter(QuizAttempt.status == QuizAttempt.STATUS_COMPLETED)
        .group_by(QuizAttempt.user_id)
        .all()
    )

    certificate_counts = dict(
        db.session.query(CompetitionCertificate.user_id, func.count(CompetitionCertificate.id))
        .group_by(CompetitionCertificate.user_id)
        .all()
    )

    medal_rows = db.session.query(
        QuizAttempt.user_id,
        func.sum(case((QuizAttempt.medal == "gold", 1), else_=0)).label("gold"),
        func.sum(case((QuizAttempt.medal == "silver", 1), else_=0)).label("silver"),
        func.sum(case((QuizAttempt.medal == "bronze", 1), else_=0)).label("bronze"),
    ).filter(QuizAttempt.status == QuizAttempt.STATUS_COMPLETED).group_by(QuizAttempt.user_id).all()

    medal_counts = {
        user_id: {
            "gold": int(gold or 0),
            "silver": int(silver or 0),
            "bronze": int(bronze or 0),
        }
        for user_id, gold, silver, bronze in medal_rows
    }

    champion_counts = dict(
        db.session.query(
            CompetitionCertificate.user_id,
            func.count(CompetitionCertificate.id),
        )
        .filter(CompetitionCertificate.position == 1)
        .group_by(CompetitionCertificate.user_id)
        .all()
    )

    progress_stats = db.session.query(
        ReadingProgress.user_id,
        func.coalesce(func.sum(ReadingProgress.current_page), 0),
        func.count(ReadingProgress.id),
    ).group_by(ReadingProgress.user_id).all()

    pages_by_user = {uid: int(pages or 0) for uid, pages, _ in progress_stats}

    completed_by_user = dict(
        db.session.query(
            ReadingProgress.user_id,
            func.count(ReadingProgress.id),
        )
        .join(DigitalBook, DigitalBook.id == ReadingProgress.book_id)
        .filter(
            DigitalBook.pages.isnot(None),
            DigitalBook.pages > 0,
            ReadingProgress.current_page >= DigitalBook.pages,
        )
        .group_by(ReadingProgress.user_id)
        .all()
    )

    users = User.query.filter_by(role=User.ROLE_USER).all()
    reader_rows = []
    for user in users:
        reader_rows.append(
            {
                "user_id": user.id,
                "name": user.fullname,
                "username": user.username,
                "faculty": user.faculty_display or "—",
                "group": user.group_name or "—",
                "score": _reader_score_row(
                    borrow_counts.get(user.id, 0),
                    pages_by_user.get(user.id, 0),
                    completed_by_user.get(user.id, 0),
                    review_counts.get(user.id, 0),
                    favorite_counts.get(user.id, 0),
                    _competition_score_for_user(user.id),
                ),
                "borrows": borrow_counts.get(user.id, 0),
                "pages_read": pages_by_user.get(user.id, 0),
                "favorites": favorite_counts.get(user.id, 0),
                "reviews": review_counts.get(user.id, 0),
                "competitions_joined": competition_attempt_counts.get(user.id, 0),
                "champion_positions": champion_counts.get(user.id, 0),
                "last_active": user.last_activity_at.strftime("%d %b %Y") if user.last_activity_at else "—",
            }
        )

    reader_rows.sort(key=lambda row: row["score"], reverse=True)
    top_readers_overall = reader_rows[:10]

    borrow_status_rows = db.session.query(
        BorrowHistory.user_id,
        func.count(BorrowHistory.id),
        func.sum(case((BorrowHistory.status == "Returned", 1), else_=0)).label("returned"),
        func.sum(case((BorrowHistory.status.in_(["Borrowed", "Overdue"]), 1), else_=0)).label("active"),
        func.sum(case((BorrowHistory.status == "Overdue", 1), else_=0)).label("overdue"),
    ).group_by(BorrowHistory.user_id).all()

    borrow_status_counts = {
        user_id: {
            "approved_requests": int(total or 0),
            "returned_books": int(returned or 0),
            "active_borrowings": int(active or 0),
            "overdue_books": int(overdue or 0),
        }
        for user_id, total, returned, active, overdue in borrow_status_rows
    }

    borrower_rows = []
    for row in reader_rows:
        borrower = borrow_status_counts.get(row["user_id"], {})
        approved_requests = borrower.get("approved_requests", 0)
        returned_books = borrower.get("returned_books", 0)
        active_borrowings = borrower.get("active_borrowings", 0)
        overdue_books = borrower.get("overdue_books", 0)
        borrower_rows.append(
            {
                "user_id": row["user_id"],
                "name": row["name"],
                "faculty": row["faculty"],
                "group": row["group"],
                "approved_requests": approved_requests,
                "returned_books": returned_books,
                "active_borrowings": active_borrowings,
                "overdue_books": overdue_books,
                "borrow_score": round(
                    approved_requests * 4
                    + returned_books * 2
                    - overdue_books * 3
                    + active_borrowings * 1.5,
                    1,
                ),
            }
        )

    borrower_rows.sort(key=lambda row: row["borrow_score"], reverse=True)
    top_borrowers_overall = borrower_rows[:10]

    competition_rows = []
    for row in reader_rows:
        attempts = competition_attempt_counts.get(row["user_id"], 0)
        certificates = certificate_counts.get(row["user_id"], 0)
        medals = medal_counts.get(row["user_id"], {"gold": 0, "silver": 0, "bronze": 0})
        champion_positions = champion_counts.get(row["user_id"], 0)
        competition_score = round(
            attempts * 3
            + certificates * 5
            + medals["gold"] * 6
            + medals["silver"] * 4
            + medals["bronze"] * 2
            + champion_positions * 8,
            1,
        )
        competition_rows.append(
            {
                "user_id": row["user_id"],
                "name": row["name"],
                "faculty": row["faculty"],
                "group": row["group"],
                "competitions_joined": attempts,
                "certificates": certificates,
                "gold_medals": medals["gold"],
                "silver_medals": medals["silver"],
                "bronze_medals": medals["bronze"],
                "champion_positions": champion_positions,
                "competition_score": competition_score,
            }
        )

    competition_rows.sort(key=lambda row: row["competition_score"], reverse=True)
    top_competition_leaders = competition_rows[:10]

    by_faculty: dict[str, list] = defaultdict(list)
    by_group: dict[str, list] = defaultdict(list)
    for row in reader_rows:
        by_faculty[row["faculty"]].append(row)
        by_group[row["group"]].append(row)

    top_readers_by_faculty = []
    for faculty_name, rows in by_faculty.items():
        if faculty_name == "—":
            continue
        top_readers_by_faculty.append(
            {
                "name": faculty_name,
                "score": sum(r["score"] for r in rows[:5]),
                "readers": rows[:5],
            }
        )
    top_readers_by_faculty.sort(key=lambda item: item["score"], reverse=True)

    top_readers_by_group = []
    for group_name, rows in by_group.items():
        if group_name == "—":
            continue
        top_readers_by_group.append(
            {
                "name": group_name,
                "score": sum(r["score"] for r in rows[:5]),
                "readers": rows[:5],
            }
        )
    top_readers_by_group.sort(key=lambda item: item["score"], reverse=True)

    faculty_rankings = []
    faculties = Faculty.query.order_by(Faculty.name.asc()).all()
    for faculty in faculties:
        faculty_user_ids = [
            u.id for u in User.query.filter_by(faculty_id=faculty.id, role=User.ROLE_USER).all()
        ]
        if not faculty_user_ids:
            legacy_users = User.query.filter(
                User.role == User.ROLE_USER,
                User.faculty == faculty.name,
            ).all()
            faculty_user_ids = [u.id for u in legacy_users]

        borrows = (
            BorrowHistory.query.filter(BorrowHistory.user_id.in_(faculty_user_ids)).count()
            if faculty_user_ids
            else 0
        )
        reviews = (
            Review.query.filter(Review.user_id.in_(faculty_user_ids)).count()
            if faculty_user_ids
            else 0
        )
        pages = sum(pages_by_user.get(uid, 0) for uid in faculty_user_ids)
        score = round(borrows * 2 + reviews * 1.5 + pages * 0.03, 1)
        faculty_rankings.append(
            {
                "name": faculty.name,
                "score": score,
                "borrows": borrows,
                "active_users": len(faculty_user_ids),
                "trend": "up" if borrows > 0 else "stable",
            }
        )
    faculty_rankings.sort(key=lambda item: item["score"], reverse=True)

    group_rankings = []
    group_names = (
        db.session.query(User.group_name)
        .filter(
            User.role == User.ROLE_USER,
            User.group_name.isnot(None),
            User.group_name != "",
        )
        .distinct()
        .all()
    )
    for (group_name,) in group_names:
        group_users = User.query.filter_by(role=User.ROLE_USER, group_name=group_name).all()
        user_ids = [u.id for u in group_users]
        borrows = BorrowHistory.query.filter(BorrowHistory.user_id.in_(user_ids)).count()
        pages = sum(pages_by_user.get(uid, 0) for uid in user_ids)
        score = round(borrows * 2 + pages * 0.04, 1)
        group_rankings.append(
            {
                "name": group_name,
                "score": score,
                "borrows": borrows,
                "active_users": len(user_ids),
            }
        )
    group_rankings.sort(key=lambda item: item["score"], reverse=True)

    physical_popular = []
    for book in PhysicalBook.query.all():
        favs = FavoriteBook.query.filter_by(book_id=book.id).count()
        revs = Review.query.filter_by(book_id=book.id).count()
        physical_popular.append(
            {
                "id": book.id,
                "title": book.title,
                "author": book.author.fullname if book.author else "Unknown",
                "category": book.category.name if book.category else "Uncategorized",
                "score": _book_popularity_score(
                    book.borrow_count or 0,
                    favs,
                    revs,
                    book.rating or 0,
                    book.borrow_count or 0,
                ),
                "borrows": book.borrow_count or 0,
                "request_count": book.request_count if hasattr(book, "request_count") else 0,
                "favorites": favs,
                "reviews": revs,
                "rating": round(book.rating or 0, 1),
            }
        )
    physical_popular.sort(key=lambda item: item["score"], reverse=True)

    # Pre-compute unique reader counts per digital book in one query (avoid N+1)
    reader_count_rows = (
        db.session.query(BookRead.book_id, func.count(func.distinct(BookRead.user_id)).label("cnt"))
        .group_by(BookRead.book_id)
        .all()
    )
    reader_counts_map = {book_id: cnt for book_id, cnt in reader_count_rows}

    digital_popular = []
    for book in DigitalBook.query.all():
        favs = FavoriteBook.query.filter_by(book_id=book.id).count()
        revs = Review.query.filter_by(book_id=book.id).count()
        readers = reader_counts_map.get(book.id, 0)
        digital_popular.append(
            {
                "id": book.id,
                "title": book.title,
                "author": book.author.fullname if book.author else "Unknown",
                "category": book.category.name if book.category else "Uncategorized",
                "score": _book_popularity_score(
                    0,
                    favs,
                    revs,
                    book.rating or 0,
                    readers,
                ),
                "views": book.view_count or 0,
                "reads": readers,
                "favorites": favs,
                "reviews": revs,
                "rating": round(book.rating or 0, 1),
            }
        )
    digital_popular.sort(key=lambda item: item["score"], reverse=True)

    engagement = {
        "most_reviewed": _books_by_metric("reviews"),
        "most_favorited": _books_by_metric("favorites"),
        "most_read_digital": _most_read_digital(8),
        "most_borrowed_physical": physical_popular[:8],
    }

    trends = {
        "borrow_months": _monthly_counts(
            BorrowHistory.borrowed_at, six_months_ago, now
        ),
        "reading_months": _monthly_counts(
            ReadingProgress.updated_at, six_months_ago, now
        ),
        "registration_months": _monthly_counts(
            User.created_at, six_months_ago, now
        ),
    }

    return {
        "overview": overview,
        "top_readers_overall": top_readers_overall,
        "top_borrowers_overall": top_borrowers_overall,
        "top_competition_leaders": top_competition_leaders,
        "top_readers_by_faculty": top_readers_by_faculty[:8],
        "top_readers_by_group": top_readers_by_group[:8],
        "faculty_rankings": faculty_rankings[:10],
        "group_rankings": group_rankings[:10],
        "popular_physical": physical_popular[:10],
        "popular_digital": digital_popular[:10],
        "engagement": engagement,
        "trends": trends,
        "generated_at": now,
    }


def _most_read_digital(limit: int = 8):
    """Return top digital books ordered by unique reader count."""
    reader_subq = (
        db.session.query(
            BookRead.book_id,
            func.count(func.distinct(BookRead.user_id)).label("reader_count"),
        )
        .group_by(BookRead.book_id)
        .subquery()
    )
    rows = (
        db.session.query(
            DigitalBook.id,
            DigitalBook.title,
            func.coalesce(reader_subq.c.reader_count, 0).label("reader_count"),
        )
        .outerjoin(reader_subq, reader_subq.c.book_id == DigitalBook.id)
        .order_by(desc("reader_count"))
        .limit(limit)
        .all()
    )
    return [{"id": r[0], "title": r[1], "metric": r[2]} for r in rows]


def _books_by_metric(metric: str):
    if metric == "reviews":
        rows = (
            db.session.query(Book.id, Book.title, func.count(Review.id).label("metric"))
            .join(Review, Review.book_id == Book.id)
            .group_by(Book.id, Book.title)
            .order_by(desc("metric"))
            .limit(8)
            .all()
        )
    else:
        rows = (
            db.session.query(Book.id, Book.title, func.count(FavoriteBook.id).label("metric"))
            .join(FavoriteBook, FavoriteBook.book_id == Book.id)
            .group_by(Book.id, Book.title)
            .order_by(desc("metric"))
            .limit(8)
            .all()
        )
    return [{"id": r[0], "title": r[1], "metric": r[2]} for r in rows]


def _monthly_counts(date_column, start_dt, end_dt):
    month_bucket = func.date_trunc("month", date_column)
    rows = (
        db.session.query(month_bucket, func.count())
        .filter(date_column >= start_dt, date_column <= end_dt)
        .group_by(month_bucket)
        .order_by(month_bucket)
        .all()
    )
    buckets: dict[str, int] = {}
    for dt, count in rows:
        key = _month_key(dt)
        if key:
            buckets[key] = count

    months = []
    cursor = start_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    while cursor <= end_dt:
        key = cursor.strftime("%Y-%m")
        months.append({"label": cursor.strftime("%b %Y"), "value": buckets.get(key, 0)})
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)
    return months[-6:]


def build_admin_dashboard_context():
    """Lightweight admin home — no analytics (see statistics page)."""
    # Build a compact dashboard context with overview, competition and recent activity
    now = now_local()
    data = build_library_analytics()
    overview = data.get("overview", {})

    # Competition stats
    from app.models.competition import ReadingCompetition, QuizAttempt, CompetitionCertificate

    active_competitions = (
        ReadingCompetition.query.filter(
            ReadingCompetition.status == ReadingCompetition.STATUS_PUBLISHED,
            ReadingCompetition.start_date <= now,
            ReadingCompetition.end_date >= now,
        ).count()
    )

    participants = (
        db.session.query(func.count(func.distinct(QuizAttempt.user_id)))
        .filter(QuizAttempt.status == QuizAttempt.STATUS_COMPLETED)
        .scalar()
        or 0
    )

    certificates_issued = CompetitionCertificate.query.count()

    avg_score = (
        db.session.query(func.avg(QuizAttempt.percentage))
        .filter(QuizAttempt.status == QuizAttempt.STATUS_COMPLETED)
        .scalar()
        or 0
    )

    completed_attempts = (
        QuizAttempt.query.filter(QuizAttempt.status == QuizAttempt.STATUS_COMPLETED).count()
    )
    passed_attempts = (
        QuizAttempt.query.filter(QuizAttempt.status == QuizAttempt.STATUS_COMPLETED, QuizAttempt.percentage >= 60).count()
    )
    pass_rate = (passed_attempts / completed_attempts * 100) if completed_attempts else 0

    # Most borrowed books and top readers (library analytics)
    most_borrowed = data.get("popular_physical", [])[:5]
    most_active_readers = data.get("top_readers_overall", [])[:5]

    # Recent activity feed
    recent_activities = (
        ActivityLog.query.order_by(desc(ActivityLog.created_at)).limit(10).all()
    )

    # Provide a lightweight `stats` mapping for templates that expect the older keys
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    stats = {
        "users": overview.get("total_users", 0),
        "students": User.query.filter_by(role=User.ROLE_USER).count(),
        "librarians": User.query.filter_by(role=User.ROLE_LIBRARIAN).count(),
        "admins": User.query.filter_by(role=User.ROLE_ADMIN).count(),
        "blocked_users": User.query.filter_by(is_blocked=True).count(),
        # number of distinct users with unpaid fines
        "users_with_unpaid_fines": (
            db.session.query(func.count(func.distinct(BorrowHistory.user_id)))
            .filter(BorrowHistory.final_fine_amount > 0, BorrowHistory.fine_status == "unpaid")
            .scalar() or 0
        ),
        "books": overview.get("total_books", 0),
        "borrowed": overview.get("active_borrowings", 0),
        "overdue": overview.get("overdue", 0),
        "pending_requests": overview.get("pending_requests", 0),
        "early_return_candidates": BorrowHistory.query.filter(
            BorrowHistory.status == "Borrowed",
            BorrowHistory.return_date > now,
        ).count(),
        "users_week": overview.get("users_week", 0),
        "borrows_week": overview.get("borrows_week", 0),
        "queued_requests": BorrowRequest.query.filter_by(status="Queued").count(),
        "approved_requests": BorrowRequest.query.filter_by(status="Approved").count(),
        "rejected_requests": BorrowRequest.query.filter_by(status="Rejected").count(),
        "today_requests": BorrowRequest.query.filter(
            BorrowRequest.request_date >= day_start,
            BorrowRequest.request_date < day_end,
        ).count(),
        "damaged_returns": BorrowHistory.query.filter_by(return_condition="damaged").count(),
        "lost_returns": BorrowHistory.query.filter_by(return_condition="lost").count(),
    }

    return {
        "overview": overview,
        "stats": stats,
        "physical_books": overview.get("physical_books", 0),
        "digital_books": overview.get("digital_books", 0),
        "competition_stats": {
            "active_competitions": active_competitions,
            "participants": participants,
            "certificates_issued": certificates_issued,
            "avg_score": round(float(avg_score or 0), 1),
            "pass_rate": round(float(pass_rate or 0), 1),
        },
        "most_borrowed": most_borrowed,
        "most_active_readers": most_active_readers,
        "recent_activities": recent_activities,
        # keep backward-compatible recent requests for other parts
        "recent_requests": BorrowRequest.query.order_by(desc(BorrowRequest.request_date)).limit(6).all(),
    }


def build_admin_statistics_context():
    """Backward-compatible wrapper for admin routes."""
    data = build_library_analytics()
    overview = data["overview"]

    now = now_local()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    stats = {
        "users": overview["total_users"],
        "students": User.query.filter_by(role=User.ROLE_USER).count(),
        "librarians": User.query.filter_by(role=User.ROLE_LIBRARIAN).count(),
        "admins": User.query.filter_by(role=User.ROLE_ADMIN).count(),
        "blocked_users": User.query.filter_by(is_blocked=True).count(),
        "books": overview["total_books"],
        "borrowed": overview["active_borrowings"],
        "overdue": overview["overdue"],
        "pending_requests": overview["pending_requests"],
        "early_return_candidates": BorrowHistory.query.filter(
            BorrowHistory.status == "Borrowed",
            BorrowHistory.return_date > now,
        ).count(),
        "users_week": overview["users_week"],
        "borrows_week": overview["borrows_week"],
        "queued_requests": BorrowRequest.query.filter_by(status="Queued").count(),
        "approved_requests": BorrowRequest.query.filter_by(status="Approved").count(),
        "rejected_requests": BorrowRequest.query.filter_by(status="Rejected").count(),
        "today_requests": BorrowRequest.query.filter(
            BorrowRequest.request_date >= day_start,
            BorrowRequest.request_date < day_end,
        ).count(),
        "damaged_returns": BorrowHistory.query.filter_by(return_condition="damaged").count(),
        "lost_returns": BorrowHistory.query.filter_by(return_condition="lost").count(),
    }

    active_competitions = (
        ReadingCompetition.query.filter(
            ReadingCompetition.status == ReadingCompetition.STATUS_PUBLISHED,
            ReadingCompetition.start_date <= now,
            ReadingCompetition.end_date >= now,
        ).count()
    )

    return {
        "stats": stats,
        "analytics_data": data,
        "overview": overview,
        "top_readers_overall": data["top_readers_overall"],
        "top_borrowers_overall": data["top_borrowers_overall"],
        "top_competition_leaders": data["top_competition_leaders"],
        "faculty_rankings": data["faculty_rankings"],
        "group_rankings": data["group_rankings"],
        "popular_physical": data["popular_physical"],
        "popular_digital": data["popular_digital"],
        "engagement": data["engagement"],
        "trends": data["trends"],
        "physical_books": overview["physical_books"],
        "digital_books": overview["digital_books"],
        "competition_stats": {
            "active_competitions": active_competitions,
            "participants": sum(r["competitions_joined"] for r in data["top_competition_leaders"]),
            "certificates_issued": sum(r["certificates"] for r in data["top_competition_leaders"]),
            "leaders": len(data["top_competition_leaders"]),
        },
        "recent_requests": BorrowRequest.query.order_by(desc(BorrowRequest.request_date)).limit(8).all(),
    }
