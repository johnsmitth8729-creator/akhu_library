from __future__ import annotations

from typing import Any
from sqlalchemy import func
from app import db
from app.models.user import User
from app.models.competition import (
    ReadingCompetition,
    QuizAttempt,
    UserBadge,
    CompetitionCertificate,
)
from app.utils.datetime import now_local


def get_competitions_rankings_summary(
    limit: int | None = None,
    status_filter: str | None = None,
) -> dict[str, Any]:
    """
    Returns high-level statistics and top winners for all reading competitions.
    """
    query = ReadingCompetition.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    else:
        # Default: published, closed, or all active non-draft competitions
        query = query.filter(ReadingCompetition.status != ReadingCompetition.STATUS_DRAFT)

    query = query.order_by(ReadingCompetition.start_date.desc())

    if limit and limit > 0:
        query = query.limit(limit)

    competitions = query.all()
    results = []

    for comp in competitions:
        # Participant count
        total_participants = db.session.query(func.count(func.distinct(QuizAttempt.user_id))).filter(
            QuizAttempt.competition_id == comp.id
        ).scalar() or 0

        # Attempt stats
        total_attempts = QuizAttempt.query.filter_by(competition_id=comp.id).count()
        completed_attempts = QuizAttempt.query.filter_by(
            competition_id=comp.id,
            status=QuizAttempt.STATUS_COMPLETED,
        ).count()

        # Top winners (from ranked attempts)
        top_attempts = (
            QuizAttempt.query.filter_by(
                competition_id=comp.id,
                status=QuizAttempt.STATUS_COMPLETED,
            )
            .filter(QuizAttempt.rank_position.isnot(None))
            .order_by(QuizAttempt.rank_position.asc(), QuizAttempt.score.desc())
            .limit(comp.top_winners_count or 3)
            .all()
        )

        winners = []
        for att in top_attempts:
            user = att.user
            winners.append({
                "rank_position": att.rank_position,
                "medal": att.medal,
                "score": att.score,
                "percentage": round(att.percentage or 0.0, 1),
                "completion_seconds": att.completion_seconds,
                "fullname": user.fullname if user else "Unknown",
                "passport_number": user.passport_number if user else None,
                "faculty": user.faculty if user else None,
                "group": user.group_name if user else None,
            })

        results.append({
            "id": comp.id,
            "title": comp.title,
            "description": comp.description,
            "competition_type": comp.competition_type,
            "status": comp.status,
            "lifecycle_status": comp.lifecycle_status,
            "start_date": comp.start_date.isoformat() if comp.start_date else None,
            "end_date": comp.end_date.isoformat() if comp.end_date else None,
            "question_count": comp.question_count,
            "total_points": comp.total_points,
            "passing_score": comp.passing_score,
            "time_limit_minutes": comp.time_limit_minutes,
            "top_winners_count": comp.top_winners_count,
            "total_participants": total_participants,
            "total_attempts": total_attempts,
            "completed_attempts": completed_attempts,
            "top_winners": winners,
        })

    return {
        "success": True,
        "total_competitions": len(results),
        "generated_at": now_local().isoformat(),
        "competitions": results,
    }


