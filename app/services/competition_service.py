from __future__ import annotations

import json
import random
from app import db
from app.models import (
    ReadingCompetition,
    CompetitionBook,
    CompetitionFaculty,
    CompetitionGroup,
    CompetitionQuestion,
    Question,
    QuestionOption,
    QuizAttempt,
    QuizAttemptAnswer,
)
from app.utils.datetime import now_local


def user_can_enter_competition(user, competition: ReadingCompetition) -> tuple[bool, str]:
    if competition.status != ReadingCompetition.STATUS_PUBLISHED:
        return False, "This competition is not published."

    now = now_local()
    if now < competition.start_date:
        return False, "This competition has not started yet."
    if now > competition.end_date:
        return False, "This competition has ended."

    # User role check
    from app.models import User
    if user.role != User.ROLE_USER:
        return False, "Only library members can participate."

    if competition.competition_type == ReadingCompetition.TYPE_FACULTY:
        allowed = {r.faculty_id for r in competition.faculty_restrictions}
        if user.faculty_id not in allowed:
            return False, "Your faculty is not eligible for this competition."

    if competition.competition_type == ReadingCompetition.TYPE_GROUP:
        allowed = {r.group_name for r in competition.group_restrictions}
        if (user.group_name or "") not in allowed:
            return False, "Your group is not eligible for this competition."

    return True, ""


def get_participant_count(competition_id: int) -> int:
    from sqlalchemy import func
    return db.session.query(func.count(func.distinct(QuizAttempt.user_id))).filter(
        QuizAttempt.competition_id == competition_id
    ).scalar() or 0


def get_user_participation_state(user_id: int, competition_id: int) -> str:
    attempts = QuizAttempt.query.filter_by(user_id=user_id, competition_id=competition_id).all()
    if not attempts:
        return "not_started"
    if any(a.status == QuizAttempt.STATUS_IN_PROGRESS for a in attempts):
        return "in_progress"
    if any(a.status == QuizAttempt.STATUS_COMPLETED for a in attempts):
        return "completed"
    return "not_started"


def get_user_attempt_count(user_id: int, competition_id: int) -> int:
    return QuizAttempt.query.filter_by(
        user_id=user_id,
        competition_id=competition_id,
    ).count()


def get_best_completed_attempt(user_id: int, competition_id: int) -> QuizAttempt | None:
    from sqlalchemy import desc
    return (
        QuizAttempt.query.filter_by(
            user_id=user_id,
            competition_id=competition_id,
            status=QuizAttempt.STATUS_COMPLETED,
        )
        .order_by(desc(QuizAttempt.score), QuizAttempt.completion_seconds.asc())
        .first()
    )


def can_start_attempt(user, competition: ReadingCompetition) -> tuple[bool, str]:
    ok, msg = user_can_enter_competition(user, competition)
    if not ok:
        return False, msg

    in_progress = QuizAttempt.query.filter_by(
        user_id=user.id,
        competition_id=competition.id,
        status=QuizAttempt.STATUS_IN_PROGRESS,
    ).first()
    if in_progress:
        return True, "resume"

    if competition.prevent_reopen_completed:
        best = get_best_completed_attempt(user.id, competition.id)
        if best:
            return False, "You have already completed this competition."

    count = get_user_attempt_count(user.id, competition.id)
    if count >= competition.max_attempts:
        return False, "You have used all allowed attempts."

    if not competition.competition_questions:
        return False, "This competition has no questions yet."

    if competition.total_points <= 0:
        return False, "This competition has no scorable questions."

    return True, "new"


def build_question_order(competition: ReadingCompetition) -> list[int]:
    if competition.randomize_questions:
        ids = [cq.question_id for cq in competition.competition_questions]
        random.shuffle(ids)
    else:
        pairs = sorted(
            competition.competition_questions,
            key=lambda cq: cq.sort_order,
        )
        ids = [cq.question_id for cq in pairs]
    return ids


def build_options_order(question: Question, randomize: bool) -> list[int]:
    ids = [o.id for o in question.options]
    if randomize:
        random.shuffle(ids)
    else:
        ids = [o.id for o in sorted(question.options, key=lambda x: x.sort_order)]
    return ids


def start_quiz_attempt(user, competition: ReadingCompetition) -> QuizAttempt:
    can, mode = can_start_attempt(user, competition)
    if not can and mode != "resume":
        raise ValueError(mode or "Cannot start attempt.")

    if mode == "resume":
        return QuizAttempt.query.filter_by(
            user_id=user.id,
            competition_id=competition.id,
            status=QuizAttempt.STATUS_IN_PROGRESS,
        ).first()

    attempt_num = get_user_attempt_count(user.id, competition.id) + 1
    order = build_question_order(competition)

    attempt = QuizAttempt(
        user_id=user.id,
        competition_id=competition.id,
        attempt_number=attempt_num,
        status=QuizAttempt.STATUS_IN_PROGRESS,
        question_order_json=json.dumps(order),
        max_score=sum(
            (cq.points_override or cq.question.points)
            for cq in competition.competition_questions
        ),
    )
    db.session.add(attempt)
    db.session.commit()
    return attempt


