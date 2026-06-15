from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import desc

from app import db
from app.models import QuestionCategory, Question
from app.forms.competition_forms import QuestionCategoryForm

categories_bp = Blueprint("categories", __name__)


def staff_required():
    if not current_user.is_authenticated or not current_user.is_staff:
        flash("Staff access required.", "danger")
        return redirect(url_for("main.home"))
    return None


@categories_bp.route("/")
@login_required
def index():
    err = staff_required()
    if err:
        return err

    categories = QuestionCategory.query.order_by(desc(QuestionCategory.created_at)).all()
    form = QuestionCategoryForm()
    return render_template(
        "competitions/manage/categories.html",
        categories=categories,
        form=form,
    )


@categories_bp.route("/create", methods=["POST"])
@login_required
def create():
    err = staff_required()
    if err:
        return err

    form = QuestionCategoryForm()
    if form.validate_on_submit():
        existing = QuestionCategory.query.filter_by(name=form.name.data.strip()).first()
        if existing:
            flash("Category name already exists.", "danger")
            return redirect(url_for("categories.index"))

        cat = QuestionCategory(
            name=form.name.data.strip(),
            description=form.description.data,
        )
        db.session.add(cat)
        db.session.commit()
        flash("Category created successfully.", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "danger")

    return redirect(url_for("categories.index"))


@categories_bp.route("/<int:category_id>/edit", methods=["POST"])
@login_required
def edit(category_id):
    err = staff_required()
    if err:
        return err

    cat = QuestionCategory.query.get_or_404(category_id)
    form = QuestionCategoryForm()
    # Populate fields from form
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name:
        flash("Category name is required.", "danger")
        return redirect(url_for("categories.index"))

    existing = QuestionCategory.query.filter(
        QuestionCategory.name == name,
        QuestionCategory.id != category_id
    ).first()
    if existing:
        flash("Category name already exists.", "danger")
        return redirect(url_for("categories.index"))

    cat.name = name
    cat.description = description
    db.session.commit()
    flash("Category updated successfully.", "success")
    return redirect(url_for("categories.index"))


@categories_bp.route("/<int:category_id>/delete", methods=["POST"])
@login_required
def delete(category_id):
    err = staff_required()
    if err:
        return err

    cat = QuestionCategory.query.get_or_404(category_id)
    # Check if questions are linked to this category
    q_count = Question.query.filter_by(category_id=category_id).count()
    if q_count > 0:
        flash(f"Cannot delete category '{cat.name}' because it contains {q_count} question(s). Please move or delete the questions first.", "danger")
        return redirect(url_for("categories.index"))

    db.session.delete(cat)
    db.session.commit()
    flash("Category deleted successfully.", "success")
    return redirect(url_for("categories.index"))