def get_competition_detail_ranking(
    competition_id: int,
    limit: int | None = None,
) -> dict[str, Any]:
    """
    Returns full ranking and detailed leaderboard for a specific competition.
    """
    comp = ReadingCompetition.query.get(competition_id)
    if not comp:
        return {
            "success": False,
            "error": "Competition not found.",
        }

    # Best completed attempts per user
    ranked_attempts = (
        QuizAttempt.query.filter_by(
            competition_id=comp.id,
            status=QuizAttempt.STATUS_COMPLETED,
        )
        .filter(QuizAttempt.rank_position.isnot(None))
        .order_by(QuizAttempt.rank_position.asc(), QuizAttempt.score.desc())
    )

    if limit and limit > 0:
        ranked_attempts = ranked_attempts.limit(limit)

    attempts_list = ranked_attempts.all()

    # Calculate statistics
    total_participants = db.session.query(func.count(func.distinct(QuizAttempt.user_id))).filter(
        QuizAttempt.competition_id == comp.id
    ).scalar() or 0

    all_completed = QuizAttempt.query.filter_by(
        competition_id=comp.id,
        status=QuizAttempt.STATUS_COMPLETED,
    ).all()

    completed_count = len(all_completed)
    passed_count = sum(1 for a in all_completed if (a.percentage or 0) >= comp.passing_score)
    scores = [a.score for a in all_completed if a.score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    highest_score = max(scores) if scores else 0
    passing_rate = round((passed_count / completed_count) * 100.0, 1) if completed_count > 0 else 0.0

    leaderboard = []
    for att in attempts_list:
        user = att.user
        cert = att.certificate
        leaderboard.append({
            "rank_position": att.rank_position,
            "medal": att.medal,
            "fullname": user.fullname if user else "Unknown",
            "passport_number": user.passport_number if user else None,
            "faculty": user.faculty if user else None,
            "group": user.group_name if user else None,
            "score": att.score,
            "max_score": att.max_score or comp.total_points,
            "percentage": round(att.percentage or 0.0, 1),
            "passed": att.passed,
            "completion_seconds": att.completion_seconds,
            "completed_at": att.completed_at.isoformat() if att.completed_at else None,
            "certificate_verification_code": cert.verification_code if cert else None,
        })

    return {
        "success": True,
        "competition": {
            "id": comp.id,
            "title": comp.title,
            "description": comp.description,
            "competition_type": comp.competition_type,
            "status": comp.status,
            "lifecycle_status": comp.lifecycle_status,
            "start_date": comp.start_date.isoformat() if comp.start_date else None,
            "end_date": comp.end_date.isoformat() if comp.end_date else None,
            "question_count": comp.question_count,
            "total_points": comp.total_points,
            "passing_score": comp.passing_score,
            "time_limit_minutes": comp.time_limit_minutes,
        },
        "statistics": {
            "total_participants": total_participants,
            "completed_count": completed_count,
            "passed_count": passed_count,
            "passing_rate_percentage": passing_rate,
            "average_score": avg_score,
            "highest_score": highest_score,
        },
        "leaderboard_count": len(leaderboard),
        "leaderboard": leaderboard,
    }


def get_student_competition_ranking(passport_number: str) -> dict[str, Any]:
    """
    Returns a single student's competition achievements and history across all competitions.
    """
    clean_passport = "".join(passport_number.split()).upper()

    user = User.query.filter(
        func.upper(func.replace(User.passport_number, " ", "")) == clean_passport
    ).first()

    if not user:
        return {
            "success": False,
            "found": False,
            "error": f"No student found with passport number '{passport_number}'.",
        }

    # All attempts for this student
    attempts = (
        QuizAttempt.query.filter_by(user_id=user.id)
        .order_by(QuizAttempt.started_at.desc())
        .all()
    )

    completed_attempts = [a for a in attempts if a.status == QuizAttempt.STATUS_COMPLETED]

    # Medals won
    gold_count = sum(1 for a in completed_attempts if a.medal == "gold")
    silver_count = sum(1 for a in completed_attempts if a.medal == "silver")
    bronze_count = sum(1 for a in completed_attempts if a.medal == "bronze")
    total_medals = gold_count + silver_count + bronze_count

    # Best rank
    ranked_positions = [a.rank_position for a in completed_attempts if a.rank_position]
    best_rank = min(ranked_positions) if ranked_positions else None

    # Badges count
    badges_count = UserBadge.query.filter_by(user_id=user.id).count()

    # Certificates count
    certs_count = CompetitionCertificate.query.filter_by(user_id=user.id).count()

    # History list
    history = []
    seen_comps = set()
    for att in completed_attempts:
        comp = att.competition
        if not comp:
            continue
        seen_comps.add(comp.id)
        cert = att.certificate
        history.append({
            "competition_id": comp.id,
            "competition_title": comp.title,
            "competition_type": comp.competition_type,
            "attempt_number": att.attempt_number,
            "rank_position": att.rank_position,
            "medal": att.medal,
            "score": att.score,
            "max_score": att.max_score or comp.total_points,
            "percentage": round(att.percentage or 0.0, 1),
            "passed": att.passed,
            "completion_seconds": att.completion_seconds,
            "completed_at": att.completed_at.isoformat() if att.completed_at else None,
            "certificate_verification_code": cert.verification_code if cert else None,
        })

    return {
        "success": True,
        "found": True,
        "student": {
            "fullname": user.fullname,
            "passport_number": user.passport_number,
            "faculty": user.faculty,
            "group": user.group_name,
            "email": user.email,
        },
        "overview": {
            "competitions_joined": len({a.competition_id for a in attempts}),
            "competitions_completed": len(seen_comps),
            "total_attempts": len(attempts),
            "medals": {
                "total": total_medals,
                "gold": gold_count,
                "silver": silver_count,
                "bronze": bronze_count,
            },
            "total_badges": badges_count,
            "total_certificates": certs_count,
            "best_rank": best_rank,
        },
        "history": history,
    }


def get_overall_competitions_leaderboard(limit: int = 50) -> dict[str, Any]:
    """
    University-wide all-time leaderboard ranking students across all reading competitions.
    Weighted scoring formula:
      - Gold medal: 15 pts
      - Silver medal: 10 pts
      - Bronze medal: 6 pts
      - Passed competition: 3 pts
      - Points scored: 1 pt per 10 points scored
    """
    completed_attempts = (
        QuizAttempt.query.filter_by(status=QuizAttempt.STATUS_COMPLETED)
        .all()
    )

    user_stats: dict[int, dict[str, Any]] = {}
    for att in completed_attempts:
        uid = att.user_id
        if uid not in user_stats:
            user = att.user
            user_stats[uid] = {
                "user_id": uid,
                "fullname": user.fullname if user else "Unknown",
                "passport_number": user.passport_number if user else None,
                "faculty": user.faculty if user else None,
                "group": user.group_name if user else None,
                "competitions_completed": 0,
                "gold_medals": 0,
                "silver_medals": 0,
                "bronze_medals": 0,
                "total_quiz_points": 0,
                "competition_rating": 0.0,
            }

        stats = user_stats[uid]
        stats["competitions_completed"] += 1
        stats["total_quiz_points"] += (att.score or 0)

        if att.medal == "gold":
            stats["gold_medals"] += 1
            stats["competition_rating"] += 15.0
        elif att.medal == "silver":
            stats["silver_medals"] += 1
            stats["competition_rating"] += 10.0
        elif att.medal == "bronze":
            stats["bronze_medals"] += 1
            stats["competition_rating"] += 6.0

        if att.passed:
            stats["competition_rating"] += 3.0

        stats["competition_rating"] += round((att.score or 0) / 10.0, 1)

    # Sort by rating desc, then gold desc, silver desc, bronze desc
    sorted_patrons = sorted(
        user_stats.values(),
        key=lambda x: (
            -x["competition_rating"],
            -x["gold_medals"],
            -x["silver_medals"],
            -x["bronze_medals"],
            -x["total_quiz_points"],
        ),
    )

    leaderboard = []
    for rank, p in enumerate(sorted_patrons[:limit], start=1):
        leaderboard.append({
            "rank": rank,
            "fullname": p["fullname"],
            "passport_number": p["passport_number"],
            "faculty": p["faculty"],
            "group": p["group"],
            "competition_rating": round(p["competition_rating"], 1),
            "medals": {
                "total": p["gold_medals"] + p["silver_medals"] + p["bronze_medals"],
                "gold": p["gold_medals"],
                "silver": p["silver_medals"],
                "bronze": p["bronze_medals"],
            },
            "competitions_completed": p["competitions_completed"],
            "total_quiz_points": p["total_quiz_points"],
        })

    return {
        "success": True,
        "total_champions": len(leaderboard),
        "generated_at": now_local().isoformat(),
        "leaderboard": leaderboard,
    }