def get_attempt_questions(attempt: QuizAttempt) -> list[Question]:
    order = json.loads(attempt.question_order_json or "[]")
    questions = {q.id: q for q in Question.query.filter(Question.id.in_(order)).all()}
    return [questions[qid] for qid in order if qid in questions]


def grade_answer(question: Question, selected_ids: list[int]) -> tuple[bool, int]:
    correct = set(question.correct_option_ids())
    selected = set(selected_ids)
    is_correct = correct == selected and len(correct) > 0
    points = question.points if is_correct else 0
    return is_correct, points


def save_draft_answer(attempt_id: int, question_id: int, selected_option_ids: list[int]) -> bool:
    attempt = QuizAttempt.query.get(attempt_id)
    if not attempt or attempt.status != QuizAttempt.STATUS_IN_PROGRESS:
        return False

    ans = QuizAttemptAnswer.query.filter_by(attempt_id=attempt_id, question_id=question_id).first()
    if not ans:
        ans = QuizAttemptAnswer(attempt_id=attempt_id, question_id=question_id)
        db.session.add(ans)
    
    ans.selected_option_ids = json.dumps(selected_option_ids)
    db.session.commit()
    return True


def submit_attempt(attempt: QuizAttempt, answers_payload: dict) -> QuizAttempt:
    if attempt.status != QuizAttempt.STATUS_IN_PROGRESS:
        raise ValueError("Attempt already submitted.")

    competition = attempt.competition
    questions = {q.id: q for q in get_attempt_questions(attempt)}
    cq_map = {
        cq.question_id: cq
        for cq in competition.competition_questions
    }

    # Persist the submitted state for every question. Missing keys mean the
    # participant left the question blank or cleared previous checkbox choices.
    for qid in questions:
        option_ids = answers_payload.get(str(qid), [])
        if isinstance(option_ids, int):
            option_ids = [option_ids]
        elif isinstance(option_ids, str):
            try:
                option_ids = [int(option_ids)]
            except ValueError:
                option_ids = []
        else:
            option_ids = [
                int(option_id)
                for option_id in option_ids
                if str(option_id).isdigit()
            ]

        ans = QuizAttemptAnswer.query.filter_by(attempt_id=attempt.id, question_id=qid).first()
        if not ans:
            ans = QuizAttemptAnswer(attempt_id=attempt.id, question_id=qid)
            db.session.add(ans)
        ans.selected_option_ids = json.dumps(option_ids)

    db.session.flush()

    # Grade all answers currently saved in the database for this attempt
    correct = 0
    wrong = 0
    total_score = 0

    saved_answers = QuizAttemptAnswer.query.filter_by(attempt_id=attempt.id).all()
    answered_qids = {ans.question_id for ans in saved_answers}

    for ans in saved_answers:
        question = questions.get(ans.question_id)
        if not question:
            continue

        selected_ids = json.loads(ans.selected_option_ids or "[]")
        is_correct, points = grade_answer(question, selected_ids)

        if is_correct:
            correct += 1
        else:
            wrong += 1

        cq = cq_map.get(ans.question_id)
        if cq and cq.points_override:
            points = cq.points_override if is_correct else 0

        total_score += points
        ans.is_correct = is_correct
        ans.points_earned = points

    # Account for unanswered questions
    for q in questions.values():
        if q.id not in answered_qids:
            wrong += 1
            # Add empty answer log
            db.session.add(QuizAttemptAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_option_ids="[]",
                is_correct=False,
                points_earned=0,
            ))

    now = now_local()
    elapsed = int((now - attempt.started_at).total_seconds())
    if competition.time_limit_minutes:
        limit = competition.time_limit_minutes * 60
        if elapsed > limit:
            elapsed = limit

    max_score = attempt.max_score or competition.total_points
    if max_score <= 0:
        raise ValueError("This attempt cannot be graded because max score is zero.")
    percentage = round((total_score / max_score) * 100, 1)

    attempt.status = QuizAttempt.STATUS_COMPLETED
    attempt.completed_at = now
    attempt.correct_count = correct
    attempt.wrong_count = wrong
    attempt.score = total_score
    attempt.max_score = max_score
    attempt.percentage = percentage
    attempt.completion_seconds = elapsed
    attempt.ranking_score = round(
        percentage * 1000 - elapsed * 0.1,
        2,
    )

    db.session.commit()

    # Recalculate ranks and award badges (circular dependencies resolved by importing inside function)
    from app.services.ranking_service import recalculate_ranks, award_badges_and_certificates
    recalculate_ranks(competition.id)
    award_badges_and_certificates(competition)

    return attempt
