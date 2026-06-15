document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("competitionBuilderForm");
    const questionList = document.getElementById("inlineQuestions");
    const template = document.getElementById("questionCardTemplate");
    const addQuestionBtn = document.getElementById("addQuestionBtn");
    const questionCountLabel = document.getElementById("questionCountLabel");
    const compTypeSelect = document.getElementById("compTypeSelect");
    const facultyGroup = document.getElementById("facultyRestrictionGroup");
    const excelInput = document.getElementById("questionsExcel");
    const excelChosen = document.getElementById("excelFileChosen");

    if (!form || !questionList || !template) {
        return;
    }

    function syncFacultyVisibility() {
        if (!facultyGroup || !compTypeSelect) {
            return;
        }
        facultyGroup.style.display = compTypeSelect.value === "faculty" ? "block" : "none";
    }

    function syncChoiceLabel(checkbox) {
        const item = checkbox.closest(".choice-item");
        if (item) {
            item.classList.toggle("selected", checkbox.checked);
        }
    }

    function updateQuestionNumbers() {
        const cards = Array.from(questionList.querySelectorAll(".inline-question-card"));
        cards.forEach((card, index) => {
            const number = card.querySelector(".question-number");
            if (number) {
                number.textContent = `Question ${index + 1}`;
            }
        });
        if (questionCountLabel) {
            questionCountLabel.textContent = `${cards.length} question${cards.length === 1 ? "" : "s"}`;
        }
    }

    function applyQuestionType(card) {
        const typeSelect = card.querySelector(".question-type-select");
        const type = typeSelect?.value || "single_choice";
        const optionA = card.querySelector(".option-a-input");
        const optionB = card.querySelector(".option-b-input");
        const optionC = card.querySelector(".option-c-input");
        const optionD = card.querySelector(".option-d-input");
        const optionalOptions = card.querySelectorAll(".optional-option");
        const correct = card.querySelector(".correct-answer-input");

        if (type === "true_false") {
            optionA.value = "True";
            optionB.value = "False";
            optionA.readOnly = true;
            optionB.readOnly = true;
            optionC.value = "";
            optionD.value = "";
            optionalOptions.forEach((el) => {
                el.style.display = "none";
                el.querySelector("input").required = false;
            });
            correct.placeholder = "True or False";
        } else {
            optionA.readOnly = false;
            optionB.readOnly = false;
            optionalOptions.forEach((el) => {
                el.style.display = "";
            });
            correct.placeholder = type === "multiple_choice" ? "A,C" : "A";
        }
    }

    function fillCard(card, data = {}) {
        card.querySelector(".question-text-input").value = data.question_text || "";
        card.querySelector(".question-type-select").value = data.question_type || "single_choice";
        card.querySelector(".option-a-input").value = data.option_a || "";
        card.querySelector(".option-b-input").value = data.option_b || "";
        card.querySelector(".option-c-input").value = data.option_c || "";
        card.querySelector(".option-d-input").value = data.option_d || "";
        card.querySelector(".correct-answer-input").value = data.correct_answer || "";
        card.querySelector(".question-points-input").value = data.points || 1;
        applyQuestionType(card);
    }

    function addQuestion(data = {}) {
        if (window.questionsLocked) {
            return;
        }
        const fragment = template.content.cloneNode(true);
        const card = fragment.querySelector(".inline-question-card");
        fillCard(card, data);

        card.querySelector(".question-type-select").addEventListener("change", () => applyQuestionType(card));
        card.querySelector(".remove-question-btn").addEventListener("click", () => {
            card.remove();
            updateQuestionNumbers();
        });

        questionList.appendChild(card);
        updateQuestionNumbers();
    }

    function validateQuestions() {
        const cards = Array.from(questionList.querySelectorAll(".inline-question-card"));
        if (cards.length === 0 && !excelInput?.files.length) {
            alert("Add at least one question or import questions from Excel.");
            return false;
        }

        for (const [index, card] of cards.entries()) {
            const text = card.querySelector(".question-text-input").value.trim();
            const type = card.querySelector(".question-type-select").value;
            const optionA = card.querySelector(".option-a-input").value.trim();
            const optionB = card.querySelector(".option-b-input").value.trim();
            const correct = card.querySelector(".correct-answer-input").value.trim();
            const points = parseInt(card.querySelector(".question-points-input").value || "0", 10);

            if (!text) {
                alert(`Question ${index + 1}: question text is required.`);
                return false;
            }
            if (!optionA || !optionB) {
                alert(`Question ${index + 1}: Option A and B are required.`);
                return false;
            }
            if (!correct) {
                alert(`Question ${index + 1}: correct answer is required.`);
                return false;
            }
            if (type === "single_choice" && correct.split(",").filter(Boolean).length > 1) {
                alert(`Question ${index + 1}: single choice can have only one correct answer.`);
                return false;
            }
            if (!points || points < 1) {
                alert(`Question ${index + 1}: points must be at least 1.`);
                return false;
            }
        }
        return true;
    }

    function validateDates() {
        const start = form.querySelector("input[name='start_date']");
        const end = form.querySelector("input[name='end_date']");
        if (!start.value || !end.value) {
            alert("Start date and end date are required.");
            return false;
        }
        if (new Date(start.value) >= new Date(end.value)) {
            alert("End date must be after start date.");
            return false;
        }
        return true;
    }

    window.submitCompetition = function submitCompetition(status) {
        const title = form.querySelector("input[name='title']");
        if (!title.value.trim()) {
            alert("Competition title is required.");
            title.focus();
            return;
        }
        if (!validateDates() || !validateQuestions()) {
            return;
        }
        document.getElementById("competitionStatus").value = status;
        form.submit();
    };

    compTypeSelect?.addEventListener("change", syncFacultyVisibility);
    document.querySelectorAll(".choice-item input[type='checkbox']").forEach((checkbox) => {
        syncChoiceLabel(checkbox);
        checkbox.addEventListener("change", () => syncChoiceLabel(checkbox));
    });

    addQuestionBtn?.addEventListener("click", () => addQuestion());
    excelInput?.addEventListener("change", () => {
        if (!excelChosen) {
            return;
        }
        const fileName = excelInput.files?.[0]?.name;
        excelChosen.classList.toggle("show", Boolean(fileName));
        excelChosen.querySelector("span").textContent = fileName || "";
    });

    syncFacultyVisibility();
    const initial = Array.isArray(window.initialCompetitionQuestions) ? window.initialCompetitionQuestions : [];
    if (!window.questionsLocked) {
        if (initial.length) {
            initial.forEach((item) => addQuestion(item));
        } else {
            addQuestion();
        }
    } else {
        initial.forEach((item) => {
            const fragment = template.content.cloneNode(true);
            const card = fragment.querySelector(".inline-question-card");
            fillCard(card, item);
            card.querySelectorAll("input, textarea, select, button").forEach((control) => {
                control.disabled = true;
            });
            questionList.appendChild(card);
        });
        updateQuestionNumbers();
    }
});
