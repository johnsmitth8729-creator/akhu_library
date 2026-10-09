from __future__ import annotations

from typing import Any
from sqlalchemy import func, case
from app import db
from app.models.user import User
from app.models.book import DigitalBook, ReadingProgress, BookRead
from app.models.borrow import BorrowRequest, BorrowHistory, FavoriteBook
from app.models.system import Review
from app.models.competition import (
    QuizAttempt,
    CompetitionCertificate,
    UserBadge,
)


def get_student_rankings(
    passport_filter: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """
    Calculates unified student ranking combining Top Readers and Top Borrowers analytics.
    Each student record includes their passport_number as the primary unique matching key.
    """
    # 1. Total borrow requests per user
    borrow_counts = dict(
        db.session.query(
            BorrowRequest.user_id,
            func.count(BorrowRequest.id),
        )
        .group_by(BorrowRequest.user_id)
        .all()
    )

    # 2. Total pages read per user (from ReadingProgress)
    pages_by_user = dict(
        db.session.query(
            ReadingProgress.user_id,
            func.coalesce(func.sum(ReadingProgress.current_page), 0),
        )
        .group_by(ReadingProgress.user_id)
        .all()
    )

    # 3. Completed digital books
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

    # 4. Reviews & Favorites
    review_counts = dict(
        db.session.query(Review.user_id, func.count(Review.id))
        .group_by(Review.user_id)
        .all()
    )
    favorite_counts = dict(
        db.session.query(FavoriteBook.user_id, func.count(FavoriteBook.id))
        .group_by(FavoriteBook.user_id)
        .all()
    )

    # 5. Borrow history stats (approved, returned, active, overdue)
    borrow_status_rows = (
        db.session.query(
            BorrowHistory.user_id,
            func.count(BorrowHistory.id),
            func.sum(case((BorrowHistory.status == "Returned", 1), else_=0)).label("returned"),
            func.sum(case((BorrowHistory.status.in_(["Borrowed", "Overdue"]), 1), else_=0)).label("active"),
            func.sum(case((BorrowHistory.status == "Overdue", 1), else_=0)).label("overdue"),
        )
        .group_by(BorrowHistory.user_id)
        .all()
    )
    borrow_status_counts = {
        user_id: {
            "approved": int(total or 0),
            "returned": int(returned or 0),
            "active": int(active or 0),
            "overdue": int(overdue or 0),
        }
        for user_id, total, returned, active, overdue in borrow_status_rows
    }

    # 6. Competition stats
    competition_attempt_counts = dict(
        db.session.query(QuizAttempt.user_id, func.count(QuizAttempt.id))
        .group_by(QuizAttempt.user_id)
        .all()
    )
    certificate_counts = dict(
        db.session.query(CompetitionCertificate.user_id, func.count(CompetitionCertificate.id))
        .group_by(CompetitionCertificate.user_id)
        .all()
    )
    champion_counts = dict(
        db.session.query(UserBadge.user_id, func.count(UserBadge.id))
        .filter(UserBadge.badge_type.in_(["gold", "silver", "bronze"]))
        .group_by(UserBadge.user_id)
        .all()
    )

    # Fetch all student users
    students = User.query.filter_by(role=User.ROLE_USER).all()
    student_records = []

    for s in students:
        uid = s.id
        borrows_total = borrow_counts.get(uid, 0)
        pages_read = int(pages_by_user.get(uid, 0) or 0)
        completed_books = int(completed_by_user.get(uid, 0) or 0)
        reviews_num = int(review_counts.get(uid, 0) or 0)
        favorites_num = int(favorite_counts.get(uid, 0) or 0)

        # Reader score formula
        reader_score = round(
            (borrows_total * 4)
            + (pages_read * 0.12)
            + (completed_books * 6)
            + (reviews_num * 2)
            + (favorites_num * 1),
            1,
        )

        b_stat = borrow_status_counts.get(uid, {})
        approved_requests = b_stat.get("approved", 0)
        returned_books = b_stat.get("returned", 0)
        active_borrowings = b_stat.get("active", 0)
        overdue_books = b_stat.get("overdue", 0)

        # Borrower score formula
        borrow_score = round(
            (approved_requests * 4)
            + (returned_books * 2)
            - (overdue_books * 3)
            + (active_borrowings * 1.5),
            1,
        )

        comp_attempts = competition_attempt_counts.get(uid, 0)
        comp_certs = certificate_counts.get(uid, 0)
        champs = champion_counts.get(uid, 0)

        # Competition score
        competition_score = round(
            (comp_attempts * 3)
            + (comp_certs * 5)
            + (champs * 8),
            1,
        )

        total_score = round(reader_score + borrow_score + competition_score, 1)

        student_records.append({
            "user_id": s.id,
            "passport_number": (s.passport_number or "").strip() or None,
            "fullname": s.fullname,
            "username": s.username,
            "faculty": s.faculty_display or s.faculty or "—",
            "group": s.group_name or "—",
            "last_active": s.last_activity_at.strftime("%Y-%m-%d %H:%M") if s.last_activity_at else None,
            "analytics": {
                "pages_read": pages_read,
                "books_completed": completed_books,
                "books_borrowed": approved_requests,
                "books_returned": returned_books,
                "active_borrowings": active_borrowings,
                "overdue_books": overdue_books,
                "competitions_joined": comp_attempts,
                "certificates_earned": comp_certs,
                "champion_titles": champs,
                "reader_score": reader_score,
                "borrow_score": borrow_score,
                "competition_score": competition_score,
                "total_score": total_score,
            },
            "total_score": total_score,
        })

    # Sort descending by total_score, tie-break on pages_read then returned_books
    student_records.sort(
        key=lambda item: (
            item["total_score"],
            item["analytics"]["pages_read"],
            item["analytics"]["books_returned"],
        ),
        reverse=True,
    )

    # Assign rank (1-indexed)
    for index, record in enumerate(student_records, start=1):
        record["rank"] = index

    # If passport_filter is specified, search for that exact student
    if passport_filter:
        normalized_filter = passport_filter.strip().upper()
        matching_student = None
        for record in student_records:
            if record["passport_number"] and record["passport_number"].strip().upper() == normalized_filter:
                matching_student = record
                break

        if matching_student:
            return {
                "success": True,
                "found": True,
                "student": matching_student,
            }
        return {
            "success": True,
            "found": False,
            "message": f"Student with passport '{passport_filter}' not found.",
        }

    # If limit is specified
    final_records = student_records[:limit] if limit and limit > 0 else student_records

    return {
        "success": True,
        "total_students": len(student_records),
        "returned_count": len(final_records),
        "rankings": final_records,
    }
