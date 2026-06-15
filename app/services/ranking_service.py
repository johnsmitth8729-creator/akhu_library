from __future__ import annotations

from app import db
from app.models import CompetitionCertificate, QuizAttempt, ReadingCompetition, UserBadge
from app.utils.datetime import now_local


def _best_attempts_for_competition(competition_id: int) -> list[QuizAttempt]:
    attempts = QuizAttempt.query.filter_by(
        competition_id=competition_id,
        status=QuizAttempt.STATUS_COMPLETED,
    ).all()

    best_by_user: dict[int, QuizAttempt] = {}
    for attempt in attempts:
        existing = best_by_user.get(attempt.user_id)
        if not existing:
            best_by_user[attempt.user_id] = attempt
            continue
        if attempt.score > existing.score:
            best_by_user[attempt.user_id] = attempt
        elif attempt.score == existing.score and (attempt.completion_seconds or 99999) < (
            existing.completion_seconds or 99999
        ):
            best_by_user[attempt.user_id] = attempt

    return sorted(
        best_by_user.values(),
        key=lambda attempt: (
            -attempt.score,
            attempt.completion_seconds or 99999,
            attempt.completed_at or now_local(),
        ),
    )


def recalculate_ranks(competition_id: int):
    QuizAttempt.query.filter_by(competition_id=competition_id).update({
        QuizAttempt.rank_position: None,
    })
    db.session.flush()

    previous_score = None
    current_rank = 0
    for index, attempt in enumerate(_best_attempts_for_competition(competition_id), start=1):
        if previous_score is None or attempt.score != previous_score:
            current_rank = index
            previous_score = attempt.score
        attempt.rank_position = current_rank

    db.session.commit()


def award_badges_and_certificates(competition: ReadingCompetition):
    QuizAttempt.query.filter_by(competition_id=competition.id).update({
        QuizAttempt.medal: None,
    })
    UserBadge.query.filter_by(competition_id=competition.id).delete()
    db.session.flush()

    top_n = competition.top_winners_count or 3
    ranked_attempts = (
        QuizAttempt.query.filter_by(
            competition_id=competition.id,
            status=QuizAttempt.STATUS_COMPLETED,
        )
        .filter(QuizAttempt.rank_position.isnot(None))
        .order_by(QuizAttempt.rank_position.asc(), QuizAttempt.score.desc())
        .all()
    )
    top_attempts = [attempt for attempt in ranked_attempts if (attempt.rank_position or 0) <= top_n]
    passed_attempts = [
        attempt
        for attempt in ranked_attempts
        if (attempt.percentage or 0) >= competition.passing_score
    ]

    certificate_attempt_ids = {attempt.id for attempt in top_attempts} | {
        attempt.id for attempt in passed_attempts
    }
    if certificate_attempt_ids:
        CompetitionCertificate.query.filter_by(competition_id=competition.id).filter(
            CompetitionCertificate.attempt_id.notin_(certificate_attempt_ids)
        ).delete(synchronize_session=False)
    else:
        CompetitionCertificate.query.filter_by(competition_id=competition.id).delete()
    db.session.flush()

    medal_map = {1: "gold", 2: "silver", 3: "bronze"}
    awarded_attempts = set()
    for attempt in top_attempts:
        attempt.medal = medal_map.get(attempt.rank_position)
        badge_type = medal_map.get(attempt.rank_position, UserBadge.BADGE_PARTICIPANT)
        label = f"{competition.title} - Rank #{attempt.rank_position}"
        if attempt.rank_position == 1:
            label = f"Gold - {competition.title}"
        elif attempt.rank_position == 2:
            label = f"Silver - {competition.title}"
        elif attempt.rank_position == 3:
            label = f"Bronze - {competition.title}"

        db.session.add(
            UserBadge(
                user_id=attempt.user_id,
                competition_id=competition.id,
                badge_type=badge_type,
                label=label,
            )
        )
        _ensure_certificate(attempt, competition)
        awarded_attempts.add(attempt.id)

    for attempt in passed_attempts:
        if attempt.id in awarded_attempts:
            continue
        _ensure_certificate(attempt, competition)

    db.session.commit()

    seen = set()
    for attempt in top_attempts + passed_attempts:
        if attempt.id in seen:
            continue
        seen.add(attempt.id)
        if attempt.certificate and not attempt.certificate.pdf_path:
            try:
                from app.services.certificate_generator import generate_certificate_pdf
                generate_certificate_pdf(attempt.certificate)
            except Exception:
                pass


def _ensure_certificate(attempt: QuizAttempt, competition: ReadingCompetition):
    certificate = attempt.certificate or CompetitionCertificate.query.filter_by(
        attempt_id=attempt.id,
    ).first()
    if certificate:
        certificate.position = attempt.rank_position or 0
        certificate.score = attempt.score
        certificate.percentage = attempt.percentage
        return

    db.session.add(
        CompetitionCertificate(
            attempt_id=attempt.id,
            user_id=attempt.user_id,
            competition_id=competition.id,
            position=attempt.rank_position or 0,
            score=attempt.score,
            percentage=attempt.percentage,
            verification_code=CompetitionCertificate.generate_code(),
        )
    )


def get_leaderboard(competition_id: int, limit: int = 20) -> list[QuizAttempt]:
    return (
        QuizAttempt.query.filter_by(
            competition_id=competition_id,
            status=QuizAttempt.STATUS_COMPLETED,
        )
        .filter(QuizAttempt.rank_position.isnot(None))
        .order_by(QuizAttempt.rank_position.asc(), QuizAttempt.score.desc())
        .limit(limit)
        .all()
    )


def get_user_competition_stats(user_id: int) -> dict:
    attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    completed = [attempt for attempt in attempts if attempt.status == QuizAttempt.STATUS_COMPLETED]
    won = [attempt for attempt in completed if attempt.rank_position and attempt.rank_position <= 3]
    badges = UserBadge.query.filter_by(user_id=user_id).count()
    best_rank = min((attempt.rank_position for attempt in completed if attempt.rank_position), default=None)
    return {
        "joined": len({attempt.competition_id for attempt in attempts}),
        "completed": len(completed),
        "won": len(won),
        "badges": badges,
        "best_rank": best_rank,
    }


def get_competition_best_score(user_id: int) -> float:
    attempts = QuizAttempt.query.filter_by(
        user_id=user_id,
        status=QuizAttempt.STATUS_COMPLETED,
    ).all()
    return max((attempt.percentage for attempt in attempts), default=0.0)


def calculate_percentile(attempt: QuizAttempt) -> float:
    ranked = _best_attempts_for_competition(attempt.competition_id)
    total_count = len(ranked)
    if total_count <= 1:
        return 100.0

    try:
        my_index = next(index for index, item in enumerate(ranked) if item.id == attempt.id)
    except StopIteration:
        return 0.0

    return round(((total_count - my_index) / total_count) * 100.0, 1)
