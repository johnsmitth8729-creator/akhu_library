from __future__ import annotations

from app import db
from app.models import Question, QuestionOption, CompetitionQuestion, QuizAttemptAnswer


def create_question(
    question_text: str,
    question_type: str,
    category_id: int | None,
    points: int,
    explanation: str | None,
    book_id: int | None,
    difficulty: str,
    options_data: list[dict],
    created_by_id: int | None,
) -> Question:
    q = Question(
        question_text=question_text.strip(),
        question_type=question_type,
        category_id=category_id or None,
        points=points,
        explanation=explanation.strip() if explanation else None,
        book_id=book_id or None,
        difficulty=difficulty,
        created_by_id=created_by_id,
    )
    db.session.add(q)
    db.session.flush()  # get ID

    if question_type == Question.TYPE_TRUE_FALSE:
        # For True/False, options_data should contain which one is correct
        correct_val = "True"
        for opt in options_data:
            if opt.get("is_correct"):
                correct_val = opt.get("option_text", "True")
        db.session.add(QuestionOption(question_id=q.id, option_text="True", is_correct=(correct_val == "True"), sort_order=0))
        db.session.add(QuestionOption(question_id=q.id, option_text="False", is_correct=(correct_val == "False"), sort_order=1))
    else:
        for idx, opt in enumerate(options_data):
            text = opt.get("option_text", "").strip()
            if not text:
                continue
            db.session.add(
                QuestionOption(
                    question_id=q.id,
                    option_text=text,
                    is_correct=opt.get("is_correct", False),
                    sort_order=idx,
                )
            )

    db.session.commit()
    return q


def update_question(
    question_id: int,
    question_text: str,
    question_type: str,
    category_id: int | None,
    points: int,
    explanation: str | None,
    book_id: int | None,
    difficulty: str,
    options_data: list[dict],
) -> Question:
    q = Question.query.get_or_404(question_id)
    q.question_text = question_text.strip()
    q.question_type = question_type
    q.category_id = category_id or None
    q.points = points
    q.explanation = explanation.strip() if explanation else None
    q.book_id = book_id or None
    q.difficulty = difficulty

    # Recreate options
    QuestionOption.query.filter_by(question_id=q.id).delete()

    if question_type == Question.TYPE_TRUE_FALSE:
        correct_val = "True"
        for opt in options_data:
            if opt.get("is_correct"):
                correct_val = opt.get("option_text", "True")
        db.session.add(QuestionOption(question_id=q.id, option_text="True", is_correct=(correct_val == "True"), sort_order=0))
        db.session.add(QuestionOption(question_id=q.id, option_text="False", is_correct=(correct_val == "False"), sort_order=1))
    else:
        for idx, opt in enumerate(options_data):
            text = opt.get("option_text", "").strip()
            if not text:
                continue
            db.session.add(
                QuestionOption(
                    question_id=q.id,
                    option_text=text,
                    is_correct=opt.get("is_correct", False),
                    sort_order=idx,
                )
            )

    db.session.commit()
    return q


def clone_question(question_id: int, created_by_id: int | None) -> Question:
    q = Question.query.get_or_404(question_id)
    
    new_q = Question(
        question_text=f"{q.question_text} (Copy)",
        question_type=q.question_type,
        category_id=q.category_id,
        points=q.points,
        explanation=q.explanation,
        book_id=q.book_id,
        difficulty=q.difficulty,
        created_by_id=created_by_id,
    )
    db.session.add(new_q)
    db.session.flush()

    for opt in q.options:
        db.session.add(
            QuestionOption(
                question_id=new_q.id,
                option_text=opt.option_text,
                is_correct=opt.is_correct,
                sort_order=opt.sort_order,
            )
        )

    db.session.commit()
    return new_q


def archive_question(question_id: int) -> bool:
    q = Question.query.get_or_404(question_id)
    q.is_archived = True
    q.is_active = False
    db.session.commit()
    return True


def delete_question(question_id: int) -> tuple[bool, str]:
    q = Question.query.get_or_404(question_id)
    # Check if used in active attempts
    used_in_results = QuizAttemptAnswer.query.filter_by(question_id=question_id).count()
    if used_in_results > 0:
        # Soft delete instead by archiving
        archive_question(question_id)
        return False, "Question has student answer history; it was archived instead of deleted."

    db.session.delete(q)
    db.session.commit()
    return True, "Question deleted successfully."


def get_question_stats(question_id: int) -> dict:
    times_used = CompetitionQuestion.query.filter_by(question_id=question_id).count()
    times_answered = QuizAttemptAnswer.query.filter_by(question_id=question_id).count()
    correct_answers = QuizAttemptAnswer.query.filter_by(question_id=question_id, is_correct=True).count()
    
    correct_pct = round((correct_answers / times_answered) * 100, 1) if times_answered > 0 else 0.0
    wrong_pct = round(100.0 - correct_pct, 1) if times_answered > 0 else 0.0
    difficulty_score = round(100.0 - correct_pct, 1) if times_answered > 0 else 0.0

    return {
        "times_used": times_used,
        "times_answered": times_answered,
        "correct_pct": correct_pct,
        "wrong_pct": wrong_pct,
        "difficulty_score": difficulty_score,
    }
